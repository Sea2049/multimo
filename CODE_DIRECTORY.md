# Multimo 代码目录文档

## 1. 项目根目录

```
multimo/
├── .env                    # 环境变量配置文件（包含 API 密钥等敏感信息）
├── .env.example            # 环境变量示例文件（用于参考）
├── .gitignore              # Git 忽略文件配置
├── .github/                # GitHub 配置
│   └── workflows/          # CI/CD 工作流
│       └── ci.yml          # 持续集成配置
├── ARCHITECTURE.md         # 架构文档
├── API.md                  # API 文档
├── CODE_DIRECTORY.md       # 代码目录文档（本文件）
├── DEVELOPMENT.md          # 开发指南
├── FRAMEWORK.md            # 框架架构文档
├── LICENSE                 # MIT 开源许可证
├── LICENSE-OASIS           # OASIS 框架 Apache 2.0 许可证
├── package.json            # 根目录依赖配置和 npm 脚本
├── package-lock.json       # 根目录依赖锁定文件
├── README.md               # 中文说明文档
├── README-EN.md            # 英文说明文档
├── REFACTORING_PLAN.md     # 重构计划文档
├── REFACTORING_STATUS.md   # 重构状态文档
├── REPORT_MODULE_TEST_REPORT.md  # 报告模块测试报告
├── TESTING.md              # 测试文档
├── replication_log.md      # 项目复制日志
├── static/                 # 静态资源目录
│   └── image/              # 图片资源
│       ├── Screenshot/     # 系统运行截图
│       │   ├── 运行截图1.png
│       │   ├── 运行截图2.png
│       │   ├── 运行截图3.png
│       │   ├── 运行截图4.png
│       │   ├── 运行截图5.png
│       │   └── 运行截图6.png
│       ├── MiroFish_logo.jpeg          # MiroFish Logo
│       ├── MiroFish_logo_compressed.jpeg  # 压缩版 Logo
│       ├── shanda_logo.png              # 盛大集团 Logo
│       ├── QQ群.png                     # QQ 交流群二维码
│       └── 武大模拟演示封面.png         # 演示视频封面
├── backend/                # 后端 Python 应用
└── frontend/               # 前端 Vue.js 应用
```

## 2. 后端目录结构 (backend/)

### 2.1 应用核心代码 (backend/app/)

```
backend/app/
├── __init__.py             # Flask 应用工厂
├── config.py               # 配置管理类（从 .env 加载配置）
├── config_new.py           # 新配置管理类（重构版）
├── api/                    # API 路由层（处理 HTTP 请求）
├── models/                 # 数据模型层（定义数据结构）
├── services/               # 业务逻辑层（核心功能实现）
├── modules/                # 功能模块层（重构后的模块化架构）
├── storage/                # 存储层（数据存储接口和实现）
├── core/                   # 核心接口层（基础类和接口定义）
└── utils/                  # 工具函数层（通用工具）
```

#### 2.1.1 应用入口

**backend/app/__init__.py**
- Flask 应用工厂函数 `create_app()`
- 配置 CORS（跨域资源共享）
- 注册 API 蓝图和路由
- 设置日志系统
- 注册错误处理器
- 支持配置覆盖机制

**backend/app/config.py**
- 统一的配置管理类 `Config`
- 从项目根目录的 .env 文件加载配置
- 包含 Flask、LLM、Zep、OASIS 等配置
- 配置验证功能 `validate()`
- 禁用 JSON ASCII 转义，支持中文显示

**backend/app/config_new.py**
- 新版本配置管理类（基于 Pydantic）
- 使用 Pydantic Settings 进行类型安全的配置
- 支持配置验证和环境变量自动加载
- 提供 `get_flask_config()` 方法

#### 2.1.2 API 路由层 (backend/app/api/)

```
backend/app/api/
├── __init__.py             # API 蓝图初始化和路由注册
├── v1/                     # API v1 版本
│   ├── __init__.py
│   ├── graph.py            # 图谱操作 API 端点
│   ├── simulation.py       # 模拟控制 API 端点
│   ├── report.py           # 报告生成 API 端点
│   ├── interaction.py      # 交互对话 API 端点
│   └── health.py           # 健康检查 API 端点
├── graph.py                # 图谱操作 API（旧版，兼容性保留）
├── simulation.py           # 模拟控制 API（旧版，兼容性保留）
└── report.py               # 报告生成 API（旧版，兼容性保留）
```

**backend/app/api/v1/graph.py**
- POST /api/v1/graph/extract - 从文本中提取实体和关系
- POST /api/v1/graph/build - 构建知识图谱
- GET /api/v1/graph/<graph_id> - 获取指定知识图谱
- GET /api/v1/graph/<graph_id>/export - 导出知识图谱为 JSON 文件
- GET /api/v1/graph/entities - 获取实体列表
- GET /api/v1/graph/relationships - 获取关系列表

