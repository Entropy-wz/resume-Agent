# src/nodes/checker.py
from typing import Dict, Any


def check_threshold_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    阈值检查节点：检查评分是否达到阈值

    Args:
        state: 工作流状态，需要包含 evaluation 和 threshold

    Returns:
        更新后的状态，包含 should_generate_questions 或 error
    """
    try:
        evaluation = state.get("evaluation")
        threshold = state.get("threshold", 70.0)

        if evaluation is None:
            return {
                **state,
                "should_generate_questions": False,
                "error": "Error: evaluation is None"
            }

        # 检查是否通过初筛
        should_generate = evaluation.passed_screening

        return {
            **state,
            "should_generate_questions": should_generate,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "should_generate_questions": False,
            "error": f"Error checking threshold: {str(e)}"
        }
