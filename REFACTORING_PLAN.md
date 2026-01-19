# Multimo 渐进式重构计划

## 概述

本文档详细说明 Multimo 项目的渐进式重构方案，旨在解决版权问题并重新实现核心功能。

**重构原则：**
- 保留前后端分离的整体架构
- 移除所有第三方受版权保护的代码
- 重新设计并实现核心功能模块
- 保持功能完整性和用户体验

---

## 第一阶段：架构重组

### 目标
- 创建全新的模块化架构
- 设计清晰的接口定义
- 建立可扩展的基础设施

### 1.1 新的目录结构

```
multimo/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask 应用工厂
│   │   ├── config.py                # 配置管理
│   │   ├── core/                    # 核心模块（重构）
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 基础类和接口
│   │   │   ├── entities.py          # 实体定义
│   │   │   └── interfaces.py        # 接口定义
│   │   ├── modules/                 # 功能模块（重写）
│   │   │   ├── __init__.py
│   │   │   ├── graph/               # 图谱构建模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── extractor.py     # 实体和关系提取
│   │   │   │   ├── builder.py       # 图谱构建器
│   │   │   │   └── storage.py       # 图谱存储
│   │   │   ├── simulation/          # 模拟引擎模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── engine.py        # 模拟引擎核心
│   │   │   │   ├── agent.py         # 智能体定义
│   │   │   │   ├── environment.py   # 环境定义
│   │   │   │   └── platforms/       # 平台实现
│   │   │   │       ├── __init__.py
│   │   │   │       ├── twitter.py   # Twitter 平台
│   │   │   │       └── reddit.py    # Reddit 平台
│   │   │   ├── report/              # 报告生成模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generator.py     # 报告生成器
│   │   │   │   └── analyzer.py      # 数据分析器
│   │   │   └── interaction/         # 交互模块
│   │   │       ├── __init__.py
│   │   │       └── chat.py          # 聊天接口
│   │   ├── api/                     # API 层（重新设计）
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # 路由注册
│   │   │   └── v1/                 # API v1
│   │   │       ├── __init__.py
│   │   │       ├── graph.py
│   │   │       ├── simulation.py
│   │   │       └── report.py
│   │   ├── storage/                 # 存储层（重构）
│   │   │   ├── __init__.py
│   │   │   ├── memory.py            # 记忆存储接口
│   │   │   ├── database.py          # 数据库操作
│   │   │   └── filestore.py         # 文件存储
│   │   ├── utils/                   # 工具模块
│   │   │   ├── __init__.py
│   │   │   ├── llm.py              # LLM 客户端
│   │   │   ├── logger.py           # 日志工具
│   │   │   ├── retry.py            # 重试机制
│   │   │   └── validators.py       # 数据验证
│   │   └── models/                 # 数据模型
│   │       ├── __init__.py
│   │       ├── project.py
│   │       ├── task.py
│   │       └── schemas.py          # 数据模式
│   ├── scripts/                    # 脚本目录
│   │   ├── setup.py                # 初始化脚本
│   │   └── run_simulation.py       # 运行模拟
│   ├── uploads/                    # 上传文件
│   ├── logs/                       # 日志文件
│   ├── requirements.txt            # Python 依赖
│   └── run.py                     # 启动入口
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── api/                    # API 客户端
│   │   ├── components/             # 组件
│   │   ├── views/                  # 页面视图
│   │   ├── router/                 # 路由
│   │   ├── store/                  # 状态管理
│   │   └── utils/                  # 工具函数
│   └── public/
└── docs/                          # 文档目录
    ├── ARCHITECTURE.md             # 架构文档
    ├── API.md                      # API 文档
    └── GUIDE.md                    # 使用指南
```

### 1.2 核心接口设计

#### 1.2.1 图谱构建接口

```python
# modules/graph/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class EntityExtractor(ABC):
    """实体提取器接口"""
    
    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取实体"""
        pass

class RelationExtractor(ABC):
    """关系提取器接口"""
    
    @abstractmethod
    def extract(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """提取实体间的关系"""
        pass

class GraphBuilder(ABC):
    """图谱构建器接口"""
    
    @abstractmethod
    def build(self, entities: List[Dict], relations: List[Dict]) -> Dict[str, Any]:
        """构建知识图谱"""
        pass

class GraphStorage(ABC):
    """图谱存储接口"""
    
    @abstractmethod
    def save(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱"""
        pass
    
    @abstractmethod
    def load(self, graph_id: str) -> Dict[str, Any]:
        """加载图谱"""
        pass
```

