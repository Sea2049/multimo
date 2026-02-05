#!/usr/bin/env python3
"""
用户数据隔离迁移脚本

执行顺序：
1. 确保 projects 表与 tasks.user_id 列存在（与 app 启动时一致）
2. 回填历史项目：将 uploads/projects 下已有项目写入 projects 表，归属到默认用户
3. 回填历史任务：将 tasks 表中 user_id 为 NULL 的按 metadata.project_id 解析归属，否则归默认用户

用法：
    cd backend && python -m scripts.migrate_user_data_isolation [--default-user-id 1]
"""

import argparse
import json
import os
import sys

# 将 backend 加入 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config_new import get_config
from app.storage.database import SQLiteStorage


def ensure_schema(storage: SQLiteStorage) -> None:
    """确保 projects 表与 tasks.user_id 存在（与 database._initialize_tables 一致）"""
    with storage.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                user_id INTEGER,
                name TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        try:
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row[1] for row in cursor.fetchall()]
            if "user_id" not in columns:
                conn.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER")
        except Exception:
            pass
        conn.commit()


def backfill_projects(storage: SQLiteStorage, projects_dir: str, default_user_id: int) -> int:
    """将文件系统中的项目写入 projects 表，归属 default_user_id。返回写入条数。"""
    count = 0
    if not os.path.isdir(projects_dir):
        return count
    for project_id in os.listdir(projects_dir):
        project_dir = os.path.join(projects_dir, project_id)
        if not os.path.isdir(project_dir):
            continue
        meta_path = os.path.join(project_dir, "project.json")
        if not os.path.exists(meta_path):
            continue
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        name = data.get("name", "Unnamed Project")
        status = data.get("status", "created")
        created_at = data.get("created_at") or ""
        updated_at = data.get("updated_at") or ""
        storage.insert_project_meta(
            project_id=project_id,
            user_id=default_user_id,
            name=name,
            status=status,
            created_at=created_at or None,
            updated_at=updated_at or None,
        )
        count += 1
    return count


def backfill_tasks(storage: SQLiteStorage, default_user_id: int) -> int:
    """将 tasks 表中 user_id 为 NULL 的按 metadata.project_id 解析归属，否则设为 default_user_id。返回更新条数。"""
    updated = 0
    task_dicts = storage.list_tasks(limit=5000)
    project_user_cache = {}
    with storage.get_connection() as conn:
        for row in task_dicts:
            task_id = row.get("task_id")
            if task_id is None:
                continue
            if row.get("user_id") is not None:
                continue
            user_id = default_user_id
            meta = row.get("metadata")
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = {}
            if isinstance(meta, dict) and meta.get("project_id"):
                pid = meta["project_id"]
                if pid not in project_user_cache:
                    project_user_cache[pid] = storage.get_project_user_id(pid)
                if project_user_cache[pid] is not None:
                    user_id = project_user_cache[pid]
            conn.execute("UPDATE tasks SET user_id = ? WHERE task_id = ?", (user_id, task_id))
            updated += 1
        conn.commit()
    return updated


def main():
    parser = argparse.ArgumentParser(description="用户数据隔离迁移")
    parser.add_argument(
        "--default-user-id",
        type=int,
        default=1,
        help="历史项目/任务归属的默认用户 ID（建议为管理员），默认 1",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅打印将执行的操作，不写入")
    args = parser.parse_args()

    config = get_config()
    db_path = config.TASKS_DATABASE_PATH
    projects_dir = os.path.join(config.UPLOAD_FOLDER, "projects")

    print(f"数据库: {db_path}")
    print(f"项目目录: {projects_dir}")
    print(f"默认归属用户 ID: {args.default_user_id}")
    if args.dry_run:
        print("（dry-run，不写入）")
        return

    storage = SQLiteStorage(db_path)
    ensure_schema(storage)
    print("Schema 已就绪")

    n_projects = backfill_projects(storage, projects_dir, args.default_user_id)
    print(f"回填项目: {n_projects} 条")

    n_tasks = backfill_tasks(storage, args.default_user_id)
    print(f"回填任务: {n_tasks} 条")

    print("迁移完成。")


if __name__ == "__main__":
    main()
