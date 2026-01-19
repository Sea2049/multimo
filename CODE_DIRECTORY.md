# MiroFish 代码目录文档

## 1. 项目根目录

```
MiroFish/
├── .env                    # 环境变量配置文件（包含 API 密钥等敏感信息）
├── .env.example            # 环境变量示例文件（用于参考）
├── .gitignore              # Git 忽略文件配置
├── CODE_DIRECTORY.md       # 代码目录文档（本文件）
├── FRAMEWORK.md            # 框架架构文档
├── LICENSE                 # AGPL-3.0 开源许可证
├── package.json            # 根目录依赖配置和 npm 脚本
├── package-lock.json       # 根目录依赖锁定文件
├── README.md               # 中文说明文档
├── README-EN.md            # 英文说明文档
├── replication_log.md      # 项目复制日志
├── body.json               # 测试数据文件
├── test.txt                # 测试文件
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
├── api/                    # API 路由层（处理 HTTP 请求）
├── models/                 # 数据模型层（定义数据结构）
├── services/               # 业务逻辑层（核心功能实现）
└── utils/                  # 工具函数层（通用工具）
```

#### 2.1.1 应用入口

**backend/app/__init__.py**
- Flask 应用工厂函数
- 配置 CORS（跨域资源共享）
- 注册 API 蓝图
- 设置日志系统
- 注册模拟进程清理函数

**backend/app/config.py**
- 统一的配置管理类
- 从项目根目录的 .env 文件加载配置
- 包含 Flask、LLM、Zep、OASIS 等配置
- 配置验证功能

#### 2.1.2 API 路由层 (backend/app/api/)

```
backend/app/api/
├── __init__.py             # API 蓝图初始化
├── graph.py                # 图谱操作 API 端点
├── simulation.py           # 模拟控制 API 端点
└── report.py               # 报告生成 API 端点
```

**backend/app/api/graph.py**
- POST /api/graph/upload - 上传种子材料
- POST /api/graph/extract - 提取实体和关系
- GET /api/graph/entities - 获取实体列表
- GET /api/graph/relationships - 获取关系列表
- GET /api/graph/export - 导出图谱数据

**backend/app/api/simulation.py**
- POST /api/simulation/config - 生成模拟配置
- POST /api/simulation/start - 启动模拟
- GET /api/simulation/status - 获取模拟状态
- POST /api/simulation/stop - 停止模拟
- GET /api/simulation/logs - 获取模拟日志
- POST /api/simulation/chat - 与智能体对话
- GET /api/simulation/history - 获取历史模拟

**backend/app/api/report.py**
- POST /api/report/generate - 生成报告
- GET /api/report/status - 获取报告生成状态
- GET /api/report/content - 获取报告内容
- GET /api/report/export - 导出报告

#### 2.1.3 数据模型层 (backend/app/models/)

```
backend/app/models/
├── __init__.py             # 模型初始化
├── project.py              # 项目数据模型
└── task.py                 # 任务数据模型
```

**backend/app/models/project.py**
- 项目数据结构定义
- 项目状态管理
- 项目元数据管理

**backend/app/models/task.py**
- 任务数据结构定义
- 任务状态管理
- 任务进度跟踪

#### 2.1.4 业务逻辑层 (backend/app/services/)

```
backend/app/services/
├── __init__.py
├── export_service.py              # 导出服务（导出图谱、报告等）
├── graph_builder.py               # 图谱构建服务（构建知识图谱）
├── oasis_profile_generator.py     # OASIS 人设生成器
├── ontology_generator.py          # 本体生成器
├── report_agent.py                # 报告智能体（生成预测报告）
├── simulation_config_generator.py # 模拟配置生成器
├── simulation_ipc.py              # 模拟进程间通信
├── simulation_manager.py          # 模拟管理器（管理模拟生命周期）
├── simulation_runner.py           # 模拟运行器（执行模拟任务）
├── text_processor.py              # 文本处理服务（文件解析、文本提取）
├── zep_entity_reader.py           # Zep 实体读取器
├── zep_graph_memory_updater.py    # Zep 图谱记忆更新器
└── zep_tools.py                   # Zep 工具函数
```

