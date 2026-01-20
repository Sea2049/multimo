## 自动驾驶模式 (Auto-Pilot Mode) 实现计划

### 一、核心设计

**功能概述**：
- 自动驾驶模式：创建模拟后，系统自动完成准备、运行、报告生成全流程
- 普通模式：保留现有手动控制能力，每步需要人工确认
- 支持随时切换模式，支持断点续传

**流程编排**：
```
自动驾驶模式流程：
[创建模拟] → [自动准备] → [自动启动] → [监控运行] → [自动生成报告] → [完成]
                              ↓
                        (支持自动重启失败步骤)
```

---

### 二、实现步骤

#### 步骤1：创建 AutoPilotManager 服务类
**文件**: `backend/app/services/auto_pilot_manager.py`

核心功能：
- `AutoPilotMode` 枚举（MANUAL / AUTO）
- `AutoPilotState` 数据类（记录当前阶段、进度、错误）
- `AutoPilotManager` 单例类：
  - `set_mode(mode)` - 设置模式
  - `start_auto_pilot(simulation_id)` - 启动自动驾驶
  - `pause_auto_pilot()` - 暂停
  - `resume_auto_pilot()` - 恢复
  - `get_auto_pilot_status()` - 获取状态
  - 内部编排：准备 → 启动 → 监控 → 报告

#### 步骤2：扩展 SimulationState
**文件**: `backend/app/services/simulation_manager.py`

新增字段：
```python
# 自动驾驶模式相关
auto_pilot_mode: bool = False  # 是否启用自动驾驶
current_auto_step: str = ""    # 当前自动步骤
auto_step_progress: int = 0    # 步骤进度
auto_started_at: Optional[str] = None  # 自动驾驶启动时间
auto_completed_at: Optional[str] = None  # 自动驾驶完成时间
auto_error: Optional[str] = None  # 自动驾驶错误信息
```

#### 步骤3：新增 API 接口
**文件**: `backend/app/api/simulation.py`

新增接口：
```
POST /api/simulation/auto-pilot/config   # 配置自动驾驶模式
POST /api/simulation/auto-pilot/start    # 启动自动驾驶
POST /api/simulation/auto-pilot/pause    # 暂停自动驾驶
POST /api/simulation/auto-pilot/resume   # 恢复自动驾驶
POST /api/simulation/auto-pilot/stop     # 停止自动驾驶
GET  /api/simulation/auto-pilot/status   # 获取自动驾驶状态
```

#### 步骤4：更新文档
- `FRAMEWORK.md` - 新增自动驾驶模式章节
- `CODE_DIRECTORY.md` - 添加 `auto_pilot_manager.py`

---

### 三、关键特性

1. **状态持久化**：自动保存进度，重启后可继续
2. **错误处理**：步骤失败自动重试，超时处理
3. **日志记录**：详细记录自动驾驶全过程
4. **模式切换**：随时在 AUTO/MANUAL 间切换

---

### 四、文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/services/auto_pilot_manager.py` | 新建 | 自动驾驶核心服务 |
| `backend/app/services/simulation_manager.py` | 修改 | 扩展状态字段 |
| `backend/app/api/simulation.py` | 修改 | 新增 API 接口 |
| `FRAMEWORK.md` | 修改 | 更新文档 |
| `CODE_DIRECTORY.md` | 修改 | 更新代码目录 |