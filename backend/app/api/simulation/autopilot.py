"""
自动驾驶模式 API 路由模块

提供模拟的自动驾驶控制功能。

路由:
    POST /auto-pilot/config     - 配置自动驾驶模式
    POST /auto-pilot/start      - 启动自动驾驶
    POST /auto-pilot/pause      - 暂停自动驾驶
    POST /auto-pilot/resume     - 恢复自动驾驶
    POST /auto-pilot/stop       - 停止自动驾驶
    POST /auto-pilot/status     - 获取自动驾驶状态
    POST /auto-pilot/reset      - 重置自动驾驶状态
"""

from flask import request, jsonify

from .. import simulation_bp, make_error_response, ErrorCode
from ...services.simulation_manager import SimulationManager
from ...services.auto_pilot_manager import AutoPilotManager, AutoPilotMode
from ...utils.logger import get_logger

logger = get_logger('multimo.api.simulation.autopilot')


@simulation_bp.route('/auto-pilot/config', methods=['POST'])
def config_auto_pilot():
    """
    配置自动驾驶模式
    
    设置模拟的自动驾驶模式（AUTO / MANUAL）
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",  // 必填，模拟ID
            "mode": "auto"                // 必填：auto / manual
        }
    
    Returns:
        配置结果
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        mode = data.get('mode', '').lower()
        if mode not in ['auto', 'manual']:
            return jsonify({
                "success": False,
                "error": "mode 必须是 'auto' 或 'manual'"
            }), 400
        
        manager = AutoPilotManager()
        auto_mode = AutoPilotMode.AUTO if mode == 'auto' else AutoPilotMode.MANUAL
        
        # 检查模拟是否存在
        sim_manager = SimulationManager()
        sim_state = sim_manager.get_simulation(simulation_id)
        if not sim_state:
            return jsonify({
                "success": False,
                "error": f"模拟不存在: {simulation_id}"
            }), 404
        
        # 设置模式
        state = manager.set_mode(simulation_id, auto_mode)
        
        # 更新 SimulationState
        sim_state.auto_pilot_enabled = (mode == 'auto')
        sim_manager._save_simulation_state(sim_state)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "mode": mode,
                "message": "自动驾驶模式已启用" if mode == 'auto' else "手动模式已启用",
                "available": True
            }
        })
        
    except Exception as e:
        logger.error(f"配置自动驾驶模式失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/start', methods=['POST'])
def start_auto_pilot():
    """
    启动自动驾驶
    
    在自动驾驶模式下，自动执行：准备 -> 启动 -> 监控 -> 生成报告
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",  // 必填，模拟ID
            "force": false                 // 可选，是否强制重新开始
        }
    
    Returns:
        启动结果和当前状态
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        force = data.get('force', False)
        
        manager = AutoPilotManager()
        
        # 检查是否已启用自动驾驶模式
        current_mode = manager.get_mode(simulation_id)
        if current_mode.value != 'auto':
            return jsonify({
                "success": False,
                "error": "请先启用自动驾驶模式（调用 /api/simulation/auto-pilot/config 设置 mode=auto）"
            }), 400
        
        # 检查模拟是否存在
        sim_manager = SimulationManager()
        sim_state = sim_manager.get_simulation(simulation_id)
        if not sim_state:
            return jsonify({
                "success": False,
                "error": f"模拟不存在: {simulation_id}"
            }), 404
        
        # 如果强制模式，重置状态
        if force:
            manager.reset_auto_pilot(simulation_id)
        
        # 启动自动驾驶
        state = manager.start_auto_pilot(simulation_id, force=force)
        
        # 更新 SimulationState
        sim_state.auto_pilot_enabled = True
        sim_state.auto_pilot_started_at = state.started_at
        sim_manager._save_simulation_state(sim_state)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "status": state.status.value,
                "current_step": state.current_step.value,
                "step_progress": state.step_progress,
                "step_message": state.step_message,
                "message": "自动驾驶已启动",
                "force_restarted": force
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"启动自动驾驶失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/pause', methods=['POST'])
def pause_auto_pilot():
    """
    暂停自动驾驶
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        暂停后的状态
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        manager = AutoPilotManager()
        state = manager.pause_auto_pilot(simulation_id)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "status": state.status.value,
                "current_step": state.current_step.value,
                "message": "自动驾驶已暂停"
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"暂停自动驾驶失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/resume', methods=['POST'])
def resume_auto_pilot():
    """
    恢复自动驾驶
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        恢复后的状态
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        manager = AutoPilotManager()
        state = manager.resume_auto_pilot(simulation_id)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "status": state.status.value,
                "current_step": state.current_step.value,
                "message": "自动驾驶已恢复"
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"恢复自动驾驶失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/stop', methods=['POST'])
def stop_auto_pilot():
    """
    停止自动驾驶
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        停止后的状态
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        manager = AutoPilotManager()
        state = manager.stop_auto_pilot(simulation_id)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "status": state.status.value,
                "message": "自动驾驶已停止"
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"停止自动驾驶失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/status', methods=['POST'])
def get_auto_pilot_status():
    """
    获取自动驾驶状态
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        详细的自动驾驶状态信息
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        manager = AutoPilotManager()
        status = manager.to_dict(simulation_id)
        
        return jsonify({
            "success": True,
            "data": status
        })
        
    except Exception as e:
        logger.error(f"获取自动驾驶状态失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/auto-pilot/reset', methods=['POST'])
def reset_auto_pilot():
    """
    重置自动驾驶状态
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        重置结果
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        manager = AutoPilotManager()
        manager.reset_auto_pilot(simulation_id)
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "message": "自动驾驶状态已重置"
            }
        })
        
    except Exception as e:
        logger.error(f"重置自动驾驶状态失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500
