



[English](./README-EN.md) | [中文文档](./README.md)

</div>

## ⚡ 项目概述

**Multimo** 是一款基于多智能体技术的新一代 AI 预测引擎。通过提取现实世界的种子信息（如突发新闻、政策草案、金融信号），自动构建出高保真的平行数字世界。在此空间内，成千上万个具备独立人格、长期记忆与行为逻辑的智能体进行自由交互与社会演化。你可透过「上帝视角」动态注入变量，精准推演未来走向——**让未来在数字沙盘中预演，助决策在百战模拟后胜出**。

> 你只需：上传种子材料（数据分析报告或者有趣的小说故事），并用自然语言描述预测需求</br>
> Multimo 将返回：一份详尽的预测报告，以及一个可深度交互的高保真数字世界

### 我们的愿景

Multimo 旨在构建一个映射现实世界的群体智能镜像——通过捕捉个体之间的互动，揭示由此涌现的集体行为规律，从而超越传统预测方法的边界。

- **宏观层面**：我们为决策者打造一个零风险的“预演实验室”，让政策制定、公共沟通等重大举措在虚拟环境中先行试错、优化迭代。
- **微观层面**：我们为每一位用户搭建一个充满想象力的“创意沙盘”——无论是推演小说情节的走向、模拟社交实验，还是探索天马行空的“如果”场景，都能轻松上手、趣味十足。

从严谨的预测分析到轻松的趣味仿真，Multimo 让每一个“假如”都有迹可循，让看见未来、探索万物成为触手可及的可能。


## 🔄 工作流程

1. **图谱构建**：现实种子提取 & 个体与群体记忆注入 & GraphRAG构建
2. **环境搭建**：实体关系抽取 & 人设生成 & 环境配置Agent注入仿真参数
3. **开始模拟**：双平台并行模拟 & 自动解析预测需求 & 动态更新时序记忆
4. **报告生成**：ReportAgent拥有丰富的工具集与模拟后环境进行深度交互
5. **深度互动**：与模拟世界中的任意一位进行对话 & 与ReportAgent进行对话

## 🚀 快速开始

### 前置要求

| 工具 | 版本要求 | 说明 | 安装检查 |
|------|---------|------|---------|
| **Node.js** | 18+ | 前端运行环境，包含 npm | `node -v` |
| **Python** | ≥3.11, ≤3.12 | 后端运行环境 | `python --version` |
| **uv** | 最新版 | Python 包管理器 | `uv --version` |

### 1. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入必要的 API 密钥
```

**必需的环境变量：**

```env
# LLM API配置（支持 OpenAI SDK 格式的任意 LLM）
# 推荐使用阿里百炼平台qwen-plus模型：https://bailian.console.aliyun.com/
# 注意消耗较大，可先进行小于40轮的模拟尝试
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Zep Cloud 配置
# 每月免费额度即可支撑简单使用：https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key
```

### 2. 安装依赖

```bash
# 一键安装所有依赖（根目录 + 前端 + 后端）
npm run setup:all
```

或者分步安装：

```bash
# 安装 Node 依赖（根目录 + 前端）
npm run setup

# 安装 Python 依赖（自动创建虚拟环境）
npm run setup:backend
```

### 3. 启动服务

```bash
# 同时启动前后端（在项目根目录执行）
npm run dev
```

**服务地址：**
- 前端：`http://localhost:3000`
- 后端 API：`http://localhost:5001`

**单独启动：**

```bash
npm run backend   # 仅启动后端
npm run frontend  # 仅启动前端
```

## 📁 项目结构

```
Multimo/
├── backend/                 # 后端 Python 应用
│   ├── app/                 # 应用核心代码
│   │   ├── api/            # API 路由层
│   │   ├── models/         # 数据模型层
│   │   ├── services/       # 业务逻辑层
│   │   ├── modules/        # 功能模块层（重构）
│   │   ├── core/           # 核心接口层
│   │   ├── storage/        # 存储层
│   │   └── utils/          # 工具函数层
│   ├── scripts/            # 脚本目录
│   ├── tests/              # 测试目录
│   ├── uploads/            # 上传文件目录
│   └── logs/               # 日志目录
├── frontend/                # 前端 Vue.js 应用
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── __tests__/      # 测试文件
│   └── public/             # 公共静态资源
├── static/                  # 静态资源（图片等）
├── FRAMEWORK.md             # 框架架构文档
├── CODE_DIRECTORY.md        # 代码目录文档
├── README.md                # 中文说明文档（本文件）
├── README-EN.md             # 英文说明文档
└── TESTING.md               # 测试文档
```