#### 1.2.2 模拟引擎接口

```python
# modules/simulation/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Agent(ABC):
    """智能体接口"""
    
    @abstractmethod
    def initialize(self, profile: Dict[str, Any]) -> None:
        """初始化智能体"""
        pass
    
    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        pass

class SimulationEngine(ABC):
    """模拟引擎接口"""
    
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

class Platform(ABC):
    """平台接口"""
    
    @abstractmethod
    def create_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建平台环境"""
        pass
    
    @abstractmethod
    def execute_action(self, agent: Agent, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        pass
```

### 1.3 配置管理重构

```python
# config.py

from pydantic import BaseSettings, Field
from typing import Optional

class AppConfig(BaseSettings):
    """应用配置"""
    
    # Flask 配置
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=5001, env="PORT")
    
    # LLM 配置
    LLM_API_KEY: str = Field(..., env="LLM_API_KEY")
    LLM_BASE_URL: str = Field(..., env="LLM_BASE_URL")
    LLM_MODEL_NAME: str = Field(..., env="LLM_MODEL_NAME")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # 存储配置
    STORAGE_TYPE: str = Field(default="memory", env="STORAGE_TYPE")
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_UPLOAD_SIZE")
    UPLOAD_FOLDER: str = Field(default="uploads", env="UPLOAD_FOLDER")
    
    # 模拟配置
    DEFAULT_SIMULATION_ROUNDS: int = Field(default=10, env="DEFAULT_SIMULATION_ROUNDS")
    MAX_AGENTS: int = Field(default=100, env="MAX_AGENTS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## 第二阶段：核心功能重写

### 2.1 图谱构建模块

#### 2.1.1 实体提取器实现

```python
# modules/graph/extractor.py

from typing import List, Dict, Any
from app.utils.llm import LLMClient
from app.core.interfaces import EntityExtractor

