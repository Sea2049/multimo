# 图谱相关路由

from flask import request, jsonify
from app.api import api_v1_bp, get_response, get_error_response
from app.utils import get_logger, validate_api_request
from app.config_new import get_config

logger = get_logger(__name__)


@api_v1_bp.route("/graph/extract", methods=["POST"])
def extract_entities():
    """从文本中提取实体"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["text"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # TODO: 实现实体提取逻辑（第二阶段）
        text = data["text"]
        logger.info(f"接收到实体提取请求: text_length={len(text)}")
        
        return jsonify(get_response({
            "entities": [],
            "message": "图谱构建模块将在第二阶段实现"
        })), 200
        
    except Exception as e:
        logger.error(f"实体提取失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/graph/build", methods=["POST"])
def build_graph():
    """构建知识图谱"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["entities", "relations"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # TODO: 实现图谱构建逻辑（第二阶段）
        logger.info("接收到图谱构建请求")
        
        return jsonify(get_response({
            "graph": {},
            "message": "图谱构建模块将在第二阶段实现"
        })), 200
        
    except Exception as e:
        logger.error(f"图谱构建失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


from app.services.simulation_manager import SimulationManager
import os
import json
from flask import send_file

@api_v1_bp.route("/graph/<graph_id>", methods=["GET"])
def get_graph(graph_id: str):
    """获取知识图谱"""
    try:
        logger.info(f"接收到获取图谱请求: graph_id={graph_id}")
        
        # 尝试从模拟目录中查找图谱
        # 注意：这里的 graph_id 可能是 simulation_id，也可能是单独的 graph_id
        # 我们假设 graph_id 就是 simulation_id，或者图谱存储在 uploads/graphs/{graph_id}.json
        
        sim_manager = SimulationManager()
        
        # 1. 尝试作为 simulation_id 查找
        sim_dir = sim_manager._get_simulation_dir(graph_id)
        graph_file = os.path.join(sim_dir, "knowledge_graph.json")
        
        if not os.path.exists(graph_file):
            # 2. 尝试在 uploads/graphs 查找
            graph_file = os.path.join(get_config().UPLOAD_FOLDER, 'graphs', f"{graph_id}.json")
            
        if not os.path.exists(graph_file):
             return jsonify(get_error_response("图谱不存在", 404)), 404
             
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
            
        return jsonify(get_response({
            "graph": graph_data,
            "message": "图谱获取成功"
        })), 200
        
    except Exception as e:
        logger.error(f"获取图谱失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/graph/<graph_id>/export", methods=["GET"])
def export_graph(graph_id: str):
    """导出知识图谱"""
    try:
        logger.info(f"接收到导出图谱请求: graph_id={graph_id}")
        
        sim_manager = SimulationManager()
        
        # 1. 尝试作为 simulation_id 查找
        sim_dir = sim_manager._get_simulation_dir(graph_id)
        graph_file = os.path.join(sim_dir, "knowledge_graph.json")
        
        if not os.path.exists(graph_file):
            # 2. 尝试在 uploads/graphs 查找
            graph_file = os.path.join(get_config().UPLOAD_FOLDER, 'graphs', f"{graph_id}.json")
            
        if not os.path.exists(graph_file):
             return jsonify(get_error_response("图谱不存在", 404)), 404
             
        return send_file(
            graph_file,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"knowledge_graph_{graph_id}.json"
        )
        
    except Exception as e:
        logger.error(f"导出图谱失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500
