"""
Test early termination on errors - validates workflow stops on failure
"""
import pytest
from unittest.mock import patch, MagicMock
from src.workflow import create_resume_screening_workflow
from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore


@pytest.mark.asyncio
async def test_workflow_terminates_on_parse_error():
    """测试：PDF解析失败时立即终止，不调用评分Agent"""
    workflow = create_resume_screening_workflow()

    # Mock parser to return error
    with patch("src.nodes.parser.PyPDFLoader") as mock_loader:
        mock_loader.side_effect = Exception("File not found")

        initial_state = {
            "resume_path": "nonexistent.pdf",
            "threshold": 70.0,
        }

        result = await workflow.ainvoke(initial_state)

        # 验证：工作流应该在parse阶段失败并终止
        assert result["error"] is not None
        assert "Error parsing PDF" in result["error"]
        assert result["resume_text"] is None
        assert result["evaluation"] is None  # 不应该执行评分
        assert result["questions"] is None  # 不应该生成题目


@pytest.mark.asyncio
async def test_evaluator_validates_input_before_llm_call():
    """测试：评分节点在调用LLM前验证输入，避免浪费API"""
    from src.nodes.evaluator import evaluate_resume_node

    # 场景：resume_text为None（解析失败后的状态）
    state = {
        "resume_text": None,  # 上一步失败
        "threshold": 70.0,
    }

    # 这里不应该调用任何LLM API
    result = await evaluate_resume_node(state)

    # 验证：立即返回错误，不浪费API调用
    assert result["evaluation"] is None
    assert result["error"] is not None
    assert "No resume text" in result["error"]


@pytest.mark.asyncio
async def test_generator_validates_inputs():
    """测试：题目生成节点验证所有必需输入"""
    from src.nodes.generator import generate_questions_node

    # 场景1：缺少resume_text
    state1 = {
        "resume_text": None,
        "evaluation": MagicMock(),  # 假装有evaluation
    }
    result1 = await generate_questions_node(state1)
    assert result1["questions"] is None
    assert "No resume text" in result1["error"]

    # 场景2：缺少evaluation
    state2 = {
        "resume_text": "Some text",
        "evaluation": None,  # 评分失败
    }
    result2 = await generate_questions_node(state2)
    assert result2["questions"] is None
    assert "No evaluation" in result2["error"]


@pytest.mark.asyncio
async def test_workflow_error_stops_expensive_operations():
    """
    集成测试：验证错误会阻止后续昂贵操作

    场景：PDF解析失败 → 不应调用评分API → 不应生成题目
    """
    workflow = create_resume_screening_workflow()

    # Mock所有节点来跟踪调用
    with patch("src.nodes.parser.PyPDFLoader") as mock_parser, \
         patch("src.agents.evaluator.evaluate_resume") as mock_evaluate, \
         patch("src.agents.question_generator.generate_questions") as mock_generate:

        # 模拟PDF解析失败
        mock_parser.side_effect = Exception("PDF corrupted")

        initial_state = {
            "resume_path": "corrupted.pdf",
            "threshold": 70.0,
        }

        result = await workflow.ainvoke(initial_state)

        # 验证：解析失败后，不应该调用评分和题目生成
        assert result["error"] is not None
        mock_evaluate.assert_not_called()  # 关键：没有浪费API调用！
        mock_generate.assert_not_called()  # 关键：没有浪费API调用！


@pytest.mark.asyncio
async def test_workflow_conditional_edges_check_errors():
    """测试：条件边会检查错误状态"""
    from src.workflow import has_error, should_generate_questions

    # 测试has_error函数
    assert has_error({"error": "Some error"}) == "end"
    assert has_error({"error": None}) == "continue"
    assert has_error({}) == "continue"

    # 测试should_generate_questions在有错误时也返回end
    state_with_error = {
        "error": "Some error",
        "should_generate_questions": True,  # 即使标记为True
    }
    assert should_generate_questions(state_with_error) == "end"

    # 无错误且通过初筛
    state_passed = {
        "error": None,
        "should_generate_questions": True,
    }
    assert should_generate_questions(state_passed) == "generate_questions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
