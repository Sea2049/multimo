# Multimo 框架架构文档

## 1. 框架概述

mulitmo 是一款基于多智能体技术的新一代 AI 预测引擎，采用前后端分离的分布式架构。框架设计遵循模块化、可扩展、高可用的原则，通过构建高保真的平行数字世界来实现对未来事件的预测。

### 1.1 设计理念

**核心理念：**
- **群体智能镜像**：通过捕捉个体互动引发的群体涌现，突破传统预测的局限
- **平行数字世界**：映射现实，在零风险环境中试错和预演
- **多平台并行**：支持 Twitter、Reddit 等多平台同时模拟
- **深度交互**：与模拟世界中的智能体和 ReportAgent 进行对话

**应用场景：**
- **宏观决策**：政策与公关在零风险中试错
- **微观创意**：推演小说结局、探索脑洞、趣味仿真
- **预测分析**：基于现实种子材料推演未来走向

### 1.2 技术栈

**后端技术：**
- Python 3.11-3.12（编程语言）
- Flask 3.0+（Web 框架）
- OpenAI SDK（LLM 交互，支持任意兼容 OpenAI SDK 格式的 LLM）
- Zep Cloud 3.13.0（长期记忆服务）
- CAMEL-OASIS 0.2.5（社交模拟引擎，Apache 2.0 开源）
- PyMuPDF（PDF 解析）

**前端技术：**
- Vue.js 3（前端框架）
- Vue Router（路由管理）
- Axios（HTTP 客户端）
- D3.js（图谱可视化）
- Vite（构建工具）

## 2. 框架架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        表现层                                 │
│                   Vue.js Frontend                           │
│  (Step1-Step5 组件, API 客户端, 路由, 状态管理, D3.js)        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────┴──────────────────────────────────────┐
│                         应用层                                │
│                    Flask Backend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ API 路由层   │  │ 业务逻辑层   │  │ 数据模型层   │       │
│  │ (api/)      │  │ (services/) │  │ (models/)   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 核心模块层   │  │ 工具函数层   │  │ 存储层       │       │
│  │ (modules/)  │  │ (utils/)    │  │ (storage/)  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                        外部服务层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ LLM 服务     │  │ Zep Cloud  │  │ OASIS 框架   │       │
│  │ (OpenAI     │  │ (记忆存储)   │  │ (模拟引擎)   │       │
│  │  兼容)       │  │             │  │             │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块架构

```
Multimo 框架
│
├── 图谱构建模块 (modules/graph/)
│   ├── 实体提取器 (extractor.py)
│   ├── 关系提取器 (extractor.py)
│   ├── 图谱构建器 (builder.py)
│   └── 图谱存储 (storage.py)
│
├── 模拟引擎模块 (modules/simulation/)
│   ├── 智能体 (agent.py)
│   ├── 模拟引擎 (engine.py)
│   ├── Twitter 平台 (platforms/twitter.py)
│   └── Reddit 平台 (platforms/reddit.py)
│
├── 报告生成模块 (modules/report/)
│   ├── 数据分析器 (analyzer.py)
│   └── 报告生成器 (generator.py)
│
├── 交互模块 (modules/interaction/)
│   └── 聊天接口 (chat.py)
│
├── 核心接口 (core/)
│   ├── 基础类 (base.py)
│   ├── 实体定义 (entities.py)
│   └── 接口定义 (interfaces.py)
│
└── 存储模块 (storage/)
    ├── 记忆存储 (memory.py)
    └── 数据库 (database.py)
```

## 3. 核心接口定义

### 3.1 图谱构建接口

**EntityExtractor（实体提取器）**
```python
class EntityExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取实体"""
        pass
```

**RelationExtractor（关系提取器）**
```python
class RelationExtractor(ABC):
    @abstractmethod
    def extract(self, entities: List[Dict[str, Any]], 
                text: str) -> List[Dict[str, Any]]:
        """提取实体间的关系"""
        pass
```

