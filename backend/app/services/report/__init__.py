"""
Report 服务模块包

将原 report_agent.py（~2950行）进行模块化拆分，提高可维护性。

模块结构：
    - logger.py  : 日志记录器 (ReportLogger, ReportConsoleLogger)
    - models.py  : 数据模型 (ReportStatus, ReportSection, ReportOutline, Report)
    - agent.py   : 报告生成 Agent (ReportAgent)
    - manager.py : 报告管理器 (ReportManager)

推荐导入方式：
    from app.services.report import ReportAgent, ReportManager
    from app.services.report import ReportStatus, ReportSection, Report
    from app.services.report import ReportLogger

原有的导入方式仍然有效（向后兼容）：
    from app.services.report_agent import ReportAgent, ReportManager
"""

# 从本地模块导入
from .logger import ReportLogger, ReportConsoleLogger
from .models import ReportStatus, ReportSection, ReportOutline, Report
from .agent import ReportAgent
from .manager import ReportManager

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