**backend/app/api/v1/simulation.py**
- POST /api/v1/simulation/create - 创建模拟
- POST /api/v1/simulation/prepare - 准备模拟环境
- POST /api/v1/simulation/prepare/status - 获取准备状态
- GET /api/v1/simulation/<id>/config - 获取模拟配置
- GET /api/v1/simulation/<id>/config/realtime - 实时配置状态
- GET /api/v1/simulation/<id>/profiles/realtime - 实时人设生成进度
- POST /api/v1/simulation/start - 启动模拟
- POST /api/v1/simulation/stop - 停止模拟
- GET /api/v1/simulation/status - 获取模拟状态
- GET /api/v1/simulation/<id>/run-status - 获取运行状态
- GET /api/v1/simulation/<id>/run-status/detail - 获取运行状态详情
- POST /api/v1/simulation/env-status - 获取环境状态
- POST /api/v1/simulation/close-env - 关闭模拟环境
- POST /api/v1/simulation/<id>/interview/batch - 批量采访智能体
- GET /api/v1/simulation/logs - 获取模拟日志
- GET /api/v1/simulation/history - 获取历史模拟
- GET /api/v1/simulation/<id> - 获取模拟信息
- GET /api/v1/simulation/<id>/export - 导出模拟数据
- 自动驾驶模式接口：
  - POST /api/v1/simulation/auto-pilot/config - 配置自动驾驶模式
  - POST /api/v1/simulation/auto-pilot/start - 启动自动驾驶
  - POST /api/v1/simulation/auto-pilot/pause - 暂停自动驾驶
  - POST /api/v1/simulation/auto-pilot/resume - 恢复自动驾驶
  - POST /api/v1/simulation/auto-pilot/stop - 停止自动驾驶
  - GET /api/v1/simulation/auto-pilot/status - 获取自动驾驶状态
  - POST /api/v1/simulation/auto-pilot/reset - 重置自动驾驶状态

**backend/app/api/v1/report.py**
- POST /api/v1/report/generate - 生成报告
- GET /api/v1/report/<simulation_id> - 获取报告（JSON格式）
- GET /api/v1/report/<simulation_id>/markdown - 获取报告（Markdown格式）
- GET /api/v1/report/list - 列出所有报告

**backend/app/api/v1/interaction.py**
- POST /api/v1/interaction/chat - 与 ReportAgent 对话
- GET /api/v1/interaction/history - 获取对话历史

**backend/app/api/v1/health.py**
- GET /api/v1/health - 健康检查端点

#### 2.1.3 数据模型层 (backend/app/models/)

```
backend/app/models/
├── __init__.py             # 模型初始化
├── project.py              # 项目数据模型
└── task.py                 # 任务数据模型
```

**backend/app/models/project.py**
- 项目数据结构定义
- 项目状态管理（created, processing, completed, failed）
- 项目元数据管理
- 项目 CRUD 操作

**backend/app/models/task.py**
- 任务数据结构定义
- 任务状态管理（pending, running, completed, failed）
- 任务进度跟踪
- 任务依赖管理

#### 2.1.4 业务逻辑层 (backend/app/services/)

```
backend/app/services/
├── __init__.py
├── auto_pilot_manager.py       # 自动驾驶管理器
├── export_service.py           # 导出服务（导出图谱、报告等）
├── graph_builder.py            # 图谱构建服务（构建知识图谱）
├── oasis_profile_generator.py  # OASIS 人设生成器
├── ontology_generator.py       # 本体生成器
├── report_agent.py             # 报告智能体（生成预测报告）
├── simulation_config_generator.py  # 模拟配置生成器
├── simulation_ipc.py           # 模拟进程间通信
├── simulation_manager.py       # 模拟管理器（管理模拟生命周期）
├── simulation_runner.py        # 模拟运行器（执行模拟任务）
├── text_processor.py           # 文本处理服务（文件解析、文本提取）
├── zep_entity_reader.py        # Zep 实体读取器
├── zep_graph_memory_updater.py # Zep 图谱记忆更新器
└── zep_tools.py                # Zep 工具函数
```

**backend/app/services/auto_pilot_manager.py**
- 自动驾驶模式核心管理器
- 自动执行准备、启动、监控、报告生成流程
- 支持暂停、恢复、停止操作
- 状态持久化支持断点续传

**backend/app/services/export_service.py**
- 提供图谱数据导出功能
- 支持多种导出格式（JSON, CSV）
- 处理导出文件生成
- 封装文件下载逻辑

**backend/app/services/graph_builder.py**
- 从文本中提取实体和关系
- 构建知识图谱结构
- 管理图谱数据存储
- 支持图谱统计和分析

