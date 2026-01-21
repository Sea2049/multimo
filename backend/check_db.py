import sqlite3
import json

conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# 查看 storage 表结构
cursor.execute("PRAGMA table_info(storage)")
columns = [col[1] for col in cursor.fetchall()]
print("\nStorage table columns:", columns)

# 查找所有 report 相关记录
cursor.execute("SELECT key FROM storage WHERE key LIKE '%report%'")
rows = cursor.fetchall()
print(f"\nFound {len(rows)} report-related keys:")
for row in rows:
    print(f"  - {row[0]}")

# 查找所有 project 相关记录
cursor.execute("SELECT key FROM storage WHERE key LIKE '%project%'")
rows = cursor.fetchall()
print(f"\nFound {len(rows)} project-related keys:")
for row in rows:
    print(f"  - {row[0]}")

# 查找所有 simulation 相关记录
cursor.execute("SELECT key FROM storage WHERE key LIKE '%simulation%'")
rows = cursor.fetchall()
print(f"\nFound {len(rows)} simulation-related keys:")
for row in rows:
    print(f"  - {row[0]}")

conn.close()
