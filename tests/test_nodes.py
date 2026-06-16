# tests/test_nodes.py
import pytest
from unittest.mock import Mock, patch


class TestParserNode:
    """测试PDF解析节点"""

    def test_parse_resume_node_success(self):
        """测试PDF解析成功"""
        from src.nodes.parser import parse_resume_node

        # Mock state with PDF path
        state = {"resume_path": "test.pdf", "resume_text": None, "error": None}

        # Mock PyPDFLoader
        with patch("src.nodes.parser.PyPDFLoader") as mock_loader:
            mock_instance = Mock()
            mock_instance.load.return_value = [
                Mock(page_content="Page 1 content"),
                Mock(page_content="Page 2 content"),
            ]
            mock_loader.return_value = mock_instance

            result = parse_resume_node(state)

            assert result["resume_text"] == "Page 1 content\nPage 2 content"
            assert result["error"] is None
            mock_loader.assert_called_once_with("test.pdf")

    def test_parse_resume_node_error(self):
        """测试PDF解析失败"""
        from src.nodes.parser import parse_resume_node

        state = {"resume_path": "nonexistent.pdf", "resume_text": None, "error": None}

        with patch("src.nodes.parser.PyPDFLoader") as mock_loader:
            mock_loader.side_effect = Exception("File not found")

            result = parse_resume_node(state)

            assert result["resume_text"] is None
            assert "Error" in result["error"]
            assert "File not found" in result["error"]

    def test_parse_resume_node_empty_pdf(self):
        """测试空PDF"""
        from src.nodes.parser import parse_resume_node

        state = {"resume_path": "empty.pdf", "resume_text": None, "error": None}

        with patch("src.nodes.parser.PyPDFLoader") as mock_loader:
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
            "error": None,
        }

        # Mock the evaluate_resume function
        mock_evaluation = EvaluationResult(
            candidate_name="张三",
            base_score=BaseScore(
                project_experience=DimensionScore(
                    dimension="项目经历", score=20, max_score=30, reasoning="有量化项目"
                ),
                internship_experience=DimensionScore(
                    dimension="实习经历", score=15, max_score=25, reasoning="实习经验一般"
                ),
                tech_stack=DimensionScore(
                    dimension="技术栈", score=18, max_score=25, reasoning="技术栈合理"
                ),
                research_experience=DimensionScore(
                    dimension="科研经历", score=10, max_score=20, reasoning="无科研"
                ),
                total_base_score=63.0,
            ),
            bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="无竞赛"),
            final_score=63.0,
            passed_screening=False,
        )

        with patch("src.nodes.evaluator.evaluate_resume", return_value=mock_evaluation):
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
            "error": None,
        }

        with patch("src.nodes.evaluator.evaluate_resume", side_effect=Exception("API error")):
            result = await evaluate_resume_node(state)

            assert result["evaluation"] is None
            assert "Error" in result["error"]
            assert "API error" in result["error"]


class TestCheckerNode:
    """测试阈值检查节点"""

    def test_check_threshold_node_passed(self):
        """测试通过初筛"""
        from src.nodes.checker import check_threshold_node
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        evaluation = EvaluationResult(
            candidate_name="张三",
            base_score=BaseScore(
                project_experience=DimensionScore(
                    dimension="项目经历", score=25, max_score=30, reasoning="优秀"
                ),
                internship_experience=DimensionScore(
                    dimension="实习经历", score=20, max_score=25, reasoning="良好"
                ),
                tech_stack=DimensionScore(
                    dimension="技术栈", score=20, max_score=25, reasoning="扎实"
                ),
                research_experience=DimensionScore(
                    dimension="科研经历", score=15, max_score=20, reasoning="不错"
                ),
                total_base_score=80.0,
            ),
            bonus_score=BonusScore(competitions=["数学建模"], bonus_points=5, reasoning="有竞赛"),
            final_score=85.0,
            passed_screening=True,
        )

        state = {
            "evaluation": evaluation,
            "threshold": 70.0,
            "should_generate_questions": None,
            "error": None,
        }

        result = check_threshold_node(state)

        assert result["should_generate_questions"] is True
        assert result["error"] is None

    def test_check_threshold_node_failed(self):
        """测试未通过初筛"""
        from src.nodes.checker import check_threshold_node
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        evaluation = EvaluationResult(
            candidate_name="李四",
            base_score=BaseScore(
                project_experience=DimensionScore(
                    dimension="项目经历", score=15, max_score=30, reasoning="一般"
                ),
                internship_experience=DimensionScore(
                    dimension="实习经历", score=10, max_score=25, reasoning="较少"
                ),
                tech_stack=DimensionScore(
                    dimension="技术栈", score=12, max_score=25, reasoning="基础"
                ),
                research_experience=DimensionScore(
                    dimension="科研经历", score=5, max_score=20, reasoning="无"
                ),
                total_base_score=42.0,
            ),
            bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="无竞赛"),
            final_score=42.0,
            passed_screening=False,
        )

        state = {
            "evaluation": evaluation,
            "threshold": 70.0,
            "should_generate_questions": None,
            "error": None,
        }

        result = check_threshold_node(state)

        assert result["should_generate_questions"] is False
        assert result["error"] is None

    def test_check_threshold_node_error(self):
        """测试缺少evaluation"""
        from src.nodes.checker import check_threshold_node

        state = {
            "evaluation": None,
            "threshold": 70.0,
            "should_generate_questions": None,
            "error": None,
        }

        result = check_threshold_node(state)

        assert result["should_generate_questions"] is False
        assert "Error" in result["error"]


