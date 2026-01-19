# 报告生成器

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from ...utils.llm_client import LLMClient
from ...utils.logger import get_logger
from .analyzer import DataAnalyzer

logger = get_logger(__name__)


class ReportStatus(str, Enum):
    """报告状态"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportGenerator:
    """报告生成器
    
    基于模拟数据生成预测报告
    """
    
    # 报告章节模板
    SECTIONS_TEMPLATE = [
        {
            "title": "模拟概述",
            "description": "介绍模拟背景、目的和基本情况",
            "sections": [
                {"title": "模拟场景", "description": "描述模拟设定的场景和条件"},
                {"title": "关键发现", "description": "总结模拟中的主要发现"}
            ]
        },
        {
            "title": "数据分析",
            "description": "深入分析模拟数据",
            "sections": [
                {"title": "动作统计", "description": "分析各类动作的分布和趋势"},
                {"title": "智能体行为", "description": "分析智能体的行为模式和特征"}
            ]
        },
        {
            "title": "趋势预测",
            "description": "基于模拟结果预测未来趋势",
            "sections": [
                {"title": "发展趋势", "description": "分析事件的发展趋势"},
                {"title": "风险评估", "description": "识别潜在风险和机会"}
            ]
        },
        {
            "title": "结论与建议",
            "description": "总结结论并提出建议",
            "sections": []
        }
    ]
    
    def __init__(
        self, 
        llm_client: Optional[LLMClient] = None,
        analyzer: Optional[DataAnalyzer] = None
    ):
        """初始化报告生成器
        
        Args:
            llm_client: LLM客户端
            analyzer: 数据分析器
        """
        self.llm_client = llm_client or LLMClient()
        self.analyzer = analyzer or DataAnalyzer()
        logger.info("报告生成器初始化完成")
    
    def generate(
        self, 
        simulation_data: List[Dict[str, Any]],
        query: str,
        simulation_requirement: str = "",
        progress_callback: Optional[Callable[[str, int, str], None]] = None
    ) -> Dict[str, Any]:
        """生成报告
        
        Args:
            simulation_data: 模拟数据
            query: 用户查询或报告主题
            simulation_requirement: 模拟需求描述
            progress_callback: 进度回调函数 (stage, progress, message)
            
        Returns:
            生成的报告
        """
        start_time = datetime.now()
        
        logger.info(f"开始生成报告，查询: {query}")
        
        if progress_callback:
            progress_callback("analyzing", 0, "正在分析模拟数据...")
        
        # 分析模拟数据
        analysis = self.analyzer.analyze_simulation_data(simulation_data)
        
        if progress_callback:
            progress_callback("analyzing", 20, "数据分析完成，正在生成报告...")
        
        # 构建报告内容
        report = {
            "report_id": self._generate_report_id(),
            "query": query,
            "simulation_requirement": simulation_requirement,
            "analysis": analysis,
            "generated_at": start_time.isoformat(),
            "sections": []
        }
        
        # 生成各章节
        total_sections = len(self.SECTIONS_TEMPLATE)
        for idx, section_template in enumerate(self.SECTIONS_TEMPLATE):
            progress = 20 + int((idx / total_sections) * 70)
            
            if progress_callback:
                progress_callback(
                    "generating", 
                    progress, 
                    f"正在生成章节: {section_template['title']} ({idx+1}/{total_sections})"
                )
            
            # 生成主章节
            section = self._generate_section(
                section_template=section_template,
                analysis=analysis,
                query=query,
                simulation_requirement=simulation_requirement
            )
            report["sections"].append(section)
            
            logger.info(f"章节已生成: {section_template['title']}")
        
        # 生成总结
        if progress_callback:
            progress_callback("finalizing", 90, "正在生成报告总结...")
        
        summary = self._generate_summary(report, analysis)
        report["summary"] = summary
        
        # 计算耗时
        elapsed_time = (datetime.now() - start_time).total_seconds()
        report["generation_time"] = round(elapsed_time, 2)
        
        if progress_callback:
            progress_callback("completed", 100, "报告生成完成")
        
        logger.info(f"报告生成完成，耗时: {elapsed_time:.2f}秒")
        
        return report
    
    def _generate_report_id(self) -> str:
        """生成报告ID"""
        return f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _generate_section(
        self,
        section_template: Dict[str, Any],
        analysis: Dict[str, Any],
        query: str,
        simulation_requirement: str
    ) -> Dict[str, Any]:
        """生成单个章节
        
        Args:
            section_template: 章节模板
            analysis: 数据分析结果
            query: 用户查询
            simulation_requirement: 模拟需求
            
        Returns:
            章节内容
        """
        # 构建提示词
        prompt = self._build_section_prompt(
            section_template=section_template,
            analysis=analysis,
            query=query,
            simulation_requirement=simulation_requirement
        )
        
        # 调用 LLM 生成内容
        content = self.llm_client.chat(
            messages=[
                {"role": "system", "content": "你是一个专业的模拟分析报告撰写专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        # 如果有子章节，也生成
        subsections = []
        for subsection_template in section_template.get("sections", []):
            subsection_content = self._generate_subsection(
                subsection_template=subsection_template,
                parent_section=section_template,
                analysis=analysis,
                query=query,
                simulation_requirement=simulation_requirement
            )
            subsections.append(subsection_content)
        
        return {
            "title": section_template["title"],
            "description": section_template["description"],
            "content": content,
            "subsections": subsections
        }
    
    def _generate_subsection(
        self,
        subsection_template: Dict[str, Any],
        parent_section: Dict[str, Any],
        analysis: Dict[str, Any],
        query: str,
        simulation_requirement: str
    ) -> Dict[str, Any]:
        """生成子章节
        
        Args:
            subsection_template: 子章节模板
            parent_section: 父章节
            analysis: 数据分析结果
            query: 用户查询
            simulation_requirement: 模拟需求
            
        Returns:
            子章节内容
        """
        prompt = self._build_subsection_prompt(
            subsection_template=subsection_template,
            parent_section=parent_section,
            analysis=analysis,
            query=query,
            simulation_requirement=simulation_requirement
        )
        
        content = self.llm_client.chat(
            messages=[
                {"role": "system", "content": "你是一个专业的模拟分析报告撰写专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        return {
            "title": subsection_template["title"],
            "description": subsection_template["description"],
            "content": content
        }
    
    def _build_section_prompt(
        self,
        section_template: Dict[str, Any],
        analysis: Dict[str, Any],
        query: str,
        simulation_requirement: str
    ) -> str:
        """构建章节生成提示词
        
        Args:
            section_template: 章节模板
            analysis: 数据分析结果
            query: 用户查询
            simulation_requirement: 模拟需求
            
        Returns:
            提示词
        """
        section_title = section_template["title"]
        section_description = section_template["description"]
        
        # 获取相关统计数据
        basic_stats = analysis.get("basic_statistics", {})
        action_stats = analysis.get("action_statistics", {})
        agent_stats = analysis.get("agent_statistics", {})
        
        prompt = f"""请为模拟分析报告撰写「{section_title}」章节。

