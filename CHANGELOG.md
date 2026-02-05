# Multimo 变更日志

本文件记录 Multimo 项目的所有版本变更历史。

## [v2.72] - 2026-02-05

### 版本亮点
- 🎉 正式发布 v2.72 版本
- 🔧 部署脚本兼容性改进

### 部署改进
- `deploy/aliyun/server-deploy.sh` 使用 `bash deploy.sh` 替代 `./deploy.sh` 调用（prod/staging/all），提升在无执行权限或不同 shell 环境下的兼容性

---

## [v2.71] - 2026-02-05

### 版本亮点
- 🎉 正式发布 v2.71 版本
- 🎨 UI 精简与体验优化
- 🏗️ 模块化重构与安全增强
- ⚡ 稳定性与容错改进

### UI 改进
- 首页图谱风格动态 Logo 替换静态图片（GraphLogo.vue）
- 报告页返回逻辑与头部按钮精简：ReportView 移除「返回模拟/日志/导出全部」
- InteractionView 新增「返回报告」、移除「导出全部」
- Favicon 使用透明 GIF 避免浏览器缓存
- 报告生成减少 AI 风格措辞

### 模块化重构
- Step2EnvSetup.vue 拆分为 6 个子组件（env-setup/）
- report_agent.py 拆分为模块化子包（logger/models/agent/manager）
- database.py 添加线程安全连接池（threading.local）

### 安全增强
- validators.py 添加 python-magic MIME 检测
- validators.py 文件内容扫描范围从 8KB 扩展到 64KB

### 修复与优化
- 图谱构建失败处理：前端显示具体错误，后端重试机制，新增 /repair API
- Auto-pilot 后台任务恢复与错误处理改进
- Nginx 对缺失 staging 后端的容错
- DELETE 路由移至 simulation/control.py 解决模块导入冲突
- 路由顺序调整，确保 /history 优先匹配
- Node.js 升级至 20 以支持 Vite 7.x

### 新增功能
- 推演记录手动删除功能

---

## [v2.70] - 2026-02-02

### 版本亮点
- 🎉 正式发布 v2.70 版本
- 🚀 生产部署优化与稳定性增强
- 🎨 UI 体验优化
- ⚡ 性能大幅提升

### 新增功能
- 新增磁盘清理脚本 (`deploy/scripts/disk-cleanup.sh`)
- InteractionView 新增导出按钮
- Docker 健康检查端点 (`/api/health`)

### 性能优化
- 报告生成速度优化（并行化处理）
- 报告生成缓存机制
- PyTorch CPU 版本优化，镜像体积减少 10GB+

### 修复
- ReACT 格式工具调用解析修复
- 响应式头部按钮优化
- Docker 数据路径统一
- 移除重复的 addLog 声明
- init_auth 的 app context 问题修复
- Nginx client_max_body_size 增加到 100M
- 移除前端 nginx 的后端代理配置
- 报告导出使用相对 API 路径

### 文档
- 更新 FRAMEWORK.md 框架架构文档
- 更新 CODE_DIRECTORY.md 代码目录文档
- 更新 README.md 项目说明文档
- 新增 CHANGELOG.md 变更日志文件

---

## [v1.61] - 2026-02-01

### 版本亮点
- 🔄 报告生成断点续传功能
- 📄 扫描版 PDF OCR 识别支持
- 📥 报告下载功能增强
- 🔧 LLM 客户端优化

### 新增功能
- 报告任务工作器 (`report_task_worker.py`)
  - 使用独立线程运行报告生成
  - 任务状态持久化到数据库
  - 支持从检查点恢复（断点续传）
  - 服务重启后自动恢复中断的任务
- 扫描版 PDF OCR 识别
  - 自动检测 PDF 是否为扫描版
  - 使用 pytesseract 进行 OCR 识别
  - 支持中英文混合文档
- 报告下载功能改进
  - 通过 simulation_id 自动查找 report_id
  - 支持多章节报告自动合并

### 后端改进
- `services/report_task_worker.py` - 报告任务断点续传
- `report_agent.py` - 新增检查点回调支持
- `file_parser.py` - 新增 OCR 识别功能
- `llm_client.py` - 优化错误处理和重试机制
- `api/v1/report.py` - 改进报告下载逻辑

### 依赖更新
- 新增 `pytesseract` - OCR 识别支持
- 新增 `Pillow` - 图像处理支持

---

## [v1.60] - 2026-01-30

### 版本亮点
- 🔐 P0+P1 安全和稳定性改进
- 🏗️ API 层模块化重构
- 🎨 前端组件库优化
- 📚 完善文档体系

