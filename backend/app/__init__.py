# Flask 应用工厂
"""
Multimo Flask 应用入口
重构版本：移除对第三方受版权保护的依赖
提供 API 认证、限流、输入验证和 CORS 安全配置
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid

from app.config_new import get_config
from app.api import init_api, register_routes
from app.utils import get_logger
from app.models.task import TaskManager

logger = get_logger(__name__)


def create_app(config_override: dict = None) -> Flask:
    """创建 Flask 应用实例
    
    Args:
        config_override: 配置覆盖字典
        
    Returns:
        Flask 应用实例
    """
    config = get_config()
    
    if config_override:
        for key, value in config_override.items():
            setattr(config, key, value)
    
    config_errors = config.validate_required_fields()
    if config_errors:
        logger.warning("配置验证警告:")
        for error in config_errors:
            logger.warning(f"  - {error}")
    
    app = Flask(__name__)
    
    flask_config = config.get_flask_config()
    for key, value in flask_config.items():
        app.config[key] = value
    
    logger.info(f"Flask 应用初始化: DEBUG={config.DEBUG}")
    
    apply_security_headers(app, config)
    
    init_rate_limiting(app, config)
    
    init_auth(app)
    
    register_routes()
    
    init_api(app)
    
    register_error_handlers(app)
    
    task_manager = TaskManager()
    task_manager.recover_tasks()
    logger.info("任务恢复检查完成")
    
    # 恢复中断的报告生成任务
    try:
        from app.services.report_task_worker import get_report_task_worker
        report_worker = get_report_task_worker()
        recovered_report_tasks = report_worker.recover_interrupted_tasks()
        if recovered_report_tasks:
            logger.info(f"已恢复 {len(recovered_report_tasks)} 个中断的报告任务")
    except Exception as e:
        logger.warning(f"报告任务恢复检查失败: {e}")
    
    logger.info("Flask 应用初始化完成")
    
    return app


def apply_security_headers(app: Flask, config) -> None:
    """应用安全响应头中间件
    
    添加多种安全响应头以防止常见的 Web 攻击
    
    Args:
        app: Flask 应用实例
        config: 配置实例
    """
    if not config.SECURITY_HEADERS_ENABLED:
        logger.info("安全响应头已禁用")
        return
    
    @app.after_request
    def add_security_headers(response):
        """在每个响应中添加安全头"""
        security_headers = config.get_security_headers()
        
        for header_name, header_value in security_headers.items():
            if header_value:
                response.headers[header_name] = header_value
        
        response.headers["X-Request-ID"] = str(uuid.uuid4())[:8]
        
        return response
    
    logger.info("安全响应头中间件已注册")


def init_rate_limiting(app: Flask, config) -> None:
    """初始化请求限流
    
    使用 Flask-Limiter 配置不同端点的限流策略
    
    Args:
        app: Flask 应用实例
        config: 配置实例
    """
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    if not config.RATE_LIMIT_ENABLED:
        logger.info("请求限流已禁用")
        app.config["RATELIMIT_ENABLED"] = False
        return
    
    limiter_config = config.get_rate_limit_config()
    
    kwargs = {
        "key_func": get_remote_address,
        "strategy": limiter_config.get("strategy", "moving-window"),
        "default_limits": [limiter_config.get("default", "200/hour")],
        "headers_enabled": True,
        "retry_after": "delta"
    }
    
    if limiter_config["storage"] == "redis" and limiter_config.get("redis_url"):
        kwargs["storage_uri"] = limiter_config["redis_url"]
        logger.info(f"使用 Redis 存储限流配置: {limiter_config['redis_url']}")
    
    limiter = Limiter(**kwargs)
    limiter.init_app(app)
    
    app.limiter = limiter
    
    logger.info(
        f"限流中间件已初始化: storage={limiter_config['storage']}, "
        f"default={limiter_config.get('default', '200/hour')}"
    )


def init_auth(app: Flask) -> None:
    """初始化认证模块
    
    加载配置好的 API Keys
    
    Args:
        app: Flask 应用实例
    """
    from app.api.auth import init_auth as auth_init
    
    auth_init(app)


def register_error_handlers(app: Flask):
    """注册错误处理器
    
    提供统一的错误处理，包括详细的日志记录和用户友好的错误响应
    
    Args:
        app: Flask 应用实例
    """
    from app.api import get_http_error_response, get_error_response, ErrorCode
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理 400 错误请求"""
        logger.warning(f"400 错误 - 请求路径: {error.description}")
        return jsonify(get_http_error_response(400)), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """处理 401 未授权错误"""
        logger.warning(f"401 未授权访问 - 路径: {error.description}")
        return jsonify(get_http_error_response(401)), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理 403 禁止访问错误"""
        logger.warning(f"403 禁止访问 - 路径: {error.description}")
        return jsonify(get_http_error_response(403)), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """处理 404 资源不存在错误"""
        logger.warning(f"404 资源不存在 - 路径: {error.description}")
        return jsonify(get_http_error_response(404)), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """处理 405 不允许的方法错误"""
        logger.warning(f"405 不支持的方法: {error.description}")
        return jsonify(get_http_error_response(405)), 405
    
    @app.errorhandler(409)
    def conflict(error):
        """处理 409 资源冲突错误"""
        logger.warning(f"409 资源冲突: {error.description}")
        return jsonify(get_http_error_response(409)), 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """处理 422 无法处理的实体错误"""
        logger.warning(f"422 数据验证失败: {error.description}")
        return jsonify(get_http_error_response(422)), 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """处理 429 请求过于频繁错误"""
        logger.warning(f"429 请求频率限制: {error.description}")
        return jsonify(get_http_error_response(429)), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理 500 服务器内部错误"""
        logger.error(f"500 服务器内部错误: {error}", exc_info=True)
        response, status = get_http_error_response(500)
        return jsonify(response), status
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """处理 502 网关错误"""
        logger.error(f"502 网关错误: {error}", exc_info=True)
        response, status = get_http_error_response(502)
        return jsonify(response), status
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """处理 503 服务不可用错误"""
        logger.error(f"503 服务暂时不可用: {error}", exc_info=True)
        response, status = get_http_error_response(503)
        return jsonify(response), status
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常
        
        记录完整的异常信息，包括堆栈跟踪，但确保不暴露敏感信息
        """
        from flask import request
        
        error_type = type(error).__name__
        
        error_context = {
            "error_type": error_type,
            "error_message": str(error),
            "request_path": request.path,
            "request_method": request.method,
            "request_endpoint": request.endpoint,
        }
        
        if request.is_json:
            try:
                error_context["request_data"] = request.get_json(silent=True)
            except Exception:
                error_context["request_data"] = "<解析失败>"
        else:
            error_context["request_data"] = "<非JSON请求>"
        
        if error_type in ["ValueError", "TypeError", "KeyError"]:
            logger.warning(f"业务逻辑错误: {error_context}", exc_info=True)
            return jsonify(get_error_response(
                error="请求数据处理失败，请检查输入格式",
                status_code=400,
                error_code=ErrorCode.VALIDATION_ERROR
            )), 400
        
        if error_type in ["ConnectionError", "TimeoutError"]:
            logger.error(f"外部服务连接错误: {error_context}", exc_info=True)
            return jsonify(get_error_response(
                error="无法连接到外部服务，请稍后重试",
                status_code=503,
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR
            )), 503
        
        if "timeout" in str(error).lower():
            logger.error(f"请求超时: {error_context}", exc_info=True)
            return jsonify(get_error_response(
                error="请求超时，请稍后重试",
                status_code=408,
                error_code=ErrorCode.TIMEOUT_ERROR
            )), 408
        
        logger.error(f"未处理的异常: {error_context}", exc_info=True)
        
        return jsonify(get_error_response(
            error="系统发生未知错误，请稍后重试",
            status_code=500,
            error_code=ErrorCode.INTERNAL_ERROR
        )), 500


def run_server():
    """运行开发服务器
    
    主要用于开发环境，生产环境应使用 gunicorn/uwsgi 等 WSGI 服务器
    """
    app = create_app()
    
    config = get_config()
    
    logger.info(f"启动开发服务器: {config.HOST}:{config.PORT}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )


if __name__ == "__main__":
    run_server()
