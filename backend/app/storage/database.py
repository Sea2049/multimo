# 数据库存储模块

import sqlite3
import json
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from datetime import datetime
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON storage(created_at)
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                progress INTEGER DEFAULT 0,
                message TEXT,
                result TEXT,
                error TEXT,
                metadata TEXT,
                progress_detail TEXT
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_status 
            ON tasks(status)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_type 
            ON tasks(task_type)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_created 
            ON tasks(created_at)
        """)
        
        # ============= 用户认证相关表 =============
        
        # 用户表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email 
            ON users(email)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        """)
        
        # 邀请码表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invitation_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                created_by INTEGER,
                max_uses INTEGER DEFAULT 1,
                used_count INTEGER DEFAULT 0,
                expires_at TIMESTAMP,
                is_active INTEGER NOT NULL DEFAULT 1,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invitation_codes_code 
            ON invitation_codes(code)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invitation_codes_active 
            ON invitation_codes(is_active)
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
    
    def store_task(self, task_data: Dict[str, Any]) -> bool:
        """存储任务"""
        try:
            def serialize_value(value):
                if isinstance(value, dict):
                    return json.dumps(value, ensure_ascii=False, default=str)
                return value
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO tasks 
                    (task_id, task_type, status, created_at, updated_at, 
                     progress, message, result, error, metadata, progress_detail)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_data.get("task_id"),
                    task_data.get("task_type"),
                    serialize_value(task_data.get("status")),
                    task_data.get("created_at"),
                    task_data.get("updated_at"),
                    task_data.get("progress", 0),
                    task_data.get("message"),
                    serialize_value(task_data.get("result")),
                    task_data.get("error"),
                    serialize_value(task_data.get("metadata")),
                    serialize_value(task_data.get("progress_detail"))
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error storing task to database: {e}")
            return False
    
    def retrieve_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """检索任务"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE task_id = ?",
                    (task_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Error retrieving task from database: {e}")
            return None
    
    def list_tasks(self, task_type: Optional[str] = None, 
                   status: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """列出任务"""
        try:
            results = []
            
            with self.get_connection() as conn:
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []
                
                if task_type:
                    query += " AND task_type = ?"
                    params.append(task_type)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                
                for row in cursor.fetchall():
                    results.append(dict(row))
            
            return results
        except Exception as e:
            print(f"Error listing tasks from database: {e}")
            return []
    
    # 允许更新的任务字段白名单（防止 SQL 注入）
    ALLOWED_TASK_FIELDS = {
        'status', 'progress', 'message', 'result', 
        'error', 'metadata', 'progress_detail'
    }
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段，必须在白名单中
            
        Returns:
            更新是否成功
            
        Raises:
            ValueError: 如果字段名不在白名单中
        """
        try:
            if not kwargs:
                return True
            
            # 验证字段名是否在白名单中（防止 SQL 注入）
            for key in kwargs.keys():
                if key not in self.ALLOWED_TASK_FIELDS:
                    raise ValueError(f"Invalid field name: {key}. Allowed fields: {self.ALLOWED_TASK_FIELDS}")
            
            with self.get_connection() as conn:
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    set_clauses.append(f"{key} = ?")
                    if isinstance(value, dict):
                        values.append(json.dumps(value, ensure_ascii=False, default=str))
                    else:
                        values.append(value)
                
                values.append(task_id)
                
                query = f"""
                    UPDATE tasks 
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """
                
                conn.execute(query, values)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating task in database: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "DELETE FROM tasks WHERE task_id = ?",
                    (task_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting task from database: {e}")
            return False
    
    def count_tasks(self, status: Optional[str] = None) -> int:
        """统计任务数量"""
        try:
            with self.get_connection() as conn:
                if status:
                    cursor = conn.execute(
                        "SELECT COUNT(*) as count FROM tasks WHERE status = ?",
                        (status,)
                    )
                else:
                    cursor = conn.execute("SELECT COUNT(*) as count FROM tasks")
                
                return cursor.fetchone()["count"]
        except Exception as e:
            print(f"Error counting tasks in database: {e}")
            return 0
    
    def cleanup_tasks(self, older_than_hours: int = 24) -> int:
        """清理旧任务（只清理已完成和失败的）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM tasks 
                    WHERE status IN ('completed', 'failed')
                    AND created_at < datetime('now', ?)
                """, (f"-{older_than_hours} hours",))
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"Error cleaning up tasks in database: {e}")
            return 0
    
    # ============= 用户管理方法 =============
    
    def create_user(self, username: str, email: str, password_hash: str, 
                   role: str = "user") -> Optional[int]:
        """创建用户
        
        Args:
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            role: 角色（admin/user）
            
        Returns:
            用户 ID，失败返回 None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (username, email, password_hash, role))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 获取用户"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        allowed_fields = {'username', 'email', 'password_hash', 'role', 'is_active'}
        try:
            if not kwargs:
                return True
            
            for key in kwargs.keys():
                if key not in allowed_fields:
                    raise ValueError(f"Invalid field: {key}")
            
            with self.get_connection() as conn:
                set_clauses = [f"{key} = ?" for key in kwargs.keys()]
                values = list(kwargs.values())
                values.append(user_id)
                
                conn.execute(f"""
                    UPDATE users 
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, values)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def count_users(self) -> int:
        """统计用户数量"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM users")
                return cursor.fetchone()["count"]
        except Exception as e:
            print(f"Error counting users: {e}")
            return 0
    
    # ============= 邀请码管理方法 =============
    
    def create_invitation_code(self, code: str, created_by: Optional[int] = None,
                               max_uses: int = 1, expires_at: Optional[str] = None,
                               note: Optional[str] = None) -> Optional[int]:
        """创建邀请码
        
        Args:
            code: 邀请码
            created_by: 创建者用户 ID
            max_uses: 最大使用次数
            expires_at: 过期时间
            note: 备注
            
        Returns:
            邀请码 ID，失败返回 None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO invitation_codes 
                    (code, created_by, max_uses, expires_at, note)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, created_by, max_uses, expires_at, note))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating invitation code: {e}")
            return None
    
    def get_invitation_code(self, code: str) -> Optional[Dict[str, Any]]:
        """根据邀请码获取记录"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM invitation_codes WHERE code = ?",
                    (code,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting invitation code: {e}")
            return None
    
    def get_invitation_code_by_id(self, code_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 获取邀请码"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM invitation_codes WHERE id = ?",
                    (code_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting invitation code by id: {e}")
            return None
    
    def list_invitation_codes(self, include_inactive: bool = False,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """列出邀请码"""
        try:
            with self.get_connection() as conn:
                if include_inactive:
                    cursor = conn.execute("""
                        SELECT * FROM invitation_codes
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (limit,))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM invitation_codes
                        WHERE is_active = 1
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error listing invitation codes: {e}")
            return []
    
    def increment_invitation_code_usage(self, code: str) -> bool:
        """增加邀请码使用次数"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE invitation_codes 
                    SET used_count = used_count + 1
                    WHERE code = ?
                """, (code,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error incrementing invitation code usage: {e}")
            return False
    
    def update_invitation_code(self, code_id: int, **kwargs) -> bool:
        """更新邀请码"""
        allowed_fields = {'max_uses', 'expires_at', 'is_active', 'note'}
        try:
            if not kwargs:
                return True
            
            for key in kwargs.keys():
                if key not in allowed_fields:
                    raise ValueError(f"Invalid field: {key}")
            
            with self.get_connection() as conn:
                set_clauses = [f"{key} = ?" for key in kwargs.keys()]
                values = list(kwargs.values())
                values.append(code_id)
                
                conn.execute(f"""
                    UPDATE invitation_codes 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                """, values)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating invitation code: {e}")
            return False
    
    def delete_invitation_code(self, code_id: int) -> bool:
        """删除邀请码"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "DELETE FROM invitation_codes WHERE id = ?",
                    (code_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting invitation code: {e}")
            return False
    
    def is_invitation_code_valid(self, code: str) -> tuple[bool, str]:
        """检查邀请码是否有效
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            invitation = self.get_invitation_code(code)
            
            if not invitation:
                return False, "邀请码不存在"
            
            if not invitation["is_active"]:
                return False, "邀请码已禁用"
            
            if invitation["used_count"] >= invitation["max_uses"]:
                return False, "邀请码已达到使用次数上限"
            
            if invitation["expires_at"]:
                from datetime import datetime
                expires_at = datetime.fromisoformat(invitation["expires_at"].replace("Z", "+00:00"))
                if datetime.now(expires_at.tzinfo) > expires_at:
                    return False, "邀请码已过期"
            
            return True, ""
        except Exception as e:
            print(f"Error checking invitation code validity: {e}")
            return False, "验证邀请码时发生错误"