class TestGeneratorNode:
    """测试题目生成节点"""

    @pytest.mark.asyncio
    async def test_generate_questions_node_success(self):
        """测试题目生成成功"""
        from src.nodes.generator import generate_questions_node
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore
        from src.models import InterviewQuestions, InterviewQuestion

        evaluation = EvaluationResult(
            candidate_name="张三",
            base_score=BaseScore(
                project_experience=DimensionScore(
                    dimension="项目经历", score=25, max_score=30, reasoning="优秀"
                ),
                internship_experience=DimensionScore(
                    dimension="实习经历", score=20, max_score=25, reasoning="良好"
                ),
                tech_stack=DimensionScore(
                    dimension="技术栈", score=20, max_score=25, reasoning="扎实"
                ),
                research_experience=DimensionScore(
                    dimension="科研经历", score=15, max_score=20, reasoning="不错"
                ),
                total_base_score=80.0,
            ),
            bonus_score=BonusScore(competitions=["数学建模"], bonus_points=5, reasoning="有竞赛"),
            final_score=85.0,
            passed_screening=True,
        )

        state = {
            "resume_text": "姓名：张三\n项目经历：量化CTA策略开发",
            "evaluation": evaluation,
            "questions": None,
            "error": None,
        }

        # Mock the generate_questions function
        mock_questions = InterviewQuestions(
            candidate_name="张三",
            basic_questions=[
                InterviewQuestion(
                    level="basic", question="问题1", related_project="项目1", focus_area="技术细节"
                ),
                InterviewQuestion(
                    level="basic", question="问题2", related_project="项目1", focus_area="实现思路"
                ),
            ],
            advanced_questions=[
                InterviewQuestion(
                    level="advanced",
                    question="问题3",
                    related_project="项目1",
                    focus_area="系统设计",
                ),
                InterviewQuestion(
                    level="advanced",
                    question="问题4",
                    related_project="项目1",
                    focus_area="优化方案",
                ),
            ],
        )

        with patch("src.nodes.generator.generate_questions", return_value=mock_questions):
            result = await generate_questions_node(state)

            assert result["questions"] == mock_questions
            assert result["error"] is None
            assert len(result["questions"].basic_questions) == 2
            assert len(result["questions"].advanced_questions) == 2

    @pytest.mark.asyncio
    async def test_generate_questions_node_error(self):
        """测试题目生成失败"""
        from src.nodes.generator import generate_questions_node
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        evaluation = EvaluationResult(
            candidate_name="张三",
            base_score=BaseScore(
                project_experience=DimensionScore(
                    dimension="项目经历", score=25, max_score=30, reasoning="优秀"
                ),
                internship_experience=DimensionScore(
                    dimension="实习经历", score=20, max_score=25, reasoning="良好"
                ),
                tech_stack=DimensionScore(
                    dimension="技术栈", score=20, max_score=25, reasoning="扎实"
                ),
                research_experience=DimensionScore(
                    dimension="科研经历", score=15, max_score=20, reasoning="不错"
                ),
                total_base_score=80.0,
            ),
            bonus_score=BonusScore(competitions=[], bonus_points=0, reasoning="无"),
            final_score=80.0,
            passed_screening=True,
        )

        state = {
            "resume_text": "invalid",
            "evaluation": evaluation,
            "questions": None,
            "error": None,
        }

        with patch("src.nodes.generator.generate_questions", side_effect=Exception("API error")):
            result = await generate_questions_node(state)

            assert result["questions"] is None
            assert "Error" in result["error"]
            assert "API error" in result["error"]
