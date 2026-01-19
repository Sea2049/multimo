# LLM 客户端模块

from typing import Dict, Any, Optional, List
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from app.utils.retry import retry_with_backoff
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """LLM 客户端封装类，支持 OpenAI SDK 格式的任意 LLM"""
    
    def __init__(self, api_key: str, base_url: str, model_name: str,
                 temperature: float = 0.7, max_tokens: int = 2000,
                 timeout: int = 60):
        """初始化 LLM 客户端
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model_name: 模型名称
            temperature: 温度参数（0-1）
            max_tokens: 最大生成令牌数
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # 创建 OpenAI 客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        
        logger.info(f"LLM 客户端初始化成功: model={model_name}, base_url={base_url}")
    
    @retry_with_backoff(max_retries=3, backoff_factor=2, exceptions=(RateLimitError, APIConnectionError))
    def chat(self, message: str, system_prompt: Optional[str] = None,
              temperature: Optional[float] = None, max_tokens: Optional[int] = None,
              response_format: Optional[Dict[str, str]] = None) -> str:
        """发送聊天消息
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            temperature: 温度参数（覆盖默认值）
            max_tokens: 最大令牌数（覆盖默认值）
            response_format: 响应格式（如 {"type": "json_object"}）
            
        Returns:
            LLM 响应内容
            
        Raises:
            APIError: API 调用失败
        """
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加用户消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 构建请求参数
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens
            }
            
            # 添加响应格式
            if response_format:
                kwargs["response_format"] = response_format
            
            logger.debug(f"发送 LLM 请求: model={self.model_name}, messages={len(messages)}")
            
            # 调用 API
            response = self.client.chat.completions.create(**kwargs)
            
            # 提取响应内容
            content = response.choices[0].message.content
            
            logger.debug(f"收到 LLM 响应: tokens={response.usage.total_tokens}")
            
            return content
            
        except RateLimitError as e:
            logger.error(f"LLM 速率限制: {e}")
            raise
        except APIConnectionError as e:
            logger.error(f"LLM 连接错误: {e}")
            raise
        except APIError as e:
            logger.error(f"LLM API 错误: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, backoff_factor=2, exceptions=(RateLimitError, APIConnectionError))
    def chat_with_history(self, message: str, history: List[Dict[str, str]],
                         system_prompt: Optional[str] = None) -> str:
        """发送带有历史记录的聊天消息
        
        Args:
            message: 用户消息
            history: 对话历史 [{"role": "user|assistant", "content": "..."}]
            system_prompt: 系统提示词
            
        Returns:
            LLM 响应内容
        """
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加历史记录
            messages.extend(history)
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            logger.debug(f"发送 LLM 请求（带历史）: model={self.model_name}, messages={len(messages)}")
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            
            logger.debug(f"收到 LLM 响应: tokens={response.usage.total_tokens}")
            
            return content
            
        except Exception as e:
            logger.error(f"LLM 调用失败（带历史）: {e}")
            raise
    
    def chat_json(self, message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """发送聊天消息并返回 JSON 格式
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词
            
        Returns:
            解析后的 JSON 字典
            
        Raises:
            ValueError: 响应不是有效的 JSON
        """
        try:
            # 添加 JSON 格式要求到系统提示词
            full_system_prompt = system_prompt or ""
            full_system_prompt += "\n\n请以 JSON 格式返回响应。"
            
            # 调用 API
            response = self.chat(
                message=message,
                system_prompt=full_system_prompt,
                response_format={"type": "json_object"}
            )
            
            # 解析 JSON
            import json
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, response={response}")
            raise ValueError(f"响应不是有效的 JSON: {response}")
        except Exception as e:
            logger.error(f"LLM JSON 调用失败: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            向量嵌入列表
        """
        try:
            logger.debug(f"获取文本嵌入: text_length={len(text)}")
            
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(f"收到嵌入向量: dimension={len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"获取嵌入失败: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """估算文本的令牌数
        
        Args:
            text: 输入文本
            
        Returns:
            令牌数
        """
        try:
            import tiktoken
            
            # 尝试获取模型的编码器
            try:
                encoding = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                # 如果模型不在列表中，使用默认编码
                encoding = tiktoken.get_encoding("cl100k_base")
            
            tokens = len(encoding.encode(text))
            
            logger.debug(f"令牌计数: text_length={len(text)}, tokens={tokens}")
            
            return tokens
            
        except Exception as e:
            logger.warning(f"令牌计数失败，使用估算: {e}")
            # 粗略估算：1 令牌 ≈ 4 字符（英文）
            return len(text) // 4
    
    def check_connection(self) -> bool:
        """检查连接是否正常
        
        Returns:
            连接是否正常
        """
        try:
            # 发送一个简单的测试请求
            response = self.chat(
                message="test",
                system_prompt="Respond with 'OK' only.",
                max_tokens=10
            )
            
            is_ok = response.strip().upper() == "OK"
            
            if is_ok:
                logger.info("LLM 连接检查成功")
            else:
                logger.warning(f"LLM 连接检查异常: response={response}")
            
            return is_ok
            
        except Exception as e:
            logger.error(f"LLM 连接检查失败: {e}")
            return False
    
    def set_temperature(self, temperature: float):
        """设置温度参数
        
        Args:
            temperature: 温度参数（0-1）
        """
        if 0 <= temperature <= 1:
            self.temperature = temperature
            logger.info(f"温度参数已更新: {temperature}")
        else:
            logger.warning(f"无效的温度参数: {temperature}，保持原值")
    
    def set_max_tokens(self, max_tokens: int):
        """设置最大令牌数
        
        Args:
            max_tokens: 最大令牌数
        """
        if max_tokens > 0:
            self.max_tokens = max_tokens
            logger.info(f"最大令牌数已更新: {max_tokens}")
        else:
            logger.warning(f"无效的最大令牌数: {max_tokens}，保持原值")
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置
        
        Returns:
            配置字典
        """
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }


def create_llm_client_from_config(config: Dict[str, Any]) -> LLMClient:
    """从配置字典创建 LLM 客户端
    
    Args:
        config: 配置字典，包含 api_key, base_url, model_name 等字段
        
    Returns:
        LLM 客户端实例
    """
    return LLMClient(
        api_key=config.get("api_key"),
        base_url=config.get("base_url"),
        model_name=config.get("model_name"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 2000),
        timeout=config.get("timeout", 60)
    )