**backend/app/services/oasis_profile_generator.py**
- 为 OASIS 框架生成智能体人设
- 基于图谱数据生成个性化配置
- 支持 Twitter 和 Reddit 平台人设
- 人设格式验证

**backend/app/services/ontology_generator.py**
- 生成本体结构
- 定义领域知识模型
- 支持知识推理
- 本体验证

**backend/app/services/report_agent.py**
- 基于 LLM 的报告智能体
- 分析模拟数据
- 生成结构化预测报告
- 提供丰富的工具集
- 支持多轮反思和优化

**backend/app/services/simulation_config_generator.py**
- 生成模拟配置文件
- 配置模拟环境参数
- 管理智能体配置
- 生成平台特定配置

**backend/app/services/simulation_ipc.py**
- 处理模拟进程间通信
- 管理进程间数据传输
- 实现进程同步机制
- 支持异步消息传递

**backend/app/services/simulation_manager.py**
- 管理模拟的完整生命周期
- 创建、启动、停止、查询模拟
- 管理模拟状态和日志
- 处理模拟错误和重试
- 支持并发模拟管理

**backend/app/services/simulation_runner.py**
- 执行模拟任务
- 集成 OASIS 框架
- 支持 Twitter 和 Reddit 双平台并行模拟
- 记录模拟日志
- 处理模拟异常

**backend/app/services/text_processor.py**
- 处理上传的文件
- 提取文本内容
- 支持 PDF、Markdown、TXT 格式
- 文本切块和预处理
- 处理文件编码问题

**backend/app/services/zep_entity_reader.py**
- 从 Zep Cloud 读取实体数据
- 管理实体关系
- 支持实体查询
- 实体数据格式转换

**backend/app/services/zep_graph_memory_updater.py**
- 更新 Zep 中的图谱记忆
- 管理时序记忆
- 同步图谱状态
- 支持增量更新

**backend/app/services/zep_tools.py**
- Zep Cloud 工具函数
- 封装 Zep API 调用
- 处理 Zep 数据格式
- Zep 会话管理

#### 2.1.5 功能模块层 (backend/app/modules/)

```
backend/app/modules/
├── __init__.py             # 模块初始化
├── graph/                  # 图谱构建模块
│   ├── __init__.py
│   ├── extractor.py        # 实体和关系提取器
│   ├── builder.py          # 图谱构建器
│   └── storage.py          # 图谱存储接口
├── simulation/             # 模拟引擎模块
│   ├── __init__.py
│   └── platforms/          # 平台实现
│       ├── __init__.py
│       ├── twitter.py      # Twitter 平台
│       └── reddit.py       # Reddit 平台
├── report/                 # 报告生成模块
│   ├── __init__.py
│   ├── analyzer.py         # 数据分析器
│   └── generator.py        # 报告生成器
└── interaction/            # 交互模块
    ├── __init__.py
    └── chat.py             # 聊天接口
```

**backend/app/modules/graph/extractor.py**
- `LLMEntityExtractor` 类：基于 LLM 的实体提取器
- `LLMRelationExtractor` 类：基于 LLM 的关系提取器
- 实现 `EntityExtractor` 和 `RelationExtractor` 接口
- 支持实体类型识别和关系类型分类
- 提供 JSON 格式的结构化输出

**backend/app/modules/graph/builder.py**
- `KnowledgeGraphBuilder` 类：知识图谱构建器
- 实现 `GraphBuilder` 接口
- 构建节点和边数据结构
- 提供图谱统计信息
- 支持图谱导出和可视化

**backend/app/modules/graph/storage.py**
- `ZepGraphStorage` 类：基于 Zep 的图谱存储
- 实现 `GraphStorage` 接口
- 管理图谱的 CRUD 操作
- 支持图谱查询和搜索
- 提供图谱版本管理

**backend/app/modules/simulation/__init__.py**
- 模拟引擎模块初始化
- 集成 OASIS 框架进行社交模拟
- OASIS 是 Apache 2.0 许可证的开源项目

**backend/app/modules/simulation/platforms/twitter.py**
- `TwitterPlatform` 类：Twitter 平台模拟
- 实现 `Platform` 接口
- 支持 post, reply, retweet, like 等动作
- 模拟 Twitter 的 280 字符限制
- 管理推文、回复、转发、点赞数据

**backend/app/modules/simulation/platforms/reddit.py**
- `RedditPlatform` 类：Reddit 平台模拟
- 实现 `Platform` 接口
- 支持 post, comment, like, dislike 等动作
- 管理 subreddit、帖子、评论数据
- 支持投票和排序机制

**backend/app/modules/report/analyzer.py**
- `DataAnalyzer` 类：模拟数据分析器
- 分析模拟数据统计信息
- 提取关键事件和趋势
- 生成分析摘要
- 支持多模拟比较

