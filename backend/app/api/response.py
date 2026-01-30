"""
API 响应构建模块

提供统一的 API 响应格式构建函数，确保所有 API 返回一致的结构。

响应格式:
    成功响应:
    {
        "success": True,
        "data": {...},
        "message": "操作成功",
        "count": 10  # 可选，列表数据时使用
    }
    
    错误响应:
    {
        "success": False,
        "error": "错误描述",
        "error_code": "ERROR_CODE",
        "recovery_suggestion": "恢复建议"
    }

使用示例:
    from app.api.response import success, error, paginated
    
    @app.route('/items')
    def get_items():
        items = [...]
        return success(items, message="获取成功", count=len(items))
    
    @app.route('/item/<id>')
    def get_item(id):
        item = find_item(id)
        if not item:
            return not_found(f"项目不存在: {id}")
        return success(item)
"""

from typing import Any, Optional, Dict, List
from flask import jsonify, Response

from . import ErrorCode, ErrorRecovery, get_config


def success(
    data: Any = None,
    message: str = "操作成功",
    count: int = None,
    status_code: int = 200,
    **extra
) -> tuple[Response, int]:
    """
    构建成功响应
    
    Args:
        data: 响应数据（任意类型）
        message: 成功消息
        count: 数据总数（用于列表响应）
        status_code: HTTP 状态码（默认 200）
        **extra: 额外字段
    
    Returns:
        (Response, status_code) 元组
    
    Example:
        return success({"id": "123", "name": "test"})
        return success(items, count=len(items))
        return success(None, message="删除成功")
    """
    response = {
        "success": True,
        "data": data,
        "message": message
    }
    
    if count is not None:
        response["count"] = count
    
    # 添加额外字段
    response.update(extra)
    
    return jsonify(response), status_code


def created(
    data: Any = None,
    message: str = "创建成功",
    **extra
) -> tuple[Response, int]:
    """
    构建创建成功响应 (201)
    
    Args:
        data: 创建的资源数据
        message: 成功消息
        **extra: 额外字段
    
    Returns:
        (Response, 201) 元组
    """
    return success(data, message=message, status_code=201, **extra)


def accepted(
    data: Any = None,
    message: str = "请求已接受，正在处理",
    task_id: str = None,
    **extra
) -> tuple[Response, int]:
    """
    构建异步任务接受响应 (202)
    
    Args:
        data: 响应数据
        message: 消息
        task_id: 异步任务 ID
        **extra: 额外字段
    
    Returns:
        (Response, 202) 元组
    """
    if task_id:
        extra["task_id"] = task_id
    return success(data, message=message, status_code=202, **extra)


def no_content() -> tuple[str, int]:
    """
    构建无内容响应 (204)
    
    Returns:
        ('', 204) 元组
    """
    return '', 204


def error(
    message: str,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    status_code: int = 400,
    recovery_suggestion: str = None,
    details: Any = None
) -> tuple[Response, int]:
    """
    构建错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码枚举
        status_code: HTTP 状态码
        recovery_suggestion: 恢复建议（不提供则使用默认值）
        details: 错误详情
    
    Returns:
        (Response, status_code) 元组
    
    Example:
        return error("参数无效", ErrorCode.INVALID_INPUT, 400)
        return error("服务器错误", ErrorCode.INTERNAL_ERROR, 500)
    """
    suggestion = recovery_suggestion or ErrorRecovery.get(error_code)
    
    response = {
        "success": False,
        "error": message,
        "error_code": error_code.value,
        "recovery_suggestion": suggestion
    }
    
    if details is not None:
        response["details"] = details
    
    return jsonify(response), status_code


def exception_error(
    e: Exception,
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    status_code: int = 500,
    custom_message: str = None
) -> tuple[Response, int]:
    """
    构建异常错误响应（自动处理 DEBUG 模式下的 traceback）
    
    Args:
        e: 捕获的异常
        error_code: 错误代码
        status_code: HTTP 状态码
        custom_message: 自定义错误消息
    
    Returns:
        (Response, status_code) 元组
    
    Example:
        try:
            do_something()
        except Exception as e:
            return exception_error(e)
    """
    import traceback
    
    config = get_config()
    message = custom_message or str(e)
    
    response = {
        "success": False,
        "error": message,
        "error_code": error_code.value,
        "recovery_suggestion": ErrorRecovery.get(error_code)
    }
    
    # 仅在 DEBUG 模式下包含 traceback
    if config.DEBUG:
        response["traceback"] = traceback.format_exc()
    
    return jsonify(response), status_code


