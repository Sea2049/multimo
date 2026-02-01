"""
Report Task Worker - 报告生成任务工作器

使用子进程运行报告生成，实现：
1. 任务状态持久化到数据库
2. 支持断点续传（从中断的章节恢复）
3. 与 Flask 主进程隔离，避免重启影响

使用方式：
    worker = ReportTaskWorker()
    task_id = worker.start_report_task(simulation_id, graph_id, simulation_requirement)
    
    # 查询进度
    status = worker.get_task_status(task_id)
    
    # 恢复中断的任务
    worker.recover_interrupted_tasks()
"""

import os
import json
import time
import signal
import multiprocessing
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger
from ..models.task import TaskManager, TaskStatus

logger = get_logger('multimo.report_task_worker')


@dataclass
class ReportCheckpoint:
    """报告生成检查点 - 用于断点续传"""
    report_id: str
    simulation_id: str
    graph_id: str
    simulation_requirement: str
    
    # 大纲信息
    outline_generated: bool = False
    outline_data: Optional[Dict] = None
    
    # 章节生成进度
    total_sections: int = 0
    completed_section_indices: List[int] = None  # 已完成的章节索引
    current_section_index: int = 0  # 当前正在生成的章节索引
    
    # 时间记录
    started_at: str = ""
    last_updated_at: str = ""
    
    def __post_init__(self):
        if self.completed_section_indices is None:
            self.completed_section_indices = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportCheckpoint':
        return cls(**data)
    
    def mark_outline_complete(self, outline_data: Dict, total_sections: int):
        """标记大纲生成完成"""
        self.outline_generated = True
        self.outline_data = outline_data
        self.total_sections = total_sections
        self.last_updated_at = datetime.now().isoformat()
    
    def mark_section_complete(self, section_index: int):
        """标记章节生成完成"""
        if section_index not in self.completed_section_indices:
            self.completed_section_indices.append(section_index)
        self.last_updated_at = datetime.now().isoformat()
    
    def get_next_section_to_generate(self) -> int:
        """获取下一个需要生成的章节索引（从1开始）"""
        for i in range(1, self.total_sections + 1):
            if i not in self.completed_section_indices:
                return i
        return 0  # 所有章节已完成
    
    def is_complete(self) -> bool:
        """检查报告是否已完成"""
        if not self.outline_generated:
            return False
        return len(self.completed_section_indices) >= self.total_sections


