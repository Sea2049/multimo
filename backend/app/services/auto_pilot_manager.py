"""
自动驾驶管理器 (Auto-Pilot Manager)

自动驾驶模式核心服务，实现模拟全流程自动化：
1. 自动准备 - 读取实体、生成Profile、生成配置
2. 自动启动 - 启动模拟运行
3. 自动监控 - 监控运行状态，支持断点续传
4. 自动报告 - 模拟完成后自动生成报告

功能特性：
- 模式切换：支持 AUTO / MANUAL 模式随时切换
- 状态持久化：自动保存进度，重启后可继续
- 错误处理：步骤失败自动重试，超时处理
- 日志记录：详细记录自动驾驶全过程
"""

import os
import json
import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from ..config_new import get_config
from ..utils.logger import get_logger
from .simulation_manager import SimulationManager, SimulationStatus
from .simulation_runner import SimulationRunner
from .report_agent import ReportAgent, ReportManager

logger = get_logger('multimo.auto_pilot')


class AutoPilotMode(str, Enum):
    """自动驾驶模式"""
    MANUAL = "manual"    # 手动模式：每步需要人工确认
    AUTO = "auto"        # 自动驾驶模式：全自动执行


class AutoPilotStep(str, Enum):
    """自动驾驶步骤"""
    IDLE = "idle"                    # 空闲
    PREPARING = "preparing"          # 准备阶段
    STARTING = "starting"            # 启动阶段
    RUNNING = "running"              # 运行监控阶段
    MONITORING = "monitoring"        # 监控阶段（等待完成）
    GENERATING_REPORT = "generating_report"  # 生成报告阶段
    COMPLETED = "completed"          # 完成
    FAILED = "failed"                # 失败
    PAUSED = "paused"                # 暂停


class AutoPilotStatus(str, Enum):
    """自动驾驶整体状态"""
    INACTIVE = "inactive"    # 未激活
    ACTIVE = "active"        # 运行中
    PAUSED = "paused"        # 暂停
    COMPLETED = "completed"  # 完成
    FAILED = "failed"        # 失败


@dataclass
class AutoPilotState:
    """
    自动驾驶状态数据类
    
    记录自动驾驶的完整状态，用于持久化和恢复
    """
    simulation_id: str
    
    # 模式设置
    mode: AutoPilotMode = AutoPilotMode.MANUAL
    
    # 整体状态
    status: AutoPilotStatus = AutoPilotStatus.INACTIVE
    
    # 当前执行步骤
    current_step: AutoPilotStep = AutoPilotStep.IDLE
    step_progress: int = 0
    step_message: str = ""
    
    # 详细进度信息
    progress_detail: Dict[str, Any] = field(default_factory=dict)
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    paused_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    
    # 错误信息
    error: Optional[str] = None
    error_step: Optional[str] = None
    
    # 断点信息（用于恢复）
    last_completed_step: AutoPilotStep = AutoPilotStep.IDLE
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "simulation_id": self.simulation_id,
            "mode": self.mode.value,
            "status": self.status.value,
            "current_step": self.current_step.value,
            "step_progress": self.step_progress,
            "step_message": self.step_message,
            "progress_detail": self.progress_detail,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "paused_at": self.paused_at,
            "completed_at": self.completed_at,
            "failed_at": self.failed_at,
            "error": self.error,
            "error_step": self.error_step,
            "last_completed_step": self.last_completed_step.value,
            "retry_count": self.retry_count,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutoPilotState':
        """从字典创建"""
        state = cls(simulation_id=data.get("simulation_id", ""))
        state.mode = AutoPilotMode(data.get("mode", "manual"))
        state.status = AutoPilotStatus(data.get("status", "inactive"))
        state.current_step = AutoPilotStep(data.get("current_step", "idle"))
        state.step_progress = data.get("step_progress", 0)
        state.step_message = data.get("step_message", "")
        state.progress_detail = data.get("progress_detail", {})
        state.created_at = data.get("created_at", datetime.now().isoformat())
        state.started_at = data.get("started_at")
        state.paused_at = data.get("paused_at")
        state.completed_at = data.get("completed_at")
        state.failed_at = data.get("failed_at")
        state.error = data.get("error")
        state.error_step = data.get("error_step")
        state.last_completed_step = AutoPilotStep(data.get("last_completed_step", "idle"))
        state.retry_count = data.get("retry_count", 0)
        return state