**backend/app/modules/report/generator.py**
- `ReportGenerator` 类：报告生成器
- 基于 LLM 的报告生成
- 实现结构化报告生成
- 支持多章节报告生成
- 转换为 Markdown 格式
- 生成简化版报告

**backend/app/modules/interaction/chat.py**
- `ChatInterface` 类：聊天交互接口
- 与模拟智能体对话
- 与 ReportAgent 对话
- 管理对话历史
- 支持上下文注入

#### 2.1.6 核心接口层 (backend/app/core/)

```
backend/app/core/
├── __init__.py             # 核心模块初始化
├── base.py                 # 基础类定义
├── entities.py             # 实体定义
└── interfaces.py           # 接口定义
```

**backend/app/core/interfaces.py**
- 定义所有核心接口：
  - `EntityExtractor`：实体提取器接口
  - `RelationExtractor`：关系提取器接口
  - `GraphBuilder`：图谱构建器接口
  - `GraphStorage`：图谱存储接口
  - `Agent`：智能体接口
  - `SimulationEngine`：模拟引擎接口
  - `Platform`：平台接口
  - `MemoryStorage`：记忆存储接口
  - `ReportGenerator`：报告生成器接口

**backend/app/core/base.py**
- 基础类定义
- 提供通用功能和方法
- 抽象类和混入类

**backend/app/core/entities.py**
- 实体数据结构定义
- 实体类型枚举
- 关系类型定义

#### 2.1.7 存储层 (backend/app/storage/)

```
backend/app/storage/
├── __init__.py             # 存储模块初始化
├── memory.py               # 记忆存储
└── database.py             # 数据库操作
```

**backend/app/storage/memory.py**
- `MemoryStorage` 类：记忆存储实现
- 实现 `MemoryStorage` 接口
- 支持键值存储
- 提供搜索功能

**backend/app/storage/database.py**
- 数据库操作封装
- SQLite 数据库管理
- 数据库连接池
- 数据库迁移支持

#### 2.1.8 工具函数层 (backend/app/utils/)

```
backend/app/utils/
├── __init__.py
├── file_parser.py          # 文件解析工具（PDF、TXT、Markdown）
├── llm_client.py           # LLM 客户端封装（支持 OpenAI SDK 格式）
├── llm.py                  # LLM 工具函数（重构版）
├── logger.py               # 日志配置（统一日志管理）
├── retry.py                # 重试机制（处理 API 调用失败）
└── validators.py           # 数据验证工具
```

**backend/app/utils/file_parser.py**
- 解析 PDF 文件（使用 PyMuPDF）
- 解析 TXT 文件
- 解析 Markdown 文件
- 处理文件编码问题
- 支持多种编码格式

**backend/app/utils/llm_client.py**
- 封装 LLM API 调用
- 支持 OpenAI SDK 格式的任意 LLM
- 实现重试机制
- 错误处理和日志记录
- 流式响应支持

**backend/app/utils/llm.py**
- LLM 工具函数（重构版）
- 统一的 LLM 客户端封装
- 支持多种 LLM 提供商
- 提示词模板管理

**backend/app/utils/logger.py**
- 配置日志系统
- 设置日志格式和级别
- 支持日志文件轮转
- 区分不同模块的日志
- 控制台和文件双输出

**backend/app/utils/retry.py**
- 实现重试机制
- 支持指数退避
- 处理临时性错误
- 可配置重试次数和间隔
- 重试装饰器

**backend/app/utils/validators.py**
- 数据验证工具
- Pydantic 模型定义
- API 参数验证
- 数据格式检查

### 2.2 脚本目录 (backend/scripts/)

```
backend/scripts/
├── action_logger.py              # 动作日志脚本
├── run_parallel_simulation.py    # 并行模拟运行脚本
├── run_reddit_simulation.py       # Reddit 模拟运行脚本
├── run_twitter_simulation.py      # Twitter 模拟运行脚本
└── test_profile_format.py        # 人设格式测试脚本
```

**backend/scripts/action_logger.py**
- 记录智能体动作日志
- 分析动作模式
- 生成动作统计报告

**backend/scripts/run_parallel_simulation.py**
- 运行并行模拟
- 管理 Twitter 和 Reddit 双平台
- 协调模拟进程

**backend/scripts/run_reddit_simulation.py**
- 专门运行 Reddit 平台模拟
- 配置 Reddit 环境参数
- 管理 Reddit 智能体

**backend/scripts/run_twitter_simulation.py**
- 专门运行 Twitter 平台模拟
- 配置 Twitter 环境参数
- 管理 Twitter 智能体

**backend/scripts/test_profile_format.py**
- 测试人设格式
- 验证人设配置
- 检查人设完整性

