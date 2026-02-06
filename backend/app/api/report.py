"""
Report API路由
提供模拟报告生成、获取、对话等接口
提供 API 认证和输入验证
"""

import os
import json
import traceback
import threading
from flask import request, jsonify, send_file, g

from . import report_bp
from . import get_error_response, make_error_response, ErrorCode
from .auth import require_api_key
from ..config_new import get_config
from ..services.report_agent import ReportAgent, ReportManager, ReportStatus
from ..services.simulation_manager import SimulationManager
from ..models.project import ProjectManager
from ..models.task import TaskManager, TaskStatus
from ..utils.logger import get_logger
from ..utils.validators import (
    validate_no_sql_injection,
    sanitize_string,
    validate_graph_id
)

logger = get_logger('multimo.api.report')


# ============== 数据隔离辅助函数 ==============

def _resolve_report_owner(report_id: str):
    """
    校验当前用户是否为报告所有者。
    链路: report -> simulation_id -> project -> project.user_id == g.current_user["id"]

    Returns:
        (report, None) 成功；(None, (response, status_code)) 失败。
    """
    report = ReportManager.get_report(report_id)
    if not report:
        return None, (jsonify(get_error_response(
            error=f"报告不存在: {report_id}",
            status_code=404,
            error_code=ErrorCode.RESOURCE_NOT_FOUND
        )), 404)

    simulation_id = getattr(report, "simulation_id", None)
    if not simulation_id:
        return None, (jsonify(get_error_response(
            error="报告归属未知",
            status_code=403,
            error_code=ErrorCode.FORBIDDEN
        )), 403)

    err = _check_simulation_belongs_to_user(simulation_id)
    if err is not None:
        return None, err

    return report, None


def _check_simulation_belongs_to_user(simulation_id: str):
    """
    校验 simulation_id 对应的项目是否属于当前用户。

    Returns:
        None 表示校验通过；否则返回 (response, status_code)。
    """
    manager = SimulationManager()
    state = manager.get_simulation(simulation_id)
    if not state:
        return (jsonify(get_error_response(
            error=f"模拟不存在: {simulation_id}",
            status_code=404,
            error_code=ErrorCode.RESOURCE_NOT_FOUND
        )), 404)

    project = ProjectManager.get_project(state.project_id)
    if not project:
        return (jsonify(get_error_response(
            error="项目不存在",
            status_code=404,
            error_code=ErrorCode.RESOURCE_NOT_FOUND
        )), 404)

    if getattr(project, "user_id", None) != g.current_user["id"]:
        return (jsonify(get_error_response(
            error="无权访问该资源",
            status_code=403,
            error_code=ErrorCode.FORBIDDEN
        )), 403)

    return None


# ============== 报告生成接口 ==============