**GraphBuilder（图谱构建器）**
```python
class GraphBuilder(ABC):
    @abstractmethod
    def build(self, entities: List[Dict], 
              relations: List[Dict]) -> Dict[str, Any]:
        """构建知识图谱"""
        pass
```

**GraphStorage（图谱存储）**
```python
class GraphStorage(ABC):
    @abstractmethod
    def save(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱"""
        pass
    
    @abstractmethod
    def load(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """加载图谱"""
        pass
```

### 3.2 模拟引擎接口

**Agent（智能体）**
```python
class Agent(ABC):
    @abstractmethod
    def initialize(self, profile: Dict[str, Any]) -> None:
        """初始化智能体"""
        pass
    
    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """获取智能体状态"""
        pass
```

**SimulationEngine（模拟引擎）**
```python
class SimulationEngine(ABC):
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化模拟环境"""
        pass
    
    @abstractmethod
    def run(self, steps: int) -> List[Dict[str, Any]]:
        """运行模拟"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止模拟"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取模拟状态"""
        pass
```

**Platform（平台接口）**
```python
class Platform(ABC):
    @abstractmethod
    def create_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建平台环境"""
        pass
    
    @abstractmethod
    def execute_action(self, agent: Agent, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """获取平台统计信息"""
        pass
```

### 3.4 自动驾驶模式接口

**AutoPilotManager（自动驾驶管理器）**
```python
class AutoPilotManager:
    @abstractmethod
    def set_mode(self, simulation_id: str, mode: AutoPilotMode) -> AutoPilotState:
        """设置自动驾驶模式（AUTO / MANUAL）"""
        pass
    
    @abstractmethod
    def start_auto_pilot(self, simulation_id: str, force: bool = False) -> AutoPilotState:
        """启动自动驾驶，自动执行准备 -> 启动 -> 监控 -> 生成报告"""
        pass
    
    @abstractmethod
    def pause_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """暂停自动驾驶"""
        pass
    
    @abstractmethod
    def resume_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """恢复自动驾驶"""
        pass
    
    @abstractmethod
    def stop_auto_pilot(self, simulation_id: str) -> AutoPilotState:
        """停止自动驾驶"""
        pass
    
    @abstractmethod
    def get_status(self, simulation_id: str) -> AutoPilotState:
        """获取自动驾驶状态"""
        pass
```

**AutoPilotMode（自动驾驶模式）**
```python
class AutoPilotMode(str, Enum):
    MANUAL = "manual"  # 手动模式：每步需要人工确认
    AUTO = "auto"      # 自动驾驶模式：全自动执行
```

**AutoPilotStep（自动驾驶步骤）**
```python
class AutoPilotStep(str, Enum):
    IDLE = "idle"                    # 空闲
    PREPARING = "preparing"          # 准备阶段
    STARTING = "starting"            # 启动阶段
    MONITORING = "monitoring"        # 监控阶段
    GENERATING_REPORT = "generating_report"  # 生成报告阶段
    COMPLETED = "completed"          # 完成
    FAILED = "failed"                # 失败
    PAUSED = "paused"                # 暂停
```

### 3.3 报告生成接口

**ReportGenerator（报告生成器）**
```python
class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, simulation_data: List[Dict[str, Any]], 
                query: str) -> Dict[str, Any]:
        """生成报告"""
        pass
```

## 4. 工作流程

### 4.1 完整工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                      用户交互流程                              │
└─────────────────────────────────────────────────────────────┘

步骤 1: 图谱构建
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 上传种子材料  │ -> │ 文本提取处理  │ -> │ 实体关系抽取  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                                      ┌─────────────┐
                                      │ 构建知识图谱  │
                                      └─────────────┘
                                              ↓
                                      ┌─────────────┐
                                      │ 存储到 Zep   │
                                      └─────────────┘

步骤 2: 环境搭建
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 实体关系读取  │ -> │ 人设生成器    │ -> │ 模拟配置生成  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                                      ┌─────────────┐
                                      │ 平台配置注入  │
                                      └─────────────┘

