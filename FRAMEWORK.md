# MiroFish 框架文档

## 1. 项目概述

MiroFish 是一个基于多智能体技术的下一代 AI 预测引擎，通过构建高保真的平行数字世界来预测未来事件。项目采用前后端分离架构，后端使用 Python + Flask，前端使用 Vue.js。

**核心功能：**
- 图谱构建：从种子材料中提取实体和关系，构建知识图谱
- 环境搭建：生成智能体人设和仿真环境配置
- 多平台模拟：支持 Twitter 和 Reddit 双平台并行模拟
- 报告生成：基于模拟结果生成预测报告
- 深度互动：与模拟世界中的智能体进行对话

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│                   Vue.js Frontend                           │
│  (Step1-Step5 组件, API 客户端, 路由, 状态管理)                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                         应用层                                │
│                    Flask Backend                            │
│  (API 蓝图, 业务逻辑服务, 数据模型, 工具函数)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                        服务层                                 │
│  - LLM 客户端 (OpenAI SDK)                                   │
│  - Zep Cloud (记忆存储)                                       │
│  - OASIS 框架 (模拟引擎)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心技术栈

**后端技术栈：**
- Python 3.11-3.12
- Flask 3.0+ (Web 框架)
- Flask-CORS (跨域支持)
- OpenAI SDK (LLM 交互)
- Zep Cloud 3.13.0 (长期记忆)
- CAMEL-OASIS 0.2.5 (社交模拟引擎)
- PyMuPDF (PDF 解析)

**前端技术栈：**
- Vue.js 3
- Vue Router (路由)
- Axios (HTTP 客户端)
- D3.js (图谱可视化)
- Vite (构建工具)

**开发工具：**
- uv (Python 包管理器)
- npm/Node.js (前端包管理)
- concurrently (进程并发管理)

## 3. 目录结构详解

### 3.1 根目录

```
MiroFish/
├── .env                    # 环境变量配置文件
├── .env.example            # 环境变量示例文件
├── .gitignore              # Git 忽略文件
├── CODE_DIRECTORY.txt      # 代码目录清单
├── FRAMEWORK.md            # 框架文档（本文件）
├── LICENSE                 # 许可证文件
├── package.json            # 根目录依赖和脚本配置
├── README.md               # 中文说明文档
├── README-EN.md            # 英文说明文档
├── replication_log.md      # 复制日志
├── body.json               # 测试数据文件
├── test.txt                # 测试文件
├── static/                 # 静态资源目录
│   └── image/              # 图片资源
│       ├── Screenshot/     # 系统截图
│       ├── MiroFish_logo*.jpeg  # Logo
│       ├── shanda_logo.png # 盛大 Logo
│       ├── QQ群.png        # QQ 群二维码
│       └── 武大模拟演示封面.png  # 演示视频封面
├── backend/                # 后端目录
└── frontend/               # 前端目录
```

### 3.2 后端目录结构 (backend/)

```
backend/
├── app/                    # 应用核心代码
│   ├── __init__.py         # Flask 应用工厂
│   ├── config.py           # 配置管理类
│   ├── api/                # API 路由层
│   │   ├── __init__.py     # API 蓝图初始化
│   │   ├── graph.py        # 图谱操作 API
│   │   ├── simulation.py    # 模拟控制 API
│   │   └── report.py        # 报告生成 API
│   ├── models/             # 数据模型层
│   │   ├── __init__.py
│   │   ├── project.py      # 项目数据模型
│   │   └── task.py         # 任务数据模型
│   ├── services/           # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── export_service.py       # 导出服务
│   │   ├── graph_builder.py        # 图谱构建服务
│   │   ├── oasis_profile_generator.py  # OASIS 人设生成器
│   │   ├── ontology_generator.py   # 本体生成器
│   │   ├── report_agent.py         # 报告智能体
│   │   ├── simulation_config_generator.py  # 模拟配置生成器
│   │   ├── simulation_ipc.py       # 模拟进程间通信
│   │   ├── simulation_manager.py   # 模拟管理器
│   │   ├── simulation_runner.py   # 模拟运行器
│   │   ├── text_processor.py      # 文本处理服务
│   │   ├── zep_entity_reader.py   # Zep 实体读取器
│   │   ├── zep_graph_memory_updater.py  # Zep 图谱记忆更新器
│   │   └── zep_tools.py           # Zep 工具函数
│   └── utils/              # 工具函数层
│       ├── __init__.py
│       ├── file_parser.py  # 文件解析工具
│       ├── llm_client.py   # LLM 客户端封装
│       ├── logger.py       # 日志配置
│       └── retry.py        # 重试机制
├── scripts/                # 脚本目录
│   ├── action_logger.py           # 动作日志脚本
│   ├── run_parallel_simulation.py # 并行模拟运行脚本
│   ├── run_reddit_simulation.py    # Reddit 模拟运行脚本
│   ├── run_twitter_simulation.py  # Twitter 模拟运行脚本
│   └── test_profile_format.py     # 人设格式测试脚本
├── uploads/                # 上传文件目录
│   ├── projects/          # 项目上传文件
│   ├── simulations/        # 模拟数据
│   └── reports/            # 报告文件
├── logs/                   # 日志目录
├── pyproject.toml          # Python 项目配置
├── requirements.txt        # Python 依赖列表
├── run.py                  # 后端启动入口
└── uv.lock                 # uv 锁文件
```

