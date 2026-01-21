# 测试规范文档

本文档描述了 Multimo 项目的测试策略、工具和运行方式。

## 1. 后端测试

### 1.1 测试框架
后端使用 `pytest` 作为测试框架，配合 `pytest-cov` 进行代码覆盖率检查。

### 1.2 目录结构
所有后端测试文件位于 `backend/tests/` 目录下。

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest 配置文件和 fixtures
├── test_api_graph.py        # 图谱 API 集成测试 (15+ 用例)
├── test_api_integration.py  # API 集成测试脚本
├── test_api_report.py       # 报告 API 集成测试 (15+ 用例)
├── test_api_simulation.py   # 模拟 API 集成测试 (20+ 用例)
├── test_auto_pilot_manager.py # 自动驾驶管理器测试 (15+ 用例)
├── test_graph_module.py     # 图谱模块测试 (72 用例)
├── test_report_agent.py     # 报告智能体测试 (15+ 用例)
├── test_report_module.py    # 报告模块测试
├── test_simulation_runner.py # 模拟运行器测试
└── test_utils.py            # 工具函数测试 (20+ 用例)
```

### 1.3 测试分类

#### P0 - API 集成测试
- `test_api_graph.py`: 图谱 API 端点测试
- `test_api_simulation.py`: 模拟 API 端点测试
- `test_api_report.py`: 报告 API 端点测试

#### P1 - 核心服务测试
- `test_simulation_runner.py`: 模拟运行器测试
- `test_report_agent.py`: 报告智能体测试
- `test_auto_pilot_manager.py`: 自动驾驶管理器测试

#### P2 - 模块和工具测试
- `test_graph_module.py`: 图谱构建模块测试
- `test_report_module.py`: 报告生成模块测试
- `test_utils.py`: 工具函数测试

### 1.4 运行测试
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

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html tests/

# 只运行 API 测试
pytest tests/test_api_*.py -v

# 只运行核心模块测试
pytest tests/test_graph_module.py tests/test_report_module.py -v

# 快速测试（跳过慢速测试）
pytest -m "not slow" -v
```

### 1.5 测试 Fixtures

`conftest.py` 提供以下 fixtures：

#### Flask 测试 Fixtures
- `app`: 创建测试用 Flask 应用实例
- `client`: 创建 Flask 测试客户端
- `runner`: 创建 Flask CLI 测试运行器

#### Mock Fixtures
- `mock_llm_client`: Mock LLM 客户端
- `mock_zep_client`: Mock Zep 客户端
- `mock_openai`: Mock OpenAI 客户端
- `mock_config`: Mock 配置对象

#### 数据 Fixtures
- `sample_project_data`: 示例项目数据
- `sample_simulation_data`: 示例模拟数据
- `sample_graph_data`: 示例图谱数据
- `sample_report_data`: 示例报告数据

#### 文件系统 Fixtures
- `temp_upload_dir`: 创建临时上传目录
- `sample_pdf_file`: 创建示例 PDF 文件
- `sample_markdown_file`: 创建示例 Markdown 文件
- `sample_txt_file`: 创建示例文本文件

### 1.6 编写新测试
- 测试文件应以 `test_` 开头。
- 测试类应以 `Test` 开头。
- 测试方法应以 `test_` 开头。
- 使用 `unittest.mock` 模拟外部依赖（如 LLM API、数据库、文件系统）。
- 使用 `conftest.py` 中的 fixtures 简化测试设置。

### 1.7 代码覆盖率

#### 当前覆盖率: 31%

| 模块 | 覆盖率 | 说明 |
|------|--------|------|
| graph.builder | 89% | 图谱构建核心模块 |
| graph.storage | 82% | 图谱存储模块 |
| report.analyzer | 90% | 报告分析模块 |
| api.graph | 35% | 图谱 API 层 |
| api.simulation | 30% | 模拟 API 层 |
| api.report | 28% | 报告 API 层 |
| services | 20-40% | 服务层 |

#### 覆盖率目标
- 短期目标 (1个月): 40%
- 中期目标 (3个月): 60%
- 长期目标 (6个月): 70%+

## 2. 前端测试

### 2.1 测试框架
使用 `Vitest` 和 `@vue/test-utils` 进行组件测试。

### 2.2 目录结构
测试文件位于 `frontend/src/__tests__/` 目录下。

```
frontend/src/__tests__/
└── example.spec.js    # 示例测试文件
```

### 2.3 运行测试

```bash
cd frontend

# 运行所有测试
npm test

# 运行测试（单次运行）
npm test -- --run

# 监视模式
npm test -- --watch

# 生成覆盖率报告
npm test -- --coverage
```

### 2.4 待添加的前端测试
- 核心组件测试 (Step1-Step5, GraphPanel)
- API 客户端测试 (graph.js, simulation.js, report.js)
- 路由测试
- 状态管理测试

## 3. 集成测试与端到端测试

### 3.1 API 集成测试
使用 Flask 测试客户端进行 API 集成测试，测试文件：
- `test_api_graph.py`
- `test_api_simulation.py`
- `test_api_report.py`

### 3.2 端到端测试
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

## 5. 测试最佳实践

### 5.1 测试命名规范
```python
# 好的命名
def test_create_simulation_success():
def test_create_simulation_missing_project_id():
def test_create_simulation_project_not_found():

# 不好的命名
def test_1():
def test_simulation():
```

### 5.2 测试隔离
- 每个测试应该独立运行，不依赖其他测试的状态
- 使用 fixtures 设置和清理测试环境
- 使用 mock 隔离外部依赖

### 5.3 测试覆盖
- 测试正常路径（happy path）
- 测试错误路径（error path）
- 测试边界条件
- 测试输入验证

### 5.4 Mock 使用
```python
from unittest.mock import patch, MagicMock

@patch('app.services.simulation_manager.SimulationManager.get_simulation')
def test_get_simulation(mock_get_sim):
    mock_sim = MagicMock()
    mock_sim.to_dict.return_value = {'id': 'test'}
    mock_get_sim.return_value = mock_sim
    
    # 测试代码...
```

## 6. 测试报告

### 6.1 生成测试报告
```bash
# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html tests/

# 报告位置
backend/htmlcov/index.html
```

### 6.2 查看测试结果
```bash
# 详细输出
pytest -v

# 显示失败测试的详细信息
pytest --tb=long

# 只显示失败的测试
pytest --tb=short -q
```

## 7. 常见问题

### 7.1 测试失败排查
1. 检查依赖是否安装完整
2. 检查环境变量配置
3. 检查 mock 是否正确设置
4. 查看详细的错误堆栈

### 7.2 覆盖率不准确
1. 确保测试文件被正确发现
2. 检查 `--cov` 参数指向正确的模块
3. 排除不需要测试的文件

### 7.3 测试运行缓慢
1. 使用 `-x` 参数在第一个失败时停止
2. 使用 `-n auto` 并行运行测试（需要 pytest-xdist）
3. 标记慢速测试并在开发时跳过
