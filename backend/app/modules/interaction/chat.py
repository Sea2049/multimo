# 交互模块 - 聊天接口

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.utils.llm import LLMClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatInterface:
    """聊天接口类，支持与模拟世界中的智能体或系统进行对话"""
    
    def __init__(self, llm_client: LLMClient, 
                 simulation_data: List[Dict[str, Any]] = None):
        """初始化聊天接口
        
        Args:
            llm_client: LLM 客户端
            simulation_data: 模拟数据（用于系统分析）
        """
        self.llm_client = llm_client
        self.simulation_data = simulation_data or []
        self.conversation_history: List[Dict[str, Any]] = []
        
        logger.info("聊天接口初始化完成")
    
    def chat_with_agent(self, agent_id: str, message: str, 
                       agent_profile: Dict[str, Any]) -> Dict[str, Any]:
        """与特定智能体对话
        
        Args:
            agent_id: 智能体 ID
            message: 用户消息
            agent_profile: 智能体人设（包含 name, personality, background, goal 等）
            
        Returns:
            对话结果字典，包含 agent_id 和 response
        """
        try:
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
            
            logger.info(f"与智能体 {agent_id} 对话完成")
            
            return {
                "agent_id": agent_id,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"与智能体 {agent_id} 对话失败: {e}")
            return {
                "agent_id": agent_id,
                "response": None,
                "success": False,
                "error": str(e)
            }
    
    def chat_with_system(self, message: str) -> Dict[str, Any]:
        """与系统对话（ReportAgent）
        
        Args:
            message: 用户消息
            
        Returns:
            对话结果字典，包含 response
        """
        try:
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
            
            logger.info("与系统对话完成")
            
            return {
                "response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"与系统对话失败: {e}")
            return {
                "response": None,
                "success": False,
                "error": str(e)
            }
    
    def chat_with_history(self, message: str, agent_id: Optional[str] = None,
                       agent_profile: Optional[Dict[str, Any]] = None,
                       history_length: int = 5) -> Dict[str, Any]:
        """带有历史记录的对话
        
        Args:
            message: 用户消息
            agent_id: 智能体 ID（可选，如果不提供则与系统对话）
            agent_profile: 智能体人设（可选）
            history_length: 历史记录条数
            
        Returns:
            对话结果字典
        """
        try:
            # 获取历史记录
            recent_history = self._get_recent_history(agent_id, history_length)
            
            # 构建提示词
            if agent_id and agent_profile:
                # 与智能体对话
                context = self._build_agent_context(agent_id, agent_profile)
                response = self.llm_client.chat_with_history(
                    message=message,
                    history=recent_history,
                    system_prompt=context
                )
            else:
                # 与系统对话
                context = self._build_system_context()
                response = self.llm_client.chat_with_history(
                    message=message,
                    history=recent_history,
                    system_prompt=context
                )
            
            # 记录对话
            self.conversation_history.append({
                "agent_id": agent_id or "system",
                "user_message": message,
                "agent_response": response,
                "timestamp": self._get_timestamp()
            })
            
            logger.info(f"带有历史记录的对话完成: agent_id={agent_id or 'system'}")
            
            return {
                "agent_id": agent_id or "system",
                "response": response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"带有历史记录的对话失败: {e}")
            return {
                "agent_id": agent_id or "system",
                "response": None,
                "success": False,
                "error": str(e)
            }
    
    def _build_agent_context(self, agent_id: str, 
                            agent_profile: Dict[str, Any]) -> str:
        """构建智能体上下文
        
        Args:
            agent_id: 智能体 ID
            agent_profile: 智能体人设
            
        Returns:
            上下文字符串
        """
        name = agent_profile.get('name', '未知')
        personality = agent_profile.get('personality', '未知')
        background = agent_profile.get('background', '未知')
        goal = agent_profile.get('goal', '未知')
        
        context = f"""
你是在模拟世界中的智能体 {agent_id}。

你的资料：
- 姓名：{name}
- 性格：{personality}
- 背景：{background}
- 目标：{goal}

请根据你的性格和背景，回答用户的问题。保持你的人设一致性，展现出你的性格特点。
"""
        return context
    
    def _build_system_context(self) -> str:
        """构建系统上下文
        
        Returns:
            上下文字符串
        """
        # 计算模拟统计信息
        total_steps = len(self.simulation_data)
        total_actions = sum(len(step.get('actions', [])) for step in self.simulation_data)
        
        # 构建上下文
        context = f"""
你是系统的分析助手（ReportAgent），负责帮助用户理解模拟结果。

模拟数据概览：
- 总步数：{total_steps}
- 总动作数：{total_actions}

你的职责：
1. 分析模拟结果
2. 回答用户关于模拟的问题
3. 提供详细的分析和见解
4. 总结关键发现

请根据模拟数据，回答用户的问题，提供详细、准确的分析。
"""
        return context
    
    def _get_agent_response(self, message: str, context: str, 
                          profile: Dict[str, Any]) -> str:
        """获取智能体响应
        
        Args:
            message: 用户消息
            context: 上下文
            profile: 智能体人设
            
        Returns:
            智能体响应
        """
        prompt = f"{context}\n\n用户问：{message}\n\n请回答："
        return self.llm_client.chat(prompt)
    
    def _get_system_response(self, message: str, context: str) -> str:
        """获取系统响应
        
        Args:
            message: 用户消息
            context: 上下文
            
        Returns:
            系统响应
        """
        prompt = f"{context}\n\n用户问：{message}\n\n请回答："
        return self.llm_client.chat(prompt)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳
        
        Returns:
            ISO 格式的时间戳字符串
        """
        return datetime.now().isoformat()
    
    def _get_recent_history(self, agent_id: Optional[str], 
                          limit: int) -> List[Dict[str, str]]:
        """获取最近的历史记录
        
        Args:
            agent_id: 智能体 ID（可选）
            limit: 返回的记录条数
            
        Returns:
            历史记录列表
        """
        # 过滤指定智能体的历史记录
        if agent_id:
            filtered = [
                h for h in self.conversation_history
                if h.get("agent_id") == agent_id
            ]
        else:
            filtered = self.conversation_history
        
        # 获取最近的记录
        recent = filtered[-limit:] if len(filtered) > limit else filtered
        
        # 转换为 LLM 客户端需要的格式
        history = []
        for record in recent:
            history.append({
                "role": "user",
                "content": record["user_message"]
            })
            history.append({
                "role": "assistant",
                "content": record["agent_response"]
            })
        
        return history
    
    def get_conversation_history(self, agent_id: Optional[str] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """获取对话历史
        
        Args:
            agent_id: 智能体 ID（可选，如果不提供则返回所有历史）
            limit: 返回的最大记录数
            
        Returns:
            对话历史列表
        """
        if agent_id:
            # 过滤指定智能体的历史
            filtered = [
                h for h in self.conversation_history
                if h.get("agent_id") == agent_id
            ]
        else:
            # 返回所有历史
            filtered = self.conversation_history
        
        # 限制数量并按时间倒序排列
        result = sorted(filtered, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        return result
    
    def clear_history(self, agent_id: Optional[str] = None):
        """清除对话历史
        
        Args:
            agent_id: 智能体 ID（可选，如果不提供则清除所有历史）
        """
        if agent_id:
            # 清除指定智能体的历史
            self.conversation_history = [
                h for h in self.conversation_history
                if h.get("agent_id") != agent_id
            ]
            logger.info(f"已清除智能体 {agent_id} 的对话历史")
        else:
            # 清除所有历史
            self.conversation_history = []
            logger.info("已清除所有对话历史")
    
    def set_simulation_data(self, simulation_data: List[Dict[str, Any]]):
        """设置模拟数据
        
        Args:
            simulation_data: 模拟数据列表
        """
        self.simulation_data = simulation_data
        logger.info(f"已更新模拟数据: {len(simulation_data)} 条记录")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取聊天统计信息
        
        Returns:
            统计信息字典
        """
        total_conversations = len(self.conversation_history)
        
        # 按智能体分组统计
        agent_stats = {}
        for record in self.conversation_history:
            agent_id = record.get("agent_id", "unknown")
            if agent_id not in agent_stats:
                agent_stats[agent_id] = 0
            agent_stats[agent_id] += 1
        
        return {
            "total_conversations": total_conversations,
            "agents": agent_stats,
            "simulation_data_size": len(self.simulation_data)
        }


def create_chat_interface(llm_client: LLMClient, 
                        simulation_data: List[Dict[str, Any]] = None) -> ChatInterface:
    """创建聊天接口实例
    
    Args:
        llm_client: LLM 客户端
        simulation_data: 模拟数据（可选）
        
    Returns:
        聊天接口实例
    """
    return ChatInterface(llm_client, simulation_data)
