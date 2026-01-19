# API 模块
from flask import Blueprint
from flask_cors import CORS

from app.config_new import get_config

# 创建蓝图
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

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
    
    # 注册蓝图
    app.register_blueprint(api_v1_bp)


def register_routes():
    """注册所有路由
    注意：实际的路由注册在各个路由文件中通过装饰器完成
    此函数用于确保所有路由模块被导入
    """
    from app.api.v1 import graph, simulation, report, health, interaction
    
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


def get_error_response(error: str, status_code: int = 400) -> dict:
    """统一错误响应格式
    
    Args:
        error: 错误消息
        status_code: HTTP 状态码
        
    Returns:
        错误响应字典
    """
    return get_response(None, status_code, error)