### 安全改进
- 修复 traceback 泄露问题
- SQL 注入防护：全面的输入验证和清理机制
- 线程安全：修复多线程环境下的竞态条件
- 定时器清理：组件卸载时自动清理
- API 超时配置

### 后端架构改进
- 新增 API 装饰器模块 (`api/decorators.py`)
- 新增 API 响应构建模块 (`api/response.py`)
- 模拟 API 模块化重构 (`api/simulation/`)
- 报告服务模块化 (`services/report/`)

### 前端架构改进
- 新增通用组件库 (`components/common/`)
  - LoadingSpinner、Modal、StatusBadge、StepCard
- 新增轮询 Composable (`composables/usePolling.js`)
- 新增工具函数 (`utils/`)
  - formatters.js、markdown.js

---

## [v1.52] - 2026-01-21

### 项目重命名
- 全局替换：`mirofish` → `multimo`
- 涉及 19 个文件，24 处替换

---

## [v1.51] - 2026-01-21

### 文档更新
- 更新 FRAMEWORK.md 框架架构文档
- 更新 CODE_DIRECTORY.md 代码目录文档
- 更新 README.md 项目说明文档
- 统一版本管理，支持版本固化
- 支持自动化 GitHub 推送

---

## [v1.50] - 2026-01-21

### 版本亮点
- 🎉 正式发布 v1.50 稳定版本
- 📚 完善文档体系
- 🔧 统一版本管理

### 功能特性
- 图谱构建功能（实体抽取、关系提取、知识图谱）
- 环境搭建功能（人设生成、配置生成）
- Twitter 和 Reddit 双平台并行模拟
- 报告生成功能（基于模拟结果的预测报告）
- 智能体对话功能（与模拟世界中的智能体交互）
- 自动驾驶模式（AUTO / MANUAL 模式切换）
- Docker 容器化部署支持

---

## [v1.4.0] - 2026-01-20

### 新增功能
- 本体生成功能：POST /api/graph/ontology/generate
- 任务状态查询：GET /api/graph/task/{task_id}
- 项目信息查询：GET /api/graph/project/{project_id}
- 文档添加功能：POST /api/graph/project/{project_id}/documents/add
- 图谱数据查询：GET /api/graph/data/{graph_id}
- 模拟恢复检查：GET /api/simulation/{id}/resumable

### 代码改进
- 前端 graph.js API 客户端重构
- 新增 requestWithRetry 统一重试机制

---

## [v1.3.0] - 2026-01-20

### 版本亮点
- 🚗 新增自动驾驶模式 (Auto-Pilot Mode)
- ☁️ 支持云端无人值守自动运行
- 🔄 支持断点续传，失败自动重试

### 新增功能
- 自动驾驶模式（AUTO / MANUAL 模式切换）
- 自动准备：读取实体、生成Profile、生成配置
- 自动启动：自动启动模拟运行
- 自动监控：实时监控运行状态，自动处理异常
- 自动报告：模拟完成后自动生成报告
- 暂停/恢复功能

### API 新增接口
- POST /api/simulation/auto-pilot/config
- POST /api/simulation/auto-pilot/start
- POST /api/simulation/auto-pilot/pause
- POST /api/simulation/auto-pilot/resume
- POST /api/simulation/auto-pilot/stop
- GET /api/simulation/auto-pilot/status
- POST /api/simulation/auto-pilot/reset

---

## [v1.2.0] - 2026-01-20

### 版本亮点
- 🎉 正式发布 v1.2.0 稳定版本
- 🚀 完整实现图谱构建功能
- 📊 完善模拟引擎和报告生成模块

### 功能特性
- 图谱构建功能（实体抽取、关系提取、知识图谱）
- 环境搭建功能（人设生成、配置生成）
- Twitter 和 Reddit 双平台并行模拟
- 报告生成功能（基于模拟结果的预测报告）
- 智能体对话功能
- 完整的 API 接口和错误处理
- Docker 容器化部署支持

---

## [v1.0.1] - 2026-01-20

### API 变更
- 添加 POST /api/v1/graph/build 接口
- 添加 GET /api/v1/graph/<graph_id> 接口
- 添加 GET /api/v1/graph/<graph_id>/export 接口

### 代码改进
- 优化图谱存储路径
- 集成 SimulationManager 进行图谱文件管理

---

## [v1.0.0] - 2026-01-20

### 初始版本
- 🎉 正式发布 v1.0 版本
- 图谱构建功能
- 环境搭建功能
- Twitter 和 Reddit 双平台并行模拟
- 报告生成功能
- 智能体对话功能

### 技术栈
- 前后端分离架构（Vue.js + Flask）
- 集成 Zep Cloud 长期记忆
- 集成 OASIS 社交模拟引擎（Apache 2.0）
- 支持 OpenAI SDK 格式的任意 LLM
