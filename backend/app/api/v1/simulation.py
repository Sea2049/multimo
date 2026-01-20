# 模拟相关路由

from flask import request, jsonify
from app.api import api_v1_bp, get_response, get_error_response
from app.utils import get_logger, validate_api_request

logger = get_logger(__name__)


@api_v1_bp.route("/simulation/start", methods=["POST"])
def start_simulation():
    """启动模拟"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["config"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # TODO: 实现模拟启动逻辑（第二阶段）
        logger.info("接收到模拟启动请求")
        
        return jsonify(get_response({
            "simulation_id": "",
            "message": "模拟引擎模块将在第二阶段实现"
        })), 200
        
    except Exception as e:
        logger.error(f"模拟启动失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/simulation/<simulation_id>/status", methods=["GET"])
def get_simulation_status(simulation_id: str):
    """获取模拟状态"""
    try:
        # TODO: 实现状态获取逻辑（第二阶段）
        logger.info(f"接收到获取模拟状态请求: simulation_id={simulation_id}")
        
        return jsonify(get_response({
            "status": "not_started",
            "message": "模拟状态查询模块将在第二阶段实现"
        })), 200
        
    except Exception as e:
        logger.error(f"获取模拟状态失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


from app.services.simulation_runner import SimulationRunner

@api_v1_bp.route("/simulation/<simulation_id>/stop", methods=["POST"])
def stop_simulation(simulation_id: str):
    """停止模拟"""
    try:
        logger.info(f"接收到停止模拟请求: simulation_id={simulation_id}")
        
        # 调用 SimulationRunner 停止模拟
        state = SimulationRunner.stop_simulation(simulation_id)
        
        return jsonify(get_response({
            "success": True,
            "message": "模拟已停止",
            "state": state.to_dict()
        })), 200
        
    except ValueError as e:
        logger.warning(f"停止模拟失败(ValueError): {e}")
        return jsonify(get_error_response(str(e), 400)), 400
    except Exception as e:
        logger.error(f"停止模拟失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/simulation/<simulation_id>/results", methods=["GET"])
def get_simulation_results(simulation_id: str):
    """获取模拟结果"""
    try:
        # TODO: 实现结果获取逻辑（第二阶段）
        logger.info(f"接收到获取模拟结果请求: simulation_id={simulation_id}")
        
        return jsonify(get_response({
            "results": [],
            "message": "模拟结果查询模块将在第二阶段实现"
        })), 200
        
    except Exception as e:
        logger.error(f"获取模拟结果失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500