步骤 3: 开始模拟
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 初始化引擎    │ -> │ 创建智能体    │ -> │ 并行模拟执行  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                                      ┌─────────────┐
                                      │ 更新时序记忆  │
                                      └─────────────┘

步骤 4: 报告生成
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 收集模拟数据  │ -> │ 数据分析处理  │ -> │ 生成预测报告  │
└─────────────┘    └─────────────┘    └─────────────┘

步骤 5: 深度互动
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 选择智能体    │ -> │ 发送消息      │ -> │ 获取响应      │
└─────────────┘    └─────────────┘    └─────────────┘

### 4.3 自动驾驶模式流程

```
┌─────────────────────────────────────────────────────────────┐
│                  自动驾驶模式工作流程                          │
└─────────────────────────────────────────────────────────────┘

模式配置
┌─────────────┐
│ 设置 AUTO 模式 │ -> 启用自动驾驶
└─────────────┘
        ↓
自动执行流程
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. 自动准备   │ -> │ 2. 自动启动  │ -> │ 3. 监控运行  │ -> │ 4. 自动报告  │
│ 读取实体      │    │ 双平台并行   │    │ 实时监控进度  │    │ 生成预测报告  │
│ 生成Profile  │    │ 启动模拟    │    │ 自动重启失败  │    │             │
│ 生成配置      │    │             │    │ 超时处理     │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
        ↓                        ↓              ↓               ↓
   [如已准备跳过]          [如已运行跳过]   [每30秒检查]    [完成后通知]

控制操作
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 暂停自动驾驶   │ -> │ 恢复自动驾驶  │ -> │ 停止自动驾驶  │
└─────────────┘    └─────────────┘    └─────────────┘
     (随时)             (恢复继续)         (完全停止)

状态查询
┌─────────────┐    ┌─────────────┐
│ 查询当前状态   │ -> │ 查询进度详情  │
└─────────────┘    └─────────────┘
    (轮询)            (含轮数、动作数)

### 4.2 数据流转

**图谱构建流程：**
```
种子材料 (PDF/MD/TXT)
    ↓
TextProcessor (文本处理)
    ↓
LLMEntityExtractor (实体抽取)
    ↓
LLMRelationExtractor (关系抽取)
    ↓
KnowledgeGraphBuilder (图谱构建)
    ↓
ZepGraphMemoryUpdater (存储到 Zep)
```

**模拟执行流程：**
```
模拟配置
    ↓
SimulationManager (模拟管理)
    ↓
OASISProfileGenerator (人设生成)
    ↓
SimulationRunner (模拟运行器)
    ↓
OASIS Framework (OASIS 框架)
    ↓
Twitter/Reddit Platform (平台模拟)
    ↓
模拟结果存储
```

**报告生成流程：**
```
模拟数据
    ↓
DataAnalyzer (数据分析)
    ↓
ReportAgent (报告智能体)
    ↓
LLM 交互生成报告
    ↓
ReportGenerator (报告格式化)
    ↓
导出 (JSON/Markdown)
```

## 5. 配置管理

### 5.1 配置文件结构

配置统一通过环境变量管理，从项目根目录的 `.env` 文件加载：

```env
# Flask 配置
SECRET_KEY=your_secret_key
FLASK_DEBUG=True

# LLM API 配置（支持 OpenAI SDK 格式的任意 LLM）
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

### 5.2 配置类设计

**Config 类** (`backend/app/config.py`)
- 统一管理所有配置项
- 从环境变量加载配置
- 提供配置验证功能
- 支持配置覆盖

**get_flask_config() 方法**
- 将配置转换为 Flask 配置格式
- 包含 Flask 特定的配置项
- JSON 配置（禁用 ASCII 转义，支持中文）

## 6. API 设计

### 6.1 API 路由结构