### 2.3 测试目录 (backend/tests/)

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest 配置文件
├── test_graph_module.py     # 图谱模块测试
├── test_report_module.py    # 报告模块测试
└── test_simulation_runner.py # 模拟运行器测试
```

**backend/tests/conftest.py**
- Pytest 测试配置
- 设置测试环境路径

**backend/tests/test_graph_module.py**
- 图谱模块单元测试
- 测试实体提取功能
- 测试关系抽取功能
- 测试图谱构建功能

**backend/tests/test_report_module.py**
- 报告模块单元测试
- 测试数据分析器功能
- 测试报告生成器功能
- 测试 Markdown 转换功能

**backend/tests/test_simulation_runner.py**
- 模拟运行器单元测试
- 测试模拟启动和停止
- 测试运行状态管理
- 使用 unittest 和 mock 进行测试

### 2.4 数据目录 (backend/uploads/)

```
backend/uploads/
├── projects/              # 项目上传文件存储
│   └── proj_*/           # 项目目录（每个项目一个）
│       ├── files/        # 项目文件
│       ├── project.json  # 项目配置
│       └── extracted_text.txt  # 提取的文本
├── simulations/          # 模拟数据存储
│   └── sim_*/            # 模拟目录（每个模拟一个）
│       ├── simulation_config.json  # 模拟配置
│       ├── state.json    # 模拟状态
│       ├── run_state.json # 运行状态
│       ├── env_status.json # 环境状态
│       ├── twitter_profiles.csv   # Twitter 人设
│       ├── reddit_profiles.json   # Reddit 人设
│       ├── twitter/       # Twitter 平台数据
│       │   └── actions.jsonl
│       ├── reddit/       # Reddit 平台数据
│       │   └── actions.jsonl
│       ├── reddit_simulation.db  # Reddit 数据库
│       └── ipc_responses/ # IPC 响应记录
└── reports/              # 报告文件存储（旧格式，兼容性保留）
    └── report_*/         # 报告目录（每个报告一个）
        ├── outline.json  # 报告大纲
        ├── meta.json     # 报告元数据
        ├── progress.json # 生成进度
        ├── console_log.txt # 控制台日志
        ├── agent_log.jsonl # 智能体日志
        ├── full_report.md # 完整报告
        └── section_*.md # 分节报告
```

### 2.5 日志目录 (backend/logs/)

```
backend/logs/
└── 2026-01-*.log         # 按日期分类的日志文件
```

### 2.6 配置文件

**backend/pyproject.toml**
- Python 项目配置文件
- 定义项目元数据和依赖
- 使用 uv 包管理器
- 配置项目脚本

**backend/requirements.txt**
- Python 依赖列表
- 兼容传统 pip 安装方式
- 核心依赖：
  - flask>=3.0.0
  - flask-cors>=6.0.0
  - openai>=1.0.0
  - zep-cloud==3.13.0
  - camel-oasis==0.2.5
  - camel-ai==0.2.78
  - PyMuPDF>=1.24.0
  - python-dotenv>=1.0.0
  - pydantic>=2.0.0

**backend/run.py**
- 后端启动入口
- 验证配置
- 启动 Flask 服务器
- 处理 Windows 控制台中文乱码问题

**backend/uv.lock**
- uv 包管理器锁文件
- 确保依赖版本一致性

**backend/Dockerfile**
- Docker 容器化部署配置
- 基于 Python 3.12-slim 镜像
- 安装依赖并启动服务

## 3. 前端目录结构 (frontend/)

### 3.1 公共资源 (frontend/public/)

```
frontend/public/
└── icon.png               # 网站图标
```

### 3.2 源代码目录 (frontend/src/)

```
frontend/src/
├── main.js                # 应用入口文件
├── App.vue                # 根组件
├── api/                   # API 客户端模块
├── assets/                # 静态资源
├── components/            # Vue 组件
├── router/                # 路由配置
├── store/                 # 状态管理
├── views/                 # 页面视图
└── __tests__/             # 测试文件
```

#### 3.2.1 应用入口

**frontend/src/main.js**
- 创建 Vue 应用实例
- 注册路由
- 挂载应用到 DOM

**frontend/src/App.vue**
- 根组件
- 应用布局结构
- 全局样式

#### 3.2.2 API 客户端 (frontend/src/api/)

```
frontend/src/api/
├── index.js               # API 基础配置（Axios 实例）
├── graph.js               # 图谱 API 客户端
├── simulation.js          # 模拟 API 客户端
└── report.js              # 报告 API 客户端
```

**frontend/src/api/index.js**
- 创建 Axios 实例
- 配置基础 URL（http://localhost:5001）
- 配置请求/响应拦截器
- 统一错误处理
- 实现 requestWithRetry 统一重试机制

**frontend/src/api/graph.js**
- 封装图谱相关 API 调用
- 上传种子材料
- 提取实体和关系
- 获取图谱数据
- 导出图谱

**frontend/src/api/simulation.js**
- 封装模拟相关 API 调用
- 创建模拟：createSimulation
- 准备模拟环境：prepareSimulation
- 获取准备状态：getPrepareStatus
- 启动/停止模拟：startSimulation, stopSimulation
- 获取运行状态：getRunStatus, getRunStatusDetail
- 获取模拟信息：getSimulation
- 获取模拟配置：getSimulationConfig
- 获取实时配置状态：getSimulationConfigRealtime
- 获取实时人设进度：getSimulationProfilesRealtime
- 批量采访智能体：interviewAgents
- 获取/关闭环境状态：getEnvStatus, closeSimulationEnv
- 获取模拟历史：getSimulationHistory
- 导出模拟数据：exportSimulationData

**frontend/src/api/report.js**
- 封装报告相关 API 调用
- 生成报告
- 获取报告状态
- 获取报告内容
- 导出报告

#### 3.2.3 静态资源 (frontend/src/assets/)

```
frontend/src/assets/
└── logo/                  # Logo 图片
    ├── MiroFish_logo_left.jpeg
    └── MiroFish_logo_compressed.jpeg
