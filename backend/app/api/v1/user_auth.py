"""
用户认证 API

提供用户注册、登录、获取当前用户信息、刷新 Token 等功能。
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, g

from app.api import api_v1_bp, get_response, get_error_response, ErrorCode
from app.api.decorators import require_user_auth, validate_json_body
from app.config_new import get_config
from app.storage.database import SQLiteStorage
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def _verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def _generate_token(user_id: int, username: str, role: str) -> str:
    """生成 JWT Token"""
    import jwt
    
    config = get_config()
    
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def _get_storage() -> SQLiteStorage:
    """获取数据库存储实例"""
    config = get_config()
    return SQLiteStorage(config.TASKS_DATABASE_PATH)


@api_v1_bp.route("/auth/register", methods=["POST"])
@validate_json_body(required=["username", "email", "password", "invitation_code"], check_sql_injection=False)
def register():
    """用户注册
    
    需要有效的邀请码才能注册。
    
    Request Body:
        {
            "username": "用户名",
            "email": "邮箱",
            "password": "密码",
            "invitation_code": "邀请码"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...},
                "token": "JWT Token"
            }
        }
    """
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        invitation_code = data.get("invitation_code", "").strip().upper()
        
        # 验证输入
        if len(username) < 2 or len(username) > 50:
            return jsonify(get_error_response(
                error="用户名长度必须在 2-50 个字符之间",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        if len(password) < 6:
            return jsonify(get_error_response(
                error="密码长度至少 6 个字符",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify(get_error_response(
                error="邮箱格式不正确",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        storage = _get_storage()
        
        # 验证邀请码
        is_valid, error_msg = storage.is_invitation_code_valid(invitation_code)
        if not is_valid:
            logger.warning(f"注册失败 - 无效邀请码: code={invitation_code}, error={error_msg}")
            return jsonify(get_error_response(
                error=error_msg,
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        # 检查用户名是否已存在
        if storage.get_user_by_username(username):
            return jsonify(get_error_response(
                error="用户名已被使用",
                status_code=400,
                error_code=ErrorCode.CONFLICT
            )), 400
        
        # 检查邮箱是否已存在
        if storage.get_user_by_email(email):
            return jsonify(get_error_response(
                error="邮箱已被注册",
                status_code=400,
                error_code=ErrorCode.CONFLICT
            )), 400
        
        # 创建用户
        password_hash = _hash_password(password)
        user_id = storage.create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            role="user"
        )
        
        if not user_id:
            logger.error(f"创建用户失败: username={username}, email={email}")
            return jsonify(get_error_response(
                error="创建用户失败，请稍后重试",
                status_code=500,
                error_code=ErrorCode.INTERNAL_ERROR
            )), 500
        
        # 增加邀请码使用次数
        storage.increment_invitation_code_usage(invitation_code)
        
        # 生成 Token
        token = _generate_token(user_id, username, "user")
        
        logger.info(f"用户注册成功: user_id={user_id}, username={username}, invitation_code={invitation_code}")
        
        return jsonify(get_response({
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": "user"
            },
            "token": token
        }, message="注册成功")), 201
        
    except Exception as e:
        logger.error(f"注册异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="注册失败，请稍后重试",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/auth/login", methods=["POST"])
@validate_json_body(required=["email", "password"], check_sql_injection=False)
def login():
    """用户登录
    
    Request Body:
        {
            "email": "邮箱",
            "password": "密码"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...},
                "token": "JWT Token"
            }
        }
    """
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        
        storage = _get_storage()
        
        # 获取用户
        user = storage.get_user_by_email(email)
        
        if not user:
            logger.warning(f"登录失败 - 用户不存在: email={email}")
            return jsonify(get_error_response(
                error="邮箱或密码错误",
                status_code=401,
                error_code=ErrorCode.UNAUTHORIZED
            )), 401
        
        # 验证密码
        if not _verify_password(password, user["password_hash"]):
            logger.warning(f"登录失败 - 密码错误: email={email}")
            return jsonify(get_error_response(
                error="邮箱或密码错误",
                status_code=401,
                error_code=ErrorCode.UNAUTHORIZED
            )), 401
        
        # 检查账户状态
        if not user.get("is_active"):
            logger.warning(f"登录失败 - 账户已禁用: email={email}")
            return jsonify(get_error_response(
                error="账户已被禁用，请联系管理员",
                status_code=401,
                error_code=ErrorCode.UNAUTHORIZED
            )), 401
        
        # 生成 Token
        token = _generate_token(user["id"], user["username"], user["role"])
        
        logger.info(f"用户登录成功: user_id={user['id']}, username={user['username']}")
        
        return jsonify(get_response({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            },
            "token": token
        }, message="登录成功")), 200
        
    except Exception as e:
        logger.error(f"登录异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="登录失败，请稍后重试",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/auth/me", methods=["GET"])
@require_user_auth
def get_current_user():
    """获取当前用户信息
    
    需要 Bearer Token 认证。
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...}
            }
        }
    """
    try:
        user = g.current_user
        
        return jsonify(get_response({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
        })), 200
        
    except Exception as e:
        logger.error(f"获取当前用户异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="获取用户信息失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


@api_v1_bp.route("/auth/refresh", methods=["POST"])
@require_user_auth
def refresh_token():
    """刷新 Token
    
    使用当前有效的 Token 获取新的 Token。
    
    Response:
        {
            "success": true,
            "data": {
                "token": "新的 JWT Token"
            }
        }
    """
    try:
        user = g.current_user
        
        # 生成新 Token
        token = _generate_token(user["id"], user["username"], user["role"])
        
        logger.info(f"Token 刷新成功: user_id={user['id']}")
        
        return jsonify(get_response({
            "token": token
        }, message="Token 刷新成功")), 200
        
    except Exception as e:
        logger.error(f"刷新 Token 异常: {e}", exc_info=True)
        return jsonify(get_error_response(
            error="刷新 Token 失败",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500
