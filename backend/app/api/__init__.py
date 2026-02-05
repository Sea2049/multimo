# API 模块
from enum import Enum
from typing import Optional
from flask import Blueprint
from flask_cors import CORS

from app.config_new import get_config


class ErrorCode(Enum):
    """错误代码枚举类
    
    用于标识不同类型的错误，便于前端分类处理和用户提示
    """
    INVALID_INPUT = "INVALID_INPUT"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    LLM_ERROR = "LLM_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorRecovery:
    """错误恢复建议映射
    
    根据错误代码提供用户友好的恢复建议
    """
    SUGGESTIONS = {
        ErrorCode.INVALID_INPUT: "请检查输入参数是否正确，确保所有必填字段都已填写。",
        ErrorCode.RESOURCE_NOT_FOUND: "请求的资源可能已被删除或不存在，请刷新页面后重试。",
        ErrorCode.UNAUTHORIZED: "请登录后重试，或检查您的登录状态是否过期。",
        ErrorCode.FORBIDDEN: "您没有权限执行此操作，请联系管理员获取权限。",
        ErrorCode.CONFLICT: "资源状态已发生变化，请刷新页面后重试。",
        ErrorCode.VALIDATION_ERROR: "请检查输入格式是否符合要求，确保所有字段格式正确。",
        ErrorCode.INTERNAL_ERROR: "服务器内部错误，请稍后重试或联系管理员。",
        ErrorCode.EXTERNAL_SERVICE_ERROR: "依赖服务暂时不可用，请稍后重试或联系管理员。",
        ErrorCode.NETWORK_ERROR: "请检查网络连接，确保网络稳定后重试。",
        ErrorCode.TIMEOUT_ERROR: "请求超时，可能是服务器繁忙，请稍后重试或刷新页面。",
        ErrorCode.RATE_LIMIT_EXCEEDED: "请求过于频繁，请稍后重试。",
        ErrorCode.PERMISSION_DENIED: "您没有权限执行此操作，请确认您的账户权限。",
        ErrorCode.CONFIGURATION_ERROR: "系统配置问题，请联系管理员检查配置。",
        ErrorCode.DATABASE_ERROR: "数据库操作失败，请稍后重试或联系管理员。",
        ErrorCode.LLM_ERROR: "AI 服务暂时不可用，请稍后重试或检查 API 配置。",
        ErrorCode.UNKNOWN_ERROR: "发生未知错误，请刷新页面后重试。如果问题持续，请联系管理员。",
    }

    @classmethod
    def get(cls, error_code: ErrorCode) -> str:
        """获取指定错误代码的恢复建议
        
        Args:
            error_code: 错误代码
            
        Returns:
            恢复建议字符串
        """
        return cls.SUGGESTIONS.get(error_code, cls.SUGGESTIONS[ErrorCode.UNKNOWN_ERROR])


# 创建蓝图
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
simulation_bp = Blueprint("simulation", __name__, url_prefix="/api/simulation")
graph_bp = Blueprint("graph", __name__, url_prefix="/api/graph")
report_bp = Blueprint("report", __name__, url_prefix="/api/report")

# 获取配置
config = get_config()


def init_api(app):
    """初始化 API
    
    Args:
        app: Flask 应用实例
    """
    # 配置 CORS
    cors_config = config.get_cors_config()
    CORS(app, **cors_config)

    # 蓝图级统一鉴权：graph / simulation / report 下所有路由需登录
    from app.api.decorators import user_auth_required_for_request
    graph_bp.before_request(user_auth_required_for_request)
    simulation_bp.before_request(user_auth_required_for_request)
    report_bp.before_request(user_auth_required_for_request)

    # 注册蓝图
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(report_bp)
    
    # 添加根级健康检查路由（兼容 Docker healthcheck）
    @app.route('/api/health', methods=['GET'])
    def root_health_check():
        """根级健康检查端点（兼容旧版配置）"""
        return {
            "success": True,
            "status": "healthy",
            "version": "2.0.0",
            "message": "Multimo API is running"
        }, 200


