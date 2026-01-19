# 数据验证模块

from typing import Any, Dict, List, Optional, Type, get_type_hints
from dataclasses import dataclass
from enum import Enum
import re
import email_validator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationType(Enum):
    """验证类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    LIST = "list"
    DICT = "dict"
    JSON = "json"


@dataclass
class ValidationError:
    """验证错误"""
    field: str
    message: str
    value: Any = None


class ValidationResult:
    """验证结果"""
    
    def __init__(self, is_valid: bool = True, 
                 errors: Optional[List[ValidationError]] = None):
        """初始化验证结果
        
        Args:
            is_valid: 是否验证通过
            errors: 错误列表
        """
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, field: str, message: str, value: Any = None):
        """添加验证错误
        
        Args:
            field: 字段名
            message: 错误消息
            value: 错误值
        """
        self.errors.append(ValidationError(field, message, value))
        self.is_valid = False
    
    def get_error_messages(self) -> List[str]:
        """获取错误消息列表"""
        return [f"{e.field}: {e.message}" for e in self.errors]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {"field": e.field, "message": e.message, "value": e.value}
                for e in self.errors
            ]
        }


class Validator:
    """通用验证器"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str = "field") -> ValidationResult:
        """验证必填字段
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = ValidationResult()
        
        if value is None or value == "":
            result.add_error(field_name, f"{field_name} 是必填字段")
        
        return result
    
    @staticmethod
    def validate_string(value: Any, field_name: str = "field",
                      min_length: Optional[int] = None,
                      max_length: Optional[int] = None,
                      pattern: Optional[str] = None) -> ValidationResult:
        """验证字符串
        
        Args:
            value: 要验证的值
            field_name: 字段名
            min_length: 最小长度
            max_length: 最大长度
            pattern: 正则表达式模式
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} 必须是字符串", value)
            return result
        
        # 验证长度
        if min_length is not None and len(value) < min_length:
            result.add_error(
                field_name,
                f"{field_name} 长度不能小于 {min_length}",
                value
            )
        
        if max_length is not None and len(value) > max_length:
            result.add_error(
                field_name,
                f"{field_name} 长度不能大于 {max_length}",
                value
            )
        
        # 验证模式
        if pattern is not None:
            if not re.match(pattern, value):
                result.add_error(
                    field_name,
                    f"{field_name} 格式不正确",
                    value
                )
        
        return result
    
    @staticmethod
    def validate_integer(value: Any, field_name: str = "field",
                       min_value: Optional[int] = None,
                       max_value: Optional[int] = None) -> ValidationResult:
        """验证整数
        
        Args:
            value: 要验证的值
            field_name: 字段名
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, int) or isinstance(value, bool):
            result.add_error(field_name, f"{field_name} 必须是整数", value)
            return result
        
        # 验证范围
        if min_value is not None and value < min_value:
            result.add_error(
                field_name,
                f"{field_name} 不能小于 {min_value}",
                value
            )
        
        if max_value is not None and value > max_value:
            result.add_error(
                field_name,
                f"{field_name} 不能大于 {max_value}",
                value
            )
        
        return result
    
    @staticmethod
    def validate_float(value: Any, field_name: str = "field",
                     min_value: Optional[float] = None,
                     max_value: Optional[float] = None) -> ValidationResult:
        """验证浮点数
        
        Args:
            value: 要验证的值
            field_name: 字段名
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            result.add_error(field_name, f"{field_name} 必须是数字", value)
            return result
        
        value = float(value)
        
        # 验证范围
        if min_value is not None and value < min_value:
            result.add_error(
                field_name,
                f"{field_name} 不能小于 {min_value}",
                value
            )
        
        if max_value is not None and value > max_value:
            result.add_error(
                field_name,
                f"{field_name} 不能大于 {max_value}",
                value
            )
        
        return result
    
    @staticmethod
    def validate_boolean(value: Any, field_name: str = "field") -> ValidationResult:
        """验证布尔值
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, bool):
            result.add_error(field_name, f"{field_name} 必须是布尔值", value)
        
        return result
    
    @staticmethod
    def validate_email(value: Any, field_name: str = "email") -> ValidationResult:
        """验证邮箱地址
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} 必须是字符串", value)
            return result
        
        try:
            email_validator.validate_email(value)
        except email_validator.EmailNotValidError:
            result.add_error(field_name, f"{field_name} 格式不正确", value)
        
        return result
    
    @staticmethod
    def validate_url(value: Any, field_name: str = "url") -> ValidationResult:
        """验证 URL
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} 必须是字符串", value)
            return result
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # TLD
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(value):
            result.add_error(field_name, f"{field_name} 格式不正确", value)
        
        return result
    
    @staticmethod
    def validate_uuid(value: Any, field_name: str = "uuid") -> ValidationResult:
        """验证 UUID
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} 必须是字符串", value)
            return result
        
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_pattern.match(value):
            result.add_error(field_name, f"{field_name} 格式不正确", value)
        
        return result
    
    @staticmethod
    def validate_list(value: Any, field_name: str = "list",
                    min_length: Optional[int] = None,
                    max_length: Optional[int] = None) -> ValidationResult:
        """验证列表
        
        Args:
            value: 要验证的值
            field_name: 字段名
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, list):
            result.add_error(field_name, f"{field_name} 必须是列表", value)
            return result
        
        # 验证长度
        if min_length is not None and len(value) < min_length:
            result.add_error(
                field_name,
                f"{field_name} 长度不能小于 {min_length}",
                value
            )
        
        if max_length is not None and len(value) > max_length:
            result.add_error(
                field_name,
                f"{field_name} 长度不能大于 {max_length}",
                value
            )
        
        return result
    
    @staticmethod
    def validate_dict(value: Any, field_name: str = "dict") -> ValidationResult:
        """验证字典
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, dict):
            result.add_error(field_name, f"{field_name} 必须是字典", value)
        
        return result
    
    @staticmethod
    def validate_json(value: Any, field_name: str = "json") -> ValidationResult:
        """验证 JSON 字符串
        
        Args:
            value: 要验证的值
            field_name: 字段名
            
        Returns:
            验证结果
        """
        result = Validator.validate_required(value, field_name)
        
        if not result.is_valid:
            return result
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{field_name} 必须是字符串", value)
            return result
        
        import json
        try:
            json.loads(value)
        except json.JSONDecodeError:
            result.add_error(field_name, f"{field_name} 格式不正确", value)
        
        return result


