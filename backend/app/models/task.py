"""
任务状态管理
用于跟踪长时间运行的任务（如图谱构建）
"""

import uuid
import threading
import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from app.storage.database import SQLiteStorage
from app.config_new import get_config


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待中
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    progress: int = 0              # 总进度百分比 0-100
    message: str = ""              # 状态消息
    result: Optional[Dict] = None  # 任务结果
    error: Optional[str] = None    # 错误信息
    metadata: Dict = field(default_factory=dict)  # 额外元数据
    progress_detail: Dict = field(default_factory=dict)  # 详细进度信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress": self.progress,
            "message": self.message,
            "progress_detail": self.progress_detail,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }


class TaskManager:
    """
    任务管理器
    线程安全的任务状态管理，支持数据库持久化
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化任务管理器"""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
                
            config = get_config()
            self._storage = SQLiteStorage(config.TASKS_DATABASE_PATH)
            self._task_lock = threading.Lock()
            self._cache: Dict[str, Task] = {}
            self._initialized = True
            
            self._load_tasks_from_db()
    
    def _load_tasks_from_db(self):
        """从数据库加载任务到内存缓存"""
        try:
            task_dicts = self._storage.list_tasks(limit=1000)
            with self._task_lock:
                for task_dict in task_dicts:
                    task = self._dict_to_task(task_dict)
                    if task:
                        self._cache[task.task_id] = task
        except Exception as e:
            print(f"Error loading tasks from database: {e}")
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """将 Task 对象转换为字典"""
        result = asdict(task)
        result["status"] = task.status.value
        if task.result:
            result["result"] = json.dumps(task.result, ensure_ascii=False, default=str)
        if task.metadata:
            result["metadata"] = json.dumps(task.metadata, ensure_ascii=False, default=str)
        if task.progress_detail:
            result["progress_detail"] = json.dumps(task.progress_detail, ensure_ascii=False, default=str)
        return result
    
    def _dict_to_task(self, task_dict: Dict[str, Any]) -> Optional[Task]:
        """将字典转换为 Task 对象"""
        try:
            task_dict = task_dict.copy()
            
            if isinstance(task_dict.get("result"), str):
                try:
                    task_dict["result"] = json.loads(task_dict["result"])
                except:
                    task_dict["result"] = None
            
            if isinstance(task_dict.get("metadata"), str):
                try:
                    task_dict["metadata"] = json.loads(task_dict["metadata"])
                except:
                    task_dict["metadata"] = {}
            
            if isinstance(task_dict.get("progress_detail"), str):
                try:
                    task_dict["progress_detail"] = json.loads(task_dict["progress_detail"])
                except:
                    task_dict["progress_detail"] = {}
            
            if isinstance(task_dict.get("status"), str):
                task_dict["status"] = TaskStatus(task_dict["status"])
            
            return Task(
                task_id=task_dict["task_id"],
                task_type=task_dict["task_type"],
                status=task_dict["status"],
                created_at=datetime.fromisoformat(task_dict["created_at"]) if isinstance(task_dict["created_at"], str) else task_dict["created_at"],
                updated_at=datetime.fromisoformat(task_dict["updated_at"]) if isinstance(task_dict["updated_at"], str) else task_dict["updated_at"],
                progress=task_dict.get("progress", 0),
                message=task_dict.get("message", ""),
                result=task_dict.get("result"),
                error=task_dict.get("error"),
                metadata=task_dict.get("metadata", {}),
                progress_detail=task_dict.get("progress_detail", {})
            )
        except Exception as e:
            print(f"Error converting dict to Task: {e}")
            return None
    
    def create_task(self, task_type: str, metadata: Optional[Dict] = None) -> str:
        """
        创建新任务
        
        Args:
            task_type: 任务类型
            metadata: 额外元数据
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        task_dict = self._task_to_dict(task)
        
        with self._task_lock:
            self._cache[task_id] = task
            self._storage.store_task(task_dict)
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        with self._task_lock:
            if task_id in self._cache:
                return self._cache[task_id]
            
            task_dict = self._storage.retrieve_task(task_id)
            if task_dict:
                task = self._dict_to_task(task_dict)
                if task:
                    self._cache[task_id] = task
                return task
            
            return None
    
    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        progress_detail: Optional[Dict] = None
    ):
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度
            message: 消息
            result: 结果
            error: 错误信息
            progress_detail: 详细进度信息
        """
        with self._task_lock:
            task = self._cache.get(task_id)
            if task:
                task.updated_at = datetime.now()
                if status is not None:
                    task.status = status
                if progress is not None:
                    task.progress = progress
                if message is not None:
                    task.message = message
                if result is not None:
                    task.result = result
                if error is not None:
                    task.error = error
                if progress_detail is not None:
                    task.progress_detail = progress_detail
                
                task_dict = self._task_to_dict(task)
                # 移除 task_id，避免重复传递参数
                task_dict.pop('task_id', None)
                self._storage.update_task(task_id, **task_dict)
    
    def complete_task(self, task_id: str, result: Dict):
        """标记任务完成"""
        self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            progress=100,
            message="任务完成",
            result=result
        )
    
    def fail_task(self, task_id: str, error: str):
        """标记任务失败"""
        self.update_task(
            task_id,
            status=TaskStatus.FAILED,
            message="任务失败",
            error=error
        )
    
    def list_tasks(self, task_type: Optional[str] = None) -> list:
        """列出任务"""
        with self._task_lock:
            if task_type:
                filtered_tasks = [
                    t for t in self._cache.values() 
                    if t.task_type == task_type
                ]
            else:
                filtered_tasks = list(self._cache.values())
            
            return [t.to_dict() for t in sorted(
                filtered_tasks, 
                key=lambda x: x.created_at, 
                reverse=True
            )]
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        with self._task_lock:
            old_ids = [
                tid for tid, task in self._cache.items()
                if task.created_at < cutoff and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            ]
            for tid in old_ids:
                del self._cache[tid]
                self._storage.delete_task(tid)
    
    def recover_tasks(self):
        """恢复未完成的任务（服务重启后调用）"""
        with self._task_lock:
            for task in list(self._cache.values()):
                if task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
                    task.status = TaskStatus.FAILED
                    task.error = "任务因服务重启而中断"
                    task.updated_at = datetime.now()
                    
                    task_dict = self._task_to_dict(task)
                    self._storage.update_task(
                        task.task_id,
                        status=task.status.value,
                        error=task.error,
                        updated_at=task.updated_at.isoformat()
                    )

