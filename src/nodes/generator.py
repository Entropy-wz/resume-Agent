# src/nodes/generator.py
from typing import Dict, Any
from src.agents.question_generator import generate_questions


async def generate_questions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    题目生成节点：调用问题生成Agent生成面试问题

    Args:
        state: 工作流状态，需要包含 resume_text 和 evaluation

    Returns:
        更新后的状态，包含 questions 或 error
    """
    try:
        resume_text = state["resume_text"]
        evaluation = state["evaluation"]

        # 调用问题生成Agent
        questions = await generate_questions(resume_text, evaluation)

        return {
            **state,
            "questions": questions,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "questions": None,
            "error": f"Error generating questions: {str(e)}"
        }