### 3.3 前端目录结构 (frontend/)

```
frontend/
├── public/                 # 公共静态资源
│   └── icon.png           # 网站图标
├── src/                    # 源代码目录
│   ├── main.js            # 应用入口文件
│   ├── App.vue            # 根组件
│   ├── api/               # API 客户端模块
│   │   ├── index.js       # API 基础配置
│   │   ├── graph.js       # 图谱 API 客户端
│   │   ├── simulation.js  # 模拟 API 客户端
│   │   └── report.js      # 报告 API 客户端
│   ├── assets/            # 静态资源
│   │   └── logo/          # Logo 图片
│   ├── components/        # Vue 组件
│   │   ├── GraphPanel.vue          # 图谱展示面板
│   │   ├── HistoryDatabase.vue     # 历史数据库组件
│   │   ├── Step1GraphBuild.vue     # 步骤1：图谱构建
│   │   ├── Step2EnvSetup.vue       # 步骤2：环境搭建
│   │   ├── Step3Simulation.vue     # 步骤3：开始模拟
│   │   ├── Step4Report.vue         # 步骤4：报告生成
│   │   └── Step5Interaction.vue    # 步骤5：深度互动
│   ├── router/            # 路由配置
│   │   └── index.js       # 路由定义
│   ├── store/             # 状态管理
│   │   └── pendingUpload.js  # 待上传状态管理
│   └── views/             # 页面视图
│       ├── Home.vue               # 首页
│       ├── MainView.vue           # 主视图
│       ├── Process.vue            # 流程页面
│       ├── SimulationView.vue     # 模拟视图
│       ├── SimulationRunView.vue  # 模拟运行视图
│       ├── InteractionView.vue    # 互动视图
│       └── ReportView.vue         # 报告视图
├── .gitignore             # Git 忽略文件
├── index.html             # HTML 入口文件
├── package.json           # 前端依赖配置
├── package-lock.json      # 依赖锁定文件
└── vite.config.js         # Vite 配置文件
```

## 4. 核心组件与数据流

### 4.1 数据流向

```
用户上传种子材料 (文本/文件)
    ↓
[前端] Step1GraphBuild.vue
    ↓
[后端 API] /api/graph/upload
    ↓
[服务] text_processor.py → 实体抽取与关系提取
    ↓
[服务] graph_builder.py → 构建知识图谱
    ↓
[存储] Zep Cloud (长期记忆)
    ↓
[前端] Step2EnvSetup.vue
    ↓
[后端 API] /api/simulation/config
    ↓
[服务] simulation_config_generator.py → 生成模拟配置
    ↓
[服务] oasis_profile_generator.py → 生成智能体人设
    ↓
[前端] Step3Simulation.vue
    ↓
[后端 API] /api/simulation/start
    ↓
[服务] simulation_manager.py → 管理模拟生命周期
    ↓
[服务] simulation_runner.py → 执行模拟 (OASIS 框架)
    ↓
[存储] 本地数据库 (SQLite) + 模拟日志
    ↓
[前端] Step4Report.vue
    ↓
[后端 API] /api/report/generate
    ↓
[服务] report_agent.py → 生成预测报告
    ↓
[前端] Step5Interaction.vue
    ↓
[后端 API] /api/simulation/chat
    ↓
[服务] 与模拟智能体对话交互
```

### 4.2 关键服务说明

#### 4.2.1 图谱构建服务 (graph_builder.py)
- 功能：从文本中提取实体和关系，构建知识图谱
- 输入：种子材料（文本、PDF 等）
- 输出：实体-关系图，存储在 Zep Cloud

#### 4.2.2 文本处理服务 (text_processor.py)
- 功能：处理上传的文件，提取文本内容
- 支持格式：PDF、Markdown、TXT
- 功能：文本切块、实体抽取

#### 4.2.3 模拟管理器 (simulation_manager.py)
- 功能：管理模拟的完整生命周期
- 职责：创建、启动、停止、查询模拟
- 存储：模拟状态、配置、日志

#### 4.2.4 模拟运行器 (simulation_runner.py)
- 功能：执行模拟任务
- 集成：OASIS 框架
- 平台：Twitter、Reddit 双平台并行

#### 4.2.5 报告智能体 (report_agent.py)
- 功能：基于模拟结果生成预测报告
- 工具：丰富的工具集用于分析模拟数据
- 输出：结构化的预测报告

#### 4.2.6 LLM 客户端 (llm_client.py)
- 功能：封装 LLM API 调用
- 支持：OpenAI SDK 格式的任意 LLM
- 功能：重试机制、错误处理

## 5. 配置管理

### 5.1 环境变量 (.env)

