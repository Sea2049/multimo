# 图谱构建模块 - 实体和关系提取器
# 提供基于 LLM 的实体提取和关系提取功能

import json
from typing import List, Dict, Any
from app.utils.llm import LLMClient
from app.core.interfaces import EntityExtractor, RelationExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMEntityExtractor(EntityExtractor):
    """基于 LLM 的实体提取器实现类
    
    该类使用大语言模型从文本中提取关键实体信息，
    支持提取实体名称、类型和描述。
    """
    
    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        """初始化实体提取器
        
        Args:
            llm_client: LLM 客户端实例，用于调用大语言模型
            system_prompt: 系统提示词，可自定义提取行为
        """
        self.llm_client = llm_client
        self.system_prompt = system_prompt or self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词
        
        Returns:
            默认的系统提示词字符串
        """
        return """你是一个专业的实体提取助手。
你的任务是从用户提供的文本中提取关键实体信息。
请严格按照指定的 JSON 格式返回结果，确保实体名称准确、类型合理、描述简洁。"""
    
    def extract(self, text: str, entity_types: List[str] = None) -> List[Dict[str, Any]]:
        """从文本中提取实体
        
        该方法接收一段文本，通过 LLM 分析并提取其中的命名实体，
        包括人物、组织、事件、地点等各类实体。
        
        Args:
            text: 输入的文本内容
            entity_types: 可选的实体类型过滤列表，如 ["人物", "组织", "地点"]
            
        Returns:
            实体列表，每个实体包含 name（名称）、type（类型）、description（描述）等字段
        """
        if not text or not text.strip():
            logger.warning("输入文本为空")
            return []
        
        try:
            prompt = self._build_prompt(text, entity_types)
            logger.info(f"开始提取实体，文本长度: {len(text)}")
            
            response = self.llm_client.chat(
                message=prompt,
                system_prompt=self.system_prompt,
                response_format={"type": "json_object"}
            )
            
            entities = self._parse_response(response)
            logger.info(f"成功提取 {len(entities)} 个实体")
            
            return entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return []
    
    def _build_prompt(self, text: str, entity_types: List[str] = None) -> str:
        """构建实体提取提示词
        
        根据输入文本和实体类型过滤构建 LLM 请求提示词
        
        Args:
            text: 输入文本
            entity_types: 实体类型过滤列表
            
        Returns:
            格式化后的提示词字符串
        """
        entity_type_hint = ""
        if entity_types:
            entity_type_hint = f"\n\n只提取以下类型的实体: {', '.join(entity_types)}"
        
        return f"""请从以下文本中提取所有关键实体：

文本内容：
{text}
{entity_type_hint}

请以 JSON 格式返回结果：
{{
    "entities": [
        {{
            "name": "实体名称",
            "type": "实体类型（如：人物、组织、事件、地点、产品、概念等）",
            "description": "实体的简要描述"
        }}
    ]
}}