**backend/app/services/export_service.py**
- 提供图谱数据导出功能
- 支持多种导出格式
- 处理导出文件生成

**backend/app/services/graph_builder.py**
- 从文本中提取实体和关系
- 构建知识图谱结构
- 管理图谱数据存储

**backend/app/services/oasis_profile_generator.py**
- 为 OASIS 框架生成智能体人设
- 基于图谱数据生成个性化配置
- 支持 Twitter 和 Reddit 平台人设

**backend/app/services/ontology_generator.py**
- 生成本体结构
- 定义领域知识模型
- 支持知识推理

**backend/app/services/report_agent.py**
- 基于 LLM 的报告智能体
- 分析模拟数据
- 生成结构化预测报告
- 提供丰富的工具集

**backend/app/services/simulation_config_generator.py**
- 生成模拟配置文件
- 配置模拟环境参数
- 管理智能体配置

**backend/app/services/simulation_ipc.py**
- 处理模拟进程间通信
- 管理进程间数据传输
- 实现进程同步机制

**backend/app/services/simulation_manager.py**
- 管理模拟的完整生命周期
- 创建、启动、停止、查询模拟
- 管理模拟状态和日志
- 处理模拟错误和重试

**backend/app/services/simulation_runner.py**
- 执行模拟任务
- 集成 OASIS 框架
- 支持 Twitter 和 Reddit 双平台并行模拟
- 记录模拟日志

**backend/app/services/text_processor.py**
- 处理上传的文件
- 提取文本内容
- 支持 PDF、Markdown、TXT 格式
- 文本切块和预处理

**backend/app/services/zep_entity_reader.py**
- 从 Zep Cloud 读取实体数据
- 管理实体关系
- 支持实体查询

**backend/app/services/zep_graph_memory_updater.py**
- 更新 Zep 中的图谱记忆
- 管理时序记忆
- 同步图谱状态

**backend/app/services/zep_tools.py**
- Zep Cloud 工具函数
- 封装 Zep API 调用
- 处理 Zep 数据格式

#### 2.1.5 工具函数层 (backend/app/utils/)

```
backend/app/utils/
├── __init__.py
├── file_parser.py          # 文件解析工具（PDF、TXT、Markdown）
├── llm_client.py            # LLM 客户端封装（支持 OpenAI SDK 格式）
├── logger.py               # 日志配置（统一日志管理）
└── retry.py                # 重试机制（处理 API 调用失败）
```

**backend/app/utils/file_parser.py**
- 解析 PDF 文件
- 解析 TXT 文件
- 解析 Markdown 文件
- 处理文件编码问题

**backend/app/utils/llm_client.py**
- 封装 LLM API 调用
- 支持 OpenAI SDK 格式的任意 LLM
- 实现重试机制
- 错误处理和日志记录

**backend/app/utils/logger.py**
- 配置日志系统
- 设置日志格式和级别
- 支持日志文件轮转
- 区分不同模块的日志

**backend/app/utils/retry.py**
- 实现重试机制
- 支持指数退避
- 处理临时性错误
- 可配置重试次数和间隔

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

### 2.3 数据目录 (backend/uploads/)

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
│       ├── simulation.log # 模拟日志
│       ├── twitter_profiles.csv   # Twitter 人设
│       ├── reddit_profiles.json   # Reddit 人设
│       ├── twitter/       # Twitter 平台数据
│       │   └── actions.jsonl
│       └── reddit_simulation.db  # Reddit 数据库
└── reports/              # 报告文件存储
    └── report_*/         # 报告目录（每个报告一个）
        ├── outline.json  # 报告大纲
        ├── meta.json     # 报告元数据
        ├── progress.json # 生成进度
        ├── console_log.txt # 控制台日志
        ├── agent_log.jsonl # 智能体日志
        ├── full_report.md # 完整报告
        └── section_*.md # 分节报告
