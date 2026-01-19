# 实体和关系定义

from typing import Dict, Any, List, Optional
from .base import BaseModel, TimestampMixin


class Entity(BaseModel, TimestampMixin):
    """实体类"""
    
    def __init__(self, name: str, entity_type: str, 
                 description: str = "", attributes: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.type = entity_type
        self.description = description
        self.attributes = attributes or {}
    
    def __repr__(self) -> str:
        return f"Entity(name='{self.name}', type='{self.type}')"
    
    def add_attribute(self, key: str, value: Any):
        """添加属性"""
        self.attributes[key] = value
        self.update_timestamp()
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """获取属性"""
        return self.attributes.get(key, default)


class Relation(BaseModel, TimestampMixin):
    """关系类"""
    
    def __init__(self, source: str, target: str, relation_type: str,
                 description: str = "", attributes: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.target = target
        self.type = relation_type
        self.description = description
        self.attributes = attributes or {}
    
    def __repr__(self) -> str:
        return f"Relation({self.source} -[{self.type}]-> {self.target})"
    
    def add_attribute(self, key: str, value: Any):
        """添加属性"""
        self.attributes[key] = value
        self.update_timestamp()
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """获取属性"""
        return self.attributes.get(key, default)


class KnowledgeGraph(BaseModel):
    """知识图谱类"""
    
    def __init__(self, graph_id: str, **kwargs):
        super().__init__(**kwargs)
        self.graph_id = graph_id
        self.entities: List[Entity] = kwargs.get("entities", [])
        self.relations: List[Relation] = kwargs.get("relations", [])
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities.append(entity)
    
    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations.append(relation)
    
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """根据名称获取实体"""
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None
    
    def get_relations_for_entity(self, entity_name: str) -> List[Relation]:
        """获取实体的所有关系"""
        return [
            r for r in self.relations
            if r.source == entity_name or r.target == entity_name
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        type_counts = {}
        for entity in self.entities:
            entity_type = entity.type
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        relation_type_counts = {}
        for relation in self.relations:
            rel_type = relation.type
            relation_type_counts[rel_type] = relation_type_counts.get(rel_type, 0) + 1
        
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "entity_types": type_counts,
            "relation_types": relation_type_counts
        }