详细的目录结构和文件说明请参考：
- [框架架构文档](./FRAMEWORK.md)
- [代码目录文档](./CODE_DIRECTORY.md)

## 🛠️ 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11-3.12 | 编程语言 |
| **Flask** | 3.0+ | Web 框架 |
| **OpenAI SDK** | 1.0+ | LLM 交互（支持任意兼容 OpenAI SDK 格式的 LLM） |
| **Zep Cloud** | 3.13.0 | 长期记忆服务 |
| **CAMEL-OASIS** | 0.2.5 | 社交模拟引擎（Apache 2.0 开源） |
| **PyMuPDF** | 1.24.0+ | PDF 解析 |
| **Pydantic** | 2.0+ | 数据验证 |
| **Pytest** | 8.0+ | 单元测试框架 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue.js** | 3.5.24 | 前端框架 |
| **Vue Router** | 4.6.3 | 路由管理 |
| **Axios** | 1.13.2 | HTTP 客户端 |
| **D3.js** | 7.9.0 | 图谱可视化 |
| **Vite** | 7.2.4 | 构建工具 |
| **Vitest** | 3.0.0 | 测试框架 |

## 📖 文档

- **[框架架构文档](./FRAMEWORK.md)** - 详细的系统架构、核心接口定义、工作流程
- **[代码目录文档](./CODE_DIRECTORY.md)** - 完整的代码目录结构和文件功能说明
- **[架构文档](./ARCHITECTURE.md)** - 系统架构设计和技术实现细节
- **[API 文档](./API.md)** - REST API 端点说明和使用示例
- **[开发指南](./DEVELOPMENT.md)** - 开发环境搭建和开发规范
- **[测试文档](./TESTING.md)** - 测试指南和用例说明

## 🏗️ 架构设计

### 核心模块

Multimo 采用模块化架构设计，核心模块包括：

#### 1. 图谱构建模块 ([`backend/app/modules/graph/`](backend/app/modules/graph/))
- **实体提取器**：基于 LLM 的智能实体识别
- **关系提取器**：提取实体间的关系
- **图谱构建器**：构建知识图谱结构
- **图谱存储**：集成 Zep Cloud 进行长期记忆存储

#### 2. 模拟引擎模块 ([`backend/app/modules/simulation/`](backend/app/modules/simulation/))
- **智能体实现**：基于 LLM 的智能体，具备独立人格和行为逻辑
- **模拟引擎**：多智能体并行模拟引擎
- **平台实现**：Twitter 和 Reddit 双平台模拟
- **集成 OASIS**：使用 Apache 2.0 开源的 OASIS 框架

#### 3. 报告生成模块 ([`backend/app/modules/report/`](backend/app/modules/report/))
- **数据分析器**：模拟数据统计分析
- **报告生成器**：基于 LLM 的结构化报告生成
- **多格式导出**：支持 JSON、Markdown 格式

#### 4. 交互模块 ([`backend/app/modules/interaction/`](backend/app/modules/interaction/))
- **聊天接口**：与模拟智能体对话
- **系统对话**：与 ReportAgent 深度交互
- **动态变量注入**：实时修改模拟参数

#### 5. 自动驾驶模块 ([`backend/app/services/auto_pilot_manager.py`](backend/app/services/auto_pilot_manager.py))
- **自动驾驶管理器**：实现全自动化的模拟流程
- **状态管理**：支持暂停、恢复、停止操作
- **断点续传**：服务重启后可继续执行

### 技术特性

