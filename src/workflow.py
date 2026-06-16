# src/workflow.py
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from src.state import WorkflowState
from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node
from src.nodes.checker import check_threshold_node
from src.nodes.generator import generate_questions_node


def has_error(state: Dict[str, Any]) -> Literal["continue", "end"]:
    """
    错误检查函数：如果有错误则提前终止工作流

    Args:
        state: 工作流状态，包含error字段

    Returns:
        "end" 如果有错误，否则 "continue"
    """
    if state.get("error"):
        return "end"
    return "continue"


def should_generate_questions(state: Dict[str, Any]) -> Literal["generate_questions", "end"]:
    """
    条件判断函数：根据should_generate_questions字段决定下一步

    Args:
        state: 工作流状态，包含should_generate_questions字段

    Returns:
        "generate_questions" 如果应该生成题目，否则 "end"
    """
    # 先检查是否有错误
    if state.get("error"):
        return "end"

    if state.get("should_generate_questions", False):
        return "generate_questions"
    return "end"


def create_resume_screening_workflow():
    """
    创建简历筛选工作流

    工作流结构:
        parse_resume → [error check] → evaluate_resume → [error check] → check_threshold → [conditional]
            → generate_questions (如果通过初筛)
            → END (如果未通过初筛或有错误)

    错误处理：
        任何节点出错都会立即终止工作流，避免浪费API调用

    Returns:
        CompiledGraph: 编译后的LangGraph工作流
    """
    # 创建StateGraph with typed state schema
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("evaluate_resume", evaluate_resume_node)
    workflow.add_node("check_threshold", check_threshold_node)
    workflow.add_node("generate_questions", generate_questions_node)

    # 设置入口点
    workflow.set_entry_point("parse_resume")

    # parse_resume 后检查错误
    workflow.add_conditional_edges(
        "parse_resume",
        has_error,
        {"continue": "evaluate_resume", "end": END},
    )

    # evaluate_resume 后检查错误
    workflow.add_conditional_edges(
        "evaluate_resume",
        has_error,
        {"continue": "check_threshold", "end": END},
    )

    # check_threshold 后根据是否通过和是否有错误决定
    workflow.add_conditional_edges(
        "check_threshold",
        should_generate_questions,
        {"generate_questions": "generate_questions", "end": END},
    )

    # 生成题目后结束
    workflow.add_edge("generate_questions", END)

    # 编译工作流
    return workflow.compile()
