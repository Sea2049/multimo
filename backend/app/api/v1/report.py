# 报告相关路由

import json
import os
from flask import request, jsonify, g
from app.api import api_v1_bp, get_response, get_error_response
from app.api.decorators import require_user_auth, require_simulation_owner
from app.utils import get_logger, validate_api_request
from app.modules.report import ReportGenerator
from app.services.simulation_manager import SimulationManager
from app.models.project import ProjectManager
from app.config_new import get_config

logger = get_logger(__name__)


def _load_simulation_data(simulation_id: str) -> list:
    """加载模拟数据
    
    Args:
        simulation_id: 模拟ID
        
    Returns:
        模拟数据列表
    """
    sim_manager = SimulationManager()
    sim_dir = sim_manager._get_simulation_dir(simulation_id)
    
    if not os.path.exists(sim_dir):
        logger.error(f"模拟数据目录不存在: {sim_dir}")
        return []
    
    simulation_data = []
    
    # 读取 Twitter 动作数据
    twitter_actions_path = os.path.join(sim_dir, "twitter", "actions.jsonl")
    if os.path.exists(twitter_actions_path):
        with open(twitter_actions_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    action_data = json.loads(line.strip())
                    # 转换为标准格式
                    if action_data.get("event_type") == "round_end":
                        round_num = action_data.get("round", 0)
                        simulation_data.append({
                            "step": round_num,
                            "platform": "twitter",
                            "timestamp": action_data.get("timestamp"),
                            "actions": []
                        })
                    elif "agent_id" in action_data and "action_type" in action_data:
                        # 查找对应的 step
                        round_num = action_data.get("round", 0)
                        step_data = next(
                            (s for s in simulation_data if s["step"] == round_num and s["platform"] == "twitter"),
                            None
                        )
                        if step_data is None:
                            step_data = {
                                "step": round_num,
                                "platform": "twitter",
                                "timestamp": action_data.get("timestamp"),
                                "actions": []
                            }
                            simulation_data.append(step_data)
                        
                        # 转换动作格式
                        step_data["actions"].append({
                            "agent_id": action_data.get("agent_id"),
                            "agent_name": action_data.get("agent_name"),
                            "action": {
                                "action_type": _convert_action_type(action_data.get("action_type")),
                                "content": action_data.get("action_args", {}).get("content", ""),
                                "target": None
                            },
                            "result": action_data.get("result"),
                            "success": action_data.get("success", True)
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 Twitter 动作数据失败: {e}")
    
    # 读取 Reddit 动作数据
    reddit_actions_path = os.path.join(sim_dir, "reddit", "actions.jsonl")
    if os.path.exists(reddit_actions_path):
        with open(reddit_actions_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    action_data = json.loads(line.strip())
                    if action_data.get("event_type") == "round_end":
                        round_num = action_data.get("round", 0)
                        simulation_data.append({
                            "step": round_num,
                            "platform": "reddit",
                            "timestamp": action_data.get("timestamp"),
                            "actions": []
                        })
                    elif "agent_id" in action_data and "action_type" in action_data:
                        round_num = action_data.get("round", 0)
                        step_data = next(
                            (s for s in simulation_data if s["step"] == round_num and s["platform"] == "reddit"),
                            None
                        )
                        if step_data is None:
                            step_data = {
                                "step": round_num,
                                "platform": "reddit",
                                "timestamp": action_data.get("timestamp"),
                                "actions": []
                            }
                            simulation_data.append(step_data)
                        
                        step_data["actions"].append({
                            "agent_id": action_data.get("agent_id"),
                            "agent_name": action_data.get("agent_name"),
                            "action": {
                                "action_type": _convert_action_type(action_data.get("action_type")),
                                "content": action_data.get("action_args", {}).get("content", ""),
                                "target": None
                            },
                            "result": action_data.get("result"),
                            "success": action_data.get("success", True)
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"解析 Reddit 动作数据失败: {e}")
    
    # 按 step 和 platform 排序
    simulation_data.sort(key=lambda x: (x["step"], x["platform"]))
    
    logger.info(f"加载模拟数据成功，共 {len(simulation_data)} 步")
    return simulation_data


def _convert_action_type(action_type: str) -> str:
    """转换动作类型
    
    Args:
        action_type: 原始动作类型
        
    Returns:
        转换后的动作类型
    """
    type_mapping = {
        "CREATE_POST": "post",
        "REPLY_POST": "reply",
        "LIKE_POST": "like",
        "SHARE_POST": "share",
        "RETWEET": "retweet"
    }
    return type_mapping.get(action_type, action_type.lower())


@api_v1_bp.route("/report/generate", methods=["POST"])
@require_user_auth
@require_simulation_owner("simulation_id")
def generate_report():
    """生成报告"""
    try:
        # 验证请求
        data = request.get_json()
        validation_result = validate_api_request(data, ["simulation_id", "query"])
        
        if not validation_result.is_valid:
            return jsonify(get_error_response(validation_result.get_error_messages()[0], 400)), 400
        
        simulation_id = data.get("simulation_id")
        query = data.get("query")
        simulation_requirement = data.get("simulation_requirement", "")
        
        logger.info(f"接收到报告生成请求: simulation_id={simulation_id}, query={query}")
        
        # 获取模拟状态
        sim_manager = SimulationManager()
        simulation_state = sim_manager.get_simulation(simulation_id)
        
        if not simulation_state:
            return jsonify(get_error_response("模拟不存在", 404)), 404
        
        # 检查模拟状态
        if simulation_state.status.value not in ["completed", "stopped"]:
            return jsonify(get_error_response(
                "模拟尚未完成，请等待模拟完成后再生成报告",
                400
            )), 400
        
        # 获取项目信息（获取模拟需求）
        project_id = simulation_state.project_id
        project_manager = ProjectManager()
        project = project_manager.get_project(project_id)
        
        if project:
            simulation_requirement = simulation_requirement or project.requirement
        
        # 加载模拟数据
        simulation_data = _load_simulation_data(simulation_id)
        
        if not simulation_data:
            return jsonify(get_error_response("模拟数据为空", 400)), 400
        
        # 生成报告
        generator = ReportGenerator()
        report = generator.generate(
            simulation_data=simulation_data,
            query=query,
            simulation_requirement=simulation_requirement,
            progress_callback=None
        )
        
        # 保存报告到文件
        report_dir = os.path.join(sim_manager.SIMULATION_DATA_DIR, simulation_id, "report")
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, "report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存 Markdown 格式
        md_report = generator.to_markdown(report)
        md_file = os.path.join(report_dir, "report.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        logger.info(f"报告生成完成: {report_file}")
        
        return jsonify(get_response({
            "report_id": report["report_id"],
            "report": report,
            "markdown": md_report,
            "message": "报告生成成功"
        })), 200
        
    except Exception as e:
        logger.error(f"报告生成失败: {e}", exc_info=True)
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/report/<simulation_id>", methods=["GET"])
@require_user_auth
@require_simulation_owner("simulation_id")
def get_report(simulation_id: str):
    """获取报告"""
    try:
        logger.info(f"接收到获取报告请求: simulation_id={simulation_id}")
        
        # 获取模拟状态
        sim_manager = SimulationManager()
        simulation_state = sim_manager.get_simulation(simulation_id)
        
        if not simulation_state:
            return jsonify(get_error_response("模拟不存在", 404)), 404
        
        # 读取报告文件
        report_dir = os.path.join(sim_manager.SIMULATION_DATA_DIR, simulation_id, "report")
        report_file = os.path.join(report_dir, "report.json")
        
        if not os.path.exists(report_file):
            return jsonify(get_error_response("报告不存在，请先生成报告", 404)), 404
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return jsonify(get_response({
            "report": report,
            "message": "报告获取成功"
        })), 200
        
    except Exception as e:
        logger.error(f"获取报告失败: {e}", exc_info=True)
        return jsonify(get_error_response(str(e), 500)), 500


@api_v1_bp.route("/report/<simulation_id>/markdown", methods=["GET"])
def get_report_markdown(simulation_id: str):
    """获取 Markdown 格式的报告"""
    try:
        logger.info(f"接收到获取 Markdown 报告请求: simulation_id={simulation_id}")
        
        sim_manager = SimulationManager()
        report_dir = os.path.join(sim_manager.SIMULATION_DATA_DIR, simulation_id, "report")
        md_file = os.path.join(report_dir, "report.md")
        
        if not os.path.exists(md_file):
            return jsonify(get_error_response("报告不存在，请先生成报告", 404)), 404
        
        with open(md_file, 'r', encoding='utf-8') as f:
            markdown = f.read()
        
        return jsonify(get_response({
            "markdown": markdown,
            "message": "Markdown 报告获取成功"
        })), 200
        
    except Exception as e:
        logger.error(f"获取 Markdown 报告失败: {e}", exc_info=True)
        return jsonify(get_error_response(str(e), 500)), 500


from flask import send_file


def _get_report_id_for_simulation(simulation_id: str) -> str:
    """
    获取 simulation 对应的最新 report_id
    
    遍历 reports 目录，找出 simulation_id 匹配的 report，
    如果有多个则返回最新的（按 created_at 排序）
    """
    import json
    
    # reports 目录路径
    reports_dir = os.path.join(get_config().UPLOAD_FOLDER, 'reports')
    if not os.path.exists(reports_dir):
        return None
    
    matching_reports = []
    
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
                    matching_reports.append({
                        "report_id": meta.get("report_id"),
                        "created_at": meta.get("created_at", ""),
                        "status": meta.get("status", "")
                    })
            except Exception:
                continue
        
        if not matching_reports:
            return None
        
        # 按创建时间倒序排序，返回最新的
        matching_reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return matching_reports[0].get("report_id")
        
    except Exception as e:
        logger.warning(f"查找 simulation {simulation_id} 的 report 失败: {e}")
        return None


@api_v1_bp.route("/report/<simulation_id>/download", methods=["GET"])
@require_user_auth
@require_simulation_owner("simulation_id")
def download_report(simulation_id: str):
    """下载报告文件"""
    try:
        format_type = request.args.get("format", "markdown")  # markdown, json
        logger.info(f"接收到下载报告请求: simulation_id={simulation_id}, format={format_type}")
        
        # 通过 simulation_id 找到对应的 report_id
        report_id = _get_report_id_for_simulation(simulation_id)
        
        if not report_id:
            return jsonify(get_error_response(
                "找不到该模拟的报告，请先生成报告", 404
            )), 404
        
        # 报告存储在 uploads/reports/{report_id}/ 目录
        reports_dir = os.path.join(get_config().UPLOAD_FOLDER, 'reports')
        report_dir = os.path.join(reports_dir, report_id)
        
        if format_type == "json":
            # 尝试读取 meta.json 或 outline.json
            file_path = os.path.join(report_dir, "meta.json")
            if not os.path.exists(file_path):
                file_path = os.path.join(report_dir, "outline.json")
            mimetype = "application/json"
            download_name = f"report_{simulation_id}.json"
        else:
            # 优先使用 full_report.md，否则尝试合并各章节
            file_path = os.path.join(report_dir, "full_report.md")
            if not os.path.exists(file_path):
                # 尝试合并各章节文件
                sections = []
                for i in range(1, 20):  # 最多支持 20 个章节
                    section_file = os.path.join(report_dir, f"section_{i:02d}.md")
                    if os.path.exists(section_file):
                        with open(section_file, 'r', encoding='utf-8') as f:
                            sections.append(f.read())
                    else:
                        break
                
                if sections:
                    # 创建临时合并文件
                    combined_content = "\n\n---\n\n".join(sections)
                    file_path = os.path.join(report_dir, "combined_report.md")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(combined_content)
            
            mimetype = "text/markdown"
            download_name = f"report_{simulation_id}.md"
            
        if not os.path.exists(file_path):
            return jsonify(get_error_response(
                "报告文件不存在，可能报告尚未生成完成", 404
            )), 404
            
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"下载报告失败: {e}", exc_info=True)
        return jsonify(get_error_response(str(e), 500)), 500
@api_v1_bp.route("/report/list", methods=["GET"])
@require_user_auth
def list_reports():
    """列出当前用户的报告（仅归属为当前用户项目的模拟下的报告）"""
    try:
        logger.info("接收到列出报告请求")
        user_project_ids = set(ProjectManager._get_storage().list_project_ids_by_user(g.current_user["id"]))
        sim_manager = SimulationManager()
        reports = []
        simulations_dir = sim_manager.SIMULATION_DATA_DIR
        if not os.path.exists(simulations_dir):
            return jsonify(get_response({
                "reports": [],
                "message": "没有报告"
            })), 200

        for sim_id in os.listdir(simulations_dir):
            report_dir = os.path.join(simulations_dir, sim_id, "report")
            if not os.path.isdir(report_dir):
                continue
            report_file = os.path.join(report_dir, "report.json")
            if not os.path.exists(report_file):
                continue
            simulation_state = sim_manager.get_simulation(sim_id)
            if not simulation_state or simulation_state.project_id not in user_project_ids:
                continue
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                reports.append({
                    "simulation_id": sim_id,
                    "report_id": report.get("report_id"),
                    "query": report.get("query"),
                    "generated_at": report.get("generated_at"),
                    "generation_time": report.get("generation_time"),
                    "project_id": simulation_state.project_id,
                })
            except Exception as e:
                logger.warning(f"读取报告失败: {sim_id}, 错误: {e}")

        reports.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        return jsonify(get_response({
            "reports": reports,
            "count": len(reports),
            "message": "报告列表获取成功"
        })), 200
    except Exception as e:
        logger.error(f"列出报告失败: {e}", exc_info=True)
        return jsonify(get_error_response(str(e), 500)), 500
