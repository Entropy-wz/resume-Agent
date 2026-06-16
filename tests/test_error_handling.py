"""
Test early termination on errors
"""
import pytest
from src.workflow import create_resume_screening_workflow


@pytest.mark.asyncio
async def test_workflow_terminates_on_parse_error():
    """测试：PDF解析失败时立即终止，不调用评分Agent"""
    workflow = create_resume_screening_workflow()

    # 模拟PDF解析失败的状态
    initial_state = {
        "resume_path": "nonexistent.pdf",
        "threshold": 70.0,
        "resume_text": None,  # 解析失败
        "error": "Error parsing PDF: File not found",
        "evaluation": None,
        "questions": None,
        "should_generate_questions": None,
    }

    result = await workflow.ainvoke(initial_state)

    # 验证：工作流应该立即终止
    assert result["error"] == "Error parsing PDF: File not found"
    assert result["resume_text"] is None
    assert result["evaluation"] is None  # 不应该执行评分
    assert result["questions"] is None  # 不应该生成题目


@pytest.mark.asyncio
async def test_workflow_terminates_on_evaluation_error():
    """测试：评分失败时立即终止，不生成题目"""
    workflow = create_resume_screening_workflow()

    # 模拟评分失败的状态
    initial_state = {
        "resume_path": "test.pdf",
        "threshold": 70.0,
        "resume_text": "Some resume text",
        "error": None,
        "evaluation": None,
        "questions": None,
        "should_generate_questions": None,
    }

    # 通过传入空text触发evaluate节点的提前检查
    initial_state["resume_text"] = None
    result = await workflow.ainvoke(initial_state)

    # 验证：应该在evaluate_resume节点返回错误
    assert result["error"] is not None
    assert "No resume text" in result["error"]
    assert result["evaluation"] is None
    assert result["questions"] is None  # 不应该生成题目


@pytest.mark.asyncio
async def test_evaluator_node_validates_input():
    """测试：评分节点会验证输入数据"""
    from src.nodes.evaluator import evaluate_resume_node

    # 测试：resume_text为None
    state = {
        "resume_text": None,
        "threshold": 70.0,
    }

    result = await evaluate_resume_node(state)

    assert result["evaluation"] is None
    assert result["error"] is not None
    assert "No resume text" in result["error"]


@pytest.mark.asyncio
async def test_generator_node_validates_input():
    """测试：题目生成节点会验证输入数据"""
    from src.nodes.generator import generate_questions_node

    # 测试1：resume_text为None
    state1 = {
        "resume_text": None,
        "evaluation": {"some": "data"},
    }
    result1 = await generate_questions_node(state1)
    assert result1["questions"] is None
    assert "No resume text" in result1["error"]

    # 测试2：evaluation为None
    state2 = {
        "resume_text": "Some text",
        "evaluation": None,
    }
    result2 = await generate_questions_node(state2)
    assert result2["questions"] is None
    assert "No evaluation" in result2["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