- ✅ **前后端分离**：Vue.js + Flask 架构
- ✅ **模块化设计**：清晰的模块划分和接口定义
- ✅ **可扩展性**：支持添加新的模拟平台和 LLM 服务
- ✅ **长期记忆**：集成 Zep Cloud 实现智能体长期记忆
- ✅ **开源框架**：集成 Apache 2.0 开源的 OASIS 框架
- ✅ **多 LLM 支持**：支持 OpenAI SDK 格式的任意 LLM
- ✅ **双平台并行**：Twitter 和 Reddit 同时模拟
- ✅ **自动驾驶模式**：支持无人值守自动运行
- ✅ **完整测试覆盖**：Pytest + Vitest 双重测试保障

## 🧪 测试框架

### 后端测试

```bash
# 运行后端测试
cd backend
pytest tests/ -v
```

**测试文件：**
- `backend/tests/conftest.py` - Pytest 配置文件
- `backend/tests/test_graph_module.py` - 图谱模块测试
- `backend/tests/test_report_module.py` - 报告模块测试
- `backend/tests/test_simulation_runner.py` - 模拟运行器测试

### 前端测试

```bash
# 运行前端测试
cd frontend
npm run test
```

**测试文件：**
- `frontend/src/__tests__/example.spec.js` - 示例测试

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范

- 遵循项目的代码风格和命名规范
- 为新功能添加必要的注释和文档
- 确保所有测试通过
- 提交前运行 lint 和 typecheck

&nbsp;

## 📄 致谢

Multimo 的仿真引擎由 **[OASIS](https://github.com/camel-ai/oasis)** 驱动，我们衷心感谢 CAMEL-AI 团队的开源贡献！

感谢所有为 Multimo 项目做出贡献的开发者和用户。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

OASIS 框架采用 [Apache 2.0 License](LICENSE-OASIS) 许可证。

## 📝 更新日志

### v2.70 (2026-02-02)

**版本固化：**
- 🎉 正式发布 v2.70 版本
- 🚀 生产部署优化与稳定性增强
- 🎨 UI 体验优化
- ⚡ 性能大幅提升

**部署改进：**
- ✅ 新增磁盘清理脚本
- ✅ Docker 健康检查端点兼容性
- ✅ PyTorch CPU 版本优化，镜像体积减少 10GB+
- ✅ Docker 数据路径统一
- ✅ Nginx 配置优化

**UI 改进：**
- 🎨 InteractionView 新增导出按钮
- 🎨 报告导出响应式头部按钮优化

**性能优化：**
- ⚡ 报告生成速度优化（并行化处理）
- ⚡ 报告生成缓存机制
- ⚡ ReACT 格式工具调用解析修复

**文档更新：**
- 📚 更新框架文档、代码目录和 README
- 📚 新增 CHANGELOG.md 变更日志文件

### v1.61 (2026-02-01)

**版本固化：**
- 🎉 正式发布 v1.61 版本
- 🔄 报告生成断点续传功能
- 📄 扫描版 PDF OCR 识别支持
- 📥 报告下载功能增强
- 🔧 LLM 客户端优化

**新增功能：**
- ✅ 报告任务工作器：使用独立线程运行报告生成，支持断点续传
- ✅ 扫描版 PDF OCR 识别：自动检测并提取扫描版 PDF 文字
- ✅ 报告下载功能改进：支持多章节报告自动合并

**后端改进：**
- 🔧 新增 `services/report_task_worker.py` - 报告任务断点续传
- 🔧 `report_agent.py` - 新增检查点回调支持
- 🔧 `file_parser.py` - 新增 OCR 识别功能
- 🔧 `api/v1/report.py` - 改进报告下载逻辑

**依赖更新：**
- 新增 `pytesseract` - OCR 识别支持
- 新增 `Pillow` - 图像处理支持

### v1.60 (2026-01-30)

**版本固化：**
- 🎉 正式发布 v1.60 版本
- 🔐 P0+P1 安全和稳定性改进
- 🏗️ API 层模块化重构
- 🎨 前端组件库优化
- 📚 完善文档体系

**安全改进：**
- ✅ 修复 traceback 泄露问题，生产环境不再暴露堆栈信息
- ✅ SQL 注入防护：全面的输入验证和清理机制
- ✅ 线程安全：修复多线程环境下的竞态条件
- ✅ 定时器清理：组件卸载时自动清理，避免内存泄漏
- ✅ API 超时配置：支持配置请求超时

**后端架构改进：**
- 🔧 新增 API 装饰器模块：统一的请求验证和参数清理
- 🔧 新增 API 响应构建模块：统一的响应格式
- 🔧 模拟 API 模块化重构：按功能拆分为多个子模块
- 🔧 报告服务模块化：独立的日志和数据模型

**前端架构改进：**
- 🎨 新增通用组件库：LoadingSpinner、Modal、StatusBadge、StepCard
- 🔧 新增轮询 Composable：统一的轮询逻辑，自动清理
- 🔧 新增工具函数：格式化和 Markdown 处理
- 🐛 修复多个前端组件和视图的问题

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 本体生成功能（生成本体结构）
- ✅ 完整的 API 接口和错误处理
- ✅ Docker 容器化部署支持
- ✅ 阿里云部署支持
- ✅ 完善的测试用例

**技术改进：**
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM
- Docker 容器化部署
- 完整的单元测试覆盖

### v1.30 (2026-01-22)

**版本固化：**
- 🎉 正式发布 v1.30 版本
- 📚 完善文档体系，更新框架文档、代码目录和 README
- 🔧 统一版本管理，支持版本固化
- 📦 完整的项目文档和代码目录
- 🚀 支持自动化 GitHub 推送
- 🐛 修复前端组件和视图的多个问题
- 🚀 新增阿里云部署支持

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 本体生成功能（生成本体结构）
- ✅ 模拟创建和准备功能
- ✅ 实时状态查询功能
- ✅ 批量采访智能体功能
- ✅ 环境管理功能
- ✅ 完整的 API 接口和错误处理
- ✅ Docker 容器化部署支持
- ✅ 阿里云部署支持
- ✅ 完善的测试用例

**技术改进：**
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM
- Docker 容器化部署
- 阿里云部署脚本和配置
- 完整的单元测试覆盖

### v1.51 (2026-01-21)

**文档更新：**
- 📚 更新 FRAMEWORK.md 框架架构文档
- 📚 更新 CODE_DIRECTORY.md 代码目录文档
- 📚 更新 README.md 项目说明文档
- 🔧 统一版本管理，支持版本固化
- 🚀 支持自动化 GitHub 推送
- ✅ 添加完整的版本历史记录
- ✅ 完善项目文档和代码目录

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 本体生成功能（生成本体结构）
- ✅ 模拟创建和准备功能
- ✅ 实时状态查询功能
- ✅ 批量采访智能体功能
- ✅ 环境管理功能
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

### v1.50 (2026-01-21)

**重大更新：**
- 🎉 正式发布 v1.50 稳定版本
- 📚 完善文档体系，更新框架文档、代码目录和 README
- 🔧 统一版本管理，支持版本固化
- 📦 完整的项目文档和代码目录
- 🚀 支持自动化 GitHub 推送

**文档更新：**
- ✅ 更新 FRAMEWORK.md 框架架构文档
- ✅ 更新 CODE_DIRECTORY.md 代码目录文档
- ✅ 更新 README.md 项目说明文档
- ✅ 添加完整的版本历史记录

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 本体生成功能（生成本体结构）
- ✅ 模拟创建和准备功能
- ✅ 实时状态查询功能
- ✅ 批量采访智能体功能
- ✅ 环境管理功能
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

### v1.4.0 (2026-01-20)

**功能更新：**
- 🚀 新增本体生成功能：POST /api/graph/ontology/generate
- 🚀 新增任务状态查询：GET /api/graph/task/{task_id}
- 🚀 新增项目信息查询：GET /api/graph/project/{project_id}
- 🚀 新增文档添加功能：POST /api/graph/project/{project_id}/documents/add
- 🚀 新增图谱数据查询：GET /api/graph/data/{graph_id}
- 🚀 新增模拟恢复检查：GET /api/simulation/{id}/resumable

**代码改进：**
- ⚡ 前端 graph.js API 客户端重构
- ⚡ 新增 requestWithRetry 统一重试机制

**前端 API 客户端新增函数：**
- 生成本体：generateOntology
- 查询任务状态：getTaskStatus
- 获取图谱数据：getGraphData
- 获取项目信息：getProject
- 添加文档：addDocuments
- 检查模拟恢复：checkResumable

### v1.3.0 (2026-01-20)

**功能更新：**
- 🚀 新增模拟创建功能：POST /api/simulation/create
- 🚀 新增准备模拟环境功能：POST /api/simulation/prepare
- 🚀 新增获取准备状态功能：POST /api/simulation/prepare/status
- 🚀 新增实时配置状态查询：GET /api/simulation/{id}/config/realtime
- 🚀 新增实时人设生成进度：GET /api/simulation/{id}/profiles/realtime
- 🚀 新增批量采访智能体功能：POST /api/simulation/{id}/interview/batch
- 🚀 新增环境状态查询：POST /api/simulation/env-status
- 🚀 新增关闭模拟环境功能：POST /api/simulation/close-env
- 🚀 新增运行状态详情查询：GET /api/simulation/{id}/run-status/detail

**代码改进：**
- ⚡ 前端 simulation.js API 客户端重构
- ⚡ 新增 requestWithRetry 统一重试机制
- ⚡ 完善测试用例覆盖

**新增文件：**
- `backend/tests/conftest.py` - Pytest 配置文件
- `backend/tests/test_report_module.py` - 报告模块测试
- `backend/tests/test_simulation_runner.py` - 模拟运行器测试
- `frontend/src/__tests__/example.spec.js` - 前端示例测试
- `TESTING.md` - 测试文档

**文件变更：**
- Logo 文件名从 Multimo_logo 改为 MiroFish_logo

### v1.3.0 (2026-01-20)

**重大更新：**
- 🚗 新增自动驾驶模式 (Auto-Pilot Mode)
- ☁️ 支持云端无人值守自动运行
- 🔄 支持断点续传，失败自动重试
- 📊 完整流程自动化：准备 -> 启动 -> 监控 -> 报告

**功能特性：**
- ✅ 自动驾驶模式（AUTO / MANUAL 模式切换）
- ✅ 自动准备：读取实体、生成Profile、生成配置
- ✅ 自动启动：自动启动模拟运行
- ✅ 自动监控：实时监控运行状态，自动处理异常
- ✅ 自动报告：模拟完成后自动生成报告
- ✅ 暂停/恢复功能：随时可暂停、恢复自动驾驶
- ✅ 状态持久化：支持服务重启后断点续传

**API 新增接口：**
- `POST /api/simulation/auto-pilot/config` - 配置自动驾驶模式
- `POST /api/simulation/auto-pilot/start` - 启动自动驾驶
- `POST /api/simulation/auto-pilot/pause` - 暂停自动驾驶
- `POST /api/simulation/auto-pilot/resume` - 恢复自动驾驶
- `POST /api/simulation/auto-pilot/stop` - 停止自动驾驶
- `GET /api/simulation/auto-pilot/status` - 获取自动驾驶状态
- `POST /api/simulation/auto-pilot/reset` - 重置自动驾驶状态

**新增文件：**
- `backend/app/services/auto_pilot_manager.py` - 自动驾驶核心服务

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

### v1.0.0 (2026-01-20)

**重大更新：**
- 🎉 正式发布 v1.0 版本
- 🏗️ 完整重构架构，移除第三方受版权保护代码
- 🔧 实现核心接口定义（[`core/interfaces.py`](backend/app/core/interfaces.py)）
- 📦 模块化设计（[`modules/`](backend/app/modules/)）

**功能特性：**
- ✅ 图谱构建功能（实体抽取、关系提取、知识图谱）
- ✅ 环境搭建功能（人设生成、配置生成）
- ✅ Twitter 和 Reddit 双平台并行模拟
- ✅ 报告生成功能（基于模拟结果的预测报告）
- ✅ 智能体对话功能（与模拟世界中的智能体交互）
- ✅ 完整的项目文档和代码注释

**技术栈：**
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM

## 🔗 相关链接

- [GitHub 仓库](https://github.com/666ghj/Multimo)
- [OASIS 框架](https://github.com/camel-ai/oasis)
- [CAMEL-AI](https://github.com/camel-ai/camel)

---

<div align="center">

**如果觉得 Multimo 对你有帮助，请给我们一个 ⭐️ Star！**

Made with ❤️ by Multimo Team

</div>
