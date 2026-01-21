# 任务管理持久化实施方案

## 现状分析

✅ **已有基础**：
- 项目已有 `SQLiteStorage` 实现（`backend/app/storage/database.py`）
- 配置系统已支持 `DATABASE_PATH` 配置
- TaskManager 已实现完整的任务管理逻辑

❌ **存在问题**：
- TaskManager 使用内存字典存储（`_tasks: Dict[str, Task] = {}`）
- 后端重启后所有任务丢失
- 无法恢复未完成的任务

---

## 实施方案

### 方案选择：使用 SQLite

**理由**：
1. 项目已有 SQLiteStorage 实现，无需额外依赖
2. 轻量级，适合单机部署
3. 无需额外服务（Redis 需要独立进程）
4. 支持事务和并发控制

---

## 详细步骤

### 步骤 1：扩展 SQLiteStorage 支持任务表

**文件**：`backend/app/storage/database.py`

**修改内容**：
1. 在 `_initialize_tables` 中添加 `tasks` 表：
```sql
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    progress INTEGER DEFAULT 0,
    message TEXT,
    result TEXT,  -- JSON
    error TEXT,
    metadata TEXT,  -- JSON
    progress_detail TEXT  -- JSON
)
```

2. 添加任务专用方法：
   - `store_task(task: Task) -> bool`
   - `retrieve_task(task_id: str) -> Optional[Task]`
   - `list_tasks() -> List[Task]`
   - `update_task(task_id: str, **kwargs) -> bool`
   - `delete_task(task_id: str) -> bool`

---

### 步骤 2：修改 TaskManager 使用数据库存储

**文件**：`backend/app/models/task.py`

**修改内容**：
1. 添加数据库存储支持：
```python
from app.storage.database import SQLiteStorage
from app.config_new import get_config

class TaskManager:
    def __init__(self):
        config = get_config()
        # 使用数据库存储
        self.storage = SQLiteStorage(config.DATABASE_PATH)
        self._task_lock = threading.Lock()
```

2. 修改所有方法使用数据库：
   - `create_task()` → 调用 `storage.store_task()`
   - `get_task()` → 调用 `storage.retrieve_task()`
   - `update_task()` → 调用 `storage.update_task()`
   - `list_tasks()` → 调用 `storage.list_tasks()`

3. 保留内存缓存（可选优化）：
```python
self._cache: Dict[str, Task] = {}  # 内存缓存
```

---

### 步骤 3：添加任务恢复机制

**文件**：`backend/app/models/task.py`

**新增方法**：
```python
def recover_tasks(self):
    """恢复未完成的任务"""
    tasks = self.storage.list_tasks()
    for task in tasks:
        if task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
            # 标记为失败（因为进程已重启）
            task.status = TaskStatus.FAILED
            task.error = "任务因服务重启而中断"
            self.storage.update_task(task.task_id, 
                status=task.status, 
                error=task.error
            )
```

**调用位置**：`backend/app/__init__.py` 的 `create_app()` 函数中

---

### 步骤 4：更新配置

**文件**：`backend/app/config_new.py`

**修改内容**：
```python
# 存储配置
STORAGE_TYPE: str = "database"  # 改为 database
DATABASE_PATH: str = str(project_root / "backend" / "tasks.db")  # 任务数据库
```

---

### 步骤 5：更新 requirements.txt

**文件**：`backend/requirements.txt`

**确认包含**：
```
# SQLite 是 Python 内置的，无需额外安装
# 但需要确保有以下依赖
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

---

### 步骤 6：测试验证

**测试步骤**：
1. 启动后端：`python run.py`
2. 创建一个图谱构建任务
3. 查看任务状态（应该正常）
4. **重启后端**
5. 再次查询任务状态（应该仍然存在）
6. 检查任务状态是否被标记为失败

**验证点**：
- ✅ 任务创建后立即保存到数据库
- ✅ 重启后任务仍然存在
- ✅ 未完成任务被标记为失败
- ✅ 任务列表正常显示

---

## 文件修改清单

### 需要修改的文件：
1. ✏️ `backend/app/storage/database.py` - 添加任务表和方法
2. ✏️ `backend/app/models/task.py` - 集成数据库存储
3. ✏️ `backend/app/__init__.py` - 添加任务恢复调用
4. ✏️ `backend/app/config_new.py` - 更新存储配置

### 无需修改的文件：
- ✅ `backend/app/api/graph.py` - 已使用 TaskManager，无需改动
- ✅ `backend/requirements.txt` - SQLite 是内置的

---

## 实施顺序

1. **第一步**：修改 `database.py` 添加任务表和方法（20 分钟）
2. **第二步**：修改 `task.py` 集成数据库存储（30 分钟）
3. **第三步**：添加任务恢复机制（15 分钟）
4. **第四步**：更新配置和初始化（10 分钟）
5. **第五步**：测试验证（30 分钟）

**预计总时间**：1.5-2 小时

---

## 风险控制

### 备份策略
- 在修改前创建 Git 分支：`git checkout -b feature/task-persistence`
- 保留原有内存实现作为备份

### 回滚方案
如果出现问题，可以：
1. 在配置中改回 `STORAGE_TYPE = "memory"`
2. 恢复 TaskManager 的内存实现

### 兼容性
- 保持 TaskManager 的公共接口不变
- 确保现有 API 调用无需修改

---

## 预期效果

✅ **解决的问题**：
- 后端重启后任务不再丢失
- 可以查询历史任务
- 支持任务恢复和清理

✅ **性能影响**：
- 轻微增加（每次操作多一次数据库 I/O）
- 可通过内存缓存优化

✅ **可维护性**：
- 代码结构更清晰
- 便于后续扩展（如迁移到 PostgreSQL）

---

**准备好开始实施了吗？**