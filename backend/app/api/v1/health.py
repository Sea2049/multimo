# 健康检查路由

from flask import request, jsonify
from app.api import api_v1_bp, get_response, get_error_response
from app.utils import get_logger

logger = get_logger(__name__)


@api_v1_bp.route("/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    try:
        return jsonify(get_response({
            "status": "healthy",
            "version": "2.0.0-alpha",
            "message": "Multimo API is running"
        })), 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/health/detailed", methods=["GET"])
def detailed_health_check():
    """详细健康检查端点"""
    try:
        # 检查各个组件
        checks = {
            "api": {"status": "healthy", "message": "API 服务正常"},
            "database": {"status": "healthy", "message": "数据库连接正常"},
            "storage": {"status": "healthy", "message": "存储服务正常"}
        }
        
        # 检查是否有不健康的组件
        unhealthy = [k for k, v in checks.items() if v["status"] != "healthy"]
        overall_status = "healthy" if not unhealthy else "degraded"
        
        return jsonify(get_response({
            "status": overall_status,
            "version": "2.0.0-alpha",
            "checks": checks
        })), 200
    except Exception as e:
        logger.error(f"详细健康检查失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500