```

#### 3.2.4 Vue 组件 (frontend/src/components/)

```
frontend/src/components/
├── GraphPanel.vue          # 图谱展示面板（D3.js 可视化）
├── HistoryDatabase.vue     # 历史数据库组件
├── Step1GraphBuild.vue     # 步骤1：图谱构建
├── Step2EnvSetup.vue       # 步骤2：环境搭建
├── Step3Simulation.vue     # 步骤3：开始模拟
├── Step4Report.vue         # 步骤4：报告生成
└── Step5Interaction.vue    # 步骤5：深度互动
```

**frontend/src/components/GraphPanel.vue**
- 使用 D3.js 实现图谱可视化
- 支持节点拖拽和缩放
- 显示实体和关系
- 交互式图谱操作

**frontend/src/components/HistoryDatabase.vue**
- 显示历史模拟列表
- 提供模拟详情查看
- 支持历史数据检索

**frontend/src/components/Step1GraphBuild.vue**
- 图谱构建界面
- 上传种子材料
- 显示提取的实体和关系
- 图谱预览

**frontend/src/components/Step2EnvSetup.vue**
- 环境搭建界面
- 配置模拟参数
- 生成智能体人设
- 平台选择

**frontend/src/components/Step3Simulation.vue**
- 模拟运行界面
- 显示模拟进度
- 实时日志展示
- 控制模拟启动/停止

**frontend/src/components/Step4Report.vue**
- 报告生成界面
- 显示生成进度
- 报告内容展示
- 导出报告功能

**frontend/src/components/Step5Interaction.vue**
- 深度互动界面
- 与智能体对话
- 与 ReportAgent 对话
- 动态变量注入

#### 3.2.5 路由配置 (frontend/src/router/)

```
frontend/src/router/
└── index.js               # 路由定义
```

**frontend/src/router/index.js**
- 定义应用路由
- 配置路由守卫
- 路由懒加载

#### 3.2.6 状态管理 (frontend/src/store/)

```
frontend/src/store/
└── pendingUpload.js       # 待上传状态管理
```

**frontend/src/store/pendingUpload.js**
- 管理待上传文件状态
- 文件上传进度跟踪
- 上传错误处理

#### 3.2.7 页面视图 (frontend/src/views/)

```
frontend/src/views/
├── Home.vue               # 首页
├── MainView.vue           # 主视图（包含 Step1-Step5）
├── Process.vue            # 流程页面
├── SimulationView.vue     # 模拟视图
├── SimulationRunView.vue  # 模拟运行视图
├── InteractionView.vue    # 互动视图
└── ReportView.vue         # 报告视图
```

**frontend/src/views/Home.vue**
- 应用首页
- 项目介绍
- 快速开始指引

**frontend/src/views/MainView.vue**
- 主视图页面
- 集成 Step1-Step5 组件
- 流程导航

**frontend/src/views/Process.vue**
- 流程展示页面
- 工作流程说明

**frontend/src/views/SimulationView.vue**
- 模拟配置页面
- 模拟参数设置

**frontend/src/views/SimulationRunView.vue**
- 模拟运行页面
- 实时状态展示
- 日志查看

**frontend/src/views/InteractionView.vue**
- 智能体对话页面
- 聊天界面
- 对话历史

**frontend/src/views/ReportView.vue**
- 报告展示页面
- 报告内容渲染
- 报告导出

#### 3.2.8 测试文件 (frontend/src/__tests__/)

```
frontend/src/__tests__/
└── example.spec.js        # 示例测试文件（Vitest）
```

### 3.3 配置文件

**frontend/.gitignore**
- 前端 Git 忽略文件配置

**frontend/index.html**
- HTML 入口文件
- 引用构建后的资源

**frontend/package.json**
- 前端依赖配置
- npm 脚本定义
- 核心依赖：
  - vue: ^3.5.24
  - vue-router: ^4.6.3
  - axios: ^1.13.2
  - d3: ^7.9.0
  - vite: ^7.2.4
  - @vitejs/plugin-vue: ^6.0.1
  - vitest: ^3.0.0

**frontend/package-lock.json**
- 前端依赖锁定文件

**frontend/vite.config.js**
- Vite 构建工具配置
- 开发服务器配置
- 插件配置
- 路径别名配置

**frontend/Dockerfile**
- Docker 容器化部署配置
- 基于 node:18-alpine 镜像
- 构建并运行前端应用

## 4. 依赖说明

### 4.1 后端依赖 (backend/requirements.txt)

```
# 核心框架
flask>=3.0.0              # Web 框架
flask-cors>=6.0.0         # 跨域支持

