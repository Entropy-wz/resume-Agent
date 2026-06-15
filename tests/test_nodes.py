# tests/test_nodes.py
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any


class TestParserNode:
    """测试PDF解析节点"""

    def test_parse_resume_node_success(self):
        """测试PDF解析成功"""
        from src.nodes.parser import parse_resume_node

        # Mock state with PDF path
        state = {
            "pdf_path": "test.pdf",
            "resume_text": None,
            "error": None
        }

        # Mock PyPDFLoader
        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_instance = Mock()
            mock_instance.load.return_value = [
                Mock(page_content="Page 1 content"),
                Mock(page_content="Page 2 content")
            ]
            mock_loader.return_value = mock_instance

            result = parse_resume_node(state)

            assert result["resume_text"] == "Page 1 content\nPage 2 content"
            assert result["error"] is None
            mock_loader.assert_called_once_with("test.pdf")

    def test_parse_resume_node_error(self):
        """测试PDF解析失败"""
        from src.nodes.parser import parse_resume_node

        state = {
            "pdf_path": "nonexistent.pdf",
            "resume_text": None,
            "error": None
        }

        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_loader.side_effect = Exception("File not found")

            result = parse_resume_node(state)

            assert result["resume_text"] is None
            assert "Error" in result["error"]
            assert "File not found" in result["error"]

    def test_parse_resume_node_empty_pdf(self):
        """测试空PDF"""
        from src.nodes.parser import parse_resume_node

        state = {
            "pdf_path": "empty.pdf",
            "resume_text": None,
            "error": None
        }

        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_instance = Mock()
            mock_instance.load.return_value = []
            mock_loader.return_value = mock_instance

            result = parse_resume_node(state)

            assert result["resume_text"] == ""
            assert result["error"] is None


class TestEvaluatorNode:
    """测试评分节点"""

    @pytest.mark.asyncio
    async def test_evaluate_resume_node_success(self):
        """测试评分节点成功"""
        from src.nodes.evaluator import evaluate_resume_node
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        state = {
            "resume_text": "姓名：张三\n项目经历：量化CTA策略开发",
            "threshold": 70.0,
            "evaluation": None,
            "error": None
        }

        # Mock the evaluate_resume function
        mock_evaluation = EvaluationResult(
            candidate_name="张三",
            base_score=BaseScore(
                project_experience=DimensionScore(dimension="项目经历", score=20, max_score=30, reasoning="有量化项目"),
                internship_experience=DimensionScore(dimension="实习经历", score=15, max_score=25, reasoning="实习经验一般"),
                tech_stack=DimensionScore(dimension="技术栈", score=18, max_score=25, reasoning="技术栈合理"),
                research_experience=DimensionScore(dimension="科研经历", score=10, max_score=20, reasoning="无科研"),
                total_base_score=63.0
            ),
            bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="无竞赛"),
            final_score=63.0,
            passed_screening=False
        )

        with patch('src.nodes.evaluator.evaluate_resume', return_value=mock_evaluation):
            result = await evaluate_resume_node(state)

            assert result["evaluation"] == mock_evaluation
            assert result["error"] is None
            assert result["evaluation"].candidate_name == "张三"
            assert result["evaluation"].final_score == 63.0

    @pytest.mark.asyncio
    async def test_evaluate_resume_node_error(self):
        """测试评分节点失败"""
        from src.nodes.evaluator import evaluate_resume_node

        state = {
            "resume_text": "invalid resume",
            "threshold": 70.0,
            "evaluation": None,
            "error": None
        }

        with patch('src.nodes.evaluator.evaluate_resume', side_effect=Exception("API error")):
            result = await evaluate_resume_node(state)

            assert result["evaluation"] is None
            assert "Error" in result["error"]
            assert "API error" in result["error"]
