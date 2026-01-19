# 图谱构建模块 - 知识图谱构建器
# 提供图谱构建、数据转换和统计分析功能

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.interfaces import GraphBuilder
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraphBuilder(GraphBuilder):
    """知识图谱构建器实现类
    
    该类负责将提取的实体和关系数据构建成标准格式的知识图谱，
    支持节点的添加、边的创建、图谱统计和导出等功能。
    """
    
    def __init__(self, graph_id: str = None):
        """初始化知识图谱构建器
        
        Args:
            graph_id: 可选的图谱 ID，如果不提供则自动生成
        """
        self.graph_id = graph_id or str(uuid.uuid4())
        self.graph = {
            "id": self.graph_id,
            "nodes": [],
            "edges": [],
            "metadata": {
                "created_at": None,
                "updated_at": None,
                "source_text": None,
                "description": None
            }
        }
        self.node_map = {}
        self.edge_set = set()
        logger.info(f"知识图谱构建器初始化完成: graph_id={self.graph_id}")
    
    def build(self, entities: List[Dict], relations: List[Dict],
              source_text: str = None, description: str = None) -> Dict[str, Any]:
        """构建知识图谱
        
        该方法接收实体列表和关系列表，将它们转换为标准格式的图谱数据。
        支持自动去重、节点映射和边集维护。
        
        Args:
            entities: 实体列表，每个实体包含 name, type, description 等字段
            relations: 关系列表，每个关系包含 source, target, type, description 等字段
            source_text: 可选的源文本，用于记录图谱来源
            description: 可选的图谱描述
            
        Returns:
            构建完成的图谱数据字典
        """
        logger.info(f"开始构建知识图谱: entities={len(entities)}, relations={len(relations)}")
        
        self._reset_graph()
        self.graph["id"] = self.graph_id
        self.graph["metadata"]["created_at"] = datetime.utcnow().isoformat()
        self.graph["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        if source_text:
            self.graph["metadata"]["source_text"] = source_text[:10000]
        if description:
            self.graph["metadata"]["description"] = description
        
        self._add_entities(entities)
        self._add_relations(relations)
        
        logger.info(f"知识图谱构建完成: nodes={len(self.graph['nodes'])}, edges={len(self.graph['edges'])}")
        
        return self.graph
    
    def _reset_graph(self):
        """重置图谱数据"""
        self.graph = {
            "id": self.graph_id,
            "nodes": [],
            "edges": [],
            "metadata": {
                "created_at": None,
                "updated_at": None,
                "source_text": None,
                "description": None
            }
        }
        self.node_map = {}
        self.edge_set = set()
    
    def _add_entities(self, entities: List[Dict]):
        """添加实体到图谱
        
        将实体列表转换为节点并添加到图谱中，
        自动处理去重和 ID 映射
        
        Args:
            entities: 实体列表
        """
        for entity in entities:
            if not entity.get("name"):
                continue
            
            node_id = entity["name"]
            
            if node_id in self.node_map:
                continue
            
            node = {
                "id": node_id,
                "type": entity.get("type", "未知"),
                "description": entity.get("description", ""),
                "attributes": entity.get("attributes", {}),
                "properties": self._extract_properties(entity)
            }
            
            self.graph["nodes"].append(node)
            self.node_map[node_id] = len(self.graph["nodes"]) - 1
    
    def _extract_properties(self, entity: Dict) -> Dict[str, Any]:
        """从实体中提取额外属性
        
        从实体字典中提取额外的属性信息，
        排除标准字段后保留其他字段
        
        Args:
            entity: 实体字典
            
        Returns:
            额外的属性字典
        """
        standard_fields = {"name", "type", "description", "attributes"}
        properties = {}
        
        for key, value in entity.items():
            if key not in standard_fields and value is not None:
                properties[key] = value
        
        return properties
    
    def _add_relations(self, relations: List[Dict]):
        """添加关系到图谱
        
        将关系列表转换为边并添加到图谱中，
        自动验证实体存在性和去重
        
        Args:
            relations: 关系列表
        """
        for relation in relations:
            source = relation.get("source")
            target = relation.get("target")
            
            if not source or not target:
                continue
            
            if source not in self.node_map or target not in self.node_map:
                logger.warning(f"关系引用的实体不存在: {source} -> {target}")
                continue
            
            edge_key = (source, target, relation.get("type", ""))
            if edge_key in self.edge_set:
                continue
            
            edge = {
                "source": source,
                "target": target,
                "type": relation.get("type", "未知"),
                "description": relation.get("description", ""),
                "attributes": relation.get("attributes", {}),
                "properties": self._extract_properties(relation)
            }
            
            self.graph["edges"].append(edge)
            self.edge_set.add(edge_key)
    
    def add_node(self, node: Dict[str, Any]) -> bool:
        """添加单个节点到图谱
        
        Args:
            node: 节点数据，包含 id, type, description 等字段
            
        Returns:
            是否添加成功
        """
        node_id = node.get("id") or node.get("name")
        if not node_id:
            return False
        
        if node_id in self.node_map:
            logger.warning(f"节点已存在: {node_id}")
            return False
        
        formatted_node = {
            "id": node_id,
            "type": node.get("type", "未知"),
            "description": node.get("description", ""),
            "attributes": node.get("attributes", {}),
            "properties": {}
        }
        
        self.graph["nodes"].append(formatted_node)
        self.node_map[node_id] = len(self.graph["nodes"]) - 1
        
        return True
    
    def add_edge(self, source: str, target: str, edge_type: str,
                 description: str = "", attributes: Dict = None) -> bool:
        """添加单条边到图谱
        
        Args:
            source: 源节点 ID
            target: 目标节点 ID
            edge_type: 边类型
            description: 边描述
            attributes: 额外属性
            
        Returns:
            是否添加成功
        """
        if source not in self.node_map or target not in self.node_map:
            logger.warning(f"边引用的节点不存在: {source} -> {target}")
            return False
        
        edge_key = (source, target, edge_type)
        if edge_key in self.edge_set:
            return False
        
        edge = {
            "source": source,
            "target": target,
            "type": edge_type,
            "description": description,
            "attributes": attributes or {}
        }
        
        self.graph["edges"].append(edge)
        self.edge_set.add(edge_key)
        
        return True
    
    def merge_graph(self, other_graph: Dict[str, Any]) -> bool:
        """合并另一个图谱
        
        将另一个图谱的节点和边合并到当前图谱
        
        Args:
            other_graph: 另一个图谱数据
            
        Returns:
            是否合并成功
        """
        try:
            other_nodes = other_graph.get("nodes", [])
            other_edges = other_graph.get("edges", [])
            
            for node in other_nodes:
                if node["id"] not in self.node_map:
                    self.graph["nodes"].append(node)
                    self.node_map[node["id"]] = len(self.graph["nodes"]) - 1
            
            for edge in other_edges:
                edge_key = (edge["source"], edge["target"], edge.get("type", ""))
                if edge_key not in self.edge_set:
                    if edge["source"] in self.node_map and edge["target"] in self.node_map:
                        self.graph["edges"].append(edge)
                        self.edge_set.add(edge_key)
            
            self.graph["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"图谱合并失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息
        
        返回图谱的基本统计信息，包括节点数、边数、各类型分布等
        
        Returns:
            统计信息字典
        """
        node_types = {}
        edge_types = {}
        
        for node in self.graph["nodes"]:
            node_type = node.get("type", "未知")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for edge in self.graph["edges"]:
            edge_type = edge.get("type", "未知")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        node_count = len(self.graph["nodes"])
        edge_count = len(self.graph["edges"])
        
        stats = {
            "graph_id": self.graph_id,
            "total_nodes": node_count,
            "total_edges": edge_count,
            "density": self._calculate_density() if node_count > 1 else 0,
            "node_types": node_types,
            "edge_types": edge_types,
            "avg_degree": (2 * edge_count / node_count) if node_count > 0 else 0,
            "connected_components": self._find_connected_components()
        }
        
        return stats
    
    def _calculate_density(self) -> float:
        """计算图谱密度
        
        密度 = 实际边数 / 最大可能边数
        
        Returns:
            图谱密度值
        """
        n = len(self.graph["nodes"])
        if n <= 1:
            return 0
        
        max_edges = n * (n - 1) / 2
        return len(self.graph["edges"]) / max_edges if max_edges > 0 else 0
    
    def _find_connected_components(self) -> int:
        """计算连通分量数量
        
        使用简单的 BFS/DFS 算法计算图谱的连通分量数
        
        Returns:
            连通分量数量
        """
        if not self.graph["nodes"]:
            return 0
        
        visited = set()
        components = 0
        
        for node in self.graph["nodes"]:
            if node["id"] not in visited:
                components += 1
                self._bfs_visit(node["id"], visited)
        
        return components
    
    def _bfs_visit(self, start_node: str, visited: set):
        """BFS 遍历访问节点
        
        Args:
            start_node: 起始节点 ID
            visited: 已访问节点集合
        """
        from collections import deque
        
        queue = deque([start_node])
        visited.add(start_node)
        
        while queue:
            current = queue.popleft()
            
            for edge in self.graph["edges"]:
                if edge["source"] == current and edge["target"] not in visited:
                    visited.add(edge["target"])
                    queue.append(edge["target"])
                elif edge["target"] == current and edge["source"] not in visited:
                    visited.add(edge["source"])
                    queue.append(edge["source"])
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取指定节点
        
        Args:
            node_id: 节点 ID
            
        Returns:
            节点数据，如果不存在则返回 None
        """
        if node_id in self.node_map:
            return self.graph["nodes"][self.node_map[node_id]]
        return None
    
    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """获取节点的邻居节点
        
        Args:
            node_id: 节点 ID
            
        Returns:
            邻居节点列表
        """
        neighbors = []
        
        for edge in self.graph["edges"]:
            if edge["source"] == node_id:
                neighbor = self.get_node(edge["target"])
                if neighbor:
                    neighbors.append({
                        "node": neighbor,
                        "relation": edge.get("type", ""),
                        "description": edge.get("description", "")
                    })
            elif edge["target"] == node_id:
                neighbor = self.get_node(edge["source"])
                if neighbor:
                    neighbors.append({
                        "node": neighbor,
                        "relation": edge.get("type", ""),
                        "description": edge.get("description", ""),
                        "reverse": True
                    })
        
        return neighbors
    
    def get_edges_by_type(self, edge_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有边
        
        Args:
            edge_type: 边类型
            
        Returns:
            边列表
        """
        return [
            edge for edge in self.graph["edges"]
            if edge.get("type", "").lower() == edge_type.lower()
        ]
    
    def get_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有节点
        
        Args:
            node_type: 节点类型
            
        Returns:
            节点列表
        """
        return [
            node for node in self.graph["nodes"]
            if node.get("type", "").lower() == node_type.lower()
        ]
    
    def search_nodes(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索节点
        
        在节点名称和描述中搜索包含关键词的节点
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的节点列表
        """
        keyword_lower = keyword.lower()
        
        return [
            node for node in self.graph["nodes"]
            if (keyword_lower in node.get("id", "").lower() or
                keyword_lower in node.get("description", "").lower())
        ]
    
    def to_cytoscape_format(self) -> Dict[str, Any]:
        """转换为 Cytoscape.js 格式
        
        将图谱数据转换为 Cytoscape.js 可视化库所需的格式
        
        Returns:
            Cytoscape 格式的图谱数据
        """
        elements = []
        
        for node in self.graph["nodes"]:
            elements.append({
                "data": {
                    "id": node["id"],
                    "label": node["id"],
                    "type": node.get("type", "未知"),
                    "description": node.get("description", "")
                }
            })
        
        for edge in self.graph["edges"]:
            edge_id = f"{edge['source']}-{edge['type']}-{edge['target']}"
            elements.append({
                "data": {
                    "id": edge_id,
                    "source": edge["source"],
                    "target": edge["target"],
                    "type": edge.get("type", ""),
                    "description": edge.get("description", "")
                }
            })
        
        return {
            "elements": elements,
            "style": self._get_default_cytoscape_style()
        }
    
    def _get_default_cytoscape_style(self) -> List[Dict[str, Any]]:
        """获取默认的 Cytoscape 样式
        
        Returns:
            Cytoscape 样式列表
        """
        return [
            {
                "selector": "node",
                "style": {
                    "label": "data(label)",
                    "background-color": "#97C2FC",
                    "width": 60,
                    "height": 60,
                    "font-size": 12
                }
            },
            {
                "selector": "edge",
                "style": {
                    "width": 2,
                    "line-color": "#848484",
                    "target-arrow-color": "#848484",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier"
                }
            }
        ]
    
    def to_networkx_format(self) -> Dict[str, Any]:
        """转换为 NetworkX 格式
        
        将图谱数据转换为 NetworkX 库所需的格式
        
        Returns:
            NetworkX 格式的图谱数据（包含 nodes 和 edges）
        """
        nodes = [
            {
                "id": node["id"],
                "type": node.get("type", "未知"),
                **node.get("attributes", {})
            }
            for node in self.graph["nodes"]
        ]
        
        edges = [
            {
                "source": edge["source"],
                "target": edge["target"],
                "type": edge.get("type", ""),
                **edge.get("attributes", {})
            }
            for edge in self.graph["edges"]
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "directed": True
        }
    
    def update_metadata(self, key: str, value: Any):
        """更新图谱元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        self.graph["metadata"][key] = value
        self.graph["metadata"]["updated_at"] = datetime.utcnow().isoformat()
    
    def get_graph(self) -> Dict[str, Any]:
        """获取当前图谱数据
        
        Returns:
            图谱数据字典
        """
        return self.graph
    
    def clear(self):
        """清空图谱数据"""
        self._reset_graph()


class GraphBuilderFactory:
    """图谱构建器工厂类
    
    提供创建不同类型图谱构建器的工厂方法
    """
    
    @staticmethod
    def create_builder(graph_id: str = None) -> KnowledgeGraphBuilder:
        """创建标准知识图谱构建器
        
        Args:
            graph_id: 可选的图谱 ID
            
        Returns:
            知识图谱构建器实例
        """
        return KnowledgeGraphBuilder(graph_id)
    
    @staticmethod
    def create_social_graph_builder(graph_id: str = None) -> KnowledgeGraphBuilder:
        """创建社交关系图谱构建器
        
        专门用于构建社交网络的图谱构建器，
        预配置了社交网络相关的节点和边类型
        
        Args:
            graph_id: 可选的图谱 ID
            
        Returns:
            知识图谱构建器实例
        """
        builder = KnowledgeGraphBuilder(graph_id)
        builder.update_metadata("graph_type", "social_network")
        return builder
    
    @staticmethod
    def create_knowledge_graph_builder(graph_id: str = None) -> KnowledgeGraphBuilder:
        """创建知识图谱构建器
        
        专门用于构建通用知识图谱的构建器，
        预配置了知识图谱相关的节点和边类型
        
        Args:
            graph_id: 可选的图谱 ID
            
        Returns:
            知识图谱构建器实例
        """
        builder = KnowledgeGraphBuilder(graph_id)
        builder.update_metadata("graph_type", "knowledge_graph")
        return builder
