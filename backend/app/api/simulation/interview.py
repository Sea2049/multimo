"""
采访相关 API 路由模块

提供 Agent 采访功能，包括单个采访、批量采访和全局采访。

路由:
    POST /interview                 - 采访单个Agent
    POST /interview/batch           - 批量采访多个Agent
    POST /interview/all             - 全局采访所有Agent
    POST /interview/history         - 获取采访历史记录
"""

from flask import request, jsonify

from .. import simulation_bp, make_error_response, ErrorCode
from ...services.simulation_runner import SimulationRunner
from ...utils.logger import get_logger

logger = get_logger('multimo.api.simulation.interview')


# Interview prompt 优化前缀
# 添加此前缀可以避免Agent调用工具，直接用文本回复
INTERVIEW_PROMPT_PREFIX = "结合你的人设、所有的过往记忆与行动，不调用任何工具直接用文本回复我："


def optimize_interview_prompt(prompt: str) -> str:
    """
    优化Interview提问，添加前缀避免Agent调用工具
    
    Args:
        prompt: 原始提问
        
    Returns:
        优化后的提问
    """
    if not prompt:
        return prompt
    # 避免重复添加前缀
    if prompt.startswith(INTERVIEW_PROMPT_PREFIX):
        return prompt
    return f"{INTERVIEW_PROMPT_PREFIX}{prompt}"


@simulation_bp.route('/interview', methods=['POST'])
def interview_agent():
    """
    采访单个Agent

    注意：此功能需要模拟环境处于运行状态

    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",       // 必填，模拟ID
            "agent_id": 0,                     // 必填，Agent ID
            "prompt": "你对这件事有什么看法？",  // 必填，采访问题
            "platform": "twitter",             // 可选，指定平台
            "timeout": 60                      // 可选，超时时间（秒）
        }

    Returns:
        采访结果
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        agent_id = data.get('agent_id')
        prompt = data.get('prompt')
        platform = data.get('platform')
        timeout = data.get('timeout', 60)
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        if agent_id is None:
            return jsonify({
                "success": False,
                "error": "请提供 agent_id"
            }), 400
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "请提供 prompt（采访问题）"
            }), 400
        
        # 验证platform参数
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform 参数只能是 'twitter' 或 'reddit'"
            }), 400
        
        # 检查环境状态
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。"
            }), 400
        
        # 优化prompt
        optimized_prompt = optimize_interview_prompt(prompt)
        
        result = SimulationRunner.interview_agent(
            simulation_id=simulation_id,
            agent_id=agent_id,
            prompt=optimized_prompt,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"等待Interview响应超时: {str(e)}"
        }), 504
        
    except Exception as e:
        logger.error(f"Interview失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/interview/batch', methods=['POST'])
def interview_agents_batch():
    """
    批量采访多个Agent

    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",
            "interviews": [
                {"agent_id": 0, "prompt": "问题1", "platform": "twitter"},
                {"agent_id": 1, "prompt": "问题2"}
            ],
            "platform": "reddit",
            "timeout": 120
        }

    Returns:
        批量采访结果
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        interviews = data.get('interviews')
        platform = data.get('platform')
        # 根据采访数量动态设置超时
        interview_count = len(interviews) if interviews else 0
        default_timeout = min(max(interview_count * 15, 120), 900)
        timeout = data.get('timeout', default_timeout)

        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400

        if not interviews or not isinstance(interviews, list):
            return jsonify({
                "success": False,
                "error": "请提供 interviews（采访列表）"
            }), 400

        # 验证platform参数
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform 参数只能是 'twitter' 或 'reddit'"
            }), 400

        # 验证每个采访项
        for i, interview in enumerate(interviews):
            if 'agent_id' not in interview:
                return jsonify({
                    "success": False,
                    "error": f"采访列表第{i+1}项缺少 agent_id"
                }), 400
            if 'prompt' not in interview:
                return jsonify({
                    "success": False,
                    "error": f"采访列表第{i+1}项缺少 prompt"
                }), 400
            item_platform = interview.get('platform')
            if item_platform and item_platform not in ("twitter", "reddit"):
                return jsonify({
                    "success": False,
                    "error": f"采访列表第{i+1}项的platform只能是 'twitter' 或 'reddit'"
                }), 400

        # 检查环境状态
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。"
            }), 400

        # 优化每个采访项的prompt
        optimized_interviews = []
        for interview in interviews:
            optimized_interview = interview.copy()
            optimized_interview['prompt'] = optimize_interview_prompt(interview.get('prompt', ''))
            optimized_interviews.append(optimized_interview)

        result = SimulationRunner.interview_agents_batch(
            simulation_id=simulation_id,
            interviews=optimized_interviews,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"等待批量Interview响应超时: {str(e)}"
        }), 504

    except Exception as e:
        logger.error(f"批量Interview失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/interview/all', methods=['POST'])
def interview_all_agents():
    """
    全局采访 - 使用相同问题采访所有Agent

    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",
            "prompt": "你对这件事整体有什么看法？",
            "platform": "reddit",
            "timeout": 180
        }

    Returns:
        全局采访结果
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        prompt = data.get('prompt')
        platform = data.get('platform')
        timeout = data.get('timeout', 180)

        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400

        if not prompt:
            return jsonify({
                "success": False,
                "error": "请提供 prompt（采访问题）"
            }), 400

        # 验证platform参数
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform 参数只能是 'twitter' 或 'reddit'"
            }), 400

        # 检查环境状态
        if not SimulationRunner.check_env_alive(simulation_id):
            return jsonify({
                "success": False,
                "error": "模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。"
            }), 400

        # 优化prompt
        optimized_prompt = optimize_interview_prompt(prompt)

        result = SimulationRunner.interview_all_agents(
            simulation_id=simulation_id,
            prompt=optimized_prompt,
            platform=platform,
            timeout=timeout
        )

        return jsonify({
            "success": result.get("success", False),
            "data": result
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    except TimeoutError as e:
        return jsonify({
            "success": False,
            "error": f"等待全局Interview响应超时: {str(e)}"
        }), 504

    except Exception as e:
        logger.error(f"全局Interview失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500


@simulation_bp.route('/interview/history', methods=['POST'])
def get_interview_history():
    """
    获取Interview历史记录

    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",
            "platform": "reddit",
            "agent_id": 0,
            "limit": 100
        }

    Returns:
        采访历史记录列表
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        platform = data.get('platform')
        agent_id = data.get('agent_id')
        limit = data.get('limit', 100)
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": "请提供 simulation_id"
            }), 400
        
        # 验证platform参数
        if platform and platform not in ("twitter", "reddit"):
            return jsonify({
                "success": False,
                "error": "platform 参数只能是 'twitter' 或 'reddit'"
            }), 400
        
        result = SimulationRunner.get_interview_history(
            simulation_id=simulation_id,
            platform=platform,
            agent_id=agent_id,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"获取Interview历史失败: {str(e)}")
        return jsonify(make_error_response(e, 500, ErrorCode.INTERNAL_ERROR)), 500