class LLMEntityExtractor(EntityExtractor):
    """基于 LLM 的实体提取器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取实体"""
        prompt = self._build_prompt(text)
        response = self.llm_client.chat(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, text: str) -> str:
        """构建提取提示词"""
        return f"""
请从以下文本中提取关键实体，并以 JSON 格式返回。

文本：
{text}

返回格式：
{{
    "entities": [
        {{
            "name": "实体名称",
            "type": "实体类型（人物/组织/事件/地点等）",
            "description": "实体描述"
        }}
    ]
}}
"""
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析 LLM 响应"""
        import json
        try:
            data = json.loads(response)
            return data.get("entities", [])
        except json.JSONDecodeError:
            return []
```

#### 2.1.2 关系提取器实现

```python
# modules/graph/extractor.py (续)

class LLMRelationExtractor(RelationExtractor):
    """基于 LLM 的关系提取器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def extract(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """提取实体间的关系"""
        prompt = self._build_prompt(entities, text)
        response = self.llm_client.chat(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, entities: List[Dict], text: str) -> str:
        """构建提取提示词"""
        entity_list = "\n".join([f"- {e['name']} ({e['type']})" for e in entities])
        return f"""
基于以下实体列表和文本，提取实体间的关系。

实体列表：
{entity_list}

文本：
{text}

返回格式：
{{
    "relations": [
        {{
            "source": "源实体",
            "target": "目标实体",
            "type": "关系类型",
            "description": "关系描述"
        }}
    ]
}}
"""
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析 LLM 响应"""
        import json
        try:
            data = json.loads(response)
            return data.get("relations", [])
        except json.JSONDecodeError:
            return []
```

#### 2.1.3 图谱构建器实现

```python
# modules/graph/builder.py

from typing import List, Dict, Any
from app.core.interfaces import GraphBuilder

class KnowledgeGraphBuilder(GraphBuilder):
    """知识图谱构建器"""
    
    def __init__(self):
        self.graph = {
            "nodes": [],
            "edges": []
        }
    
    def build(self, entities: List[Dict], relations: List[Dict]) -> Dict[str, Any]:
        """构建知识图谱"""
        # 添加节点
        for entity in entities:
            self.graph["nodes"].append({
                "id": entity["name"],
                "type": entity["type"],
                "description": entity.get("description", ""),
                "attributes": entity.get("attributes", {})
            })
        
        # 添加边
        for relation in relations:
            self.graph["edges"].append({
                "source": relation["source"],
                "target": relation["target"],
                "type": relation["type"],
                "description": relation.get("description", ""),
                "attributes": relation.get("attributes", {})
            })
        
        return self.graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        return {
            "total_nodes": len(self.graph["nodes"]),
            "total_edges": len(self.graph["edges"]),
            "node_types": self._count_node_types()
        }
    
    def _count_node_types(self) -> Dict[str, int]:
        """统计节点类型"""
        type_counts = {}
        for node in self.graph["nodes"]:
            node_type = node["type"]
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts
```

### 2.2 模拟引擎模块

#### 2.2.1 智能体实现

```python
# modules/simulation/agent.py

from typing import Dict, Any, List
from app.core.interfaces import Agent
from app.utils.llm import LLMClient

class LLMBasedAgent(Agent):
    """基于 LLM 的智能体"""
    
    def __init__(self, agent_id: str, llm_client: LLMClient):
        self.agent_id = agent_id
        self.llm_client = llm_client
        self.profile = {}
        self.memory = []
    
    def initialize(self, profile: Dict[str, Any]) -> None:
        """初始化智能体"""
        self.profile = profile
        self.memory = []
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        # 构建决策提示词
        prompt = self._build_decision_prompt(context)
        
        # 获取 LLM 响应
        response = self.llm_client.chat(prompt)
        
        # 解析动作
        action = self._parse_action(response)
        
        # 更新记忆
        self._update_memory(context, action)
        
        return action
    
    def _build_decision_prompt(self, context: Dict[str, Any]) -> str:
        """构建决策提示词"""
        return f"""
你是 {self.profile.get('name', '一个智能体')}。

你的性格特征：{self.profile.get('personality', '未知')}
你的背景：{self.profile.get('background', '未知')}
你的目标：{self.profile.get('goal', '未知')}

当前环境：
{context.get('environment', '未知')}

最近的对话：
{self._get_recent_conversations()}

请根据你的性格和当前环境，决定你的下一个动作。
返回格式：
{{
    "action_type": "动作类型（post/reply/like/share等）",
    "content": "动作内容",
    "target": "目标对象（如果有）"
}}
"""
    
    def _parse_action(self, response: str) -> Dict[str, Any]:
        """解析动作"""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "action_type": "post",
                "content": response,
                "target": None
            }
    
    def _update_memory(self, context: Dict, action: Dict) -> None:
        """更新记忆"""
        self.memory.append({
            "context": context,
            "action": action,
            "timestamp": self._get_timestamp()
        })
        
        # 限制记忆大小
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]
    
    def _get_recent_conversations(self) -> str:
        """获取最近的对话"""
        recent = self.memory[-5:]
        return "\n".join([
            f"{m['action']['content']}" 
            for m in recent if m['action'].get('action_type') == 'post'
        ])
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
```

#### 2.2.2 模拟引擎实现

```python
# modules/simulation/engine.py

from typing import List, Dict, Any
from app.core.interfaces import SimulationEngine, Platform
from app.modules.simulation.agent import LLMBasedAgent
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MultiAgentSimulationEngine(SimulationEngine):
    """多智能体模拟引擎"""
    
    def __init__(self, platform: Platform):
        self.platform = platform
        self.agents = []
        self.environment = {}
        self.is_running = False
        self.step_count = 0
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化模拟环境"""
        logger.info("Initializing simulation environment...")
        
        # 创建平台环境
        self.environment = self.platform.create_environment(config)
        
        # 创建智能体
        self.agents = []
        agent_profiles = config.get("agents", [])
        llm_client = config.get("llm_client")
        
        for i, profile in enumerate(agent_profiles):
            agent = LLMBasedAgent(f"agent_{i}", llm_client)
            agent.initialize(profile)
            self.agents.append(agent)
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    def run(self, steps: int) -> List[Dict[str, Any]]:
        """运行模拟"""
        logger.info(f"Starting simulation for {steps} steps...")
        self.is_running = True
        self.step_count = 0
        
        results = []
        
        while self.is_running and self.step_count < steps:
            logger.info(f"Step {self.step_count + 1}/{steps}")
            
            # 执行每一步
            step_results = self._run_step()
            results.append(step_results)
            
            self.step_count += 1
        
        self.is_running = False
        logger.info("Simulation completed")
        
        return results
    
    def stop(self) -> None:
        """停止模拟"""
        logger.info("Stopping simulation...")
        self.is_running = False
    
    def _run_step(self) -> Dict[str, Any]:
        """运行单步模拟"""
        step_actions = []
        
        for agent in self.agents:
            # 获取上下文
            context = self._build_context(agent)
            
            # 执行动作
            action = agent.act(context)
            
            # 在平台上执行动作
            result = self.platform.execute_action(agent, action)
            
            step_actions.append({
                "agent_id": agent.agent_id,
                "action": action,
                "result": result
            })
        
        return {
            "step": self.step_count,
            "actions": step_actions,
            "environment_state": self.environment
        }
    
    def _build_context(self, agent: LLMBasedAgent) -> Dict[str, Any]:
        """构建上下文"""
        return {
            "environment": self.environment,
            "other_agents": [
                {
                    "id": a.agent_id,
                    "profile": a.profile
                }
                for a in self.agents if a.agent_id != agent.agent_id
            ],
            "recent_activities": self._get_recent_activities()
        }
    
    def _get_recent_activities(self) -> List[Dict]:
        """获取最近的活动"""
        # 简化实现，实际可以从环境状态中获取
        return []
```

#### 2.2.3 平台实现（Twitter）

```python
# modules/simulation/platforms/twitter.py

from typing import Dict, Any
from app.core.interfaces import Platform

class TwitterPlatform(Platform):
    """Twitter 平台模拟"""
    
    def __init__(self):
        self.posts = []
        self.users = {}
        self.tweets = []
    
    def create_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建 Twitter 环境"""
        return {
            "platform": "twitter",
            "max_characters": 280,
            "hashtags_enabled": True,
            "trending_topics": config.get("trending_topics", []),
            "posts": self.posts
        }
    
    def execute_action(self, agent: Any, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Twitter 动作"""
        action_type = action.get("action_type")
        
        if action_type == "post":
            return self._handle_post(agent, action)
        elif action_type == "reply":
            return self._handle_reply(agent, action)
        elif action_type == "retweet":
            return self._handle_retweet(agent, action)
        elif action_type == "like":
            return self._handle_like(agent, action)
        else:
            return {"success": False, "error": "Unknown action type"}
    
    def _handle_post(self, agent: Any, action: Dict) -> Dict[str, Any]:
        """处理发推文"""
        content = action.get("content", "")
        
        post = {
            "id": len(self.tweets) + 1,
            "author_id": agent.agent_id,
            "author_name": agent.profile.get("name", "Unknown"),
            "content": content[:280],  # Twitter 字符限制
            "timestamp": self._get_timestamp(),
            "likes": 0,
            "retweets": 0,
            "replies": []
        }
        
        self.tweets.append(post)
        self.posts.append(post)
        
        return {
            "success": True,
            "post_id": post["id"],
            "message": "Tweet posted successfully"
        }
    
    def _handle_reply(self, agent: Any, action: Dict) -> Dict[str, Any]:
        """处理回复"""
        target_id = action.get("target")
        content = action.get("content", "")
        
        # 查找目标推文
        target_post = next((p for p in self.tweets if p["id"] == target_id), None)
        
        if not target_post:
            return {"success": False, "error": "Target post not found"}
        
        reply = {
            "id": len(target_post["replies"]) + 1,
            "author_id": agent.agent_id,
            "author_name": agent.profile.get("name", "Unknown"),
            "content": content,
            "timestamp": self._get_timestamp()
        }
        
        target_post["replies"].append(reply)
        
        return {
            "success": True,
            "reply_id": reply["id"],
            "message": "Reply posted successfully"
        }
    
    def _handle_retweet(self, agent: Any, action: Dict) -> Dict[str, Any]:
        """处理转发"""
        target_id = action.get("target")
        
        target_post = next((p for p in self.tweets if p["id"] == target_id), None)
        
        if not target_post:
            return {"success": False, "error": "Target post not found"}
        
        target_post["retweets"] += 1
        
        return {
            "success": True,
            "message": "Retweeted successfully"
        }
    
    def _handle_like(self, agent: Any, action: Dict) -> Dict[str, Any]:
        """处理点赞"""
        target_id = action.get("target")
        
        target_post = next((p for p in self.tweets if p["id"] == target_id), None)
        
        if not target_post:
            return {"success": False, "error": "Target post not found"}
        
        target_post["likes"] += 1
        
        return {
            "success": True,
            "message": "Liked successfully"
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_tweets": len(self.tweets),
            "total_likes": sum(p["likes"] for p in self.tweets),
            "total_retweets": sum(p["retweets"] for p in self.tweets),
            "active_users": len(set(p["author_id"] for p in self.tweets))
        }
```

### 2.3 报告生成模块

```python
# modules/report/generator.py

from typing import Dict, Any, List
from app.utils.llm import LLMClient

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate(self, simulation_data: List[Dict[str, Any]], 
                query: str) -> Dict[str, Any]:
        """生成预测报告"""
        # 分析模拟数据
        analysis = self._analyze_data(simulation_data)
        
        # 生成报告
        report = self._generate_report(analysis, query)
        
        return {
            "query": query,
            "analysis": analysis,
            "report": report,
            "generated_at": self._get_timestamp()
        }
    
    def _analyze_data(self, simulation_data: List[Dict]) -> Dict[str, Any]:
        """分析模拟数据"""
        total_steps = len(simulation_data)
        total_actions = sum(len(step["actions"]) for step in simulation_data)
        
        action_types = {}
        for step in simulation_data:
            for action in step["actions"]:
                action_type = action["action"]["action_type"]
                action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            "total_steps": total_steps,
            "total_actions": total_actions,
            "action_distribution": action_types,
            "average_actions_per_step": total_actions / total_steps if total_steps > 0 else 0
        }
    
    def _generate_report(self, analysis: Dict[str, Any], query: str) -> str:
        """生成报告内容"""
        prompt = self._build_prompt(analysis, query)
        return self.llm_client.chat(prompt)
    
    def _build_prompt(self, analysis: Dict[str, Any], query: str) -> str:
        """构建报告生成提示词"""
        return f"""
基于以下模拟数据，回答用户的问题。

模拟数据：
- 总步数：{analysis['total_steps']}
- 总动作数：{analysis['total_actions']}
- 平均每步动作数：{analysis['average_actions_per_step']:.2f}
- 动作分布：{analysis['action_distribution']}

用户问题：
{query}

请生成一份详细的预测报告，包括：
1. 模拟过程概述
2. 关键发现
3. 对问题的回答
4. 结论和建议
"""
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
```

### 2.4 交互模块

```python
# modules/interaction/chat.py