@report_bp.route('/generate', methods=['POST'])
@require_api_key(permissions=["write"], signature_required=False)
def generate_report():
    """
    生成模拟分析报告（异步任务）
    
    这是一个耗时操作，接口会立即返回task_id，
    使用 GET /api/report/generate/status 查询进度
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",    // 必填，模拟ID
            "force_regenerate": false        // 可选，强制重新生成
        }
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "task_id": "task_xxxx",
                "status": "generating",
                "message": "报告生成任务已启动"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify(get_error_response(
                error="请提供 simulation_id",
                status_code=400,
                error_code=ErrorCode.INVALID_INPUT
            )), 400
        
        graph_id_result = validate_graph_id(simulation_id, "simulation_id")
        if not graph_id_result.is_valid:
            return jsonify({
                "success": False,
                "error": "无效的 simulation_id 格式",
                "errors": graph_id_result.get_error_messages()
            }), 400
        
        simulation_id = sanitize_string(simulation_id, max_length=100)
        
        sql_result = validate_no_sql_injection(data, "request_data")
        if not sql_result.is_valid:
            return jsonify({
                "success": False,
                "error": "输入包含敏感字符",
                "errors": sql_result.get_error_messages()
            }), 400
        
        force_regenerate = data.get('force_regenerate', False)
        
        # 获取模拟信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify(get_error_response(
                error=f"模拟不存在: {simulation_id}",
                status_code=404,
                error_code=ErrorCode.RESOURCE_NOT_FOUND
            )), 404
        
        # 检查是否已有报告
        if not force_regenerate:
            existing_report = ReportManager.get_report_by_simulation(simulation_id)
            if existing_report and existing_report.status == ReportStatus.COMPLETED:
                return jsonify({
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "report_id": existing_report.report_id,
                        "status": "completed",
                        "message": "报告已存在",
                        "already_generated": True
                    }
                })
        
        # 获取项目信息
        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": f"项目不存在: {state.project_id}"
            }), 404
        
        graph_id = state.graph_id or project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": "缺少图谱ID，请确保已构建图谱"
            }), 400
        
        simulation_requirement = project.simulation_requirement
        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": "缺少模拟需求描述"
            }), 400
        
        # 使用新的持久化任务工作器（支持断点续传）
        from ..services.report_task_worker import get_report_task_worker
        
        worker = get_report_task_worker()
        result = worker.start_report_task(
            simulation_id=simulation_id,
            graph_id=graph_id,
            simulation_requirement=simulation_requirement,
            force_regenerate=force_regenerate,
            user_id=g.current_user["id"],
        )
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "report_id": result.get("report_id"),
                "task_id": result.get("task_id"),
                "status": result.get("status", "pending"),
                "message": result.get("message", "报告生成任务已启动"),
                "already_generated": result.get("already_exists", False)
            }
        })
        
    except Exception as e:
        logger.error(f"启动报告生成任务失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/generate/status', methods=['POST'])
def get_generate_status():
    """
    查询报告生成任务进度（需校验归属）
    
    请求（JSON）：
        {
            "task_id": "task_xxxx",         // 可选，generate返回的task_id
            "simulation_id": "sim_xxxx"     // 可选，模拟ID
        }
    
    返回：
        {
            "success": true,
            "data": {
                "task_id": "task_xxxx",
                "status": "processing|completed|failed",
                "progress": 45,
                "message": "..."
            }
        }
    """
    try:
        data = request.get_json() or {}
        task_id = data.get('task_id')
        simulation_id = data.get('simulation_id')

        # 如果提供了 simulation_id，先校验归属
        if simulation_id:
            err = _check_simulation_belongs_to_user(simulation_id)
            if err is not None:
                return err

            existing_report = ReportManager.get_report_by_simulation(simulation_id)
            if existing_report and existing_report.status == ReportStatus.COMPLETED:
                return jsonify({
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "report_id": existing_report.report_id,
                        "status": "completed",
                        "progress": 100,
                        "message": "报告已生成",
                        "already_completed": True
                    }
                })

        # 如果没有提供 task_id，尝试通过 simulation_id 查找任务
        task_manager = TaskManager()
        if not task_id and simulation_id:
            # 查找该 simulation 对应的报告生成任务
            all_tasks = task_manager.list_tasks(task_type="report_generate", user_id=g.current_user["id"])
            task = None
            for t_dict in all_tasks:
                t_metadata = t_dict.get("metadata", {})
                if isinstance(t_metadata, str):
                    try:
                        t_metadata = json.loads(t_metadata)
                    except:
                        t_metadata = {}
                if t_metadata.get("simulation_id") == simulation_id:
                    # 找到对应的任务，检查状态
                    task_obj = task_manager.get_task(t_dict.get("task_id"))
                    if task_obj:
                        # 只返回进行中的任务（pending 或 processing）
                        if task_obj.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
                            task = task_obj
                            break
                        # 如果任务已完成或失败，继续查找是否有其他进行中的任务
            if not task:
                return jsonify({
                    "success": False,
                    "error": "未找到进行中的报告生成任务"
                }), 404

        if not task_id and not task:
            return jsonify({
                "success": False,
                "error": "请提供 task_id 或 simulation_id"
            }), 400

        # 如果提供了 task_id，获取任务
        if task_id and not task:
            task = task_manager.get_task(task_id)
            if not task:
                return jsonify({
                    "success": False,
                    "error": f"任务不存在: {task_id}"
                }), 404

        # 校验任务归属
        task_user_id = getattr(task, "user_id", None) or (task.metadata or {}).get("user_id")
        if task_user_id is not None and task_user_id != g.current_user["id"]:
            return jsonify(get_error_response(
                error="无权操作该任务",
                status_code=403,
                error_code=ErrorCode.FORBIDDEN
            )), 403

        return jsonify({
            "success": True,
            "data": task.to_dict()
        })
    except Exception as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============== 报告获取接口 ==============

@report_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id: str):
    """
    获取报告详情（仅报告所有者）
    """
    try:
        report, err = _resolve_report_owner(report_id)
        if err is not None:
            return err
        
        return jsonify({
            "success": True,
            "data": report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/by-simulation/<simulation_id>', methods=['GET'])
def get_report_by_simulation(simulation_id: str):
    """
    根据模拟ID获取报告（仅模拟所有者）
    """
    try:
        err = _check_simulation_belongs_to_user(simulation_id)
        if err is not None:
            return err

        report = ReportManager.get_report_by_simulation(simulation_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": f"该模拟暂无报告: {simulation_id}",
                "has_report": False
            }), 404
        
        return jsonify({
            "success": True,
            "data": report.to_dict(),
            "has_report": True
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/list', methods=['GET'])
def list_reports():
    """
    列出当前用户的报告（数据隔离）
    
    Query参数：
        simulation_id: 按模拟ID过滤（可选）
        limit: 返回数量限制（默认50）
    
    返回：
        {
            "success": true,
            "data": [...],
            "count": 10
        }
    """
    try:
        simulation_id = request.args.get('simulation_id')
        limit = request.args.get('limit', 50, type=int)

        # 如果指定了 simulation_id，先校验归属
        if simulation_id:
            err = _check_simulation_belongs_to_user(simulation_id)
            if err is not None:
                return err

        reports = ReportManager.list_reports(
            simulation_id=simulation_id,
            limit=limit
        )

        # 未指定 simulation_id 时，过滤只保留当前用户的报告
        if not simulation_id:
            user_project_ids = set(
                ProjectManager._get_storage().list_project_ids_by_user(
                    g.current_user["id"]
                )
            )
            sim_manager = SimulationManager()
            filtered = []
            for r in reports:
                sid = getattr(r, "simulation_id", None)
                if not sid:
                    continue
                state = sim_manager.get_simulation(sid)
                if state and state.project_id in user_project_ids:
                    filtered.append(r)
            reports = filtered
        
        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in reports],
            "count": len(reports)
        })
        
    except Exception as e:
        logger.error(f"列出报告失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>/download', methods=['GET'])
def download_report(report_id: str):
    """
    下载报告（Markdown格式，仅报告所有者）
    """
    try:
        report, err = _resolve_report_owner(report_id)
        if err is not None:
            return err
        
        md_path = ReportManager._get_report_markdown_path(report_id)
        
        if not os.path.exists(md_path):
            # 如果MD文件不存在，使用内存缓冲区返回
            import io
            buffer = io.BytesIO()
            buffer.write(report.markdown_content.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='text/markdown',
                as_attachment=True,
                download_name=f"{report_id}.md"
            )
        
        return send_file(
            md_path,
            as_attachment=True,
            download_name=f"{report_id}.md"
        )
        
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id: str):
    """删除报告（仅报告所有者）"""
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        success = ReportManager.delete_report(report_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": f"报告不存在: {report_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "message": f"报告已删除: {report_id}"
        })
        
    except Exception as e:
        logger.error(f"删除报告失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== Report Agent对话接口 ==============

@report_bp.route('/chat', methods=['POST'])
def chat_with_report_agent():
    """
    与Report Agent对话
    
    Report Agent可以在对话中自主调用检索工具来回答问题
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",        // 必填，模拟ID
            "message": "请解释一下舆情走向",    // 必填，用户消息
            "chat_history": [                   // 可选，对话历史
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    
    返回：
        {
            "success": true,
            "data": {
                "response": "Agent回复...",
                "tool_calls": [调用的工具列表],
                "sources": [信息来源]
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        if not message:
            return jsonify({
                "success": False,
                "error": "请提供 message"
            }), 400
        
        # 输入验证和清理
        simulation_id = sanitize_string(simulation_id, max_length=100)
        message = sanitize_string(message, max_length=5000)
        
        sql_result = validate_no_sql_injection(message, "message")
        if not sql_result.is_valid:
            return jsonify({
                "success": False,
                "error": "输入包含敏感字符"
            }), 400
        
        # 校验模拟归属（数据隔离）
        err = _check_simulation_belongs_to_user(simulation_id)
        if err is not None:
            return err

        # 获取模拟和项目信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": f"模拟不存在: {simulation_id}"
            }), 404
        
        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": f"项目不存在: {state.project_id}"
            }), 404
        
        graph_id = state.graph_id or project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": "缺少图谱ID"
            }), 400
        
        simulation_requirement = project.simulation_requirement or ""
        
        # 创建Agent并进行对话
        agent = ReportAgent(
            graph_id=graph_id,
            simulation_id=simulation_id,
            simulation_requirement=simulation_requirement
        )
        
        result = agent.chat(message=message, chat_history=chat_history)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"对话失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== 报告进度与分章节接口 ==============