```

### 2.4 日志目录 (backend/logs/)

```
backend/logs/
└── 2026-01-*.log         # 按日期分类的日志文件
```

### 2.5 配置文件

**backend/pyproject.toml**
- Python 项目配置文件
- 定义项目元数据和依赖
- 使用 uv 包管理器

**backend/requirements.txt**
- Python 依赖列表
- 兼容传统 pip 安装方式

**backend/run.py**
- 后端启动入口
- 验证配置
- 启动 Flask 服务器
- 处理 Windows 控制台中文乱码问题

**backend/uv.lock**
- uv 包管理器锁文件
- 确保依赖版本一致性

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
└── views/                 # 页面视图
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
- 配置基础 URL
- 配置请求/响应拦截器
- 统一错误处理

**frontend/src/api/graph.js**
- 封装图谱相关 API 调用
- 上传种子材料
- 提取实体和关系
- 获取图谱数据
- 导出图谱

**frontend/src/api/simulation.js**
- 封装模拟相关 API 调用
- 生成模拟配置
- 启动/停止模拟
- 获取模拟状态
- 获取模拟日志
- 与智能体对话

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

### 3.3 配置文件

**frontend/.gitignore**
- 前端 Git 忽略文件配置

**frontend/index.html**
- HTML 入口文件
- 引用构建后的资源

**frontend/package.json**
- 前端依赖配置
- npm 脚本定义

**frontend/package-lock.json**
- 前端依赖锁定文件

**frontend/vite.config.js**
- Vite 构建工具配置
- 开发服务器配置
- 插件配置

## 4. 依赖说明

### 4.1 后端依赖 (backend/requirements.txt)

```
flask>=3.0.0              # Web 框架
flask-cors>=6.0.0         # 跨域支持
openai>=1.0.0             # LLM SDK
zep-cloud==3.13.0         # 长期记忆服务
camel-oasis==0.2.5        # 社交模拟引擎
camel-ai==0.2.78          # CAMEL 框架
PyMuPDF>=1.24.0           # PDF 解析
python-dotenv>=1.0.0      # 环境变量管理
pydantic>=2.0.0           # 数据验证
```

### 4.2 前端依赖 (frontend/package.json)

```json
{
  "dependencies": {
    "vue": "^3.x.x",              # Vue.js 框架
    "vue-router": "^4.x.x",       # 路由管理
    "axios": "^1.x.x",            # HTTP 客户端
    "d3": "^7.x.x"                # 图谱可视化
  },
  "devDependencies": {
    "vite": "^5.x.x",            // 构建工具
    "@vitejs/plugin-vue": "^5.x.x"  // Vue 插件
  }
}
```

### 4.3 根目录依赖 (package.json)

```json
{
  "devDependencies": {
    "concurrently": "^9.1.2"      // 进程并发管理
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
- **数据层**：定义数据模型和存储
- **工具层**：提供通用工具函数

### 6.2 模块化设计
- 每个模块职责单一
- 模块间通过接口通信
- 便于独立测试和维护

### 6.3 代码复用
- 提取通用功能到工具层
- 封装常用操作到服务层
- 使用继承和组合实现复用

## 7. 更新记录

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
- 集成 OASIS 社交模拟引擎
- 支持 OpenAI SDK 格式的任意 LLM

**主要特性：**
- 上传种子材料并构建知识图谱
- 自动生成智能体人设
- 双平台并行模拟（Twitter + Reddit）
- 自动生成预测报告
- 与模拟智能体深度交互
- 完整的项目文档和代码注释

### 2026-01-19
- 初始版本创建
- 完整的目录结构文档
- 详细的文件功能说明
