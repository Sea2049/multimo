# 数据分析器

from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime
import statistics

from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataAnalyzer:
    """数据分析器
    
    负责分析模拟数据，提取统计信息和关键指标
    """
    
    def __init__(self):
        """初始化数据分析器"""
        self.cached_stats = None
        self.cached_raw_data = None
    
    def analyze_simulation_data(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析模拟数据
        
        Args:
            simulation_data: 模拟数据列表，每一步的数据包含 actions 和 environment_state
            
        Returns:
            分析结果，包含各种统计指标
        """
        if not simulation_data:
            return self._empty_analysis()
        
        logger.info(f"开始分析模拟数据，共 {len(simulation_data)} 步")
        
        # 基础统计
        basic_stats = self._calculate_basic_stats(simulation_data)
        
        # 动作分析
        action_stats = self._analyze_actions(simulation_data)
        
        # 智能体分析
        agent_stats = self._analyze_agents(simulation_data)
        
        # 时间趋势分析
        time_trends = self._analyze_time_trends(simulation_data)
        
        # 关键事件提取
        key_events = self._extract_key_events(simulation_data)
        
        result = {
            "basic_statistics": basic_stats,
            "action_statistics": action_stats,
            "agent_statistics": agent_stats,
            "time_trends": time_trends,
            "key_events": key_events,
            "analysis_metadata": {
                "total_steps": len(simulation_data),
                "analyzed_at": datetime.now().isoformat()
            }
        }
        
        logger.info("模拟数据分析完成")
        return result
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """返回空数据的分析结果"""
        return {
            "basic_statistics": {
                "total_steps": 0,
                "total_actions": 0,
                "average_actions_per_step": 0
            },
            "action_statistics": {
                "total_by_type": {},
                "distribution": {},
                "most_common_actions": []
            },
            "agent_statistics": {
                "total_agents": 0,
                "agent_activity": {},
                "most_active_agents": []
            },
            "time_trends": {
                "action_volume_over_time": [],
                "agent_participation_over_time": []
            },
            "key_events": [],
            "analysis_metadata": {
                "total_steps": 0,
                "analyzed_at": datetime.now().isoformat()
            }
        }
    
    def _calculate_basic_stats(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算基础统计信息"""
        total_steps = len(simulation_data)
        total_actions = sum(len(step.get("actions", [])) for step in simulation_data)
        avg_actions_per_step = total_actions / total_steps if total_steps > 0 else 0
        
        return {
            "total_steps": total_steps,
            "total_actions": total_actions,
            "average_actions_per_step": round(avg_actions_per_step, 2)
        }
    
    def _analyze_actions(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析动作统计"""
        action_types = []
        action_contents = []
        
        for step in simulation_data:
            for action_data in step.get("actions", []):
                action = action_data.get("action", {})
                action_type = action.get("action_type", "unknown")
                action_types.append(action_type)
                action_contents.append({
                    "type": action_type,
                    "content": action.get("content", ""),
                    "target": action.get("target")
                })
        
        # 统计动作类型
        type_counts = Counter(action_types)
        total_actions = len(action_types)
        
        # 计算分布
        distribution = {
            action_type: {
                "count": count,
                "percentage": round(count / total_actions * 100, 2) if total_actions > 0 else 0
            }
            for action_type, count in type_counts.items()
        }
        
        # 最常见的动作
        most_common = type_counts.most_common(10)
        
        return {
            "total_by_type": dict(type_counts),
            "distribution": distribution,
            "most_common_actions": [
                {"type": action_type, "count": count} 
                for action_type, count in most_common
            ],
            "total_unique_types": len(type_counts)
        }
    
    def _analyze_agents(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析智能体统计"""
        agent_activities = defaultdict(lambda: {
            "total_actions": 0,
            "action_types": Counter(),
            "first_action": None,
            "last_action": None
        })
        
        for step_idx, step in enumerate(simulation_data):
            for action_data in step.get("actions", []):
                agent_id = action_data.get("agent_id", "unknown")
                action = action_data.get("action", {})
                action_type = action.get("action_type", "unknown")
                
                agent_activities[agent_id]["total_actions"] += 1
                agent_activities[agent_id]["action_types"][action_type] += 1
                
                if agent_activities[agent_id]["first_action"] is None:
                    agent_activities[agent_id]["first_action"] = step_idx
                
                agent_activities[agent_id]["last_action"] = step_idx
        
        # 转换为列表并排序
        agents_list = [
            {
                "agent_id": agent_id,
                "total_actions": stats["total_actions"],
                "action_types": dict(stats["action_types"]),
                "activity_span": stats["last_action"] - stats["first_action"] + 1 
                if stats["first_action"] is not None else 0
            }
            for agent_id, stats in agent_activities.items()
        ]
        
        # 按活跃度排序
        agents_list.sort(key=lambda x: x["total_actions"], reverse=True)
        
        return {
            "total_agents": len(agents_list),
            "agent_activity": {a["agent_id"]: a for a in agents_list},
            "most_active_agents": agents_list[:10],
            "average_actions_per_agent": round(
                sum(a["total_actions"] for a in agents_list) / len(agents_list), 2
            ) if agents_list else 0
        }
    
    def _analyze_time_trends(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析时间趋势"""
        action_volume = []
        agent_participation = []
        
        for step_idx, step in enumerate(simulation_data):
            actions = step.get("actions", [])
            
            # 每步动作数量
            action_volume.append({
                "step": step_idx,
                "action_count": len(actions)
            })
            
            # 参与的智能体数量
            unique_agents = set(action.get("agent_id") for action in actions)
            agent_participation.append({
                "step": step_idx,
                "unique_agents": len(unique_agents),
                "agent_ids": list(unique_agents)
            })
        
        # 计算统计信息
        action_counts = [v["action_count"] for v in action_volume]
        participation_counts = [p["unique_agents"] for p in agent_participation]
        
        return {
            "action_volume_over_time": action_volume,
            "agent_participation_over_time": agent_participation,
            "action_volume_stats": {
                "min": min(action_counts) if action_counts else 0,
                "max": max(action_counts) if action_counts else 0,
                "average": round(statistics.mean(action_counts), 2) if action_counts else 0,
                "median": round(statistics.median(action_counts), 2) if action_counts else 0
            },
            "participation_stats": {
                "min": min(participation_counts) if participation_counts else 0,
                "max": max(participation_counts) if participation_counts else 0,
                "average": round(statistics.mean(participation_counts), 2) if participation_counts else 0
            }
        }
    
    def _extract_key_events(
        self, 
        simulation_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """提取关键事件"""
        key_events = []
        
        for step_idx, step in enumerate(simulation_data):
            for action_data in step.get("actions", []):
                action = action_data.get("action", {})
                action_type = action.get("action_type", "")
                content = action.get("content", "")
                
                # 识别关键事件
                event = None
                
                # 发布内容事件
                if action_type == "post" and content:
                    event = {
                        "type": "content_post",
                        "step": step_idx,
                        "agent_id": action_data.get("agent_id"),
                        "description": f"Agent {action_data.get('agent_id')} 发布了内容",
                        "content": content
                    }
                
                # 互动事件（回复、点赞、转发）
                elif action_type in ["reply", "like", "retweet", "share"]:
                    target = action.get("target")
                    event = {
                        "type": f"{action_type}_action",
                        "step": step_idx,
                        "agent_id": action_data.get("agent_id"),
                        "target_id": target,
                        "description": f"Agent {action_data.get('agent_id')} {action_type} 了 {target}"
                    }
                
                if event:
                    key_events.append(event)
        
        # 按步骤排序，限制数量
        key_events.sort(key=lambda x: x["step"])
        return key_events[:50]
    
    def get_summary(self, analysis: Dict[str, Any]) -> str:
        """生成分析摘要文本
        
        Args:
            analysis: 分析结果
            
        Returns:
            摘要文本
        """
        basic = analysis.get("basic_statistics", {})
        action_stats = analysis.get("action_statistics", {})
        agent_stats = analysis.get("agent_statistics", {})
        
        summary_parts = []
        
        # 基础统计
        summary_parts.append(
            f"模拟共进行了 {basic.get('total_steps', 0)} 步，"
            f"产生了 {basic.get('total_actions', 0)} 个动作，"
            f"平均每步 {basic.get('average_actions_per_step', 0)} 个动作。"
        )
        
        # 动作类型
        most_common = action_stats.get("most_common_actions", [])
        if most_common:
            top_action = most_common[0]
            summary_parts.append(
                f"最常见的动作类型是「{top_action['type']}」，"
                f"共 {top_action['count']} 次。"
            )
        
        # 智能体
        total_agents = agent_stats.get("total_agents", 0)
        avg_actions = agent_stats.get("average_actions_per_agent", 0)
        summary_parts.append(
            f"共有 {total_agents} 个智能体参与模拟，"
            f"平均每个智能体执行 {avg_actions} 个动作。"
        )
        
        return " ".join(summary_parts)
    
    def compare_simulations(
        self, 
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """比较多个模拟的分析结果
        
        Args:
            analyses: 多个分析结果的列表
            
        Returns:
            比较结果
        """
        if not analyses:
            return {"error": "没有提供分析结果"}
        
        comparison = {
            "total_simulations": len(analyses),
            "comparisons": []
        }
        
        for i, analysis in enumerate(analyses):
            basic = analysis.get("basic_statistics", {})
            action_stats = analysis.get("action_statistics", {})
            agent_stats = analysis.get("agent_statistics", {})
            
            comparison["comparisons"].append({
                "simulation_index": i + 1,
                "total_steps": basic.get("total_steps", 0),
                "total_actions": basic.get("total_actions", 0),
                "total_agents": agent_stats.get("total_agents", 0),
                "most_common_action": action_stats.get("most_common_actions", [{}])[0].get("type", "N/A")
            })
        
        return comparison
