"""
报告日志记录模块

提供报告生成过程中的日志记录功能。

类:
    ReportLogger: 结构化 JSON 日志记录器
    ReportConsoleLogger: 控制台风格日志记录器
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from ...config_new import get_config
from ...utils.logger import get_logger

logger = get_logger('multimo.report.logger')


class ReportLogger:
    """
    Report Agent 详细日志记录器
    
    在报告文件夹中生成 agent_log.jsonl 文件，记录每一步详细动作。
    每行是一个完整的 JSON 对象，包含时间戳、动作类型、详细内容等。
    """
    
    def __init__(self, report_id: str):
        """
        初始化日志记录器
        
        Args:
            report_id: 报告ID，用于确定日志文件路径
        """
        self.report_id = report_id
        config = get_config()
        self.log_file_path = os.path.join(
            config.UPLOAD_FOLDER, 'reports', report_id, 'agent_log.jsonl'
        )
        self.start_time = datetime.now()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """确保日志文件所在目录存在"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _get_elapsed_time(self) -> float:
        """获取从开始到现在的耗时（秒）"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def log(
        self, 
        action: str, 
        stage: str,
        details: Dict[str, Any],
        section_title: str = None,
        section_index: int = None
    ):
        """
        记录一条日志
        
        Args:
            action: 动作类型
            stage: 当前阶段
            details: 详细内容字典
            section_title: 当前章节标题
            section_index: 当前章节索引
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(self._get_elapsed_time(), 2),
            "report_id": self.report_id,
            "action": action,
            "stage": stage,
            "section_title": section_title,
            "section_index": section_index,
            "details": details
        }
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except IOError as e:
            logger.error(f"Failed to write agent log to {self.log_file_path}: {e}")
    
    def log_start(self, simulation_id: str, graph_id: str, simulation_requirement: str):
        """记录报告生成开始"""
        self.log(
            action="report_start",
            stage="pending",
            details={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "simulation_requirement": simulation_requirement,
                "message": "报告生成任务开始"
            }
        )
    
    def log_planning_start(self):
        """记录大纲规划开始"""
        self.log(
            action="planning_start",
            stage="planning",
            details={"message": "开始规划报告大纲"}
        )
    
    def log_planning_context(self, context: Dict[str, Any]):
        """记录规划时获取的上下文信息"""
        self.log(
            action="planning_context",
            stage="planning",
            details={
                "message": "获取模拟上下文信息",
                "context": context
            }
        )
    
    def log_planning_complete(self, outline_dict: Dict[str, Any]):
        """记录大纲规划完成"""
        self.log(
            action="planning_complete",
            stage="planning",
            details={
                "message": "大纲规划完成",
                "outline": outline_dict
            }
        )
    
    def log_section_start(self, section_title: str, section_index: int):
        """记录章节生成开始"""
        self.log(
            action="section_start",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={"message": f"开始生成章节: {section_title}"}
        )
    
    def log_react_thought(self, section_title: str, section_index: int, iteration: int, thought: str):
        """记录 ReACT 思考过程"""
        self.log(
            action="react_thought",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "thought": thought,
                "message": f"ReACT 第{iteration}轮思考"
            }
        )
    
    def log_tool_call(
        self, 
        section_title: str, 
        section_index: int,
        tool_name: str, 
        parameters: Dict[str, Any],
        iteration: int
    ):
        """记录工具调用"""
        self.log(
            action="tool_call",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "parameters": parameters,
                "message": f"调用工具: {tool_name}"
            }
        )
    
    def log_tool_result(
        self,
        section_title: str,
        section_index: int,
        tool_name: str,
        result: str,
        iteration: int
    ):
        """记录工具调用结果"""
        self.log(
            action="tool_result",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "tool_name": tool_name,
                "result": result,
                "result_length": len(result),
                "message": f"工具 {tool_name} 返回结果"
            }
        )
    
    def log_llm_response(
        self,
        section_title: str,
        section_index: int,
        response: str,
        iteration: int,
        has_tool_calls: bool,
        has_final_answer: bool
    ):
        """记录 LLM 响应"""
        self.log(
            action="llm_response",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "iteration": iteration,
                "response": response,
                "response_length": len(response),
                "has_tool_calls": has_tool_calls,
                "has_final_answer": has_final_answer,
                "message": f"LLM 响应 (工具调用: {has_tool_calls}, 最终答案: {has_final_answer})"
            }
        )
    
    def log_section_content(
        self,
        section_title: str,
        section_index: int,
        content: str,
        tool_calls_count: int,
        is_subsection: bool = False
    ):
        """记录章节内容生成完成"""
        action = "subsection_content" if is_subsection else "section_content"
        self.log(
            action=action,
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": content,
                "content_length": len(content),
                "tool_calls_count": tool_calls_count,
                "is_subsection": is_subsection,
                "message": f"{'子章节' if is_subsection else '主章节'} {section_title} 内容生成完成"
            }
        )
    
    def log_section_full_complete(
        self,
        section_title: str,
        section_index: int,
        full_content: str,
        subsection_count: int
    ):
        """记录完整章节生成完成"""
        self.log(
            action="section_complete",
            stage="generating",
            section_title=section_title,
            section_index=section_index,
            details={
                "content": full_content,
                "content_length": len(full_content),
                "subsection_count": subsection_count,
                "message": f"章节 {section_title} 完整生成完成（含 {subsection_count} 个子章节）"
            }
        )
    
    def log_report_complete(self, total_sections: int, total_time_seconds: float):
        """记录报告生成完成"""
        self.log(
            action="report_complete",
            stage="completed",
            details={
                "total_sections": total_sections,
                "total_time_seconds": round(total_time_seconds, 2),
                "message": "报告生成完成"
            }
        )
    
    def log_error(self, error_message: str, stage: str, section_title: str = None):
        """记录错误"""
        self.log(
            action="error",
            stage=stage,
            section_title=section_title,
            section_index=None,
            details={
                "error": error_message,
                "message": f"发生错误: {error_message}"
            }
        )


