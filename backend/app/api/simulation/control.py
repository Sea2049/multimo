"""
模拟运行控制 API 路由模块

提供模拟的启动、停止和恢复状态检查功能。

路由:
    POST /start                         - 开始运行模拟
    POST /stop                          - 停止模拟
    GET  /<simulation_id>/resumable     - 检查模拟是否可以恢复
"""

import os
from flask import request, jsonify

from .. import simulation_bp, get_error_response, make_error_response, ErrorCode
from ...config_new import get_config
from ...services.simulation_manager import SimulationManager, SimulationStatus
from ...services.simulation_runner import SimulationRunner, RunnerStatus
from ...services.report_agent import ReportManager
from ...models.project import ProjectManager
from ...utils.logger import get_logger
from .prepare import _check_simulation_prepared

logger = get_logger('multimo.api.simulation.control')


def _get_report_ids_for_simulation(simulation_id: str) -> list:
    """
    获取 simulation 对应的所有 report_id 列表
    
    遍历 reports 目录，找出所有 simulation_id 匹配的 report
    
    Args:
        simulation_id: 模拟ID
        
    Returns:
        report_id 列表（可能为空）
    """
    import json
    
    # reports 目录路径
    reports_dir = os.path.join(get_config().UPLOAD_FOLDER, 'reports')
    if not os.path.exists(reports_dir):
        return []
    
    report_ids = []
    
    try:
        for report_folder in os.listdir(reports_dir):
            report_path = os.path.join(reports_dir, report_folder)
            if not os.path.isdir(report_path):
                continue
            
            meta_file = os.path.join(report_path, "meta.json")
            if not os.path.exists(meta_file):
                continue
            
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                if meta.get("simulation_id") == simulation_id:
                    report_id = meta.get("report_id")
                    if report_id:
                        report_ids.append(report_id)
            except Exception:
                continue
        
    except Exception as e:
        logger.warning(f"查找 simulation {simulation_id} 的所有 report 失败: {e}")
    
    return report_ids


