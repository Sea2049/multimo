"""
向后兼容模块 - 所有类已迁移到 services/report/ 子包

本模块保留仅为兼容现有的导入语句。
所有功能已迁移至模块化的子包结构：

    services/report/
        __init__.py    - 包入口，统一导出所有类
        logger.py      - ReportLogger, ReportConsoleLogger
        models.py      - ReportStatus, ReportSection, ReportOutline, Report
        agent.py       - ReportAgent
        manager.py     - ReportManager

推荐的新导入方式：
    from app.services.report import (
        ReportLogger, ReportConsoleLogger,
        ReportStatus, ReportSection, ReportOutline, Report,
        ReportAgent, ReportManager,
    )

原有的导入方式仍然有效（通过本模块转发）：
    from app.services.report_agent import ReportAgent, ReportManager
"""

# 从新的模块化子包导入所有类
from app.services.report import (
    ReportLogger,
    ReportConsoleLogger,
    ReportStatus,
    ReportSection,
    ReportOutline,
    Report,
    ReportAgent,
    ReportManager,
)

__all__ = [
    'ReportLogger',
    'ReportConsoleLogger',
    'ReportStatus',
    'ReportSection',
    'ReportOutline',
    'Report',
    'ReportAgent',
    'ReportManager',
]