def register_routes():
    """注册所有路由
    注意：实际的路由注册在各个路由文件中通过装饰器完成
    此函数用于确保所有路由模块被导入
    """
    # v1 旧版路由
    from app.api.v1 import graph, simulation, report, health, interaction
    
    # 用户认证和邀请码路由
    from app.api.v1 import user_auth, invitation
    
    # 新版完整路由
    from app.api import graph as graph_module
    from app.api import simulation as simulation_module
    from app.api import report as report_module
    
    # 路由模块导入后自动注册


def get_response(data: any, status_code: int = 200, 
                 message: str = "success") -> dict:
    """统一 API 响应格式
    
    Args:
        data: 响应数据
        status_code: HTTP 状态码
        message: 响应消息
        
    Returns:
        响应字典
    """
    return {
        "success": status_code < 400,
        "status_code": status_code,
        "message": message,
        "data": data
    }


def get_error_response(
    error: str,
    status_code: int = 400,
    error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
    recovery_suggestion: Optional[str] = None
) -> dict:
    """统一错误响应格式
    
    提供统一的错误响应结构，包含错误代码和恢复建议
    
    Args:
        error: 错误消息
        status_code: HTTP 状态码
        error_code: 错误代码枚举值
        recovery_suggestion: 自定义恢复建议，如果不提供则使用默认值
        
    Returns:
        错误响应字典
    """
    suggestion = recovery_suggestion if recovery_suggestion else ErrorRecovery.get(error_code)
    
    return {
        "success": False,
        "status_code": status_code,
        "error_code": error_code.value,
        "message": error,
        "recovery_suggestion": suggestion,
        "data": None
    }


def make_error_response(
    error: Exception,
    status_code: int = 500,
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    custom_message: str = None
) -> dict:
    """生成安全的错误响应（仅在 DEBUG 模式下包含 traceback）
    
    用于 API 端点的异常处理，自动根据环境决定是否暴露详细错误信息
    
    Args:
        error: 捕获的异常对象
        status_code: HTTP 状态码
        error_code: 错误代码枚举值
        custom_message: 自定义错误消息，如果不提供则使用异常消息
        
    Returns:
        错误响应字典
    """
    import traceback
    
    config = get_config()
    error_message = custom_message if custom_message else str(error)
    
    response = {
        "success": False,
        "error": error_message,
        "error_code": error_code.value,
        "recovery_suggestion": ErrorRecovery.get(error_code)
    }
    
    # 仅在 DEBUG 模式下包含 traceback，生产环境不泄露敏感信息
    if config.DEBUG:
        response["traceback"] = traceback.format_exc()
    
    return response


def get_http_error_response(status_code: int, error_message: str = None) -> tuple:
    """根据 HTTP 状态码获取统一的错误响应
    
    用于 Flask 错误处理器中生成标准化的错误响应
    
    Args:
        status_code: HTTP 状态码
        error_message: 自定义错误消息，如果不提供则使用默认消息
        
    Returns:
        (响应字典, 状态码) 元组
    """
    error_code_map = {
        400: ErrorCode.INVALID_INPUT,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        405: ErrorCode.INVALID_INPUT,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_ERROR,
        502: ErrorCode.EXTERNAL_SERVICE_ERROR,
        503: ErrorCode.EXTERNAL_SERVICE_ERROR,
    }
    
    default_messages = {
        400: "请求参数错误",
        401: "未授权访问",
        403: "禁止访问",
        404: "资源不存在",
        405: "不支持的请求方法",
        409: "资源冲突",
        422: "数据验证失败",
        429: "请求过于频繁",
        500: "服务器内部错误",
        502: "网关错误",
        503: "服务暂时不可用",
    }
    
    error_code = error_code_map.get(status_code, ErrorCode.UNKNOWN_ERROR)
    message = error_message or default_messages.get(status_code, "发生错误")
    
    response = get_error_response(
        error=message,
        status_code=status_code,
        error_code=error_code
    )
    
    return response, status_code