@simulation_bp.route('/start', methods=['POST'])
def start_simulation():
    """
    开始运行模拟

    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",          // 必填，模拟ID
            "platform": "parallel",                // 可选: twitter / reddit / parallel (默认)
            "max_rounds": 100,                     // 可选: 最大模拟轮数
            "enable_graph_memory_update": false,   // 可选: 是否启用图谱记忆更新
            "force": false                         // 可选: 强制重新开始
        }

    关于 force 参数：
        - 启用后会先停止运行中的模拟并清理日志
        - 适用于需要重新运行模拟的场景

    关于 enable_graph_memory_update：
        - 启用后，Agent活动会实时更新到Zep图谱

    Returns:
        运行状态信息
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400

        platform = data.get('platform', 'parallel')
        max_rounds = data.get('max_rounds')
        enable_graph_memory_update = data.get('enable_graph_memory_update', False)
        force = data.get('force', False)
        resume = data.get('resume', False)

        # 验证 max_rounds 参数
        if max_rounds is not None:
            try:
                max_rounds = int(max_rounds)
                if max_rounds <= 0:
                    return jsonify({
                        "success": False,
                        "error": "max_rounds 必须是正整数"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error": "max_rounds 必须是有效的整数"
                }), 400

        if platform not in ['twitter', 'reddit', 'parallel']:
            return jsonify({
                "success": False,
                "error": f"无效的平台类型: {platform}，可选: twitter/reddit/parallel"
            }), 400

        # 检查模拟是否已准备好
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)

        if not state:
            return jsonify({
                "success": False,
                "error": f"模拟不存在: {simulation_id}"
            }), 404

        force_restarted = False
        
        # 智能处理状态：如果准备工作已完成，允许重新启动
        if state.status != SimulationStatus.READY:
            is_prepared, prepare_info = _check_simulation_prepared(simulation_id)

            if is_prepared:
                if state.status == SimulationStatus.RUNNING:
                    run_state = SimulationRunner.get_run_state(simulation_id)
                    if run_state and run_state.runner_status.value == "running":
                        if force:
                            logger.info(f"强制模式：停止运行中的模拟 {simulation_id}")
                            try:
                                SimulationRunner.stop_simulation(simulation_id)
                            except Exception as e:
                                logger.warning(f"停止模拟时出现警告: {str(e)}")
                        else:
                            return jsonify({
                                "success": False,
                                "error": f"模拟正在运行中，请先调用 /stop 接口停止，或使用 force=true 强制重新开始"
                            }), 400

                # 如果是强制模式，清理运行日志
                if force:
                    logger.info(f"强制模式：清理模拟日志 {simulation_id}")
                    cleanup_result = SimulationRunner.cleanup_simulation_logs(simulation_id)
                    if not cleanup_result.get("success"):
                        logger.warning(f"清理日志时出现警告: {cleanup_result.get('errors')}")
                    force_restarted = True
                    resume = False

                # 重置状态为 ready
                logger.info(f"模拟 {simulation_id} 准备工作已完成，重置状态为 ready（原状态: {state.status.value}）")
                state.status = SimulationStatus.READY
                manager._save_simulation_state(state)
            else:
                return jsonify({
                    "success": False,
                    "error": f"模拟未准备好，当前状态: {state.status.value}，请先调用 /prepare 接口"
                }), 400
        
        # 获取图谱ID（用于图谱记忆更新）
        graph_id = None
        if enable_graph_memory_update:
            graph_id = state.graph_id
            if not graph_id:
                project = ProjectManager.get_project(state.project_id)
                if project:
                    graph_id = project.graph_id
            
            if not graph_id:
                return jsonify({
                    "success": False,
                    "error": "启用图谱记忆更新需要有效的 graph_id，请确保项目已构建图谱"
                }), 400
            
            logger.info(f"启用图谱记忆更新: simulation_id={simulation_id}, graph_id={graph_id}")
        
        # 启动模拟
        run_state = SimulationRunner.start_simulation(
            simulation_id=simulation_id,
            platform=platform,
            max_rounds=max_rounds,
            enable_graph_memory_update=enable_graph_memory_update,
            graph_id=graph_id,
            resume=resume
        )
        
        # 更新模拟状态
        state.status = SimulationStatus.RUNNING
        manager._save_simulation_state(state)
        
        response_data = run_state.to_dict()
        if max_rounds:
            response_data['max_rounds_applied'] = max_rounds
        response_data['graph_memory_update_enabled'] = enable_graph_memory_update
        response_data['force_restarted'] = force_restarted
        response_data['resumed'] = resume
        if enable_graph_memory_update:
            response_data['graph_id'] = graph_id
        
        return jsonify({
            "success": True,
            "data": response_data
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"启动模拟失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/stop', methods=['POST'])
def stop_simulation():
    """
    停止模拟
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx"  // 必填，模拟ID
        }
    
    Returns:
        停止后的状态信息
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        run_state = SimulationRunner.stop_simulation(simulation_id)
        
        # 更新模拟状态
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if state:
            state.status = SimulationStatus.PAUSED
            manager._save_simulation_state(state)
        
        return jsonify({
            "success": True,
            "data": run_state.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"停止模拟失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/<simulation_id>/resumable', methods=['GET'])
def check_resumable(simulation_id: str):
    """
    检查模拟是否可以恢复
    
    Args:
        simulation_id: 模拟ID
    
    Returns:
        可恢复状态信息，包含进度和数据详情
    """
    try:
        # 检查模拟是否存在
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": f"模拟不存在: {simulation_id}"
            }), 404
        
        # 获取运行状态
        run_state = SimulationRunner.get_run_state(simulation_id)
        
        # 检查数据文件是否存在
        sim_dir = os.path.join(SimulationRunner.RUN_STATE_DIR, simulation_id)
        twitter_db = os.path.join(sim_dir, "twitter_simulation.db")
        reddit_db = os.path.join(sim_dir, "reddit_simulation.db")
        has_twitter_data = os.path.exists(twitter_db)
        has_reddit_data = os.path.exists(reddit_db)
        has_data = has_twitter_data or has_reddit_data
        
        # 判断是否可以恢复
        resumable = False
        current_round = 0
        total_rounds = 0
        progress_percent = 0
        last_run_time = None
        twitter_actions = 0
        reddit_actions = 0
        
        if run_state:
            current_round = run_state.current_round
            total_rounds = run_state.total_rounds
            twitter_actions = run_state.twitter_actions_count
            reddit_actions = run_state.reddit_actions_count
            
            if total_rounds > 0:
                progress_percent = int((current_round / total_rounds) * 100)
            
            # 可以恢复的条件
            if (run_state.runner_status.value in ['paused', 'stopped'] and 
                current_round > 0 and 
                current_round < total_rounds and
                has_data):
                resumable = True
            
            # 获取最后运行时间
            if run_state.completed_at:
                last_run_time = run_state.completed_at
            elif run_state.started_at:
                last_run_time = run_state.started_at
        
        return jsonify({
            "success": True,
            "data": {
                "resumable": resumable,
                "current_round": current_round,
                "total_rounds": total_rounds,
                "progress_percent": progress_percent,
                "last_run_time": last_run_time,
                "status": state.status.value,
                "runner_status": run_state.runner_status.value if run_state else None,
                "has_data": has_data,
                "has_twitter_data": has_twitter_data,
                "has_reddit_data": has_reddit_data,
                "twitter_actions": twitter_actions,
                "reddit_actions": reddit_actions
            }
        })
        
    except Exception as e:
        logger.error(f"检查可恢复状态失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/<simulation_id>', methods=['DELETE'])
def delete_simulation(simulation_id: str):
    """
    删除推演记录
    
    流程：
    1. 删除该 simulation 关联的所有报告
    2. 调用 SimulationManager.delete_simulation（内部会先停止运行中的模拟、清理内存、删除目录）
    
    Args:
        simulation_id: 模拟ID
    """
    try:
        # 校验 simulation_id 格式（防止路径遍历）
        if not simulation_id or not simulation_id.startswith('sim_'):
            return jsonify(get_error_response(
                error="无效的模拟ID格式",
                status_code=400,
                error_code=ErrorCode.INVALID_INPUT
            )), 400
        
        # 1. 删除该 simulation 关联的所有报告
        report_ids = _get_report_ids_for_simulation(simulation_id)
        deleted_reports = []
        failed_reports = []
        
        for report_id in report_ids:
            try:
                success = ReportManager.delete_report(report_id)
                if success:
                    deleted_reports.append(report_id)
                    logger.info(f"已删除报告: {report_id} (simulation: {simulation_id})")
                else:
                    failed_reports.append(report_id)
                    logger.warning(f"报告不存在或删除失败: {report_id}")
            except Exception as e:
                failed_reports.append(report_id)
                logger.error(f"删除报告失败: {report_id}, error={e}")
        
        # 2. 删除模拟记录（内部会先停止运行中的模拟、清理内存、删除目录）
        manager = SimulationManager()
        manager.delete_simulation(simulation_id)
        
        message = f"推演记录已删除: {simulation_id}"
        if deleted_reports:
            message += f"，已删除 {len(deleted_reports)} 个关联报告"
        if failed_reports:
            message += f"，{len(failed_reports)} 个报告删除失败（可能已不存在）"
        
        return jsonify({
            "success": True,
            "message": message,
            "deleted_reports": deleted_reports,
            "failed_reports": failed_reports if failed_reports else None
        }), 200
        
    except ValueError as e:
        # 停止模拟失败等情况
        return jsonify(get_error_response(
            error=str(e),
            status_code=400,
            error_code=ErrorCode.INVALID_INPUT
        )), 400
        
    except Exception as e:
        logger.error(f"删除推演记录失败: {simulation_id}, error={str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500