注意事项：
1. 每个实体必须有 name、type 和 description 字段
2. 如果文本中没有实体，返回空的 entities 数组
3. 实体名称应简洁准确，类型应合理分类
4. 描述应简洁概括实体的主要特征"""
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析 LLM 响应结果
        
        尝试将 LLM 返回的 JSON 字符串解析为实体列表，
        如果解析失败则返回空列表
        
        Args:
            response: LLM 返回的响应字符串
            
        Returns:
            解析后的实体列表
        """
        import json
        
        try:
            data = json.loads(response)
            entities = data.get("entities", [])
            
            for entity in entities:
                if "name" not in entity:
                    entity["name"] = ""
                if "type" not in entity:
                    entity["type"] = "未知"
                if "description" not in entity:
                    entity["description"] = ""
            
            return entities
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, response={response}")
            return []
    
    def extract_with_attributes(self, text: str, attributes: List[str] = None) -> List[Dict[str, Any]]:
        """提取实体及其附加属性
        
        扩展的实体提取方法，可以提取实体的附加属性信息
        
        Args:
            text: 输入文本
            attributes: 需要提取的属性列表，如 ["成立时间", "主要产品", "创始人"]
            
        Returns:
            包含附加属性的实体列表
        """
        if not text or not text.strip():
            return []
        
        try:
            prompt = self._build_prompt_with_attributes(text, attributes)
            
            response = self.llm_client.chat(
                message=prompt,
                system_prompt=self.system_prompt,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            entities = data.get("entities", [])
            
            for entity in entities:
                if "attributes" not in entity:
                    entity["attributes"] = {}
            
            return entities
            
        except Exception as e:
            logger.error(f"带属性的实体提取失败: {e}")
            return []
    
    def _build_prompt_with_attributes(self, text: str, attributes: List[str] = None) -> str:
        """构建带属性的实体提取提示词
        
        Args:
            text: 输入文本
            attributes: 属性列表
            
        Returns:
            格式化后的提示词字符串
        """
        attr_hint = ""
        if attributes:
            attr_hint = f"\n\n需要提取的附加属性: {', '.join(attributes)}"
        
        return f"""请从以下文本中提取实体及其属性信息：

文本内容：
{text}
{attr_hint}

请以 JSON 格式返回结果：
{{
    "entities": [
        {{
            "name": "实体名称",
            "type": "实体类型",
            "description": "实体描述",
            "attributes": {{
                "属性名": "属性值"
            }}
        }}
    ]
}}"""


class LLMRelationExtractor(RelationExtractor):
    """基于 LLM 的关系提取器实现类
    
    该类使用大语言模型从文本中提取实体之间的关系信息，
    支持识别各类实体间的关系类型。
    """
    
    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        """初始化关系提取器
        
        Args:
            llm_client: LLM 客户端实例，用于调用大语言模型
            system_prompt: 系统提示词，可自定义提取行为
        """
        self.llm_client = llm_client
        self.system_prompt = system_prompt or self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词
        
        Returns:
            默认的系统提示词字符串
        """
        return """你是一个专业的关系提取助手。
你的任务是从实体列表和原文中提取实体之间的语义关系。
请严格按照指定的 JSON 格式返回结果，确保关系准确、类型合理。"""
    
    def extract(self, entities: List[Dict[str, Any]], text: str,
                relation_types: List[str] = None) -> List[Dict[str, Any]]:
        """提取实体之间的关系
        
        该方法基于已识别的实体列表和原文，分析并提取实体之间的语义关系，
        包括但不限于人物关系、组织关系、事件关系等。
        
        Args:
            entities: 已提取的实体列表
            text: 输入的原始文本内容
            relation_types: 可选的关系类型过滤列表，如 ["所属", "合作", "竞争"]
            
        Returns:
            关系列表，每个关系包含 source（源实体）、target（目标实体）、
            type（关系类型）、description（描述）等字段
        """
        if not entities or len(entities) == 0:
            logger.warning("输入实体列表为空")
            return []
        
        if not text or not text.strip():
            logger.warning("输入文本为空")
            return []
        
        try:
            prompt = self._build_prompt(entities, text, relation_types)
            logger.info(f"开始提取关系，实体数量: {len(entities)}")
            
            response = self.llm_client.chat(
                message=prompt,
                system_prompt=self.system_prompt,
                response_format={"type": "json_object"}
            )
            
            relations = self._parse_response(response)
            logger.info(f"成功提取 {len(relations)} 个关系")
            
            return relations
            
        except Exception as e:
            logger.error(f"关系提取失败: {e}")
            return []
    
    def _build_prompt(self, entities: List[Dict], text: str,
                     relation_types: List[str] = None) -> str:
        """构建关系提取提示词
        
        Args:
            entities: 实体列表
            text: 输入文本
            relation_types: 关系类型过滤列表
            
        Returns:
            格式化后的提示词字符串
        """
        entity_list = "\n".join([
            f"- {e.get('name', '')} ({e.get('type', '未知')}): {e.get('description', '')}"
            for e in entities
        ])
        
        relation_type_hint = ""
        if relation_types:
            relation_type_hint = f"\n\n只提取以下类型的关系: {', '.join(relation_types)}"
        
        return f"""基于以下实体列表和原文，提取实体之间的语义关系：

实体列表：
{entity_list}

原文内容：
{text}
{relation_type_hint}

请以 JSON 格式返回结果：
{{
    "relations": [
        {{
            "source": "源实体名称（关系的发起方）",
            "target": "目标实体名称（关系的接收方）",
            "type": "关系类型（如：所属、合作、竞争、亲属、朋友、敌对等）",
            "description": "关系的具体描述"
        }}
    ]
}}

注意事项：
1. 每个关系必须有 source、target、type 和 description 字段
2. 如果两个实体之间没有关系，不要提取
3. 关系类型应简洁明确，如"创立"、"投资"、"合作"等
4. 描述应说明关系的具体内容和含义"""
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """解析 LLM 响应结果
        
        Args:
            response: LLM 返回的响应字符串
            
        Returns:
            解析后的关系列表
        """
        import json
        
        try:
            data = json.loads(response)
            relations = data.get("relations", [])
            
            for relation in relations:
                if "source" not in relation:
                    relation["source"] = ""
                if "target" not in relation:
                    relation["target"] = ""
                if "type" not in relation:
                    relation["type"] = "未知"
                if "description" not in relation:
                    relation["description"] = ""
            
            return relations
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, response={response}")
            return []
    
    def extract_typed_relations(self, entities: List[Dict[str, Any]], text: str,
                                custom_relation_types: Dict[str, List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """按类型分组提取关系
        
        该方法可以按照预定义的关系类型分类提取关系，
        支持自定义关系类型及其示例
        
        Args:
            entities: 实体列表
            text: 输入文本
            custom_relation_types: 自定义关系类型字典，键为关系类型，值为该类型的示例
            
        Returns:
            按关系类型分组的关系字典
        """
        if not entities or len(entities) == 0:
            return {}
        
        if not text or not text.strip():
            return {}
        
        try:
            prompt = self._build_typed_relations_prompt(entities, text, custom_relation_types)
            
            response = self.llm_client.chat(
                message=prompt,
                system_prompt=self.system_prompt,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            typed_relations = data.get("typed_relations", {})
            
            for relation_type in typed_relations:
                for relation in typed_relations[relation_type]:
                    if "source" not in relation:
                        relation["source"] = ""
                    if "target" not in relation:
                        relation["target"] = ""
                    if "description" not in relation:
                        relation["description"] = ""
            
            return typed_relations
            
        except Exception as e:
            logger.error(f"分类关系提取失败: {e}")
            return {}
    
    def _build_typed_relations_prompt(self, entities: List[Dict], text: str,
                                      custom_relation_types: Dict[str, List[str]] = None) -> str:
        """构建分类关系提取提示词
        
        Args:
            entities: 实体列表
            text: 输入文本
            custom_relation_types: 自定义关系类型
            
        Returns:
            格式化后的提示词字符串
        """
        entity_list = "\n".join([
            f"- {e.get('name', '')} ({e.get('type', '未知')}): {e.get('description', '')}"
            for e in entities
        ])
        
        type_examples = ""
        if custom_relation_types:
            type_examples = "\n\n关系类型定义及示例："
            for rel_type, examples in custom_relation_types.items():
                type_examples += f"\n- {rel_type}: {', '.join(examples)}"
        
        return f"""基于以下实体列表和原文，按类型提取实体之间的关系：

实体列表：
{entity_list}

原文内容：
{text}
{type_examples}

请按以下关系类型分类提取，每种类型返回一个关系列表：

{{
    "typed_relations": {{
        "合作关系": [
            {{
                "source": "实体A",
                "target": "实体B",
                "description": "具体合作内容"
            }}
        ],
        "竞争关系": [...],
        "所属关系": [...],
        "其他关系": [...]
    }}
}}"""


class CombinedExtractor:
    """组合提取器类
    
    该类将实体提取和关系提取组合在一起，
    可以一次性完成从文本到图谱元素的提取
    """
    
    def __init__(self, llm_client: LLMClient):
        """初始化组合提取器
        
        Args:
            llm_client: LLM 客户端实例
        """
        self.entity_extractor = LLMEntityExtractor(llm_client)
        self.relation_extractor = LLMRelationExtractor(llm_client)
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """一次性提取实体和关系
        
        该方法封装了实体提取和关系提取的完整流程，
        从输入文本中同时提取实体列表和关系列表
        
        Args:
            text: 输入文本
            
        Returns:
            包含 entities 和 relations 的字典
        """
        if not text or not text.strip():
            return {"entities": [], "relations": []}
        
        logger.info("开始组合提取实体和关系")
        
        entities = self.entity_extractor.extract(text)
        
        if len(entities) == 0:
            logger.info("未提取到实体，跳过关系提取")
            return {"entities": [], "relations": []}
        
        relations = self.relation_extractor.extract(entities, text)
        
        return {
            "entities": entities,
            "relations": relations
        }
    
    def extract_all_with_types(self, text: str, entity_types: List[str] = None,
                               relation_types: List[str] = None) -> Dict[str, Any]:
        """按指定类型提取实体和关系
        
        Args:
            text: 输入文本
            entity_types: 实体类型过滤列表
            relation_types: 关系类型过滤列表
            
        Returns:
            包含 entities 和 relations 的字典
        """
        if not text or not text.strip():
            return {"entities": [], "relations": []}
        
        entities = self.entity_extractor.extract(text, entity_types)
        
        if len(entities) == 0:
            return {"entities": [], "relations": []}
        
        relations = self.relation_extractor.extract(entities, text, relation_types)
        
        return {
            "entities": entities,
            "relations": relations
        }