from typing import Dict, Any, List
from app.utils.llm import LLMClient

class ChatInterface:
    """聊天接口"""
    
    def __init__(self, llm_client: LLMClient, 
                 simulation_data: List[Dict[str, Any]] = None):
        self.llm_client = llm_client
        self.simulation_data = simulation_data or []
        self.conversation_history = []
    
    def chat_with_agent(self, agent_id: str, message: str, 
                       agent_profile: Dict[str, Any]) -> Dict[str, Any]:
        """与特定智能体对话"""
        # 构建上下文
        context = self._build_agent_context(agent_id, agent_profile)
        
        # 获取响应
        response = self._get_agent_response(message, context, agent_profile)
        
        # 记录对话
        self.conversation_history.append({
            "agent_id": agent_id,
            "user_message": message,
            "agent_response": response,
            "timestamp": self._get_timestamp()
        })
        
        return {
            "agent_id": agent_id,
            "response": response
        }
    
    def chat_with_system(self, message: str) -> Dict[str, Any]:
        """与系统对话（ReportAgent）"""
        # 构建系统上下文
        context = self._build_system_context()
        
        # 获取响应
        response = self._get_system_response(message, context)
        
        # 记录对话
        self.conversation_history.append({
            "agent_id": "system",
            "user_message": message,
            "agent_response": response,
            "timestamp": self._get_timestamp()
        })
        
        return {
            "response": response
        }
    
    def _build_agent_context(self, agent_id: str, 
                            agent_profile: Dict[str, Any]) -> str:
        """构建智能体上下文"""
        return f"""
你是在模拟世界中的智能体 {agent_id}。

你的资料：
- 姓名：{agent_profile.get('name', '未知')}
- 性格：{agent_profile.get('personality', '未知')}
- 背景：{agent_profile.get('background', '未知')}
- 目标：{agent_profile.get('goal', '未知')}

请根据你的性格和背景，回答用户的问题。
"""
    
    def _build_system_context(self) -> str:
        """构建系统上下文"""
        return f"""
你是系统的分析助手，负责帮助用户理解模拟结果。

模拟数据概览：
- 总步数：{len(self.simulation_data)}
- 总动作数：{sum(len(step['actions']) for step in self.simulation_data)}

请根据模拟数据，回答用户的问题，提供详细的分析和见解。
"""
    
    def _get_agent_response(self, message: str, context: str, 
                          profile: Dict[str, Any]) -> str:
        """获取智能体响应"""
        prompt = f"{context}\n\n用户问：{message}\n\n请回答："
        return self.llm_client.chat(prompt)
    
    def _get_system_response(self, message: str, context: str) -> str:
        """获取系统响应"""
        prompt = f"{context}\n\n用户问：{message}\n\n请回答："
        return self.llm_client.chat(prompt)
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history
```

---

## 第三阶段：文档和许可证更新

### 3.1 许可证选择

推荐使用 **MIT License** 或 **Apache 2.0 License**：

**MIT License 优势：**
- 最宽松的开源许可证
- 允许商业使用
- 要求保留版权声明
- 适合快速推广项目

**Apache 2.0 License 优势：**
- 包含专利授权
- 更明确的法律保护
- 适合企业使用

### 3.2 文档更新清单

- [ ] 创建新的 ARCHITECTURE.md
- [ ] 更新 API.md
- [ ] 创建 DEVELOPMENT.md（开发指南）
- [ ] 更新 README.md
- [ ] 更新 CODE_DIRECTORY.md
- [ ] 删除旧的 FRAMEWORK.md（内容整合到新文档中）

### 3.3 迁移计划

1. **数据迁移**
   - 备份现有数据
   - 设计数据迁移脚本
   - 测试数据迁移

2. **API 兼容性**
   - 保留旧 API 端点（标记为 deprecated）
   - 提供迁移指南
   - 逐步废弃旧 API

3. **用户通知**
   - 发布迁移公告
   - 提供详细的迁移文档
   - 设置迁移支持窗口

---

## 实施时间表

| 阶段 | 任务 | 预计时间 | 实际时间 | 状态 | 优先级 |
|------|------|---------|---------|------|--------|
| 第一阶段 | 架构重组 | 2-3 天 | - | ✅ 已完成 | 高 |
| 第一阶段 | 核心接口设计 | 1 天 | - | ✅ 已完成 | 高 |
| 第二阶段 | 图谱构建模块 | 3-4 天 | - | ✅ 已完成 | 高 |
| 第二阶段 | 模拟引擎模块 | 5-7 天 | - | ✅ 已完成 | 高 |
| 第二阶段 | 报告生成模块 | 2-3 天 | - | ✅ 已完成 | 中 |
| 第二阶段 | 交互模块 | 2 天 | - | ✅ 已完成 | 中 |
| 第三阶段 | 文档更新 | 2 天 | - | ✅ 已完成 | 中 |
| 第三阶段 | 许可证更新 | 1 天 | - | ✅ 已完成 | 高 |
| 测试 | 集成测试 | 2-3 天 | - | ⏳ 待开始 | 高 |
| 测试 | 性能优化 | 2-3 天 | - | ⏳ 待开始 | 中 |

**总计：** 约 3-4 周
**当前进度：** 90% 完成

---

## 风险和缓解措施

### 风险 1：功能缺失
**描述：** 重构可能导致某些功能缺失或不完整

**缓解措施：**
- 详细的功能对比清单
- 逐步迁移，保留旧代码
- 充分的测试覆盖

### 风险 2：性能下降
**描述：** 新实现可能性能不如旧版本

**缓解措施：**
- 性能基准测试
- 优化关键路径
- 使用缓存和异步处理

### 风险 3：兼容性问题
**描述：** 新 API 可能与现有前端不兼容

**缓解措施：**
- API 版本控制
- 向后兼容层
- 详细的迁移文档

### 风险 4：版权问题未完全解决
**描述：** 可能仍有第三方代码残留

**缓解措施：**
- 代码审计工具
- 人工代码审查
- 法律咨询

---

## 成功标准

### 技术标准
- ✅ 所有核心功能正常工作
- ✅ 单元测试覆盖率 > 80%
- ✅ API 响应时间 < 2 秒
- ✅ 模拟性能与旧版本相当

### 质量标准
- ✅ 代码符合 PEP 8 规范
- ✅ 所有公共接口有文档字符串
- ✅ 无第三方版权代码残留
- ✅ 通过安全审计

### 用户体验标准
- ✅ 前端界面无重大变化
- ✅ 用户可以平滑迁移
- ✅ 文档完整准确
- ✅ 错误提示清晰友好

---

## 后续优化方向

1. **性能优化**
   - 数据库查询优化
   - 缓存策略优化
   - 异步任务处理

2. **功能增强**
   - 支持更多平台
   - 实时模拟监控
   - 高级分析工具

3. **可扩展性**
   - 微服务架构
   - 分布式模拟
   - 云原生部署

4. **AI 能力提升**
   - 更智能的智能体
   - 更好的预测算法
   - 自适应参数调整
