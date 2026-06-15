# src/workflow.py
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node
from src.nodes.checker import check_threshold_node
from src.nodes.generator import generate_questions_node


def should_generate_questions(state: Dict[str, Any]) -> Literal["generate_questions", "end"]:
    """
    条件判断函数：根据should_generate_questions字段决定下一步

    Args:
        state: 工作流状态，包含should_generate_questions字段

    Returns:
        "generate_questions" 如果应该生成题目，否则 "end"
    """
    if state.get("should_generate_questions", False):
        return "generate_questions"
    return "end"


def create_resume_screening_workflow():
    """
    创建简历筛选工作流

    工作流结构:
        parse_resume → evaluate_resume → check_threshold → [conditional]
            → generate_questions (如果通过初筛)
            → END (如果未通过初筛)

    Returns:
        CompiledGraph: 编译后的LangGraph工作流
    """
    # 创建StateGraph
    workflow = StateGraph(dict)

    # 添加节点
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("evaluate_resume", evaluate_resume_node)
    workflow.add_node("check_threshold", check_threshold_node)
    workflow.add_node("generate_questions", generate_questions_node)

    # 设置入口点
    workflow.set_entry_point("parse_resume")

    # 添加顺序边
    workflow.add_edge("parse_resume", "evaluate_resume")
    workflow.add_edge("evaluate_resume", "check_threshold")

    # 添加条件边
    workflow.add_conditional_edges(
        "check_threshold",
        should_generate_questions,
        {
            "generate_questions": "generate_questions",
            "end": END
        }
    )

    # 生成题目后结束
    workflow.add_edge("generate_questions", END)

    # 编译工作流
    return workflow.compile()