```
/api/v1/
├── health/           # 健康检查
├── graph/            # 图谱相关
│   ├── upload        # 上传种子材料
│   ├── extract       # 提取实体和关系
│   ├── build         # 构建知识图谱
│   ├── <id>          # 获取指定图谱
│   ├── <id>/export   # 导出指定图谱
│   ├── entities      # 获取实体列表
│   └── relationships # 获取关系列表
├── simulation/       # 模拟相关
│   ├── config        # 生成模拟配置
│   ├── start         # 启动模拟
│   ├── stop          # 停止模拟
│   ├── status        # 获取模拟状态
│   ├── logs          # 获取模拟日志
│   ├── chat          # 与智能体对话
│   ├── history       # 获取历史模拟
│   └── auto-pilot/   # 自动驾驶模式
│       ├── config    # 配置自动驾驶模式（AUTO/MANUAL）
│       ├── start     # 启动自动驾驶
│       ├── pause     # 暂停自动驾驶
│       ├── resume    # 恢复自动驾驶
│       ├── stop      # 停止自动驾驶
│       ├── status    # 获取自动驾驶状态
│       └── reset     # 重置自动驾驶状态
├── report/           # 报告相关
│   ├── generate      # 生成报告
│   └── <id>          # 获取报告
└── interaction/      # 交互相关
    └── chat          # 与 ReportAgent 对话
```

### 6.2 响应格式

**成功响应：**
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

## 7. 存储架构

### 7.1 存储层次

```
存储层
├── Zep Cloud (长期记忆)
│   ├── 实体数据
│   ├── 关系数据
│   └── 时序记忆
├── 本地文件系统
│   ├── 项目文件 (uploads/projects/)
│   ├── 模拟数据 (uploads/simulations/)
│   └── 日志文件 (logs/)
└── SQLite 数据库
    ├── 项目数据
    ├── 任务数据
    └── 配置数据
```

### 7.2 存储策略

**Zep Cloud：**
- 存储知识图谱实体和关系
- 存储智能体长期记忆
- 支持时序记忆更新
- 提供语义搜索能力

**本地文件系统：**
- 项目上传文件存储
- 模拟运行数据存储
- 报告文件存储
- 日志文件存储

## 8. 安全设计

### 8.1 安全措施

**API 密钥管理：**
- 使用环境变量存储敏感信息
- .env 文件不提交到版本控制
- 生产环境使用密钥管理服务

**文件上传安全：**
- 限制文件类型（PDF、MD、TXT）
- 限制文件大小（50MB）
- 验证文件内容
- 隔离上传目录

**输入验证：**
- API 参数验证（Pydantic）
- SQL 注入防护
- XSS 防护

### 8.2 CORS 配置

**开发环境：**
- 允许所有来源（CORS 全开）

**生产环境：**
- 限制具体域名
- 配置允许的 HTTP 方法
- 配置允许的请求头

## 9. 性能优化

### 9.1 优化策略

**异步处理：**
- 模拟任务异步执行
- 报告生成异步处理
- 使用多进程并行模拟

**缓存机制：**
- LLM 响应缓存
- API 响应缓存
- 静态资源缓存

**并发控制：**
- Twitter 和 Reddit 双平台并行模拟
- 智能体并发执行
- 连接池管理

### 9.2 性能指标

| 指标 | 目标值 | 当前状态 |
|------|-------|---------|
| API 响应时间 | < 2 秒 | ✅ 达标 |
| 模拟启动时间 | < 5 秒 | ✅ 达标 |
| 报告生成时间 | < 30 秒 | ✅ 达标 |
| 并发模拟数 | 10+ | ✅ 达标 |

## 10. 可扩展性

### 10.1 水平扩展

- 后端服务可部署多个实例
- 使用负载均衡分发请求
- 模拟任务可分布式执行
- 支持容器化部署（Docker）

### 10.2 垂直扩展

**添加新的模拟平台：**
1. 实现 Platform 接口
2. 定义平台特定动作
3. 创建平台配置文件
4. 注册到模拟引擎

**集成新的 LLM 服务：**
1. 使用 OpenAI SDK 格式
2. 配置 LLM_BASE_URL 和 API_KEY
3. 选择合适的模型名称

