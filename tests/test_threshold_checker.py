"""
Test threshold checking logic
"""
import pytest
from src.nodes.checker import check_threshold_node
from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore


def test_check_threshold_node_calculates_correctly():
    """测试：checker节点真正计算阈值，不只是透传"""

    # 创建一个evaluation（初始passed_screening为False）
    evaluation = EvaluationResult(
        candidate_name="Test",
        base_score=BaseScore(
            project_experience=DimensionScore(dimension="项目", score=20, max_score=30, reasoning="test"),
            internship_experience=DimensionScore(dimension="实习", score=20, max_score=25, reasoning="test"),
            tech_stack=DimensionScore(dimension="技术栈", score=20, max_score=25, reasoning="test"),
            research_experience=DimensionScore(dimension="科研", score=15, max_score=20, reasoning="test"),
            total_base_score=75.0,
        ),
        bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="test"),
        final_score=75.0,
        timestamp="2026-01-01T00:00:00",
        passed_screening=False,  # 初始为False
    )

    # final_score = 75
    assert evaluation.final_score == 75.0

    # 场景1：阈值70，应该通过
    state1 = {
        "evaluation": evaluation,
        "threshold": 70.0,
    }
    result1 = check_threshold_node(state1)

    assert result1["should_generate_questions"] is True
    assert result1["evaluation"].passed_screening is True  # 被更新了

    # 场景2：阈值80，应该不通过
    state2 = {
        "evaluation": evaluation,
        "threshold": 80.0,
    }
    result2 = check_threshold_node(state2)

    assert result2["should_generate_questions"] is False
    assert result2["evaluation"].passed_screening is False  # 被更新了


def test_check_threshold_uses_state_threshold_not_hardcoded():
    """测试：checker使用state中的threshold，不是硬编码"""

    evaluation = EvaluationResult(
        candidate_name="Test",
        base_score=BaseScore(
            project_experience=DimensionScore(dimension="项目", score=18, max_score=30, reasoning="test"),
            internship_experience=DimensionScore(dimension="实习", score=15, max_score=25, reasoning="test"),
            tech_stack=DimensionScore(dimension="技术栈", score=15, max_score=25, reasoning="test"),
            research_experience=DimensionScore(dimension="科研", score=12, max_score=20, reasoning="test"),
            total_base_score=60.0,
        ),
        bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="test"),
        final_score=60.0,
        timestamp="2026-01-01T00:00:00",
        passed_screening=False,
    )

    # final_score = 60
    assert evaluation.final_score == 60.0

    # 不同阈值应该产生不同结果
    assert check_threshold_node({"evaluation": evaluation, "threshold": 50.0})["should_generate_questions"] is True
    assert check_threshold_node({"evaluation": evaluation, "threshold": 60.0})["should_generate_questions"] is True
    assert check_threshold_node({"evaluation": evaluation, "threshold": 70.0})["should_generate_questions"] is False


def test_check_threshold_is_single_source_of_truth():
    """测试：checker是阈值判断的唯一真相源"""

    evaluation = EvaluationResult(
        candidate_name="Test",
        base_score=BaseScore(
            project_experience=DimensionScore(dimension="项目", score=25, max_score=30, reasoning="test"),
            internship_experience=DimensionScore(dimension="实习", score=20, max_score=25, reasoning="test"),
            tech_stack=DimensionScore(dimension="技术栈", score=20, max_score=25, reasoning="test"),
            research_experience=DimensionScore(dimension="科研", score=15, max_score=20, reasoning="test"),
            total_base_score=80.0,
        ),
        bonus_score=BonusScore(competitions=[], bonus_points=10, reasoning="test"),
        final_score=90.0,
        timestamp="2026-01-01T00:00:00",
        passed_screening=False,  # 故意设置错误的初始值
    )

    # final_score = 90
    assert evaluation.final_score == 90.0

    # 即使evaluation初始passed_screening=False，checker也应该纠正它
    state = {
        "evaluation": evaluation,
        "threshold": 70.0,
    }
    result = check_threshold_node(state)

    # checker纠正了错误的passed_screening
    assert result["should_generate_questions"] is True
    assert result["evaluation"].passed_screening is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