【章节目标】
{section_description}

【模拟背景】
模拟需求：{simulation_requirement}
用户关注的问题：{query}

【数据统计】
- 总模拟步数：{basic_stats.get('total_steps', 0)}
- 总动作数：{basic_stats.get('total_actions', 0)}
- 平均每步动作数：{basic_stats.get('average_actions_per_step', 0)}
- 参与智能体数：{agent_stats.get('total_agents', 0)}
- 最常见的动作类型：{action_stats.get('most_common_actions', [{}])[0].get('type', 'N/A')}

【写作要求】
1. 内容要基于真实的模拟数据，不要虚构
2. 使用数据支撑观点，引用具体统计数字
3. 分析要深入，不仅描述现象，还要解释原因
4. 语言专业、简洁、清晰
5. 使用 Markdown 格式，包括标题、列表、粗体等
6. 避免使用「本次报告」等重复性表述

【输出格式】
直接输出章节内容，使用 Markdown 格式。章节标题已由系统添加，请直接开始正文内容。
"""
        return prompt
    
    def _build_subsection_prompt(
        self,
        subsection_template: Dict[str, Any],
        parent_section: Dict[str, Any],
        analysis: Dict[str, Any],
        query: str,
        simulation_requirement: str
    ) -> str:
        """构建子章节生成提示词"""
        subsection_title = subsection_template["title"]
        subsection_description = subsection_template["description"]
        parent_title = parent_section["title"]
        
        prompt = f"""请为报告章节「{parent_title}」撰写子章节「{subsection_title}」。

