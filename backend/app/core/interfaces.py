# 核心接口定义

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class EntityExtractor(ABC):
    """实体提取器接口"""
    
    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取实体
        
        Args:
            text: 输入文本
            
        Returns:
            实体列表，每个实体包含 name, type, description 等字段
        """
        pass


class RelationExtractor(ABC):
    """关系提取器接口"""
    
    @abstractmethod
    def extract(self, entities: List[Dict[str, Any]], 
                text: str) -> List[Dict[str, Any]]:
        """提取实体间的关系
        
        Args:
            entities: 实体列表
            text: 输入文本
            
        Returns:
            关系列表，每个关系包含 source, target, type, description 等字段
        """
        pass


class GraphBuilder(ABC):
    """图谱构建器接口"""
    
    @abstractmethod
    def build(self, entities: List[Dict], 
              relations: List[Dict]) -> Dict[str, Any]:
        """构建知识图谱
        
        Args:
            entities: 实体列表
            relations: 关系列表
            
        Returns:
            构建好的图谱数据
        """
        pass


class GraphStorage(ABC):
    """图谱存储接口"""
    
    @abstractmethod
    def save(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱
        
        Args:
            graph_id: 图谱唯一标识
            graph_data: 图谱数据
            
        Returns:
            是否保存成功
        """
        pass
    
    @abstractmethod
    def load(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """加载图谱
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            图谱数据，如果不存在则返回 None
        """
        pass
    
    @abstractmethod
    def delete(self, graph_id: str) -> bool:
        """删除图谱
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def exists(self, graph_id: str) -> bool:
        """检查图谱是否存在
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            图谱是否存在
        """
        pass


class Agent(ABC):
    """智能体接口"""
    
    @abstractmethod
    def initialize(self, profile: Dict[str, Any]) -> None:
        """初始化智能体
        
        Args:
            profile: 智能体人设，包含 name, personality, background, goal 等字段
        """
        pass
    
    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作
        
        Args:
            context: 当前上下文信息
            
        Returns:
            执行的动作，包含 action_type, content, target 等字段
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """获取智能体状态
        
        Returns:
            智能体的当前状态信息
        """
        pass


class SimulationEngine(ABC):
    """模拟引擎接口"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化模拟环境
        
        Args:
            config: 模拟配置，包含 agents, environment 等字段
        """
        pass
    
    @abstractmethod
    def run(self, steps: int) -> List[Dict[str, Any]]:
        """运行模拟
        
        Args:
            steps: 模拟步数
            
        Returns:
            模拟结果列表，每个结果包含单步的详细信息
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止模拟"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """获取模拟状态
        
        Returns:
            模拟状态信息，包含 is_running, step_count 等字段
        """
        pass


class Platform(ABC):
    """平台接口"""
    
    @abstractmethod
    def create_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建平台环境
        
        Args:
            config: 平台配置
            
        Returns:
            环境配置信息
        """
        pass
    
    @abstractmethod
    def execute_action(self, agent: Agent, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作
        
        Args:
            agent: 执行动作的智能体
            action: 动作信息
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """获取平台统计信息
        
        Returns:
            统计信息，包含 posts, users 等数据
        """
        pass


class MemoryStorage(ABC):
    """记忆存储接口"""
    
    @abstractmethod
    def store(self, key: str, value: Any) -> bool:
        """存储数据
        
        Args:
            key: 存储键
            value: 存储值
            
        Returns:
            是否存储成功
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """检索数据
        
        Args:
            key: 存储键
            
        Returns:
            存储的值，如果不存在则返回 None
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除数据
        
        Args:
            key: 存储键
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Any]:
        """搜索数据
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的数据列表
        """
        pass


class ReportGenerator(ABC):
    """报告生成器接口"""
    
    @abstractmethod
    def generate(self, simulation_data: List[Dict[str, Any]], 
                query: str) -> Dict[str, Any]:
        """生成报告
        
        Args:
            simulation_data: 模拟数据
            query: 用户查询
            
        Returns:
            生成的报告
        """
        pass
