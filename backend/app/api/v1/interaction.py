# 交互相关路由

from flask import request, jsonify
from app.api import api_v1_bp, get_response, get_error_response
from app.utils import get_logger, validate_api_request
from app.utils.llm import LLMClient
from app.modules.interaction import create_chat_interface
from app.config_new import get_config

logger = get_logger(__name__)

# 全局聊天接口实例
chat_interface = None
llm_client = None


def _get_chat_interface():
    """获取聊天接口实例（单例模式）
    
    Returns:
        ChatInterface 实例
    """
    global chat_interface, llm_client
    
    if chat_interface is None:
        # 创建 LLM 客户端
        config = get_config()
        llm_client = LLMClient(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            model_name=config.LLM_MODEL_NAME,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
            timeout=config.LLM_TIMEOUT
        )
        
        # 创建聊天接口
        chat_interface = create_chat_interface(llm_client)
        
        logger.info("聊天接口实例已创建")
    
    return chat_interface


@api_v1_bp.route("/interaction/agent", methods=["POST"])
def chat_with_agent():
    """与特定智能体对话"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["agent_id", "message", "agent_profile"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # 获取参数
        agent_id = data["agent_id"]
        message = data["message"]
        agent_profile = data["agent_profile"]
        
        logger.info(f"接收到与智能体对话请求: agent_id={agent_id}")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 执行对话
        result = interface.chat_with_agent(agent_id, message, agent_profile)
        
        if result.get("success"):
            return jsonify(get_response(result, 200)), 200
        else:
            return jsonify(get_error_response(result.get("error", "对话失败"), 500)), 500
        
    except Exception as e:
        logger.error(f"与智能体对话失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/system", methods=["POST"])
def chat_with_system():
    """与系统对话（ReportAgent）"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["message"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # 获取参数
        message = data["message"]
        simulation_data = data.get("simulation_data", [])
        
        logger.info("接收到与系统对话请求")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 如果有模拟数据，更新接口
        if simulation_data:
            interface.set_simulation_data(simulation_data)
        
        # 执行对话
        result = interface.chat_with_system(message)
        
        if result.get("success"):
            return jsonify(get_response(result, 200)), 200
        else:
            return jsonify(get_error_response(result.get("error", "对话失败"), 500)), 500
        
    except Exception as e:
        logger.error(f"与系统对话失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/agent/<agent_id>/history", methods=["GET"])
def get_agent_history(agent_id: str):
    """获取与特定智能体的对话历史"""
    try:
        # 获取查询参数
        limit = request.args.get("limit", 100, type=int)
        
        logger.info(f"接收到获取对话历史请求: agent_id={agent_id}, limit={limit}")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 获取历史
        history = interface.get_conversation_history(agent_id, limit)
        
        return jsonify(get_response({
            "agent_id": agent_id,
            "history": history,
            "total": len(history)
        })), 200
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/history", methods=["GET"])
def get_all_history():
    """获取所有对话历史"""
    try:
        # 获取查询参数
        limit = request.args.get("limit", 100, type=int)
        
        logger.info(f"接收到获取所有对话历史请求: limit={limit}")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 获取历史
        history = interface.get_conversation_history(limit=limit)
        
        return jsonify(get_response({
            "history": history,
            "total": len(history)
        })), 200
        
    except Exception as e:
        logger.error(f"获取所有对话历史失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/agent/<agent_id>/history", methods=["DELETE"])
def clear_agent_history(agent_id: str):
    """清除与特定智能体的对话历史"""
    try:
        logger.info(f"接收到清除对话历史请求: agent_id={agent_id}")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 清除历史
        interface.clear_history(agent_id)
        
        return jsonify(get_response({
            "message": f"已清除智能体 {agent_id} 的对话历史"
        })), 200
        
    except Exception as e:
        logger.error(f"清除对话历史失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/history", methods=["DELETE"])
def clear_all_history():
    """清除所有对话历史"""
    try:
        logger.info("接收到清除所有对话历史请求")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 清除历史
        interface.clear_history()
        
        return jsonify(get_response({
            "message": "已清除所有对话历史"
        })), 200
        
    except Exception as e:
        logger.error(f"清除所有对话历史失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/statistics", methods=["GET"])
def get_chat_statistics():
    """获取聊天统计信息"""
    try:
        logger.info("接收到获取聊天统计信息请求")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 获取统计
        stats = interface.get_statistics()
        
        return jsonify(get_response(stats)), 200
        
    except Exception as e:
        logger.error(f"获取聊天统计信息失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/interaction/simulation-data", methods=["POST"])
def set_simulation_data():
    """设置模拟数据"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["simulation_data"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        # 获取参数
        simulation_data = data["simulation_data"]
        
        logger.info(f"接收到设置模拟数据请求: {len(simulation_data)} 条记录")
        
        # 获取聊天接口
        interface = _get_chat_interface()
        
        # 设置模拟数据
        interface.set_simulation_data(simulation_data)
        
        return jsonify(get_response({
            "message": "模拟数据已更新",
            "simulation_data_size": len(simulation_data)
        })), 200
        
    except Exception as e:
        logger.error(f"设置模拟数据失败: {e}")
        return jsonify(get_error_response(str(e), 500)), 500
