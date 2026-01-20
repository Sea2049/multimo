# 测试规范文档

本文档描述了 Multimo 项目的测试策略、工具和运行方式。

## 1. 后端测试

### 1.1 测试框架
后端使用 `pytest` 作为测试框架，配合 `pytest-cov` 进行代码覆盖率检查。

### 1.2 目录结构
所有后端测试文件位于 `backend/tests/` 目录下。
- `conftest.py`: Pytest 配置和 Fixtures。
- `test_graph_module.py`: 图谱构建模块的单元测试。
- `test_report_module.py`: 报告生成模块的测试。
- `test_simulation_runner.py`: 模拟运行器的测试。

### 1.3 运行测试
在 `backend` 目录下运行以下命令：

```bash
# 运行所有测试
pytest

# 运行特定文件的测试
pytest tests/test_simulation_runner.py

# 详细输出模式
pytest -v

# 生成覆盖率报告
pytest --cov=app tests/
```

### 1.4 编写新测试
- 测试文件应以 `test_` 开头。
- 测试类应以 `Test` 开头。
- 测试方法应以 `test_` 开头。
- 使用 `unittest.mock` 模拟外部依赖（如 LLM API、数据库、文件系统）。

## 2. 前端测试 (计划中)

### 2.1 测试框架
建议使用 `Vitest` 和 `@vue/test-utils` 进行组件测试。

### 2.2 目录结构
建议在 `frontend/src/components/__tests__/` 或 `frontend/tests/` 下存放测试文件。

### 2.3 运行测试
(待配置)

## 3. 集成测试与端到端测试

目前主要依赖单元测试和模块级集成测试。
端到端测试建议使用 Playwright 或 Cypress (待实施)。

## 4. CI/CD 集成

项目已配置 GitHub Actions 进行持续集成。配置文件位于 `.github/workflows/ci.yml`。

### 4.1 触发条件
- 推送到 `main` 或 `master` 分支。
- 针对 `main` 或 `master` 分支的 Pull Request。

### 4.2 流程步骤
CI 流程包含两个并行任务：

1.  **Backend Test**:
    - 设置 Python 3.11 环境。
    - 安装依赖 (`requirements.txt` + `pytest`).
    - 运行 `pytest` 并检查覆盖率。

2.  **Frontend Test**:
    - 设置 Node.js 20 环境。
    - 安装依赖 (`npm install`).
    - 运行 `npm test -- --run`。