class SchemaValidator:
    """基于 Schema 的验证器"""
    
    def __init__(self, schema: Dict[str, Dict[str, Any]]):
        """初始化 Schema 验证器
        
        Args:
            schema: Schema 定义，格式：
                {
                    "field_name": {
                        "type": ValidationType.STRING,
                        "required": True,
                        "min_length": 1,
                        "max_length": 100
                    }
                }
        """
        self.schema = schema
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """验证数据
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            验证结果
        """
        result = ValidationResult()
        
        for field_name, field_config in self.schema.items():
            value = data.get(field_name)
            
            # 检查必填
            if field_config.get("required", True):
                required_result = Validator.validate_required(value, field_name)
                if not required_result.is_valid:
                    result.errors.extend(required_result.errors)
                    continue
            
            # 如果值为 None 且非必填，跳过验证
            if value is None and not field_config.get("required", True):
                continue
            
            # 根据类型验证
            validation_type = field_config.get("type")
            
            if validation_type == ValidationType.STRING:
                validation_result = Validator.validate_string(
                    value,
                    field_name,
                    field_config.get("min_length"),
                    field_config.get("max_length"),
                    field_config.get("pattern")
                )
            elif validation_type == ValidationType.INTEGER:
                validation_result = Validator.validate_integer(
                    value,
                    field_name,
                    field_config.get("min_value"),
                    field_config.get("max_value")
                )
            elif validation_type == ValidationType.FLOAT:
                validation_result = Validator.validate_float(
                    value,
                    field_name,
                    field_config.get("min_value"),
                    field_config.get("max_value")
                )
            elif validation_type == ValidationType.BOOLEAN:
                validation_result = Validator.validate_boolean(value, field_name)
            elif validation_type == ValidationType.EMAIL:
                validation_result = Validator.validate_email(value, field_name)
            elif validation_type == ValidationType.URL:
                validation_result = Validator.validate_url(value, field_name)
            elif validation_type == ValidationType.UUID:
                validation_result = Validator.validate_uuid(value, field_name)
            elif validation_type == ValidationType.LIST:
                validation_result = Validator.validate_list(
                    value,
                    field_name,
                    field_config.get("min_length"),
                    field_config.get("max_length")
                )
            elif validation_type == ValidationType.DICT:
                validation_result = Validator.validate_dict(value, field_name)
            elif validation_type == ValidationType.JSON:
                validation_result = Validator.validate_json(value, field_name)
            else:
                logger.warning(f"未知的验证类型: {validation_type}")
                continue
            
            if not validation_result.is_valid:
                result.errors.extend(validation_result.errors)
        
        # 更新验证状态
        result.is_valid = len(result.errors) == 0
        
        return result


def validate_api_request(data: Dict[str, Any], 
                       required_fields: List[str]) -> ValidationResult:
    """验证 API 请求
    
    Args:
        data: 请求数据
        required_fields: 必填字段列表
        
    Returns:
        验证结果
    """
    result = ValidationResult()
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            result.add_error(field, f"{field} 是必填字段")
    
    return result


def sanitize_string(value: str, 
                  max_length: int = 1000,
                  remove_html: bool = True) -> str:
    """清理字符串，防止 XSS 攻击
    
    Args:
        value: 输入字符串
        max_length: 最大长度
        remove_html: 是否移除 HTML 标签
        
    Returns:
        清理后的字符串
    """
    if not isinstance(value, str):
        return ""
    
    # 截断长度
    value = value[:max_length]
    
    # 移除 HTML 标签
    if remove_html:
        import html
        value = html.escape(value)
    
    return value


def sanitize_dict(data: Dict[str, Any], 
                 max_string_length: int = 1000) -> Dict[str, Any]:
    """清理字典中的所有字符串
    
    Args:
        data: 输入字典
        max_string_length: 最大字符串长度
        
    Returns:
        清理后的字典
    """
    result = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_string(value, max_string_length)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, max_string_length)
        elif isinstance(value, list):
            result[key] = [
                sanitize_string(item, max_string_length) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result
