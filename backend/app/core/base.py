# 基础类和接口定义

from typing import Dict, Any, Optional
from datetime import datetime


class BaseModel:
    """基础数据模型类"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """从字典创建实例"""
        return cls(**data)


class TimestampMixin:
    """时间戳混入类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
    
    def update_timestamp(self):
        """更新时间戳"""
        self.updated_at = datetime.utcnow()
