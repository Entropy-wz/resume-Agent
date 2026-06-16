# src/nodes/evaluator.py
from typing import Dict, Any
from src.agents.evaluator import evaluate_resume


async def evaluate_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    评分节点：调用评分Agent对简历进行评分

    Args:
        state: 工作流状态，需要包含 resume_text, threshold, api_key, api_base_url

    Returns:
        更新后的状态，包含 evaluation 或 error
    """
    try:
        # 提前检查：如果没有resume_text，直接返回错误
        resume_text = state.get("resume_text")
        if not resume_text:
            return {
                **state,
                "evaluation": None,
                "error": "Error: No resume text to evaluate (previous step failed)",
            }

        threshold = state.get("threshold", 70.0)
        api_key = state.get("api_key")
        api_base_url = state.get("api_base_url")

        # 调用评分Agent（传递API配置）
        evaluation = await evaluate_resume(resume_text, threshold, api_key, api_base_url)

        return {**state, "evaluation": evaluation, "error": None}
    except Exception as e:
        return {**state, "evaluation": None, "error": f"Error evaluating resume: {str(e)}"}
