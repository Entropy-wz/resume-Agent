# src/nodes/checker.py
from typing import Dict, Any


def check_threshold_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    阈值检查节点：根据threshold重新计算是否通过初筛

    这是唯一决定是否生成题目的地方（单一真相源原则）

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
                "error": "Error: evaluation is None",
            }

        # 真正的阈值检查逻辑（单一真相源）
        should_generate = evaluation.final_score >= threshold

        # 更新evaluation的passed_screening字段保持一致
        evaluation.passed_screening = should_generate

        return {**state, "should_generate_questions": should_generate, "error": None}
    except Exception as e:
        return {
            **state,
            "should_generate_questions": False,
            "error": f"Error checking threshold: {str(e)}",
        }