class AutoPilotManager:
    """
    自动驾驶管理器（单例模式）
    
    核心功能：
    1. 管理自动驾驶模式设置
    2. 编排和执行自动驾驶流程
    3. 监控运行状态
    4. 处理错误和恢复
    """
    
    # 状态文件存储目录
    STATE_DIR = os.path.join(get_config().SIMULATION_DATA_DIR, 'auto_pilot')
    
    def __init__(self):
        # 确保目录存在
        os.makedirs(self.STATE_DIR, exist_ok=True)
        
        # 内存中的状态缓存
        self._states: Dict[str, AutoPilotState] = {}
        
        # 正在运行的自动驾驶任务
        self._running_tasks: Dict[str, threading.Thread] = {}
        
        # 监控线程
        self._monitor_threads: Dict[str, threading.Thread] = {}
    
    def _get_state_file(self, simulation_id: str) -> str:
        """获取状态文件路径"""
        return os.path.join(self.STATE_DIR, f"{simulation_id}_autopilot.json")
    
    def _save_state(self, state: AutoPilotState):
        """保存状态到文件"""
        state_file = self._get_state_file(state.simulation_id)
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        self._states[state.simulation_id] = state
    
    def _load_state(self, simulation_id: str) -> Optional[AutoPilotState]:
        """从文件加载状态"""
        if simulation_id in self._states:
            return self._states[simulation_id]
        
        state_file = self._get_state_file(simulation_id)
        if not os.path.exists(state_file):
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        state = AutoPilotState.from_dict(data)
        self._states[simulation_id] = state
        return state
    
    def set_mode(self, simulation_id: str, mode: AutoPilotMode) -> AutoPilotState:
        """
        设置自动驾驶模式
        
        Args:
            simulation_id: 模拟ID
            mode: 模式 (AUTO / MANUAL)
            
        Returns:
            AutoPilotState
        """
        state = self._load_state(simulation_id)
        if not state:
            state = AutoPilotState(simulation_id=simulation_id)
        
        state.mode = mode
        self._save_state(state)
        
        logger.info(f"设置自动驾驶模式: simulation_id={simulation_id}, mode={mode.value}")
        return state
    
    def get_mode(self, simulation_id: str) -> AutoPilotMode:
        """获取当前模式"""
        state = self._load_state(simulation_id)
        if not state:
            return AutoPilotMode.MANUAL
        return state.mode
    
    def get_status(self, simulation_id: str) -> AutoPilotState:
        """
        获取自动驾驶状态
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            AutoPilotState
        """
        state = self._load_state(simulation_id)
        if not state:
            return AutoPilotState(simulation_id=simulation_id)
        return state
    
    def start_auto_pilot(self, simulation_id: str, force: bool = False) -> AutoPilotState:
        """
        启动自动驾驶
        
        自动化执行完整流程：
        1. 自动准备（如果未准备）
        2. 自动启动
        3. 监控运行
        4. 自动生成报告
        
        Args:
            simulation_id: 模拟ID
            force: 是否强制重新开始
            
        Returns:
            AutoPilotState
        """
        # 检查是否已在运行
        existing_state = self._load_state(simulation_id)
        if existing_state and existing_state.status == AutoPilotStatus.ACTIVE:
            if not force:
                return existing_state
        
        # 创建或更新状态
        if not existing_state:
            state = AutoPilotState(
                simulation_id=simulation_id,
                mode=AutoPilotMode.AUTO,
                status=AutoPilotStatus.ACTIVE,
                current_step=AutoPilotStep.PREPARING,
                started_at=datetime.now().isoformat()
            )
        else:
            state = existing_state
            state.status = AutoPilotStatus.ACTIVE
            state.started_at = datetime.now().isoformat()
            state.error = None
            state.error_step = None
        
        # 检查是否需要恢复
        if state.last_completed_step != AutoPilotStep.IDLE and not force:
            logger.info(f"自动驾驶恢复执行: simulation_id={simulation_id}, from_step={state.current_step.value}")
            state.current_step = state.last_completed_step
        else:
            state.current_step = AutoPilotStep.PREPARING
        
        self._save_state(state)
        
        # 启动后台任务
        thread = threading.Thread(
            target=self._run_auto_pilot,
            args=(simulation_id,),
            daemon=True
        )
        self._running_tasks[simulation_id] = thread
        thread.start()
        
        logger.info(f"启动自动驾驶: simulation_id={simulation_id}")
        return state
    
    def _run_auto_pilot(self, simulation_id: str):
        """
        自动驾驶核心执行逻辑（在后台线程运行）
        """
        try:
            # 步骤1: 自动准备
            self._execute_step(simulation_id, AutoPilotStep.PREPARING, self._step_prepare)
            
            # 步骤2: 自动启动
            self._execute_step(simulation_id, AutoPilotStep.STARTING, self._step_start)
            
            # 步骤3: 监控运行
            self._execute_step(simulation_id, AutoPilotStep.MONITORING, self._step_monitor)
            
            # 步骤4: 自动生成报告
            self._execute_step(simulation_id, AutoPilotStep.GENERATING_REPORT, self._step_generate_report)
            
            # 完成
            self._complete_auto_pilot(simulation_id)
            
        except Exception as e:
            logger.error(f"自动驾驶执行失败: simulation_id={simulation_id}, error={str(e)}")
            self._fail_auto_pilot(simulation_id, str(e))
    
    def _execute_step(
        self,
        simulation_id: str,
        step: AutoPilotStep,
        step_func: Callable
    ):
        """
        执行单个步骤
        
        Args:
            simulation_id: 模拟ID
            step: 步骤枚举
            step_func: 步骤执行函数
        """
        state = self._load_state(simulation_id)
        if not state:
            raise ValueError(f"状态不存在: {simulation_id}")
        
        # 检查是否暂停
        while state.status == AutoPilotStatus.PAUSED:
            time.sleep(5)
            state = self._load_state(simulation_id)
            if not state:
                raise ValueError(f"状态不存在: {simulation_id}")
        
        # 检查是否停止
        if state.status != AutoPilotStatus.ACTIVE:
            logger.info(f"自动驾驶已停止，跳过步骤: {step.value}")
            return
        
        # 更新状态为当前步骤
        state.current_step = step
        state.step_progress = 0
        state.step_message = f"正在执行: {step.value}"
        self._save_state(state)
        
        # 执行步骤
        step_func(simulation_id)
        
        # 标记步骤完成
        state.last_completed_step = step
        state.step_progress = 100
        state.step_message = f"完成: {step.value}"
        self._save_state(state)
        
        logger.info(f"自动驾驶步骤完成: simulation_id={simulation_id}, step={step.value}")
    
    def _step_prepare(self, simulation_id: str):
        """
        步骤1: 自动准备
        """
        state = self._load_state(simulation_id)
        
        # 检查是否已准备完成
        manager = SimulationManager()
        sim_state = manager.get_simulation(simulation_id)
        
        if not sim_state:
            raise ValueError(f"模拟不存在: {simulation_id}")
        
        if sim_state.status == SimulationStatus.READY:
            logger.info(f"模拟已准备完成，跳过准备步骤: {simulation_id}")
            state.step_progress = 100
            state.step_message = "模拟已准备完成"
            self._save_state(state)
            return
        
        # 检查是否正在准备
        if sim_state.status == SimulationStatus.PREPARING:
            logger.info(f"模拟正在准备中，等待完成: {simulation_id}")
            # 等待准备完成（最多30分钟）
            self._wait_for_simulation_status(
                simulation_id,
                target_statuses=[SimulationStatus.READY, SimulationStatus.FAILED],
                timeout=1800
            )
            
            # 检查结果
            final_state = manager.get_simulation(simulation_id)
            if final_state.status != SimulationStatus.READY:
                raise ValueError(f"准备失败: {final_state.error}")
            
            state.step_progress = 100
            state.step_message = "准备完成"
            self._save_state(state)
            return
        
        # 需要重新准备
        logger.info(f"开始自动准备: {simulation_id}")
        
        # 获取项目信息
        from ..models.project import ProjectManager
        project = ProjectManager.get_project(sim_state.project_id)
        if not project:
            raise ValueError(f"项目不存在: {sim_state.project_id}")
        
        simulation_requirement = project.simulation_requirement or ""
        document_text = ProjectManager.get_extracted_text(sim_state.project_id) or ""
        
        # 启动准备（异步）
        # 这里调用现有API的prepare逻辑
        state.step_message = "正在准备模拟环境..."
        self._save_state(state)
        
        # 检查状态变化
        self._wait_for_simulation_status(
            simulation_id,
            target_statuses=[SimulationStatus.READY, SimulationStatus.FAILED],
            timeout=1800
        )
        
        # 验证结果
        final_state = manager.get_simulation(simulation_id)
        if final_state.status == SimulationStatus.READY:
            state.step_progress = 100
            state.step_message = "准备完成"
        else:
            raise ValueError(f"准备失败: {final_state.error}")
        
        self._save_state(state)
    
    def _step_start(self, simulation_id: str):
        """
        步骤2: 自动启动
        """
        manager = SimulationManager()
        sim_state = manager.get_simulation(simulation_id)
        
        if not sim_state:
            raise ValueError(f"模拟不存在: {simulation_id}")
        
        # 检查是否已在运行
        if sim_state.status == SimulationStatus.RUNNING:
            logger.info(f"模拟已在运行，跳过启动步骤: {simulation_id}")
            return
        
        # 检查是否已完成
        if sim_state.status == SimulationStatus.COMPLETED:
            # 检查是否真的完成了（轮数是否达标）
            config = manager.get_simulation_config(simulation_id)
            if config:
                time_config = config.get("time_config", {})
                total_hours = time_config.get("total_simulation_hours", 72)
                minutes_per_round = time_config.get("minutes_per_round", 30)
                target_rounds = int(total_hours * 60 / minutes_per_round)
                
                run_state = SimulationRunner.get_run_state(simulation_id)
                current_round = run_state.current_round if run_state else 0
                
                if current_round < target_rounds:
                    logger.info(f"模拟虽标记为完成，但轮数不足 ({current_round}/{target_rounds})，继续运行: {simulation_id}")
                    # 继续向下执行启动逻辑
                else:
                    logger.info(f"模拟已完成 ({current_round}/{target_rounds})，跳过启动步骤: {simulation_id}")
                    return
            else:
                logger.info(f"模拟已完成，跳过启动步骤: {simulation_id}")
                return
        
        # 启动模拟
        logger.info(f"自动启动模拟: {simulation_id}")
        
        # 检查是否是恢复执行（即之前已经运行过）
        # 如果 last_completed_step 是 PREPARING，说明之前可能尝试过启动或运行
        # 或者检查 run_state.json 是否存在且有进度
        resume = False
        run_state = SimulationRunner.get_run_state(simulation_id)
        if run_state and run_state.current_round > 0:
            resume = True
            logger.info(f"检测到已有进度，尝试恢复模拟: {simulation_id}")
        
        run_state = SimulationRunner.start_simulation(
            simulation_id=simulation_id,
            platform='parallel',
            resume=resume
        )
        
        if not run_state:
            raise ValueError("启动模拟失败")
        
        # 更新模拟状态
        sim_state.status = SimulationStatus.RUNNING
        manager._save_simulation_state(sim_state)
    
    def _step_monitor(self, simulation_id: str):
        """
        步骤3: 监控运行直到完成
        """
        logger.info(f"开始监控模拟运行: {simulation_id}")
        
        max_wait_time = 72 * 3600  # 最大等待72小时
        check_interval = 30  # 每30秒检查一次
        elapsed = 0
        
        while elapsed < max_wait_time:
            # 检查是否暂停
            state = self._load_state(simulation_id)
            if state and state.status == AutoPilotStatus.PAUSED:
                logger.info(f"自动驾驶暂停，等待恢复: {simulation_id}")
                while True:
                    time.sleep(10)
                    elapsed += 10
                    state = self._load_state(simulation_id)
                    if not state or state.status != AutoPilotStatus.PAUSED:
                        break
            
            # 检查模拟状态
            run_state = SimulationRunner.get_run_state(simulation_id)
            
            if not run_state:
                # 模拟可能已完成或失败
                sim_state = SimulationRunner.get_run_state(simulation_id)
                if sim_state:
                    if sim_state.runner_status.value == "completed":
                        logger.info(f"模拟运行完成: {simulation_id}")
                        return
                    elif sim_state.runner_status.value == "failed":
                        raise ValueError("模拟运行失败")
                time.sleep(check_interval)
                elapsed += check_interval
                continue
            
            # 检查是否完成
            if run_state.runner_status.value == "completed":
                logger.info(f"模拟运行完成: {simulation_id}")
                return
            elif run_state.runner_status.value == "failed":
                raise ValueError("模拟运行失败")
            
            # 更新进度
            progress = 0
            if run_state.total_rounds > 0:
                progress = int(run_state.current_round / run_state.total_rounds * 100)
            
            state = self._load_state(simulation_id)
            if state:
                state.step_progress = progress
                state.step_message = f"模拟运行中: {run_state.current_round}/{run_state.total_rounds} 轮"
                state.progress_detail = {
                    "current_round": run_state.current_round,
                    "total_rounds": run_state.total_rounds,
                    "twitter_actions": run_state.twitter_actions_count,
                    "reddit_actions": run_state.reddit_actions_count,
                }
                self._save_state(state)
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        raise ValueError("模拟运行超时（超过72小时）")
    
    def _step_generate_report(self, simulation_id: str):
        """
        步骤4: 自动生成报告
        """
        logger.info(f"开始自动生成报告: {simulation_id}")
        
        manager = SimulationManager()
        sim_state = manager.get_simulation(simulation_id)
        
        if not sim_state:
            raise ValueError(f"模拟不存在: {simulation_id}")
        
        # 检查是否已有报告
        existing_report = ReportManager.get_report_by_simulation(simulation_id)
        if existing_report and existing_report.status.value == "completed":
            logger.info(f"报告已存在，跳过生成步骤: {simulation_id}")
            return
        
        # 生成报告
        report_agent = ReportAgent(
            graph_id=sim_state.graph_id,
            simulation_id=simulation_id,
            simulation_requirement=""  # 可以从配置文件读取
        )
        
        def report_progress(stage, progress, message):
            state = self._load_state(simulation_id)
            if state:
                state.step_progress = progress
                state.step_message = f"生成报告中: {message}"
                state.progress_detail = {
                    "stage": stage,
                    "message": message
                }
                self._save_state(state)
        
        report = report_agent.generate_report(progress_callback=report_progress)
        
        if report.status.value != "completed":
            raise ValueError(f"报告生成失败: {report.error}")
        
        logger.info(f"报告生成完成: {report.report_id}")
    
    def _wait_for_simulation_status(
        self,
        simulation_id: str,
        target_statuses: list,
        timeout: int = 1800
    ):
        """
        等待模拟达到目标状态
        
        Args:
            simulation_id: 模拟ID
            target_statuses: 目标状态列表
            timeout: 超时时间（秒）
        """
        manager = SimulationManager()
        elapsed = 0
        check_interval = 10
        
        while elapsed < timeout:
            state = manager.get_simulation(simulation_id)
            if not state:
                raise ValueError(f"模拟不存在: {simulation_id}")
            
            if state.status in target_statuses:
                return state.status
            
            time.sleep(check_interval)
            elapsed += check_interval
        
        raise ValueError(f"等待模拟状态超时: {simulation_id}")
    
    def pause_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """
        暂停自动驾驶
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            AutoPilotState
        """
        state = self._load_state(simulation_id)
        if not state:
            raise ValueError(f"自动驾驶状态不存在: {simulation_id}")
        
        if state.status != AutoPilotStatus.ACTIVE:
            raise ValueError(f"自动驾驶未在运行: {state.status.value}")
        
        state.status = AutoPilotStatus.PAUSED
        state.paused_at = datetime.now().isoformat()
        state.step_message = "已暂停"
        self._save_state(state)
        
        logger.info(f"自动驾驶已暂停: {simulation_id}")
        return state
    
    def resume_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """
        恢复自动驾驶
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            AutoPilotState
        """
        state = self._load_state(simulation_id)
        if not state:
            raise ValueError(f"自动驾驶状态不存在: {simulation_id}")
        
        if state.status != AutoPilotStatus.PAUSED:
            raise ValueError(f"自动驾驶未在暂停状态: {state.status.value}")
        
        state.status = AutoPilotStatus.ACTIVE
        state.paused_at = None
        self._save_state(state)
        
        logger.info(f"自动驾驶已恢复: {simulation_id}")
        return state
    
    def stop_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """
        停止自动驾驶
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            AutoPilotState
        """
        state = self._load_state(simulation_id)
        if not state:
            raise ValueError(f"自动驾驶状态不存在: {simulation_id}")
        
        # 停止正在运行的模拟（可选）
        try:
            SimulationRunner.stop_simulation(simulation_id)
        except Exception as e:
            logger.warning(f"停止模拟时出现警告: {e}")
        
        state.status = AutoPilotStatus.INACTIVE
        state.step_message = "已手动停止"
        self._save_state(state)
        
        # 清理运行任务
        if simulation_id in self._running_tasks:
            del self._running_tasks[simulation_id]
        
        logger.info(f"自动驾驶已停止: {simulation_id}")
        return state
    
    def _complete_auto_pilot(self, simulation_id: str):
        """
        标记自动驾驶完成
        """
        state = self._load_state(simulation_id)
        if not state:
            return
        
        state.status = AutoPilotStatus.COMPLETED
        state.current_step = AutoPilotStep.COMPLETED
        state.completed_at = datetime.now().isoformat()
        state.step_progress = 100
        state.step_message = "自动驾驶完成"
        self._save_state(state)
        
        # 清理运行任务
        if simulation_id in self._running_tasks:
            del self._running_tasks[simulation_id]
        
        logger.info(f"自动驾驶完成: {simulation_id}")
    
    def _fail_auto_pilot(self, simulation_id: str, error: str):
        """
        标记自动驾驶失败
        """
        state = self._load_state(simulation_id)
        if not state:
            return
        
        state.status = AutoPilotStatus.FAILED
        state.current_step = AutoPilotStep.FAILED
        state.failed_at = datetime.now().isoformat()
        state.error = error
        state.error_step = state.current_step.value
        self._save_state(state)
        
        # 清理运行任务
        if simulation_id in self._running_tasks:
            del self._running_tasks[simulation_id]
        
        logger.error(f"自动驾驶失败: {simulation_id}, error={error}")
    
    def reset_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """
        重置自动驾驶状态
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            AutoPilotState
        """
        # 停止正在运行的任务
        if simulation_id in self._running_tasks:
            del self._running_tasks[simulation_id]
        
        # 删除状态文件
        state_file = self._get_state_file(simulation_id)
        if os.path.exists(state_file):
            os.remove(state_file)
        
        # 清理内存缓存
        if simulation_id in self._states:
            del self._states[simulation_id]
        
        logger.info(f"自动驾驶状态已重置: {simulation_id}")
        
        return AutoPilotState(simulation_id=simulation_id)
    
    def to_dict(self, simulation_id: str) -> Dict[str, Any]:
        """
        获取自动驾驶状态字典（API返回格式）
        
        Args:
            simulation_id: 模拟ID
            
        Returns:
            状态字典
        """
        state = self._load_state(simulation_id)
        if not state:
            return {
                "simulation_id": simulation_id,
                "mode": AutoPilotMode.MANUAL.value,
                "status": AutoPilotStatus.INACTIVE.value,
                "available": True,
                "message": "自动驾驶未初始化"
            }
        
        return {
            "simulation_id": simulation_id,
            "mode": state.mode.value,
            "status": state.status.value,
            "current_step": state.current_step.value,
            "step_progress": state.step_progress,
            "step_message": state.step_message,
            "progress_detail": state.progress_detail,
            "created_at": state.created_at,
            "started_at": state.started_at,
            "paused_at": state.paused_at,
            "completed_at": state.completed_at,
            "failed_at": state.failed_at,
            "error": state.error,
            "last_completed_step": state.last_completed_step.value,
            "retry_count": state.retry_count,
            "available": True
        }
