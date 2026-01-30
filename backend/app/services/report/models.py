"""
报告数据模型模块

定义报告相关的数据类和枚举。

类:
    ReportStatus: 报告状态枚举
    ReportSection: 报告章节数据类
    ReportOutline: 报告大纲数据类
    Report: 完整报告数据类
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ReportStatus(str, Enum):
    """报告状态枚举"""
    PENDING = "pending"       # 等待处理
    PLANNING = "planning"     # 规划大纲中
    GENERATING = "generating" # 生成内容中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


@dataclass
class ReportSection:
    """
    报告章节数据类
    
    支持嵌套子章节结构。
    """
    title: str                                              # 章节标题
    content: str = ""                                       # 章节内容
    subsections: List['ReportSection'] = field(default_factory=list)  # 子章节列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "content": self.content,
            "subsections": [s.to_dict() for s in self.subsections]
        }
    
    def to_markdown(self, level: int = 2) -> str:
        """
        转换为 Markdown 格式
        
        Args:
            level: 标题级别（默认为二级标题）
            
        Returns:
            Markdown 格式的章节内容
        """
        md = f"{'#' * level} {self.title}\n\n"
        if self.content:
            md += f"{self.content}\n\n"
        for sub in self.subsections:
            md += sub.to_markdown(level + 1)
        return md
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportSection':
        """从字典创建章节"""
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            subsections=[cls.from_dict(s) for s in data.get("subsections", [])]
        )


@dataclass
class ReportOutline:
    """
    报告大纲数据类
    
    包含报告标题、摘要和章节列表。
    """
    title: str                       # 报告标题
    summary: str                     # 报告摘要
    sections: List[ReportSection]    # 章节列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections]
        }
    
    def to_markdown(self) -> str:
        """
        转换为 Markdown 格式
        
        Returns:
            完整的 Markdown 格式报告
        """
        md = f"# {self.title}\n\n"
        md += f"> {self.summary}\n\n"
        for section in self.sections:
            md += section.to_markdown()
        return md
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportOutline':
        """从字典创建大纲"""
        return cls(
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            sections=[ReportSection.from_dict(s) for s in data.get("sections", [])]
        )


@dataclass
class Report:
    """
    完整报告数据类
    
    包含报告的所有元信息和内容。
    """
    report_id: str                              # 报告ID
    simulation_id: str                          # 关联的模拟ID
    graph_id: str                               # 关联的图谱ID
    simulation_requirement: str                 # 模拟需求描述
    status: ReportStatus                        # 当前状态
    outline: Optional[ReportOutline] = None     # 报告大纲
    markdown_content: str = ""                  # Markdown 格式内容
    created_at: str = ""                        # 创建时间
    completed_at: str = ""                      # 完成时间
    error: Optional[str] = None                 # 错误信息（如果失败）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "simulation_id": self.simulation_id,
            "graph_id": self.graph_id,
            "simulation_requirement": self.simulation_requirement,
            "status": self.status.value,
            "outline": self.outline.to_dict() if self.outline else None,
            "markdown_content": self.markdown_content,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """从字典创建报告"""
        outline_data = data.get("outline")
        return cls(
            report_id=data.get("report_id", ""),
            simulation_id=data.get("simulation_id", ""),
            graph_id=data.get("graph_id", ""),
            simulation_requirement=data.get("simulation_requirement", ""),
            status=ReportStatus(data.get("status", "pending")),
            outline=ReportOutline.from_dict(outline_data) if outline_data else None,
            markdown_content=data.get("markdown_content", ""),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at", ""),
            error=data.get("error")
        )
