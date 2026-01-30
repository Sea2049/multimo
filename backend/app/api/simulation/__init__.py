"""
Simulation API 模块包

将原 simulation.py（3211行）拆分为 7 个独立模块，提高可维护性。

模块结构：
    - entities.py   : 实体相关接口 (~150行)
    - prepare.py    : 模拟准备接口 (~450行)
    - control.py    : 运行控制接口 (~300行)
    - data.py       : 数据查询接口 (~800行)
    - interview.py  : 采访相关接口 (~350行)
    - autopilot.py  : 自动驾驶接口 (~400行)
    - env.py        : 环境管理接口 (~120行)

原有的导入方式仍然有效：
    from app.api.simulation import xxx
    
蓝图注册在 app/api/__init__.py 中完成。
"""

# 导入所有子模块，触发路由注册
from . import entities
from . import prepare
from . import control
from . import data
from . import interview
from . import autopilot
from . import env

# 为了向后兼容，从 prepare.py 导出辅助函数
from .prepare import _check_simulation_prepared

# 从 interview.py 导出常量和函数
from .interview import INTERVIEW_PROMPT_PREFIX, optimize_interview_prompt

__all__ = [
    # 子模块
    'entities',
    'prepare',
    'control',
    'data',
    'interview',
    'autopilot',
    'env',
    # 向后兼容的导出
    '_check_simulation_prepared',
    'INTERVIEW_PROMPT_PREFIX',
    'optimize_interview_prompt',
]