【子章节目标】
{subsection_description}

【模拟背景】
模拟需求：{simulation_requirement}
用户关注的问题：{query}

【写作要求】
1. 聚焦于子章节的主题
2. 使用具体的数据和案例支撑观点
3. 保持与父章节的逻辑连贯性
4. 语言简洁明了
5. 使用 Markdown 格式

【输出格式】
直接输出子章节内容，使用 Markdown 格式。子章节标题已由系统添加，请直接开始正文内容。
"""
        return prompt
    
    def _generate_summary(
        self, 
        report: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> str:
        """生成报告摘要
        
        Args:
            report: 报告内容
            analysis: 数据分析结果
            
        Returns:
            摘要文本
        """
        # 获取数据分析摘要
        data_summary = self.analyzer.get_summary(analysis)
        
        # 构建摘要提示词
        prompt = f"""请为以下模拟分析报告撰写一份简洁的执行摘要（Executive Summary）。

【模拟数据摘要】
{data_summary}

【报告主题】
{report['query']}

【报告章节概览】
{', '.join([s['title'] for s in report['sections']])}

【写作要求】
1. 用3-5段文字概括整个报告
2. 突出关键发现和结论
3. 语言简洁专业
4. 让读者快速了解报告核心内容

【输出格式】
直接输出摘要文本，不要包含标题。
"""
        
        summary = self.llm_client.chat(
            messages=[
                {"role": "system", "content": "你是一个专业的执行摘要撰写专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1024
        )
        
        return summary
    
    def to_markdown(self, report: Dict[str, Any]) -> str:
        """将报告转换为 Markdown 格式
        
        Args:
            report: 报告数据
            
        Returns:
            Markdown 格式的报告文本
        """
        md_lines = []
        
        # 报告标题
        md_lines.append(f"# {report['query']}\n")
        
        # 摘要
        if report.get("summary"):
            md_lines.append("## 执行摘要\n")
            md_lines.append(f"{report['summary']}\n")
            md_lines.append("---\n")
        
        # 章节内容
        for section in report.get("sections", []):
            md_lines.append(f"## {section['title']}\n")
            md_lines.append(f"{section['content']}\n")
            
            # 子章节
            for subsection in section.get("subsections", []):
                md_lines.append(f"### {subsection['title']}\n")
                md_lines.append(f"{subsection['content']}\n")
        
        return "\n".join(md_lines)
    
    def generate_simple_report(
        self,
        simulation_data: List[Dict[str, Any]],
        query: str,
        simulation_requirement: str = ""
    ) -> str:
        """生成简化版报告（纯文本）
        
        Args:
            simulation_data: 模拟数据
            query: 用户查询
            simulation_requirement: 模拟需求
            
        Returns:
            简化报告文本
        """
        logger.info("生成简化版报告")
        
        # 快速分析
        analysis = self.analyzer.analyze_simulation_data(simulation_data)
        summary = self.analyzer.get_summary(analysis)
        
        # 构建简化报告
        prompt = f"""基于以下模拟数据，回答用户的问题。

【模拟数据摘要】
{summary}

【模拟需求】
{simulation_requirement}

【用户问题】
{query}

【要求】
1. 基于模拟数据回答问题
2. 引用具体数据支撑观点
3. 语言简洁直接
4. 突出关键发现

请直接回答问题，不需要复杂的格式。
"""
        
        response = self.llm_client.chat(
            messages=[
                {"role": "system", "content": "你是一个专业的模拟分析助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        return response