class ReportConsoleLogger:
    """
    Report Agent 控制台日志记录器
    
    将控制台风格的日志写入报告文件夹中的 console_log.txt 文件。
    """
    
    def __init__(self, report_id: str):
        """
        初始化控制台日志记录器
        
        Args:
            report_id: 报告ID
        """
        self.report_id = report_id
        config = get_config()
        self.log_file_path = os.path.join(
            config.UPLOAD_FOLDER, 'reports', report_id, 'console_log.txt'
        )
        self._file_handle = None
        self.start_time = datetime.now()
        self._ensure_log_file()
        self._open_file()
    
    def _ensure_log_file(self):
        """确保日志文件所在目录存在"""
        log_dir = os.path.dirname(self.log_file_path)
        os.makedirs(log_dir, exist_ok=True)
    
    def _open_file(self):
        """打开日志文件"""
        try:
            self._file_handle = open(self.log_file_path, 'a', encoding='utf-8')
        except IOError as e:
            logger.error(f"Failed to open console log file: {e}")
    
    def _get_elapsed_time(self) -> str:
        """获取格式化的耗时"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        elif elapsed < 3600:
            return f"{elapsed/60:.1f}m"
        else:
            return f"{elapsed/3600:.1f}h"
    
    def _format_timestamp(self) -> str:
        """格式化时间戳"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _write_line(self, line: str):
        """写入一行日志"""
        if self._file_handle:
            try:
                self._file_handle.write(line + '\n')
                self._file_handle.flush()
            except IOError as e:
                logger.error(f"Failed to write console log: {e}")
    
    def info(self, message: str, prefix: str = "INFO"):
        """记录信息日志"""
        timestamp = self._format_timestamp()
        elapsed = self._get_elapsed_time()
        self._write_line(f"[{timestamp}] [{elapsed}] {prefix}: {message}")
    
    def warning(self, message: str):
        """记录警告日志"""
        self.info(message, "WARNING")
    
    def error(self, message: str):
        """记录错误日志"""
        self.info(message, "ERROR")
    
    def section(self, title: str):
        """记录章节分隔"""
        self._write_line(f"\n{'='*60}")
        self._write_line(f"  {title}")
        self._write_line(f"{'='*60}\n")
    
    def subsection(self, title: str):
        """记录子章节分隔"""
        self._write_line(f"\n{'-'*40}")
        self._write_line(f"  {title}")
        self._write_line(f"{'-'*40}\n")
    
    def tool_call(self, tool_name: str, params: Dict[str, Any]):
        """记录工具调用"""
        params_str = ", ".join(f"{k}={v}" for k, v in params.items())
        self.info(f"🔧 {tool_name}({params_str})", "TOOL")
    
    def tool_result(self, tool_name: str, result_preview: str):
        """记录工具结果"""
        preview = result_preview[:200] + "..." if len(result_preview) > 200 else result_preview
        self.info(f"📋 {tool_name} -> {preview}", "RESULT")
    
    def thinking(self, thought: str):
        """记录思考过程"""
        preview = thought[:300] + "..." if len(thought) > 300 else thought
        self.info(f"💭 {preview}", "THINK")
    
    def progress(self, current: int, total: int, message: str):
        """记录进度"""
        percent = (current / total * 100) if total > 0 else 0
        self.info(f"[{current}/{total}] ({percent:.0f}%) {message}", "PROGRESS")
    
    def close(self):
        """关闭文件句柄"""
        if self._file_handle:
            try:
                self._file_handle.close()
            except IOError:
                pass
            self._file_handle = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
