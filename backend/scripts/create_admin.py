#!/usr/bin/env python3
"""
管理员账户创建工具

用法:
    uv run python scripts/create_admin.py --username admin --email admin@example.com --password secret123

参数:
    --username: 用户名（必填）
    --email: 邮箱（必填）
    --password: 密码（必填，至少 6 个字符）
"""

import argparse
import sys
import os
import re

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config_new import get_config
from app.storage.database import SQLiteStorage


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_admin(username: str, email: str, password: str) -> bool:
    """创建管理员账户
    
    Args:
        username: 用户名
        email: 邮箱
        password: 密码
        
    Returns:
        是否创建成功
    """
    config = get_config()
    storage = SQLiteStorage(config.TASKS_DATABASE_PATH)
    
    # 检查用户名是否已存在
    if storage.get_user_by_username(username):
        print(f"[ERROR] 用户名 '{username}' 已存在")
        return False
    
    # 检查邮箱是否已存在
    if storage.get_user_by_email(email):
        print(f"[ERROR] 邮箱 '{email}' 已被注册")
        return False
    
    # 创建管理员用户
    password_hash = hash_password(password)
    user_id = storage.create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        role="admin"
    )
    
    if user_id:
        print(f"[SUCCESS] 管理员账户创建成功!")
        print(f"   用户 ID: {user_id}")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   角色: admin")
        return True
    else:
        print("[ERROR] 创建用户失败")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="创建管理员账户",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    uv run python scripts/create_admin.py --username admin --email admin@example.com --password secret123
    
注意:
    - 密码至少需要 6 个字符
    - 邮箱必须是有效的邮箱格式
    - 用户名和邮箱必须唯一
        """
    )
    
    parser.add_argument(
        "--username", "-u",
        required=True,
        help="管理员用户名"
    )
    parser.add_argument(
        "--email", "-e",
        required=True,
        help="管理员邮箱"
    )
    parser.add_argument(
        "--password", "-p",
        required=True,
        help="管理员密码（至少 6 个字符）"
    )
    
    args = parser.parse_args()
    
    # 验证输入
    username = args.username.strip()
    email = args.email.strip().lower()
    password = args.password
    
    if len(username) < 2 or len(username) > 50:
        print("[ERROR] 用户名长度必须在 2-50 个字符之间")
        sys.exit(1)
    
    if not validate_email(email):
        print("[ERROR] 邮箱格式不正确")
        sys.exit(1)
    
    if len(password) < 6:
        print("[ERROR] 密码长度至少 6 个字符")
        sys.exit(1)
    
    # 创建管理员
    print(f"\n正在创建管理员账户...")
    print(f"数据库路径: {get_config().TASKS_DATABASE_PATH}\n")
    
    success = create_admin(username, email, password)
    
    if success:
        print("\n[TIP] 现在可以使用以下命令测试登录:")
        print(f'   curl -X POST http://localhost:5001/api/v1/auth/login \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"email":"{email}","password":"{password}"}}\'')
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
