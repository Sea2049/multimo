"""
API 认证模块

提供 API Key 认证和请求签名验证功能，保护后端 API 免受未授权访问。
"""

import hashlib
import hmac
import time
import secrets
from functools import wraps
from typing import Optional, Dict, Any, Callable
from flask import request, jsonify, current_app, g

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """认证错误异常"""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def generate_api_key(length: int = 32) -> str:
    """
    生成安全的 API Key

    Args:
        length: 密钥长度（字节）

    Returns:
        生成的 API Key
    """
    return secrets.token_hex(length)


def hash_api_key(api_key: str) -> str:
    """
    对 API Key 进行哈希处理（用于存储）

    Args:
        api_key: 原始 API Key

    Returns:
        哈希后的密钥
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    验证 API Key 是否匹配

    Args:
        api_key: 待验证的 API Key
        hashed_key: 存储的哈希密钥

    Returns:
        是否匹配
    """
    return hmac.compare_digest(hash_api_key(api_key), hashed_key)


def generate_signature(
    method: str,
    path: str,
    timestamp: str,
    body: str,
    secret: str
) -> str:
    """
    生成请求签名

    Args:
        method: HTTP 方法
        path: 请求路径
        timestamp: 时间戳
        body: 请求体
        secret: 签名密钥

    Returns:
        生成的签名
    """
    message = f"{method}\n{path}\n{timestamp}\n{body}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_signature(
    method: str,
    path: str,
    timestamp: str,
    body: str,
    signature: str,
    secret: str,
    max_age: int = 300
) -> bool:
    """
    验证请求签名

    Args:
        method: HTTP 方法
        path: 请求路径
        timestamp: 时间戳
        body: 请求体
        signature: 待验证的签名
        secret: 签名密钥
        max_age: 签名最大有效期（秒）

    Returns:
        签名是否有效
    """
    try:
        request_time = int(timestamp)
        current_time = int(time.time())

        if abs(current_time - request_time) > max_age:
            logger.warning(f"签名已过期: timestamp={timestamp}, current={current_time}")
            return False
    except (ValueError, TypeError):
        logger.warning(f"无效的时间戳格式: {timestamp}")
        return False

    expected_signature = generate_signature(method, path, timestamp, body, secret)

    return hmac.compare_digest(signature, expected_signature)


class APIKeyManager:
    """API Key 管理器"""

    def __init__(self):
        """初始化 API Key 管理器"""
        self._api_keys: Dict[str, Dict[str, Any]] = {}

    def add_api_key(
        self,
        key_id: str,
        hashed_key: str,
        name: str = "",
        permissions: list = None,
        rate_limit: str = "100/hour"
    ) -> None:
        """
        添加 API Key

        Args:
            key_id: Key 标识符
            hashed_key: 哈希后的密钥
            name: Key 名称
            permissions: 权限列表
            rate_limit: 限流策略
        """
        self._api_keys[key_id] = {
            "hashed_key": hashed_key,
            "name": name,
            "permissions": permissions or [],
            "rate_limit": rate_limit,
            "created_at": time.time(),
            "last_used": None,
            "active": True
        }
        logger.info(f"添加 API Key: key_id={key_id}, name={name}")

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        验证 API Key

        Args:
            api_key: 原始 API Key

        Returns:
            Key 信息（无效返回 None）
        """
        hashed = hash_api_key(api_key)

        for key_id, key_info in self._api_keys.items():
            if key_info["active"] and hmac.compare_digest(hashed, key_info["hashed_key"]):
                key_info["last_used"] = time.time()
                return {
                    "key_id": key_id,
                    **key_info
                }

        return None

    def revoke_api_key(self, key_id: str) -> bool:
        """
        撤销 API Key

        Args:
            key_id: Key 标识符

        Returns:
            是否成功撤销
        """
        if key_id in self._api_keys:
            self._api_keys[key_id]["active"] = False
            logger.info(f"撤销 API Key: key_id={key_id}")
            return True
        return False

    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 Key 信息

        Args:
            key_id: Key 标识符

        Returns:
            Key 信息
        """
        if key_id in self._api_keys:
            return {
                "key_id": key_id,
                **self._api_keys[key_id]
            }
        return None