# LLM 相关
openai>=1.0.0             # LLM SDK（支持 OpenAI 格式的任意 LLM）

# Zep Cloud
zep-cloud==3.13.0         # 长期记忆服务

# OASIS 社交媒体模拟
camel-oasis==0.2.5        # 社交模拟引擎（Apache 2.0）
camel-ai==0.2.78          # CAMEL 框架

# 文件处理
PyMuPDF>=1.24.0           # PDF 解析

# 工具库
python-dotenv>=1.0.0      # 环境变量管理
pydantic>=2.0.0           # 数据验证
pydantic-settings>=2.0.0  # Pydantic 配置
email-validator>=2.0.0     # 邮箱验证

# 测试框架
pytest>=8.0.0             # 测试框架
pytest-cov>=4.0.0         # 代码覆盖率
```

### 4.2 前端依赖 (frontend/package.json)

```json
{
  "dependencies": {
    "vue": "^3.5.24",              // Vue.js 框架
    "vue-router": "^4.6.3",       // 路由管理
    "axios": "^1.13.2",           // HTTP 客户端
    "d3": "^7.9.0"                // 图谱可视化
  },
  "devDependencies": {
    "vite": "^7.2.4",            // 构建工具
    "@vitejs/plugin-vue": "^6.0.1",  // Vue 插件
    "vitest": "^3.0.0"           // 测试框架
  }
}
```

### 4.3 根目录依赖 (package.json)

```json
{
  "devDependencies": {
    "concurrently": "^9.1.2"      // 进程并发管理
  },
  "scripts": {
    "setup": "npm install && cd frontend && npm install",
    "setup:all": "npm install && cd frontend && npm install && cd ../backend && uv pip install -r requirements.txt",
    "dev": "concurrently \"npm run backend\" \"npm run frontend\"",
    "backend": "cd backend && python run.py",
    "frontend": "cd frontend && npm run dev"
  }
}
```

## 5. 文件命名规范

### 5.1 Python 文件
- 使用小写字母和下划线：`service_name.py`
- 模块初始化文件：`__init__.py`
- 配置文件：`config.py`
- 启动文件：`run.py`

### 5.2 Vue 组件
- 使用大驼峰命名：`ComponentName.vue`
- 步骤组件：`Step1GraphBuild.vue`
- 视图组件：`ViewName.vue`

### 5.3 JavaScript 文件
- 使用小写字母和下划线：`file_name.js`
- API 文件：按模块命名：`graph.js`, `simulation.js`

### 5.4 配置文件
- 使用小写字母和点号：`.env`, `.gitignore`
- 项目配置：`package.json`, `pyproject.toml`

## 6. 代码组织原则

### 6.1 分层架构
- **API 层**：处理 HTTP 请求和响应
- **服务层**：实现核心业务逻辑
- **模块层**：功能模块化封装
- **数据层**：定义数据模型和存储
- **工具层**：提供通用工具函数

### 6.2 模块化设计
- 每个模块职责单一
- 模块间通过接口通信
- 便于独立测试和维护
- 支持插件式扩展

### 6.3 代码复用
- 提取通用功能到工具层
- 封装常用操作到服务层
- 使用继承和组合实现复用
- 避免代码重复

## 7. 更新记录

### v1.3.0 (2026-01-20)

**重大更新：**
- 🚗 新增自动驾驶模式 (Auto-Pilot Mode)
- ☁️ 支持云端无人值守自动运行
- 🔄 支持断点续传，失败自动重试
- 📊 完整流程自动化：准备 -> 启动 -> 监控 -> 报告
- 🚀 新增模拟创建和准备功能：POST /api/simulation/create, prepare, prepare/status
- 🚀 新增实时状态查询：config/realtime, profiles/realtime, run-status/detail
- 🚀 新增批量采访智能体功能：POST /api/simulation/{id}/interview/batch
- 🚀 新增环境管理功能：env-status, close-env
- ⚡ 前端 simulation.js API 客户端重构，新增 requestWithRetry 统一重试机制
- ✅ 完善测试用例覆盖

**功能特性：**
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 自动准备：读取实体、生成Profile、生成配置
- ✅ 自动启动：自动启动模拟运行
- ✅ 自动监控：实时监控运行状态，自动处理异常
- ✅ 自动报告：模拟完成后自动生成报告
- ✅ 暂停/恢复功能：随时可暂停、恢复自动驾驶
- ✅ 状态持久化：支持服务重启后断点续传

**API 新增接口：**
- `POST /api/simulation/create` - 创建模拟
- `POST /api/simulation/prepare` - 准备模拟环境
- `POST /api/simulation/prepare/status` - 获取准备状态
- `GET /api/simulation/{id}/config/realtime` - 实时配置状态
- `GET /api/simulation/{id}/profiles/realtime` - 实时人设生成进度
- `GET /api/simulation/{id}/run-status/detail` - 运行状态详情
- `POST /api/simulation/{id}/interview/batch` - 批量采访智能体
- `POST /api/simulation/env-status` - 获取环境状态
- `POST /api/simulation/close-env` - 关闭模拟环境
- `POST /api/simulation/auto-pilot/config` - 配置自动驾驶模式
- `POST /api/simulation/auto-pilot/start` - 启动自动驾驶
- `POST /api/simulation/auto-pilot/pause` - 暂停自动驾驶
- `POST /api/simulation/auto-pilot/resume` - 恢复自动驾驶
- `POST /api/simulation/auto-pilot/stop` - 停止自动驾驶
- `GET /api/simulation/auto-pilot/status` - 获取自动驾驶状态
- `POST /api/simulation/auto-pilot/reset` - 重置自动驾驶状态

**新增文件：**
- `backend/app/services/auto_pilot_manager.py` - 自动驾驶核心服务
- `backend/tests/conftest.py` - Pytest 配置文件
- `backend/tests/test_report_module.py` - 报告模块测试
- `backend/tests/test_simulation_runner.py` - 模拟运行器测试
- `frontend/src/__tests__/example.spec.js` - 前端示例测试

**文件变更：**
- Logo 文件名从 Multimo_logo 改为 MiroFish_logo

### v1.2.0 (2026-01-20)

**重大更新：**
- 🎉 正式发布 v1.2.0 稳定版本
- 🚀 完整实现图谱构建功能
- 📊 完善模拟引擎和报告生成模块
- 🔧 优化代码结构和性能
- 📦 完整的测试覆盖

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 完整的 API 接口和错误处理
- ✅ Docker 容器化部署支持
- ✅ 完善的测试用例

**技术改进：**
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM
- Docker 容器化部署
- 完整的单元测试覆盖

### v1.0.1 (2026-01-20)

**API 变更：**
- 添加 POST /api/v1/graph/build 接口：支持构建知识图谱
- 添加 GET /api/v1/graph/<graph_id> 接口：获取知识图谱数据
- 添加 GET /api/v1/graph/<graph_id>/export 接口：导出知识图谱
- 移除旧的接口（合并到统一流程）

**代码改进：**
- 优化图谱存储路径，支持模拟目录和独立图谱目录两种存储方式
- 集成 SimulationManager 进行图谱文件管理和路径解析
- 添加完整的错误处理和日志记录
- 保持与现有 API 的一致性设计

### v1.0.0 (2026-01-20)
- 正式发布 v1.0 版本
- 完整实现图谱构建功能（实体抽取、关系提取、知识图谱）
- 完整实现环境搭建功能（人设生成、配置生成）
- 完整实现 Twitter 和 Reddit 双平台并行模拟
- 完整实现报告生成功能（基于模拟结果的预测报告）
- 完整实现智能体对话功能（与模拟世界中的智能体交互）
- 添加完整的文档（FRAMEWORK.md、CODE_DIRECTORY.md、README）
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM
- 重构架构，移除第三方受版权保护代码
- 实现核心接口定义（core/）
- 模块化设计（modules/）

**主要特性：**
- 上传种子材料并构建知识图谱
- 自动生成智能体人设
- 双平台并行模拟（Twitter + Reddit）
- 自动生成预测报告
- 与模拟智能体深度交互
- 完整的项目文档和代码注释
- 重构后的清晰架构设计
- 可扩展的模块化设计

### 2026-01-19
- 初始版本创建
- 完整的目录结构文档
- 详细的文件功能说明