class ReportTaskWorker:
    """
    报告任务工作器
    
    管理报告生成任务的创建、执行、恢复
    """
    
    TASK_TYPE = "report_generate"
    
    def __init__(self):
        self.task_manager = TaskManager()
        self._active_processes: Dict[str, multiprocessing.Process] = {}
    
    def start_report_task(
        self,
        simulation_id: str,
        graph_id: str,
        simulation_requirement: str,
        report_id: Optional[str] = None,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        启动报告生成任务
        
        Args:
            simulation_id: 模拟ID
            graph_id: 图谱ID
            simulation_requirement: 模拟需求
            report_id: 报告ID（可选，如果不传则自动生成）
            force_regenerate: 是否强制重新生成
            
        Returns:
            {
                "task_id": "xxx",
                "report_id": "xxx",
                "status": "pending",
                "message": "xxx"
            }
        """
        import uuid
        
        # 生成 report_id
        if not report_id:
            report_id = f"report_{uuid.uuid4().hex[:12]}"
        
        # 检查是否有正在进行的任务
        existing_task = self._find_active_task_for_simulation(simulation_id)
        if existing_task and not force_regenerate:
            return {
                "task_id": existing_task.task_id,
                "report_id": existing_task.metadata.get("report_id"),
                "status": existing_task.status.value,
                "message": "已有报告生成任务正在进行中",
                "already_exists": True
            }
        
        # 创建检查点
        checkpoint = ReportCheckpoint(
            report_id=report_id,
            simulation_id=simulation_id,
            graph_id=graph_id,
            simulation_requirement=simulation_requirement,
            started_at=datetime.now().isoformat()
        )
        
        # 创建任务
        task_id = self.task_manager.create_task(
            task_type=self.TASK_TYPE,
            metadata={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "report_id": report_id,
                "checkpoint": checkpoint.to_dict()
            }
        )
        
        # 启动工作进程
        self._start_worker_process(task_id)
        
        logger.info(f"报告生成任务已启动: task_id={task_id}, report_id={report_id}")
        
        return {
            "task_id": task_id,
            "report_id": report_id,
            "status": "pending",
            "message": "报告生成任务已启动"
        }
    
    def _find_active_task_for_simulation(self, simulation_id: str):
        """查找指定模拟的活跃任务"""
        tasks = self.task_manager.list_tasks(task_type=self.TASK_TYPE)
        for task_dict in tasks:
            if task_dict.get("status") in ["pending", "processing"]:
                metadata = task_dict.get("metadata", {})
                if metadata.get("simulation_id") == simulation_id:
                    return self.task_manager.get_task(task_dict["task_id"])
        return None
    
    def _start_worker_process(self, task_id: str):
        """启动工作进程"""
        # 使用线程而非进程，因为需要访问 Flask 应用上下文
        # 但使用 daemon=False 确保不会随主线程退出
        import threading
        
        thread = threading.Thread(
            target=self._run_report_generation,
            args=(task_id,),
            daemon=False,  # 非守护线程，不会因 Flask 重启而立即终止
            name=f"ReportWorker-{task_id[:8]}"
        )
        thread.start()
        
        logger.info(f"工作线程已启动: {thread.name}")
    
    def _run_report_generation(self, task_id: str):
        """
        执行报告生成（在工作线程中运行）
        
        支持从检查点恢复
        """
        from .report_agent import ReportAgent, ReportManager, ReportStatus, Report
        
        task = self.task_manager.get_task(task_id)
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return
        
        metadata = task.metadata
        checkpoint_data = metadata.get("checkpoint", {})
        checkpoint = ReportCheckpoint.from_dict(checkpoint_data)
        
        report_id = checkpoint.report_id
        simulation_id = checkpoint.simulation_id
        graph_id = checkpoint.graph_id
        simulation_requirement = checkpoint.simulation_requirement
        
        try:
            # 更新任务状态
            self.task_manager.update_task(
                task_id,
                status=TaskStatus.PROCESSING,
                progress=0,
                message="初始化 Report Agent..."
            )
            
            # 创建 Report Agent
            agent = ReportAgent(
                graph_id=graph_id,
                simulation_id=simulation_id,
                simulation_requirement=simulation_requirement
            )
            
            # 定义进度回调
            def progress_callback(stage: str, progress: int, message: str):
                self.task_manager.update_task(
                    task_id,
                    progress=progress,
                    message=f"[{stage}] {message}"
                )
            
            # 生成报告（支持断点续传）
            report = agent.generate_report_with_checkpoint(
                checkpoint=checkpoint,
                progress_callback=progress_callback,
                checkpoint_callback=lambda cp: self._save_checkpoint(task_id, cp)
            )
            
            # 保存报告
            ReportManager.save_report(report)
            
            if report.status == ReportStatus.COMPLETED:
                self.task_manager.complete_task(
                    task_id,
                    result={
                        "report_id": report.report_id,
                        "simulation_id": simulation_id,
                        "status": "completed"
                    }
                )
                logger.info(f"报告生成完成: {report_id}")
            else:
                self.task_manager.fail_task(task_id, report.error or "报告生成失败")
                logger.error(f"报告生成失败: {report_id}, error={report.error}")
                
        except Exception as e:
            logger.error(f"报告生成异常: {e}", exc_info=True)
            self.task_manager.fail_task(task_id, str(e))
    
    def _save_checkpoint(self, task_id: str, checkpoint: ReportCheckpoint):
        """保存检查点到任务元数据"""
        task = self.task_manager.get_task(task_id)
        if task:
            metadata = task.metadata.copy()
            metadata["checkpoint"] = checkpoint.to_dict()
            
            # 更新任务的 metadata（通过 progress_detail 保存）
            self.task_manager.update_task(
                task_id,
                progress_detail={"checkpoint": checkpoint.to_dict()}
            )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.task_manager.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    def recover_interrupted_tasks(self) -> List[str]:
        """
        恢复中断的任务
        
        在服务启动时调用，检查所有处于 pending/processing 状态的报告任务，
        并尝试恢复它们。
        
        Returns:
            恢复的任务ID列表
        """
        recovered_tasks = []
        
        tasks = self.task_manager.list_tasks(task_type=self.TASK_TYPE)
        
        for task_dict in tasks:
            task_id = task_dict.get("task_id")
            status = task_dict.get("status")
            
            if status in ["pending", "processing"]:
                metadata = task_dict.get("metadata", {})
                checkpoint_data = metadata.get("checkpoint") or task_dict.get("progress_detail", {}).get("checkpoint")
                
                if checkpoint_data:
                    checkpoint = ReportCheckpoint.from_dict(checkpoint_data)
                    
                    # 检查是否可以恢复
                    if not checkpoint.is_complete():
                        logger.info(f"发现中断的报告任务: {task_id}, report_id={checkpoint.report_id}")
                        logger.info(f"  - 大纲已生成: {checkpoint.outline_generated}")
                        logger.info(f"  - 已完成章节: {checkpoint.completed_section_indices}/{checkpoint.total_sections}")
                        
                        # 重新启动工作进程
                        self._start_worker_process(task_id)
                        recovered_tasks.append(task_id)
                    else:
                        # 任务实际已完成，更新状态
                        self.task_manager.complete_task(
                            task_id,
                            result={
                                "report_id": checkpoint.report_id,
                                "status": "completed",
                                "recovered": True
                            }
                        )
                else:
                    # 没有检查点，标记为失败
                    self.task_manager.fail_task(
                        task_id,
                        "任务因服务重启而中断，无法恢复（缺少检查点）"
                    )
        
        if recovered_tasks:
            logger.info(f"已恢复 {len(recovered_tasks)} 个中断的报告任务")
        
        return recovered_tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.task_manager.get_task(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            self.task_manager.fail_task(task_id, "任务已被用户取消")
            return True
        return False


# 全局单例
_worker_instance = None

def get_report_task_worker() -> ReportTaskWorker:
    """获取报告任务工作器单例"""
    global _worker_instance
    if _worker_instance is None:
        _worker_instance = ReportTaskWorker()
    return _worker_instance