# ============== 常用错误响应快捷函数 ==============

def bad_request(
    message: str = "请求参数错误",
    error_code: ErrorCode = ErrorCode.INVALID_INPUT,
    details: Any = None
) -> tuple[Response, int]:
    """
    400 Bad Request 响应
    """
    return error(message, error_code, 400, details=details)


def unauthorized(
    message: str = "未授权访问",
    error_code: ErrorCode = ErrorCode.UNAUTHORIZED
) -> tuple[Response, int]:
    """
    401 Unauthorized 响应
    """
    return error(message, error_code, 401)


def forbidden(
    message: str = "禁止访问",
    error_code: ErrorCode = ErrorCode.FORBIDDEN
) -> tuple[Response, int]:
    """
    403 Forbidden 响应
    """
    return error(message, error_code, 403)


def not_found(
    message: str = "资源不存在",
    resource_type: str = None,
    resource_id: str = None
) -> tuple[Response, int]:
    """
    404 Not Found 响应
    
    Args:
        message: 错误消息
        resource_type: 资源类型（可选，用于生成更具体的消息）
        resource_id: 资源 ID（可选）
    """
    if resource_type and resource_id:
        message = f"{resource_type}不存在: {resource_id}"
    elif resource_type:
        message = f"{resource_type}不存在"
    
    return error(message, ErrorCode.RESOURCE_NOT_FOUND, 404)


def conflict(
    message: str = "资源冲突",
    error_code: ErrorCode = ErrorCode.CONFLICT
) -> tuple[Response, int]:
    """
    409 Conflict 响应
    """
    return error(message, error_code, 409)


def validation_error(
    message: str = "数据验证失败",
    errors: List[str] = None
) -> tuple[Response, int]:
    """
    422 Unprocessable Entity 响应（验证错误）
    
    Args:
        message: 错误消息
        errors: 具体的验证错误列表
    """
    details = {"validation_errors": errors} if errors else None
    return error(message, ErrorCode.VALIDATION_ERROR, 422, details=details)


def rate_limited(
    message: str = "请求过于频繁，请稍后重试"
) -> tuple[Response, int]:
    """
    429 Too Many Requests 响应
    """
    return error(message, ErrorCode.RATE_LIMIT_EXCEEDED, 429)


def internal_error(
    message: str = "服务器内部错误",
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR
) -> tuple[Response, int]:
    """
    500 Internal Server Error 响应
    """
    return error(message, error_code, 500)


def service_unavailable(
    message: str = "服务暂时不可用",
    error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR
) -> tuple[Response, int]:
    """
    503 Service Unavailable 响应
    """
    return error(message, error_code, 503)


# ============== 分页响应 ==============

def paginated(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "获取成功"
) -> tuple[Response, int]:
    """
    构建分页响应
    
    Args:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码（从 1 开始）
        page_size: 每页大小
        message: 成功消息
    
    Returns:
        (Response, 200) 元组
    
    Example:
        items = get_items(page=1, size=20)
        total = count_items()
        return paginated(items, total, page=1, page_size=20)
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    response = {
        "success": True,
        "data": items,
        "message": message,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return jsonify(response), 200


# ============== 流式响应 ==============

def stream(
    generator,
    content_type: str = "text/event-stream"
) -> Response:
    """
    构建流式响应（用于 SSE 等）
    
    Args:
        generator: 数据生成器
        content_type: 内容类型
    
    Returns:
        Flask Response 对象
    
    Example:
        def generate():
            for i in range(10):
                yield f"data: {i}\\n\\n"
        return stream(generate())
    """
    from flask import Response as FlaskResponse
    return FlaskResponse(
        generator,
        mimetype=content_type,
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )
