# 图谱构建模块 - 图谱存储
# 提供图谱数据的持久化存储和检索功能

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.interfaces import GraphStorage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JSONFileGraphStorage(GraphStorage):
    """基于 JSON 文件的图谱存储实现类
    
    该类提供基于文件系统的图谱持久化存储功能，
    支持图谱的保存、加载、删除和查询操作。
    """
    
    def __init__(self, storage_dir: str = "graphs"):
        """初始化文件存储
        
        Args:
            storage_dir: 存储目录路径，相对于应用根目录
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
        logger.info(f"图谱文件存储初始化完成: storage_dir={storage_dir}")
    
    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"创建图谱存储目录: {self.storage_dir}")
    
    def _get_file_path(self, graph_id: str) -> str:
        """获取图谱文件路径
        
        Args:
            graph_id: 图谱 ID
            
        Returns:
            完整的文件路径
        """
        return os.path.join(self.storage_dir, f"{graph_id}.json")
    
    def save(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱到文件
        
        将图谱数据序列化为 JSON 格式并保存到文件
        
        Args:
            graph_id: 图谱唯一标识
            graph_data: 图谱数据
            
        Returns:
            是否保存成功
        """
        try:
            file_path = self._get_file_path(graph_id)
            
            enriched_data = {
                **graph_data,
                "storage_metadata": {
                    "saved_at": datetime.utcnow().isoformat(),
                    "file_path": file_path
                }
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(enriched_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"图谱保存成功: graph_id={graph_id}, file_path={file_path}")
            return True
            
        except Exception as e:
            logger.error(f"图谱保存失败: graph_id={graph_id}, error={e}")
            return False
    
    def load(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """从文件加载图谱
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            图谱数据，如果不存在则返回 None
        """
        try:
            file_path = self._get_file_path(graph_id)
            
            if not os.path.exists(file_path):
                logger.warning(f"图谱文件不存在: graph_id={graph_id}")
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
            
            logger.info(f"图谱加载成功: graph_id={graph_id}")
            return graph_data
            
        except json.JSONDecodeError as e:
            logger.error(f"图谱文件解析失败: graph_id={graph_id}, error={e}")
            return None
        except Exception as e:
            logger.error(f"图谱加载失败: graph_id={graph_id}, error={e}")
            return None
    
    def load_with_metadata(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """加载图谱及其元数据
        
        在基础加载功能上添加时间戳和文件信息
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            包含元数据的图谱数据
        """
        graph_data = self.load(graph_id)
        
        if graph_data is None:
            return None
        
        file_path = self._get_file_path(graph_id)
        file_info = {}
        
        if os.path.exists(file_path):
            file_info = {
                "file_size": os.path.getsize(file_path),
                "modified_at": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat()
            }
        
        return {
            "graph": graph_data,
            "file_info": file_info
        }
    
    def delete(self, graph_id: str) -> bool:
        """删除图谱文件
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            是否删除成功
        """
        try:
            file_path = self._get_file_path(graph_id)
            
            if not os.path.exists(file_path):
                logger.warning(f"图谱文件不存在，无法删除: graph_id={graph_id}")
                return False
            
            os.remove(file_path)
            logger.info(f"图谱删除成功: graph_id={graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"图谱删除失败: graph_id={graph_id}, error={e}")
            return False
    
    def exists(self, graph_id: str) -> bool:
        """检查图谱是否存在
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            图谱是否存在
        """
        file_path = self._get_file_path(graph_id)
        return os.path.exists(file_path)
    
    def list_graphs(self, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """列出所有图谱
        
        返回存储目录中的所有图谱列表
        
        Args:
            include_metadata: 是否包含文件元数据
            
        Returns:
            图谱列表
        """
        graphs = []
        
        if not os.path.exists(self.storage_dir):
            return graphs
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                graph_id = filename[:-5]
                graph_info = {"graph_id": graph_id}
                
                if include_metadata:
                    file_path = os.path.join(self.storage_dir, filename)
                    graph_info["file_size"] = os.path.getsize(file_path)
                    graph_info["modified_at"] = datetime.fromtimestamp(
                        os.path.getmtime(file_path)
                    ).isoformat()
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            graph_data = json.load(f)
                            graph_info["node_count"] = len(graph_data.get("nodes", []))
                            graph_info["edge_count"] = len(graph_data.get("edges", []))
                            graph_info["metadata"] = graph_data.get("metadata", {})
                    except Exception:
                        graph_info["node_count"] = 0
                        graph_info["edge_count"] = 0
                
                graphs.append(graph_info)
        
        graphs.sort(key=lambda x: x.get("graph_id", ""))
        
        return graphs
    
    def update(self, graph_id: str, updates: Dict[str, Any]) -> bool:
        """更新图谱部分数据
        
        加载现有图谱，合并更新内容后保存
        
        Args:
            graph_id: 图谱唯一标识
            updates: 更新内容
            
        Returns:
            是否更新成功
        """
        try:
            graph_data = self.load(graph_id)
            
            if graph_data is None:
                logger.warning(f"图谱不存在，无法更新: graph_id={graph_id}")
                return False
            
            graph_data.update(updates)
            graph_data["storage_metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            return self.save(graph_id, graph_data)
            
        except Exception as e:
            logger.error(f"图谱更新失败: graph_id={graph_id}, error={e}")
            return False
    
    def backup(self, graph_id: str, backup_dir: str = None) -> Optional[str]:
        """备份图谱文件
        
        将图谱文件复制到备份目录
        
        Args:
            graph_id: 图谱唯一标识
            backup_dir: 备份目录，默认为 storage_dir/backup
            
        Returns:
            备份文件路径，失败返回 None
        """
        try:
            if backup_dir is None:
                backup_dir = os.path.join(self.storage_dir, "backup")
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            source_path = self._get_file_path(graph_id)
            
            if not os.path.exists(source_path):
                logger.warning(f"源图谱文件不存在: graph_id={graph_id}")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{graph_id}_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            with open(source_path, "r", encoding="utf-8") as src:
                with open(backup_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            
            logger.info(f"图谱备份成功: graph_id={graph_id}, backup_path={backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"图谱备份失败: graph_id={graph_id}, error={e}")
            return None
    
    def restore(self, backup_path: str, target_graph_id: str = None) -> bool:
        """从备份恢复图谱
        
        Args:
            backup_path: 备份文件路径
            target_graph_id: 目标图谱 ID，不指定则使用备份的文件名
            
        Returns:
            是否恢复成功
        """
        try:
            if not os.path.exists(backup_path):
                logger.warning(f"备份文件不存在: backup_path={backup_path}")
                return False
            
            with open(backup_path, "r", encoding="utf-8") as f:
                graph_data = json.load(f)
            
            graph_id = target_graph_id or graph_data.get("id")
            
            if not graph_id:
                logger.warning("无法从备份获取图谱 ID")
                return False
            
            graph_data["storage_metadata"] = {
                "restored_at": datetime.utcnow().isoformat(),
                "backup_path": backup_path
            }
            
            return self.save(graph_id, graph_data)
            
        except Exception as e:
            logger.error(f"图谱恢复失败: backup_path={backup_path}, error={e}")
            return False
    
    def export_to_json(self, graph_id: str, output_path: str = None) -> Optional[str]:
        """导出图谱到 JSON 文件
        
        Args:
            graph_id: 图谱唯一标识
            output_path: 输出路径，默认使用原文件路径
            
        Returns:
            导出文件路径
        """
        graph_data = self.load(graph_id)
        
        if graph_data is None:
            return None
        
        if output_path is None:
            output_path = self._get_file_path(graph_id)
        
        storage_metadata = graph_data.pop("storage_metadata", None)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"图谱导出成功: graph_id={graph_id}, output_path={output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"图谱导出失败: graph_id={graph_id}, error={e}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息
        
        Returns:
            存储统计信息
        """
        graphs = self.list_graphs(include_metadata=True)
        
        total_size = 0
        total_nodes = 0
        total_edges = 0
        
        for graph in graphs:
            total_size += graph.get("file_size", 0)
            total_nodes += graph.get("node_count", 0)
            total_edges += graph.get("edge_count", 0)
        
        return {
            "total_graphs": len(graphs),
            "total_size_bytes": total_size,
            "total_size_human": self._format_size(total_size),
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "storage_dir": self.storage_dir
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小
        
        Args:
            size_bytes: 字节大小
            
        Returns:
            格式化后的大小字符串
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


class InMemoryGraphStorage(GraphStorage):
    """内存图谱存储实现类
    
    该类提供基于内存的图谱存储，
    适用于临时存储或测试场景
    """
    
    def __init__(self):
        """初始化内存存储"""
        self.graphs = {}
        logger.info("内存图谱存储初始化完成")
    
    def save(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱到内存
        
        Args:
            graph_id: 图谱唯一标识
            graph_data: 图谱数据
            
        Returns:
            是否保存成功
        """
        try:
            graph_data["storage_metadata"] = {
                "saved_at": datetime.utcnow().isoformat(),
                "storage_type": "memory"
            }
            self.graphs[graph_id] = graph_data
            logger.info(f"图谱保存成功: graph_id={graph_id}")
            return True
            
        except Exception as e:
            logger.error(f"图谱保存失败: graph_id={graph_id}, error={e}")
            return False
    
    def load(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """从内存加载图谱
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            图谱数据
        """
        graph_data = self.graphs.get(graph_id)
        
        if graph_data is None:
            logger.warning(f"图谱不存在: graph_id={graph_id}")
            return None
        
        logger.info(f"图谱加载成功: graph_id={graph_id}")
        return graph_data
    
    def delete(self, graph_id: str) -> bool:
        """从内存删除图谱
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            是否删除成功
        """
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            logger.info(f"图谱删除成功: graph_id={graph_id}")
            return True
        
        logger.warning(f"图谱不存在，无法删除: graph_id={graph_id}")
        return False
    
    def exists(self, graph_id: str) -> bool:
        """检查图谱是否存在
        
        Args:
            graph_id: 图谱唯一标识
            
        Returns:
            是否存在
        """
        return graph_id in self.graphs
    
    def list_graphs(self, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """列出所有图谱
        
        Args:
            include_metadata: 是否包含元数据
            
        Returns:
            图谱列表
        """
        graphs = []
        
        for graph_id, graph_data in self.graphs.items():
            graph_info = {"graph_id": graph_id}
            
            if include_metadata:
                graph_info["node_count"] = len(graph_data.get("nodes", []))
                graph_info["edge_count"] = len(graph_data.get("edges", []))
                graph_info["metadata"] = graph_data.get("metadata", {})
                storage_meta = graph_data.get("storage_metadata", {})
                graph_info["saved_at"] = storage_meta.get("saved_at")
            
            graphs.append(graph_info)
        
        return sorted(graphs, key=lambda x: x.get("graph_id", ""))
    
    def clear(self):
        """清空所有图谱"""
        self.graphs.clear()
        logger.info("内存图谱存储已清空")
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """获取所有图谱
        
        Returns:
            所有图谱数据
        """
        return self.graphs.copy()


class GraphStorageManager:
    """图谱存储管理器
    
    提供统一的图谱存储接口，支持内存和文件两种存储方式
    """
    
    def __init__(self, storage_type: str = "file", **kwargs):
        """初始化存储管理器
        
        Args:
            storage_type: 存储类型，"file" 或 "memory"
            **kwargs: 存储配置参数
        """
        if storage_type == "file":
            storage_dir = kwargs.get("storage_dir", "graphs")
            self.storage = JSONFileGraphStorage(storage_dir)
        else:
            self.storage = InMemoryGraphStorage()
        
        self.storage_type = storage_type
        logger.info(f"图谱存储管理器初始化完成: type={storage_type}")
    
    def save_graph(self, graph_id: str, graph_data: Dict[str, Any]) -> bool:
        """保存图谱"""
        return self.storage.save(graph_id, graph_data)
    
    def load_graph(self, graph_id: str) -> Optional[Dict[str, Any]]:
        """加载图谱"""
        return self.storage.load(graph_id)
    
    def delete_graph(self, graph_id: str) -> bool:
        """删除图谱"""
        return self.storage.delete(graph_id)
    
    def graph_exists(self, graph_id: str) -> bool:
        """检查图谱是否存在"""
        return self.storage.exists(graph_id)
    
    def list_graphs(self, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """列出所有图谱"""
        return self.storage.list_graphs(include_metadata)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取存储统计"""
        if hasattr(self.storage, "get_storage_stats"):
            return self.storage.get_storage_stats()
        
        graphs = self.storage.list_graphs(include_metadata=True)
        total_nodes = sum(g.get("node_count", 0) for g in graphs)
        total_edges = sum(g.get("edge_count", 0) for g in graphs)
        
        return {
            "total_graphs": len(graphs),
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "storage_type": self.storage_type
        }
