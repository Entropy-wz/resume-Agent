"""
Test concurrent execution without environment variable pollution
"""
import pytest
import asyncio
import os
from src import ResumeScreeningAgent


def test_no_environment_variable_pollution_on_init():
    """测试：初始化Agent不应污染环境变量"""
    # 设置初始环境变量
    original_key = os.environ.get("OPENAI_API_KEY", "")
    os.environ["OPENAI_API_KEY"] = "original-test-key"

    # 创建Agent
    agent = ResumeScreeningAgent(openai_api_key="new-test-key-123", threshold=70.0)

    # 验证：环境变量应该保持不变
    assert os.environ["OPENAI_API_KEY"] == "original-test-key"
    assert agent.openai_api_key == "new-test-key-123"

    # 恢复原始值
    if original_key:
        os.environ["OPENAI_API_KEY"] = original_key
    else:
        del os.environ["OPENAI_API_KEY"]


@pytest.mark.asyncio
async def test_concurrent_agents_with_different_keys():
    """测试：多个Agent实例可以并发运行且不互相干扰"""
    from unittest.mock import AsyncMock, patch, MagicMock
    from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

    # Mock evaluation结果
    def create_mock_evaluation(score: float, name: str):
        return EvaluationResult(
            candidate_name=name,
            base_score=BaseScore(
                project_experience=DimensionScore(dimension="项目", score=score/4, max_score=30, reasoning="test"),
                internship_experience=DimensionScore(dimension="实习", score=score/4, max_score=25, reasoning="test"),
                tech_stack=DimensionScore(dimension="技术", score=score/4, max_score=25, reasoning="test"),
                research_experience=DimensionScore(dimension="科研", score=score/4, max_score=20, reasoning="test"),
                total_base_score=score,
            ),
            bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="test"),
            final_score=score,
            timestamp="2026-01-01T00:00:00",
            passed_screening=score >= 70,
        )

    # 创建两个Agent，使用不同的API key
    agent1 = ResumeScreeningAgent(openai_api_key="key-for-agent-1", threshold=70.0)
    agent2 = ResumeScreeningAgent(openai_api_key="key-for-agent-2", threshold=80.0)

    # 验证：每个agent存储了自己的key
    assert agent1.openai_api_key == "key-for-agent-1"
    assert agent2.openai_api_key == "key-for-agent-2"

    # Mock PDF解析和API调用
    with patch("src.nodes.parser.pdfplumber.open") as mock_pdf, \
         patch("src.agents.evaluator.evaluate_resume") as mock_eval, \
         patch("src.agents.question_generator.generate_questions") as mock_gen:

        # Mock PDF解析
        mock_pdf.return_value.__enter__.return_value.pages = [
            MagicMock(extract_text=lambda: "Resume text 1", extract_tables=lambda: [])
        ]

        # Mock评分 - 根据传入的api_key返回不同结果
        async def mock_evaluate(text, threshold, api_key, base_url):
            if api_key == "key-for-agent-1":
                return create_mock_evaluation(85, "Candidate1")
            else:
                return create_mock_evaluation(75, "Candidate2")

        mock_eval.side_effect = mock_evaluate

        # Mock题目生成
        mock_gen.return_value = MagicMock()

        # 并发运行两个agent
        results = await asyncio.gather(
            agent1.screen_resume("test1.pdf"),
            agent2.screen_resume("test2.pdf"),
        )

        # 验证：两个结果应该不同（说明没有互相污染）
        assert results[0]["evaluation"].candidate_name == "Candidate1"
        assert results[0]["evaluation"].final_score == 85

        assert results[1]["evaluation"].candidate_name == "Candidate2"
        assert results[1]["evaluation"].final_score == 75

        # 验证：API调用时传递了正确的key
        assert mock_eval.call_count == 2
        call_args_list = mock_eval.call_args_list

        # 第一个调用应该使用agent1的key
        assert call_args_list[0][1]["api_key"] == "key-for-agent-1"

        # 第二个调用应该使用agent2的key
        assert call_args_list[1][1]["api_key"] == "key-for-agent-2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