@report_bp.route('/<report_id>/progress', methods=['GET'])
def get_report_progress(report_id: str):
    """
    获取报告生成进度（实时，仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        progress = ReportManager.get_progress(report_id)
        
        if not progress:
            return jsonify({
                "success": False,
                "error": f"报告不存在或进度信息不可用: {report_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "data": progress
        })
        
    except Exception as e:
        logger.error(f"获取报告进度失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>/sections', methods=['GET'])
def get_report_sections(report_id: str):
    """
    获取已生成的章节列表（分章节输出，仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        sections = ReportManager.get_generated_sections(report_id)
        
        # 获取报告状态
        report = ReportManager.get_report(report_id)
        is_complete = report is not None and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "report_id": report_id,
                "sections": sections,
                "total_sections": len(sections),
                "is_complete": is_complete
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节列表失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>/section/<int:section_index>', methods=['GET'])
def get_single_section(report_id: str, section_index: int):
    """
    获取单个章节内容（仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        section_path = ReportManager._get_section_path(report_id, section_index)
        
        if not os.path.exists(section_path):
            return jsonify({
                "success": False,
                "error": f"章节不存在: section_{section_index:02d}.md"
            }), 404
        
        with open(section_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "data": {
                "filename": f"section_{section_index:02d}.md",
                "section_index": section_index,
                "content": content
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节内容失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== 报告状态检查接口 ==============

@report_bp.route('/check/<simulation_id>', methods=['GET'])
def check_report_status(simulation_id: str):
    """
    检查模拟是否有报告，以及报告状态
    
    用于前端判断是否解锁Interview功能
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "has_report": true,
                "report_status": "completed",
                "report_id": "report_xxxx",
                "interview_unlocked": true
            }
        }
    """
    try:
        # 校验模拟归属（数据隔离）
        err = _check_simulation_belongs_to_user(simulation_id)
        if err is not None:
            return err

        report = ReportManager.get_report_by_simulation(simulation_id)
        
        has_report = report is not None
        report_status = report.status.value if report else None
        report_id = report.report_id if report else None
        
        # 只有报告完成后才解锁interview
        interview_unlocked = has_report and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "has_report": has_report,
                "report_status": report_status,
                "report_id": report_id,
                "interview_unlocked": interview_unlocked
            }
        })
        
    except Exception as e:
        logger.error(f"检查报告状态失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== Agent 日志接口 ==============

@report_bp.route('/<report_id>/agent-log', methods=['GET'])
def get_agent_log(report_id: str):
    """
    获取 Report Agent 的详细执行日志（仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_agent_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>/agent-log/stream', methods=['GET'])