**添加新的报告模板：**
1. 扩展 ReportGenerator
2. 定义报告结构
3. 配置生成逻辑

## 11. 版本历史

### v2.70 (2026-02-02)

**版本固化：**
- 🎉 正式发布 v2.70 版本
- 🚀 生产部署优化与稳定性增强
- 🎨 UI 体验优化
- ⚡ 性能大幅提升

**部署改进：**
- ✅ 新增磁盘清理脚本 (`deploy/scripts/disk-cleanup.sh`)
- ✅ Docker 健康检查端点兼容性 (`/api/health`)
- ✅ PyTorch CPU 版本优化，镜像体积减少 10GB+
- ✅ Docker 数据路径统一，简化卷挂载
- ✅ 数据库迁移到 uploads 目录
- ✅ Nginx client_max_body_size 增加到 100M
- ✅ 移除前端 nginx 的后端代理配置
- ✅ 修复 init_auth 的 app context 问题

**UI 改进：**
- 🎨 InteractionView 新增导出按钮
- 🎨 报告导出响应式头部按钮优化
- 🐛 移除重复的 addLog 声明

**性能优化：**
- ⚡ 报告生成速度优化（并行化处理）
- ⚡ 报告生成缓存机制
- ⚡ ReACT 格式工具调用解析修复

**API 改进：**
- 🔧 报告导出使用相对 API 路径
- 🔧 生产环境使用相对 API 路径

**文档更新：**
- 📚 更新 FRAMEWORK.md 框架架构文档
- 📚 更新 CODE_DIRECTORY.md 代码目录文档
- 📚 更新 README.md 项目说明文档
- 📚 新增 CHANGELOG.md 变更日志文件

### v1.61 (2026-02-01)

**版本固化：**
- 🎉 正式发布 v1.61 版本
- 🔄 报告生成断点续传功能
- 📄 扫描版 PDF OCR 识别支持
- 📥 报告下载功能增强
- 🔧 LLM 客户端优化

**新增功能：**
- ✅ 报告任务工作器 (`report_task_worker.py`)：
  - 使用独立线程运行报告生成，与 Flask 主进程隔离
  - 任务状态持久化到数据库
  - 支持从检查点恢复（断点续传）
  - 服务重启后自动恢复中断的任务
- ✅ 扫描版 PDF OCR 识别：
  - 自动检测 PDF 是否为扫描版（无文字或文字过少）
  - 使用 pytesseract 进行 OCR 识别
  - 支持中英文混合文档 (`chi_sim+eng`)
- ✅ 报告下载功能改进：
  - 通过 simulation_id 自动查找对应的 report_id
  - 支持多章节报告自动合并
  - 优先返回完整报告，否则合并各章节

**后端改进：**
- 🔧 新增 `services/report_task_worker.py`：
  - `ReportCheckpoint` 类：报告生成检查点数据模型
  - `ReportTaskWorker` 类：报告任务工作器
  - `get_report_task_worker()` 全局单例
- 🔧 `report_agent.py` 增强：
  - 新增 `generate_report_with_checkpoint()` 方法
  - 支持进度回调和检查点保存
- 🔧 `file_parser.py` 增强：
  - `OCR_ENABLED` 配置开关
  - `_extract_from_pdf_with_ocr()` OCR 提取方法
  - `_is_scanned_pdf()` 扫描版检测
- 🔧 `llm_client.py` 优化：
  - 增强错误处理和重试机制
  - 优化流式响应处理
- 🔧 `api/v1/report.py` 改进：
  - 新增 `_get_report_id_for_simulation()` 辅助函数
  - 改进 `/report/<simulation_id>/download` 端点

**依赖更新：**
- 新增 `pytesseract` 依赖（OCR 支持）
- 新增 `Pillow` 依赖（图像处理）

**技术改进：**
- 报告生成任务与 Flask 主进程解耦
- 支持长时间运行任务的断点恢复
- 扫描版 PDF 自动识别和处理
- 多格式报告下载支持

### v1.60 (2026-01-30)

