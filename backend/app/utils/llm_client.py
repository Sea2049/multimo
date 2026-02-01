"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config_new import get_config

logger = logging.getLogger(__name__)

# 不支持 response_format 参数的模型前缀
MODELS_WITHOUT_JSON_MODE = ["deepseek", "glm"]


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        config = get_config()
        self.api_key = api_key or config.LLM_API_KEY
        self.base_url = base_url or config.LLM_BASE_URL
        self.model = model or config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        # 创建 OpenAI 客户端，不设置全局 timeout，在请求级别设置
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _supports_json_mode(self) -> bool:
        """检查当前模型是否支持 response_format 参数"""
        model_lower = self.model.lower()
        for prefix in MODELS_WITHOUT_JSON_MODE:
            if model_lower.startswith(prefix):
                return False
        return True
    
    def _extract_json_from_response(self, response: str) -> str:
        """从响应中提取 JSON 内容（处理 markdown 代码块等情况）"""
        if not response:
            raise ValueError("LLM 返回空响应")
        
        # 尝试直接解析
        response = response.strip()
        
        # 处理 markdown 代码块: ```json ... ``` 或 ``` ... ```
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        match = re.search(code_block_pattern, response)
        if match:
            json_str = match.group(1).strip()
        else:
            # 尝试找到 JSON 对象的边界 { ... }
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end + 1]
            else:
                json_str = response
        
        # 修复常见的 JSON 格式问题
        json_str = self._fix_json(json_str)
        return json_str
    
    def _fix_json(self, json_str: str) -> str:
        """修复常见的 JSON 格式问题"""
        # 移除尾随逗号（在 ] 或 } 之前的逗号）
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
        
        # 移除 JavaScript 风格的注释
        json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # 处理单引号（某些 LLM 可能用单引号）
        # 注意：这是一个简化处理，可能在某些复杂情况下有问题
        # 只在键名位置替换单引号为双引号
        # json_str = re.sub(r"'([^']*)'(?=\s*:)", r'"\1"', json_str)
        
        return json_str
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            timeout: 超时时间（秒），默认 300 秒
            
        Returns:
            模型响应文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # 只有支持 JSON mode 的模型才添加 response_format 参数
        if response_format and self._supports_json_mode():
            kwargs["response_format"] = response_format
        
        # 设置超时时间，默认 300 秒（5 分钟）
        request_timeout = timeout if timeout is not None else 300
        kwargs["timeout"] = request_timeout
        
        logger.debug(f"调用 LLM: model={self.model}, supports_json_mode={self._supports_json_mode()}")
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 超时时间（秒），默认 300 秒
            
        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            timeout=timeout
        )
        
        # 从响应中提取 JSON（处理 DeepSeek 等模型可能返回的 markdown 格式）
        json_str = self._extract_json_from_response(response)
        return json.loads(json_str)

