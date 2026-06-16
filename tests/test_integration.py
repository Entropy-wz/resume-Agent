# tests/test_integration.py
import pytest
from unittest.mock import patch, AsyncMock


class TestResumeScreeningAgent:
    """测试ResumeScreeningAgent主接口"""

    def test_agent_initialization(self):
        """测试Agent初始化"""
        from src import ResumeScreeningAgent

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=75.0)

        assert agent is not None
        assert agent.threshold == 75.0

    def test_agent_initialization_default_threshold(self):
        """测试Agent默认阈值"""
        from src import ResumeScreeningAgent

        agent = ResumeScreeningAgent(openai_api_key="test_key")

        assert agent.threshold == 70.0

    @pytest.mark.asyncio
    async def test_screen_resume_passed(self):
        """测试筛选通过的简历"""
        from src import ResumeScreeningAgent
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore
        from src.models import InterviewQuestions, InterviewQuestion

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=70.0)

        # Mock workflow结果
        mock_result = {
            "resume_path": "test.pdf",
            "resume_text": "姓名：张三\n项目经历：量化CTA策略开发",
            "evaluation": EvaluationResult(
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
                bonus_score=BonusScore(
                    competitions=["数学建模"], bonus_points=5, reasoning="有竞赛"
                ),
                final_score=85.0,
                passed_screening=True,
            ),
            "should_generate_questions": True,
            "questions": InterviewQuestions(
                candidate_name="张三",
                basic_questions=[
                    InterviewQuestion(
                        level="basic",
                        question="问题1",
                        related_project="项目1",
                        focus_area="技术细节",
                    ),
                    InterviewQuestion(
                        level="basic",
                        question="问题2",
                        related_project="项目1",
                        focus_area="实现思路",
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
            ),
            "error": None,
        }

        # Mock workflow.ainvoke
        with patch.object(
            agent.workflow, "ainvoke", new_callable=AsyncMock, return_value=mock_result
        ):
            result = await agent.screen_resume("test.pdf")

            assert result["evaluation"] is not None
            assert result["evaluation"].final_score == 85.0
            assert result["evaluation"].passed_screening is True
            assert result["questions"] is not None
            assert len(result["questions"].basic_questions) == 2

    @pytest.mark.asyncio
    async def test_screen_resume_failed(self):
        """测试筛选未通过的简历"""
        from src import ResumeScreeningAgent
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=70.0)

        # Mock workflow结果
        mock_result = {
            "resume_path": "test.pdf",
            "resume_text": "姓名：李四\n项目经历：较少",
            "evaluation": EvaluationResult(
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
            ),
            "should_generate_questions": False,
            "questions": None,
            "error": None,
        }

        # Mock workflow.ainvoke
        with patch.object(
            agent.workflow, "ainvoke", new_callable=AsyncMock, return_value=mock_result
        ):
            result = await agent.screen_resume("test.pdf")

            assert result["evaluation"] is not None
            assert result["evaluation"].final_score == 42.0
            assert result["evaluation"].passed_screening is False
            assert result["questions"] is None

    @pytest.mark.asyncio
    async def test_screen_resume_custom_threshold(self):
        """测试使用自定义阈值"""
        from src import ResumeScreeningAgent

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=70.0)

        # Mock workflow.ainvoke
        mock_ainvoke = AsyncMock(
            return_value={"evaluation": None, "questions": None, "error": None}
        )

        with patch.object(agent.workflow, "ainvoke", mock_ainvoke):
            await agent.screen_resume("test.pdf", threshold=80.0)

            # 验证调用参数
            call_args = mock_ainvoke.call_args[0][0]
            assert call_args["threshold"] == 80.0

    def test_screen_resume_sync(self):
        """测试同步接口"""
        from src import ResumeScreeningAgent
        from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=70.0)

        # Mock workflow结果
        mock_result = {
            "resume_path": "test.pdf",
            "resume_text": "姓名：张三",
            "evaluation": EvaluationResult(
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
            ),
            "should_generate_questions": True,
            "questions": None,
            "error": None,
        }

        # Mock workflow.invoke
        with patch.object(agent.workflow, "invoke", return_value=mock_result):
            result = agent.screen_resume_sync("test.pdf")

            assert result["evaluation"] is not None
            assert result["evaluation"].final_score == 80.0

    @pytest.mark.asyncio
    async def test_screen_resume_error_handling(self):
        """测试错误处理"""
        from src import ResumeScreeningAgent

        agent = ResumeScreeningAgent(openai_api_key="test_key", threshold=70.0)

        # Mock workflow抛出异常
        with patch.object(agent.workflow, "ainvoke", side_effect=Exception("Workflow error")):
            with pytest.raises(Exception) as exc_info:
                await agent.screen_resume("test.pdf")

            assert "Workflow error" in str(exc_info.value)