**版本固化：**
- 🎉 正式发布 v1.60 版本
- 🔐 P0+P1 安全和稳定性改进
- 🏗️ API 层模块化重构
- 🎨 前端组件库优化
- 📚 完善文档体系

**安全改进：**
- ✅ 修复 traceback 泄露问题，生产环境不再暴露堆栈信息
- ✅ SQL 注入防护：新增全面的输入验证和清理机制
- ✅ 线程安全：修复多线程环境下的竞态条件
- ✅ 定时器清理：组件卸载时自动清理所有定时器，避免内存泄漏
- ✅ API 超时配置：支持配置请求超时，防止长时间挂起

**后端架构改进：**
- 🔧 新增 API 装饰器模块 (`api/decorators.py`)
  - 统一的请求验证装饰器
  - SQL 注入检测装饰器
  - 参数清理和验证装饰器
- 🔧 新增 API 响应构建模块 (`api/response.py`)
  - 统一的成功/错误响应格式
  - 分页响应支持
  - 流式响应支持
- 🔧 模拟 API 模块化重构 (`api/simulation/`)
  - `autopilot.py` - 自动驾驶 API
  - `control.py` - 模拟控制 API
  - `data.py` - 数据 API
  - `entities.py` - 实体 API
  - `env.py` - 环境 API
  - `interview.py` - 采访 API
  - `prepare.py` - 准备 API
- 🔧 报告服务模块化 (`services/report/`)
  - `logger.py` - 报告日志服务
  - `models.py` - 报告数据模型

**前端架构改进：**
- 🎨 新增通用组件库 (`components/common/`)
  - `LoadingSpinner.vue` - 加载动画组件
  - `Modal.vue` - 模态框组件
  - `StatusBadge.vue` - 状态徽章组件
  - `StepCard.vue` - 步骤卡片组件
- 🔧 新增 Composables
  - `usePolling.js` - 统一的轮询逻辑，自动清理
  - `useBackoffPolling` - 带退避策略的轮询
  - `usePollingManager` - 多轮询任务管理
- 🔧 新增工具函数 (`utils/`)
  - `formatters.js` - 数据格式化工具
  - `markdown.js` - Markdown 处理工具
- 🐛 修复多个前端组件和视图的问题

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

### v1.52 (2026-01-21)

**项目重命名：**
- 🔄 全局替换：将所有 `mirofish` 字段替换为 `multimo`
- 📝 更新范围：
  - Logger 名称：`get_logger('multimo.xxx')`（2处）
  - 导出文件名：`multimo_export_{simulation_id}.zip`（2处）
  - Docker 镜像：`multimo:latest`（2处）
  - 项目名称：`multimo-backend`（1处）
  - API 文档示例：`multimo_xxxx`（6处）
  - 测试数据：`multimo_test_001`（9处）
- ✅ 验证：所有 24 处替换已完成，无遗漏
- ✅ 测试文件已更新，确保测试用例正常运行

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

### v1.0.1 (2026-01-20)

**功能更新：**
- 图谱获取功能：添加 GET /api/v1/graph/<graph_id> 接口
- 图谱导出功能：添加 GET /api/v1/graph/<graph_id>/export 接口
- 图谱构建功能：添加 POST /api/v1/graph/build 接口
- 集成 SimulationManager 进行图谱文件管理和路径解析

**代码改进：**
- 优化图谱存储路径，支持模拟目录和独立图谱目录两种存储方式
- 添加完整的错误处理和日志记录
- 保持与现有 API 的一致性设计

## 12. 参考资料

### 官方文档
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Vue.js 官方文档](https://vuejs.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Zep Cloud 文档](https://docs.getzep.com/)
- [OASIS 框架文档](https://github.com/camel-ai/oasis)

### 相关项目
- [CAMEL-AI](https://github.com/camel-ai/camel) - CAMEL 框架
- [OASIS](https://github.com/camel-ai/oasis) - 社交模拟引擎

### 开源许可
- Multimo: MIT License
- OASIS: Apache 2.0 License