def stream_agent_log(report_id: str):
    """
    获取完整的 Agent 日志（仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        logs = ReportManager.get_agent_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== 控制台日志接口 ==============

@report_bp.route('/<report_id>/console-log', methods=['GET'])
def get_console_log(report_id: str):
    """
    获取 Report Agent 的控制台输出日志（仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_console_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/<report_id>/console-log/stream', methods=['GET'])
def stream_console_log(report_id: str):
    """
    获取完整的控制台日志（仅报告所有者）
    """
    try:
        _, err = _resolve_report_owner(report_id)
        if err is not None:
            return err

        logs = ReportManager.get_console_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


# ============== 工具调用接口（供调试使用）==============

@report_bp.route('/tools/search', methods=['POST'])
def search_graph_tool():
    """
    图谱搜索工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "multimo_xxxx",
            "query": "搜索查询",
            "limit": 10
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        query = data.get('query')
        limit = data.get('limit', 10)
        
        if not graph_id or not query:
            return jsonify({
                "success": False,
                "error": "请提供 graph_id 和 query"
            }), 400
        
        # 输入验证和清理
        graph_id = sanitize_string(graph_id, max_length=100)
        query = sanitize_string(query, max_length=1000)
        
        graph_result = validate_graph_id(graph_id, "graph_id")
        if not graph_result.is_valid:
            return jsonify({
                "success": False,
                "error": "无效的 graph_id 格式"
            }), 400
        
        sql_result = validate_no_sql_injection(query, "query")
        if not sql_result.is_valid:
            return jsonify({
                "success": False,
                "error": "输入包含敏感字符"
            }), 400
        
        # 校验图谱归属（数据隔离）
        from .graph import _resolve_graph_owner_project
        _, err = _resolve_graph_owner_project(graph_id)
        if err is not None:
            return err

        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"图谱搜索失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@report_bp.route('/tools/statistics', methods=['POST'])
def get_graph_statistics_tool():
    """
    图谱统计工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "multimo_xxxx"
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        
        if not graph_id:
            return jsonify({
                "success": False,
                "error": "请提供 graph_id"
            }), 400
        
        # 输入验证和清理
        graph_id = sanitize_string(graph_id, max_length=100)
        
        graph_result = validate_graph_id(graph_id, "graph_id")
        if not graph_result.is_valid:
            return jsonify({
                "success": False,
                "error": "无效的 graph_id 格式"
            }), 400
        
        # 校验图谱归属（数据隔离）
        from .graph import _resolve_graph_owner_project
        _, err = _resolve_graph_owner_project(graph_id)
        if err is not None:
            return err

        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.get_graph_statistics(graph_id)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"获取图谱统计失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500
