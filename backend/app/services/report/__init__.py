"""
Report 服务模块包

将原 report_agent.py（2534行）进行模块化拆分，提高可维护性。

模块结构：
    - logger.py  : 日志记录器 (ReportLogger, ReportConsoleLogger)
    - models.py  : 数据模型 (ReportStatus, ReportSection, ReportOutline, Report)

为保持向后兼容，以下类从原 report_agent 模块重新导出：
    - ReportAgent: 报告生成 Agent
    - ReportManager: 报告管理器

原有的导入方式仍然有效：
    from app.services.report_agent import ReportAgent, ReportManager
    
新的推荐导入方式：
    from app.services.report import ReportAgent, ReportManager
    from app.services.report.models import ReportStatus, ReportSection, Report
    from app.services.report.logger import ReportLogger
"""

# 从本地模块导入
from .logger import ReportLogger, ReportConsoleLogger
from .models import ReportStatus, ReportSection, ReportOutline, Report

# 从原模块导入主要类（保持向后兼容）
# 注意：原 report_agent.py 文件仍然保留，这些类暂时从那里导入
# 后续可以逐步将 ReportAgent 和 ReportManager 也迁移到独立模块
try:
    from ..report_agent import ReportAgent, ReportManager
except ImportError:
    # 如果原模块已完全迁移，从本地模块导入
    ReportAgent = None
    ReportManager = None

__all__ = [
    # 日志相关
    'ReportLogger',
    'ReportConsoleLogger',
    # 数据模型
    'ReportStatus',
    'ReportSection',
    'ReportOutline',
    'Report',
    # 主要服务类
    'ReportAgent',
    'ReportManager',
]