def get_api_key_manager() -> APIKeyManager:
    """
    获取全局 API Key 管理器实例

    Returns:
        API Key 管理器实例
    """
    if not hasattr(current_app, "_api_key_manager"):
        current_app._api_key_manager = APIKeyManager()
    return current_app._api_key_manager


def require_api_key(
    permissions: list = None,
    signature_required: bool = False
) -> Callable:
    """
    API Key 认证装饰器

    Args:
        permissions: 需要的权限列表
        signature_required: 是否需要请求签名

    Returns:
        装饰器函数
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.config_new import get_config
            config = get_config()

            if not config.API_KEY_ENABLED:
                return f(*args, **kwargs)

            api_key_header = config.API_KEY_HEADER
            api_key = request.headers.get(api_key_header)

            if not api_key:
                logger.warning(f"缺少 API Key: path={request.path}")
                return jsonify({
                    "success": False,
                    "error": "缺少 API Key",
                    "error_code": "MISSING_API_KEY"
                }), 401

            manager = get_api_key_manager()
            key_info = manager.validate_api_key(api_key)

            if not key_info:
                logger.warning(f"无效的 API Key: path={request.path}")
                return jsonify({
                    "success": False,
                    "error": "无效的 API Key",
                    "error_code": "INVALID_API_KEY"
                }), 401

            if not key_info["active"]:
                logger.warning(f"API Key 已禁用: key_id={key_info['key_id']}")
                return jsonify({
                    "success": False,
                    "error": "API Key 已禁用",
                    "error_code": "DISABLED_API_KEY"
                }), 401

            if permissions:
                key_permissions = key_info.get("permissions", [])
                if not any(p in key_permissions for p in permissions):
                    logger.warning(
                        f"权限不足: key_id={key_info['key_id']}, "
                        f"required={permissions}, has={key_permissions}"
                    )
                    return jsonify({
                        "success": False,
                        "error": "权限不足",
                        "error_code": "INSUFFICIENT_PERMISSIONS"
                    }), 403

            if signature_required and config.SIGNATURE_ENABLED:
                signature = request.headers.get("X-Signature")
                timestamp = request.headers.get("X-Timestamp")

                if not signature or not timestamp:
                    logger.warning(f"缺少签名: path={request.path}")
                    return jsonify({
                        "success": False,
                        "error": "缺少请求签名",
                        "error_code": "MISSING_SIGNATURE"
                    }), 401

                body = request.get_data(as_text=True) or ""
                is_valid = verify_signature(
                    request.method,
                    request.path,
                    timestamp,
                    body,
                    signature,
                    config.SIGNATURE_SECRET
                )

                if not is_valid:
                    logger.warning(f"签名验证失败: path={request.path}")
                    return jsonify({
                        "success": False,
                        "error": "签名验证失败",
                        "error_code": "INVALID_SIGNATURE"
                    }), 401

            g.api_key_info = {
                "key_id": key_info["key_id"],
                "name": key_info.get("name", ""),
                "permissions": key_info.get("permissions", [])
            }

            logger.debug(f"API Key 认证成功: key_id={key_info['key_id']}")

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def init_auth(app) -> None:
    """
    初始化认证模块

    Args:
        app: Flask 应用实例
    """
    from app.config_new import get_config
    config = get_config()

    if not config.API_KEY_ENABLED:
        logger.info("API Key 认证未启用")
        return

    manager = get_api_key_manager()

    if config.API_KEYS:
        for key_config in config.API_KEYS:
            key_id = key_config.get("id", f"key_{len(manager._api_keys) + 1}")
            raw_key = key_config.get("key")
            if raw_key:
                hashed = hash_api_key(raw_key)
                manager.add_api_key(
                    key_id=key_id,
                    hashed_key=hashed,
                    name=key_config.get("name", ""),
                    permissions=key_config.get("permissions", []),
                    rate_limit=key_config.get("rate_limit", "100/hour")
                )
                logger.info(f"加载 API Key: key_id={key_id}, name={key_config.get('name', '')}")

    logger.info(f"认证模块初始化完成，共加载 {len(manager._api_keys)} 个 API Key")
