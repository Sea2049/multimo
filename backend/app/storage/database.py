# 数据库存储模块

import sqlite3
import json
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from app.core.interfaces import MemoryStorage


class DatabaseStorage(MemoryStorage):
    """数据库存储基类"""
    
    def __init__(self, database_url: str):
        """初始化数据库存储
        
        Args:
            database_url: 数据库连接 URL
        """
        self.database_url = database_url
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = self._connect()
        try:
            yield conn
        finally:
            conn.close()
    
    def _connect(self):
        """建立数据库连接"""
        raise NotImplementedError
    
    def _initialize_tables(self, conn):
        """初始化数据库表"""
        raise NotImplementedError


class SQLiteStorage(DatabaseStorage):
    """SQLite 存储实现"""
    
    def __init__(self, database_path: str = "storage.db"):
        """初始化 SQLite 存储
        
        Args:
            database_path: 数据库文件路径
        """
        super().__init__(database_path)
        self.database_path = database_path
        self._initialize()
    
    def _connect(self):
        """建立 SQLite 连接"""
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize(self):
        """初始化数据库"""
        with self.get_connection() as conn:
            self._initialize_tables(conn)
    
    def _initialize_tables(self, conn):
        """初始化数据库表"""
        # 创建存储表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON storage(created_at)
        """)
        
        conn.commit()
    
    def store(self, key: str, value: Any) -> bool:
        """存储数据"""
        try:
            value_json = json.dumps(value, ensure_ascii=False)
            
            with self.get_connection() as conn:
                # 检查是否已存在
                cursor = conn.execute(
                    "SELECT key FROM storage WHERE key = ?",
                    (key,)
                )
                exists = cursor.fetchone() is not None
                
                if exists:
                    # 更新
                    conn.execute("""
                        UPDATE storage 
                        SET value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE key = ?
                    """, (value_json, key))
                else:
                    # 插入
                    conn.execute("""
                        INSERT INTO storage (key, value)
                        VALUES (?, ?)
                    """, (key, value_json))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error storing data to database: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """检索数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM storage WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row["value"])
                return None
        except Exception as e:
            print(f"Error retrieving data from database: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "DELETE FROM storage WHERE key = ?",
                    (key,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting data from database: {e}")
            return False
    
    def search(self, query: str) -> List[Any]:
        """搜索数据"""
        try:
            results = []
            query_pattern = f"%{query}%"
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT key, value FROM storage 
                    WHERE value LIKE ?
                """, (query_pattern,))
                
                for row in cursor.fetchall():
                    results.append({
                        "key": row["key"],
                        "value": json.loads(row["value"])
                    })
            
            return results
        except Exception as e:
            print(f"Error searching data in database: {e}")
            return []
    
    def keys(self) -> List[str]:
        """获取所有键"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT key FROM storage")
                return [row["key"] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting keys from database: {e}")
            return []
    
    def size(self) -> int:
        """获取存储大小"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM storage")
                return cursor.fetchone()["count"]
        except Exception as e:
            print(f"Error getting size from database: {e}")
            return 0
    
    def clear(self) -> None:
        """清空所有数据"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM storage")
                conn.commit()
        except Exception as e:
            print(f"Error clearing database: {e}")
    
    def store_with_metadata(self, key: str, value: Any, 
                           metadata: Dict[str, Any]) -> bool:
        """存储数据并附加元数据"""
        try:
            value_json = json.dumps(value, ensure_ascii=False)
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO storage (key, value, metadata)
                    VALUES (?, ?, ?)
                """, (key, value_json, metadata_json))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error storing data with metadata: {e}")
            return False
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """获取元数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT metadata FROM storage WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row and row["metadata"]:
                    return json.loads(row["metadata"])
                return None
        except Exception as e:
            print(f"Error getting metadata from database: {e}")
            return None
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的数据"""
        try:
            results = []
            
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT key, value, created_at FROM storage
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                for row in cursor.fetchall():
                    results.append({
                        "key": row["key"],
                        "value": json.loads(row["value"]),
                        "created_at": row["created_at"]
                    })
            
            return results
        except Exception as e:
            print(f"Error getting recent data from database: {e}")
            return []
