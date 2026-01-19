# Flask 应用工厂
"""
Multimo Flask 应用入口
重构版本：移除对第三方受版权保护的依赖
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

from app.config_new import get_config
from app.api import init_api, register_routes
from app.utils import get_logger

logger = get_logger(__name__)


def create_app(config_override: dict = None) -> Flask:
    """创建 Flask 应用实例
    
    Args:
        config_override: 配置覆盖字典
        
    Returns:
        Flask 应用实例
    """
    # 获取配置
    config = get_config()
    
    # 如果有配置覆盖，应用覆盖
    if config_override:
        for key, value in config_override.items():
            setattr(config, key, value)
    
    # 验证配置
    config_errors = config.validate_required_fields()
    if config_errors:
        logger.warning("配置验证警告:")
        for error in config_errors:
            logger.warning(f"  - {error}")
    
    # 创建 Flask 应用
    app = Flask(__name__)
    
    # 配置 Flask
    flask_config = config.get_flask_config()
    for key, value in flask_config.items():
        app.config[key] = value
    
    logger.info(f"Flask 应用初始化: DEBUG={config.DEBUG}")
    
    # 注册所有路由（在注册蓝图之前）
    register_routes()
    
    # 初始化 API（注册蓝图）
    init_api(app)
    
    # 配置错误处理器
    register_error_handlers(app)
    
    logger.info("Flask 应用初始化完成")
    
    return app


def register_error_handlers(app: Flask):
    """注册错误处理器
    
    Args:
        app: Flask 应用实例
    """
    from app.api import get_error_response
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理 400 错误"""
        logger.warning(f"400 错误: {error}")
        return jsonify(get_error_response("Bad Request", 400)), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """处理 404 错误"""
        logger.warning(f"404 错误: {error}")
        return jsonify(get_error_response("Not Found", 404)), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """处理 405 错误"""
        logger.warning(f"405 错误: {error}")
        return jsonify(get_error_response("Method Not Allowed", 405)), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理 500 错误"""
        logger.error(f"500 错误: {error}")
        return jsonify(get_error_response("Internal Server Error", 500)), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        logger.error(f"未捕获的异常: {error}", exc_info=True)
        return jsonify(get_error_response(str(error), 500)), 500


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
