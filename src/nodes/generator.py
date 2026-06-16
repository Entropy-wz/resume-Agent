# src/nodes/generator.py
from typing import Dict, Any
from src.agents.question_generator import generate_questions


async def generate_questions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    题目生成节点：调用问题生成Agent生成面试问题

    Args:
        state: 工作流状态，需要包含 resume_text, evaluation, api_key, api_base_url

    Returns:
        更新后的状态，包含 questions 或 error
    """
    try:
        # 提前检查：如果没有必需数据，直接返回错误
        resume_text = state.get("resume_text")
        evaluation = state.get("evaluation")

        if not resume_text:
            return {
                **state,
                "questions": None,
                "error": "Error: No resume text available for question generation",
            }

        if not evaluation:
            return {
                **state,
                "questions": None,
                "error": "Error: No evaluation available for question generation",
            }

        api_key = state.get("api_key")
        api_base_url = state.get("api_base_url")

        # 调用问题生成Agent（传递API配置）
        questions = await generate_questions(resume_text, evaluation, api_key, api_base_url)

        return {**state, "questions": questions, "error": None}
    except Exception as e:
        return {**state, "questions": None, "error": f"Error generating questions: {str(e)}"}
