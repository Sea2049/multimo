# 测试报告生成模块

import sys
import json
from app.modules.report import DataAnalyzer, ReportGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_data_analyzer():
    """测试数据分析器"""
    logger.info("=" * 50)
    logger.info("测试数据分析器")
    logger.info("=" * 50)
    
    # 创建测试数据
    test_simulation_data = [
        {
            "step": 0,
            "platform": "twitter",
            "timestamp": "2026-01-19T16:52:18",
            "actions": [
                {
                    "agent_id": 1,
                    "agent_name": "业委会",
                    "action": {
                        "action_type": "post",
                        "content": "业委会通知：关于'引入第三方资金平台'议题，根据区住建局及市局规定，需作为单一议题且附带风险提示。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                },
                {
                    "agent_id": 2,
                    "agent_name": "物业办工作人员",
                    "action": {
                        "action_type": "post",
                        "content": "物业办公告：近期有业主咨询'第三方资金平台'事宜。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                }
            ]
        },
        {
            "step": 1,
            "platform": "twitter",
            "timestamp": "2026-01-19T16:52:19",
            "actions": [
                {
                    "agent_id": 3,
                    "agent_name": "业主",
                    "action": {
                        "action_type": "reply",
                        "content": "支持这个决定，保障业主知情权很重要。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                },
                {
                    "agent_id": 4,
                    "agent_name": "王亮组长",
                    "action": {
                        "action_type": "like",
                        "content": "",
                        "target": 1
                    },
                    "result": None,
                    "success": True
                }
            ]
        },
        {
            "step": 2,
            "platform": "reddit",
            "timestamp": "2026-01-19T16:52:20",
            "actions": [
                {
                    "agent_id": 1,
                    "agent_name": "业委会",
                    "action": {
                        "action_type": "post",
                        "content": "Reddit上的讨论：我们需要更透明的资金管理机制。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                }
            ]
        }
    ]
    
    # 创建数据分析器
    analyzer = DataAnalyzer()
    
    # 分析数据
    analysis = analyzer.analyze_simulation_data(test_simulation_data)
    
    # logger.info(f"基础统计: {json.dumps(analysis['basic_statistics'], ensure_ascii=False, indent=2)}")
    # logger.info(f"动作统计: {json.dumps(analysis['action_statistics'], ensure_ascii=False, indent=2)}")
    # logger.info(f"智能体统计: {json.dumps(analysis['agent_statistics'], ensure_ascii=False, indent=2)}")
    # logger.info(f"关键事件数量: {len(analysis['key_events'])}")
    
    # 生成摘要
    summary = analyzer.get_summary(analysis)
    # logger.info(f"\n分析摘要:\n{summary}")
    
    logger.info("\n✅ 数据分析器测试通过")
    return analysis


def test_report_generator():
    """测试报告生成器"""
    logger.info("\n" + "=" * 50)
    logger.info("测试报告生成器")
    logger.info("=" * 50)
    
    # 创建测试数据
    test_simulation_data = [
        {
            "step": 0,
            "platform": "twitter",
            "timestamp": "2026-01-19T16:52:18",
            "actions": [
                {
                    "agent_id": 1,
                    "agent_name": "业委会",
                    "action": {
                        "action_type": "post",
                        "content": "业委会通知：关于'引入第三方资金平台'议题，根据区住建局及市局规定，需作为单一议题且附带风险提示。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                }
            ]
        },
        {
            "step": 1,
            "platform": "twitter",
            "timestamp": "2026-01-19T16:52:19",
            "actions": [
                {
                    "agent_id": 2,
                    "agent_name": "业主",
                    "action": {
                        "action_type": "reply",
                        "content": "支持这个决定，保障业主知情权很重要。",
                        "target": None
                    },
                    "result": None,
                    "success": True
                }
            ]
        }
    ]
    
    # 创建报告生成器（不实际调用 LLM，只测试逻辑）
    generator = ReportGenerator()
    
    # 测试简化报告生成（不调用 LLM）
    logger.info("测试简化报告生成（不调用 LLM）...")
    
    # 首先测试数据分析
    analyzer = DataAnalyzer()
    analysis = analyzer.analyze_simulation_data(test_simulation_data)
    
    # logger.info(f"分析结果: {json.dumps(analysis['basic_statistics'], ensure_ascii=False)}")
    # logger.info(f"分析摘要: {analyzer.get_summary(analysis)}")
    
    logger.info("\n✅ 报告生成器逻辑测试通过（未调用 LLM）")
    
    # 注意：实际调用 LLM 需要配置 API 密钥，这里只测试逻辑
    logger.info("\n注意：完整的报告生成需要配置 LLM_API_KEY")


def test_to_markdown():
    """测试 Markdown 转换"""
    logger.info("\n" + "=" * 50)
    logger.info("测试 Markdown 转换")
    logger.info("=" * 50)
    
    # 创建测试报告数据
    test_report = {
        "report_id": "test_report_001",
        "query": "分析业主对引入第三方资金平台的看法",
        "simulation_requirement": "模拟业主对第三方资金平台的讨论",
        "generated_at": "2026-01-19T16:52:18",
        "summary": "本报告分析了模拟中业主对引入第三方资金平台的看法。",
        "sections": [
            {
                "title": "模拟概述",
                "description": "介绍模拟背景、目的和基本情况",
                "content": "本次模拟分析了业主对引入第三方资金平台的态度。",
                "subsections": [
                    {
                        "title": "模拟场景",
                        "description": "描述模拟设定的场景和条件",
                        "content": "模拟场景设定在住宅小区，涉及业主、业委会、物业办等角色。"
                    },
                    {
                        "title": "关键发现",
                        "description": "总结模拟中的主要发现",
                        "content": "模拟发现业主普遍关注资金透明度和安全性。"
                    }
                ]
            },
            {
                "title": "结论与建议",
                "description": "总结结论并提出建议",
                "content": "建议在引入第三方平台前进行充分的风险评估。",
                "subsections": []
            }
        ]
    }
    
    # 创建报告生成器
    generator = ReportGenerator()
    
    # 转换为 Markdown
    markdown = generator.to_markdown(test_report)
    
    # logger.info("生成的 Markdown 内容:\n")
    # logger.info(markdown)
    
    logger.info("\n✅ Markdown 转换测试通过")
    return markdown