```env
# Flask 配置
SECRET_KEY=mirofish-secret-key
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# LLM API 配置（支持 OpenAI SDK 格式）
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Zep Cloud 配置
ZEP_API_KEY=your_zep_api_key

# OASIS 模拟配置
OASIS_DEFAULT_MAX_ROUNDS=10

# Report Agent 配置
REPORT_AGENT_MAX_TOOL_CALLS=5
REPORT_AGENT_MAX_REFLECTION_ROUNDS=2
REPORT_AGENT_TEMPERATURE=0.5
```

### 5.2 配置类 (app/config.py)

```python
class Config:
    """Flask 配置类"""
    # Flask 配置
    SECRET_KEY = ...
    DEBUG = ...
    JSON_AS_ASCII = False  # 支持中文显示
    
    # LLM 配置
    LLM_API_KEY = ...
    LLM_BASE_URL = ...
    LLM_MODEL_NAME = ...
    
    # Zep 配置
    ZEP_API_KEY = ...
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 50MB
    UPLOAD_FOLDER = ...
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # OASIS 模拟配置
    OASIS_DEFAULT_MAX_ROUNDS = ...
    OASIS_SIMULATION_DATA_DIR = ...
    OASIS_TWITTER_ACTIONS = [...]
    OASIS_REDDIT_ACTIONS = [...]
    
    # Report Agent 配置
    REPORT_AGENT_MAX_TOOL_CALLS = ...
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = ...
    REPORT_AGENT_TEMPERATURE = ...
```

## 6. API 端点

### 6.1 图谱 API (/api/graph/*)
- `POST /api/graph/upload` - 上传种子材料
- `POST /api/graph/extract` - 提取实体和关系
- `GET /api/graph/entities` - 获取实体列表
- `GET /api/graph/relationships` - 获取关系列表
- `GET /api/graph/export` - 导出图谱数据

### 6.2 模拟 API (/api/simulation/*)
- `POST /api/simulation/config` - 生成模拟配置
- `POST /api/simulation/start` - 启动模拟
- `GET /api/simulation/status` - 获取模拟状态
- `POST /api/simulation/stop` - 停止模拟
- `GET /api/simulation/logs` - 获取模拟日志
- `POST /api/simulation/chat` - 与智能体对话
- `GET /api/simulation/history` - 获取历史模拟

### 6.3 报告 API (/api/report/*)
- `POST /api/report/generate` - 生成报告
- `GET /api/report/status` - 获取报告生成状态
- `GET /api/report/content` - 获取报告内容
- `GET /api/report/export` - 导出报告

## 7. 工作流程

### 7.1 完整工作流程

1. **图谱构建**
   - 用户上传种子材料
   - 后端处理文件并提取文本
   - 使用 LLM 抽取实体和关系
   - 构建知识图谱并存储

2. **环境搭建**
   - 基于图谱生成智能体人设
   - 配置仿真环境参数
   - 生成模拟配置文件

3. **开始模拟**
   - 初始化 OASIS 模拟环境
   - Twitter 和 Reddit 双平台并行运行
   - 智能体自主交互与演化
   - 动态更新时序记忆

4. **报告生成**
   - ReportAgent 分析模拟数据
   - 使用工具集深度交互
   - 生成结构化预测报告

5. **深度互动**
   - 与模拟世界中的任意智能体对话
   - 与 ReportAgent 进行对话
   - 动态注入变量重新推演

## 8. 部署说明

### 8.1 开发环境

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的 API 密钥

# 2. 安装依赖
npm run setup:all

# 3. 启动服务
npm run dev
```

服务地址：
- 前端：http://localhost:3000
- 后端 API：http://localhost:5001

### 8.2 生产环境

**后端部署：**
```bash
cd backend
uv run gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**前端部署：**
```bash
cd frontend
npm run build
# 将 dist 目录部署到 Web 服务器
```

### 8.3 环境要求

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18+ | 前端运行环境 |
| Python | ≥3.11, ≤3.12 | 后端运行环境 |
| uv | 最新版 | Python 包管理器 |

## 9. 安全注意事项

1. **API 密钥管理**
   - 永远不要将 .env 文件提交到版本控制
   - 在生产环境中使用安全的密钥管理服务

2. **CORS 配置**
   - 生产环境中建议将 origins 设置为具体的前端域名
   - 避免使用 "*" 以防止 CSRF 攻击

3. **文件上传安全**
   - 限制文件类型和大小
   - 验证上传文件的内容

4. **SQL 注入防护**
   - 使用参数化查询
   - 验证用户输入

5. **XSS 防护**
   - 前端使用 Vue.js 的自动转义
   - 后端对用户输出进行转义

## 10. 扩展性设计

### 10.1 模块化架构
- 清晰的分层架构（API、服务、工具）
- 每个模块职责单一
- 便于独立开发和测试

### 10.2 可扩展性
- 支持添加新的模拟平台
- 支持集成新的 LLM 服务
- 支持添加新的报告生成策略

### 10.3 可维护性
- 统一的日志管理
- 统一的错误处理
- 详细的代码注释

## 11. 更新日志

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

### v0.1.0
- 初始版本发布
- 实现基础图谱构建功能
- 实现 Twitter 和 Reddit 双平台模拟
- 实现报告生成功能
- 实现智能体对话功能
