# 记忆存储模块

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.interfaces import MemoryStorage


class InMemoryStorage(MemoryStorage):
    """内存存储实现"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = None):
        """初始化内存存储
        
        Args:
            max_size: 最大存储条目数
            ttl_seconds: 数据过期时间（秒），None 表示不过期
        """
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
    
    def store(self, key: str, value: Any) -> bool:
        """存储数据"""
        try:
            # 检查存储容量
            if len(self._storage) >= self._max_size and key not in self._storage:
                self._evict_oldest()
            
            # 存储数据
            self._storage[key] = {"value": value, "metadata": {}}
            self._timestamps[key] = datetime.utcnow()
            
            return True
        except Exception as e:
            print(f"Error storing data: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """检索数据"""
        # 检查过期
        if self._is_expired(key):
            self.delete(key)
            return None
        
        entry = self._storage.get(key)
        if entry:
            return entry["value"]
        return None
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        try:
            self._storage.pop(key, None)
            self._timestamps.pop(key, None)
            return True
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def search(self, query: str) -> List[Any]:
        """搜索数据"""
        results = []
        
        for key, entry in self._storage.items():
            # 跳过过期数据
            if self._is_expired(key):
                continue
            
            value = entry["value"]
            
            # 简单的字符串匹配搜索
            if self._matches_query(value, query):
                results.append({
                    "key": key,
                    "value": value,
                    "metadata": entry["metadata"]
                })
        
        return results
    
    def store_with_metadata(self, key: str, value: Any, 
                           metadata: Dict[str, Any]) -> bool:
        """存储数据并附加元数据"""
        try:
            if len(self._storage) >= self._max_size and key not in self._storage:
                self._evict_oldest()
            
            self._storage[key] = {
                "value": value,
                "metadata": metadata
            }
            self._timestamps[key] = datetime.utcnow()
            
            return True
        except Exception as e:
            print(f"Error storing data with metadata: {e}")
            return False
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """获取元数据"""
        entry = self._storage.get(key)
        if entry:
            return entry["metadata"]
        return None
    
    def clear(self) -> None:
        """清空所有数据"""
        self._storage.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """获取存储大小"""
        return len(self._storage)
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return list(self._storage.keys())
    
    def _is_expired(self, key: str) -> bool:
        """检查数据是否过期"""
        if self._ttl_seconds is None:
            return False
        
        if key not in self._timestamps:
            return True
        
        timestamp = self._timestamps[key]
        elapsed = datetime.utcnow() - timestamp
        
        return elapsed > timedelta(seconds=self._ttl_seconds)
    
    def _evict_oldest(self) -> None:
        """移除最旧的数据"""
        if not self._timestamps:
            return
        
        # 找到最旧的键
        oldest_key = min(self._timestamps.keys(), 
                       key=lambda k: self._timestamps[k])
        self.delete(oldest_key)
    
    def _matches_query(self, value: Any, query: str) -> bool:
        """检查值是否匹配查询"""
        query_lower = query.lower()
        
        # 字符串匹配
        if isinstance(value, str):
            return query_lower in value.lower()
        
        # 字典匹配
        elif isinstance(value, dict):
            for v in value.values():
                if isinstance(v, str) and query_lower in v.lower():
                    return True
            return False
        
        # 列表匹配
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and query_lower in item.lower():
                    return True
            return False
        
        return False
