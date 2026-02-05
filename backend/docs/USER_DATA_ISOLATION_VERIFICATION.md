# 用户数据隔离验证文档

## 概述

本文档说明如何验证用户数据隔离功能是否正常工作，以及如何执行数据迁移脚本。

## 1. 迁移脚本执行

### 1.1 检查迁移状态

在运行迁移脚本之前，检查数据库中是否已有 `user_id` 数据：

```sql
-- 检查 projects 表中 user_id 为 NULL 的记录数
SELECT COUNT(*) FROM projects WHERE user_id IS NULL;

-- 检查 tasks 表中 user_id 为 NULL 的记录数
SELECT COUNT(*) FROM tasks WHERE user_id IS NULL;
```

### 1.2 执行迁移脚本

```bash
cd backend
python -m scripts.migrate_user_data_isolation --default-user-id 1
```

**参数说明：**
- `--default-user-id`: 历史项目/任务归属的默认用户 ID（建议为管理员），默认为 1
- `--dry-run`: 仅打印将执行的操作，不实际写入数据库

### 1.3 验证迁移结果

迁移完成后，检查：

```sql
-- 确认所有项目都有 user_id
SELECT COUNT(*) FROM projects WHERE user_id IS NULL;
-- 应该返回 0

-- 确认所有任务都有 user_id
SELECT COUNT(*) FROM tasks WHERE user_id IS NULL;
-- 应该返回 0（或很少，如果有无法关联的项目）
```

## 2. 功能验证

### 2.1 多用户环境测试

#### 准备测试数据

1. **创建两个测试用户**
   - 用户 A (user_id: 1)
   - 用户 B (user_id: 2)

2. **为每个用户创建项目和模拟**
   - 用户 A: 创建项目 `proj_user_a`，运行模拟 `sim_user_a`
   - 用户 B: 创建项目 `proj_user_b`，运行模拟 `sim_user_b`

#### 验证步骤

1. **使用用户 A 的 Token 访问 `/api/simulation/history`**
   ```bash
   curl -H "Authorization: Bearer <user_a_token>" \
        http://localhost:5000/api/simulation/history
   ```
   - **预期结果**: 只返回用户 A 的模拟历史
   - **验证点**: 响应中不应包含 `sim_user_b`

2. **使用用户 B 的 Token 访问 `/api/simulation/history`**
   ```bash
   curl -H "Authorization: Bearer <user_b_token>" \
        http://localhost:5000/api/simulation/history
   ```
   - **预期结果**: 只返回用户 B 的模拟历史
   - **验证点**: 响应中不应包含 `sim_user_a`

3. **使用用户 A 的 Token 访问 `/api/simulation/list`**
   ```bash
   curl -H "Authorization: Bearer <user_a_token>" \
        http://localhost:5000/api/simulation/list
   ```
   - **预期结果**: 只返回用户 A 的模拟列表
   - **验证点**: 响应中不应包含用户 B 的项目

### 2.2 前端验证

1. **登录用户 A**
   - 访问首页，查看"推演记录"区域
   - 应该只显示用户 A 创建的项目/模拟

2. **登录用户 B**
   - 访问首页，查看"推演记录"区域
   - 应该只显示用户 B 创建的项目/模拟
   - 不应看到用户 A 的数据

3. **验证删除功能**
   - 用户 A 删除自己的模拟 → 应该成功
   - 用户 A 尝试删除用户 B 的模拟 → 应该失败（403 Forbidden）

## 3. 安全检查清单

- [ ] `/api/simulation/history` 接口只返回当前用户的项目对应的模拟
- [ ] `/api/simulation/list` 接口只返回当前用户的项目对应的模拟
- [ ] `/api/graph/project/list` 接口只返回当前用户的项目
- [ ] 所有需要项目 ID 的操作都通过 `@require_project_owner` 或 `@require_simulation_owner` 验证所有权
- [ ] 未登录用户无法访问任何需要认证的接口（返回 401）
- [ ] 用户无法通过修改请求参数访问其他用户的数据

## 4. 常见问题

### Q: 迁移脚本执行后，历史数据都归属到默认用户了，怎么办？

**A**: 这是预期行为。迁移脚本会将所有历史数据归属到指定的默认用户（通常是管理员）。如果需要将数据分配给其他用户，需要手动更新数据库：

```sql
UPDATE projects SET user_id = <target_user_id> WHERE project_id = '<project_id>';
UPDATE tasks SET user_id = <target_user_id> WHERE task_id = '<task_id>';
```

### Q: 迁移脚本执行失败怎么办？

**A**: 
1. 检查数据库文件权限
2. 确认数据库文件未被其他进程锁定
3. 检查 `projects` 表和 `tasks` 表结构是否正确
4. 查看错误日志，根据具体错误信息处理

### Q: 如何回滚迁移？

**A**: 迁移脚本不会删除数据，只是添加 `user_id` 字段。如果需要回滚：

```sql
-- 注意：这会删除 user_id 列，需要先备份数据
ALTER TABLE projects DROP COLUMN user_id;
ALTER TABLE tasks DROP COLUMN user_id;
```

**建议**: 在执行迁移前先备份数据库文件。

## 5. 相关文件

- 迁移脚本: `backend/scripts/migrate_user_data_isolation.py`
- API 装饰器: `backend/app/api/decorators.py`
- 存储层: `backend/app/storage/database.py`
- 项目模型: `backend/app/models/project.py`
- 模拟 API: `backend/app/api/simulation.py`
