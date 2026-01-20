import sys
import os
import pytest

# 将 backend 目录添加到 sys.path，以便可以导入 app 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
