from datetime import datetime
from src.models import (
    DimensionScore,
    BaseScore,
    BonusScore,
    EvaluationResult,
    InterviewQuestion,
    InterviewQuestions,
)


def test_dimension_score_creation():
    """测试维度评分模型创建"""
    score = DimensionScore(
        dimension="项目经历",
        score=25.0,
        max_score=30.0,
        reasoning="候选人有丰富的量化项目经验"
    )
    assert score.dimension == "项目经历"
    assert score.score == 25.0
    assert score.max_score == 30.0


def test_base_score_total_calculation():
    """测试基础分数总分计算"""
    base_score = BaseScore(
        project_experience=DimensionScore(
            dimension="项目经历", score=25.0, max_score=30.0, reasoning="优秀"
        ),
        internship_experience=DimensionScore(
            dimension="实习经历", score=20.0, max_score=25.0, reasoning="良好"
        ),
        tech_stack=DimensionScore(
            dimension="技术栈", score=22.0, max_score=25.0, reasoning="扎实"
        ),
        research_experience=DimensionScore(
            dimension="科研经历", score=15.0, max_score=20.0, reasoning="有潜力"
        ),
        total_base_score=82.0
    )
    assert base_score.total_base_score == 82.0


def test_bonus_score_creation():
    """测试竞赛加分模型"""
    bonus = BonusScore(
        competitions=["数学建模国赛一等奖", "ACM-ICPC区域赛银奖"],
        bonus_points=12.0,
        reasoning="两项重要竞赛获奖"
    )
    assert len(bonus.competitions) == 2
    assert bonus.bonus_points == 12.0
    assert bonus.bonus_points <= 15.0


def test_evaluation_result_creation():
    """测试完整评估结果"""
    evaluation = EvaluationResult(
        candidate_name="张三",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目经历", score=25.0, max_score=30.0, reasoning="优秀"
            ),
            internship_experience=DimensionScore(
                dimension="实习经历", score=20.0, max_score=25.0, reasoning="良好"
            ),
            tech_stack=DimensionScore(
                dimension="技术栈", score=22.0, max_score=25.0, reasoning="扎实"
            ),
            research_experience=DimensionScore(
                dimension="科研经历", score=15.0, max_score=20.0, reasoning="有潜力"
            ),
            total_base_score=82.0
        ),
        bonus_score=BonusScore(
            competitions=["数学建模"],
            bonus_points=8.0,
            reasoning="数学建模竞赛获奖"
        ),
        final_score=90.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    assert evaluation.candidate_name == "张三"
    assert evaluation.final_score == 90.0
    assert evaluation.passed_screening is True
    assert evaluation.final_score <= 115.0


def test_interview_question_creation():
    """测试面试题目模型"""
    question = InterviewQuestion(
        level="basic",
        question="请介绍你最擅长的量化策略类型",
        related_project="CTA策略回测系统",
        focus_area="策略理解"
    )
    assert question.level in ["basic", "advanced"]
    assert len(question.question) > 0


def test_interview_questions_collection():
    """测试面试题目集合"""
    questions = InterviewQuestions(
        candidate_name="张三",
        basic_questions=[
            InterviewQuestion(
                level="basic",
                question="请介绍你的量化策略经验",
                related_project="CTA策略",
                focus_area="策略概况"
            ),
            InterviewQuestion(
                level="basic",
                question="你使用过哪些量化工具",
                related_project="回测系统",
                focus_area="技术栈"
            )
        ],
        advanced_questions=[
            InterviewQuestion(
                level="advanced",
                question="如何处理alpha因子的过拟合",
                related_project="多因子选股",
                focus_area="风险控制"
            ),
            InterviewQuestion(
                level="advanced",
                question="高频交易中的延迟优化方法",
                related_project="高频交易系统",
                focus_area="系统优化"
            )
        ],
        generation_timestamp=datetime.now()
    )
    assert len(questions.basic_questions) == 2
    assert len(questions.advanced_questions) == 2
    assert all(q.level == "basic" for q in questions.basic_questions)
    assert all(q.level == "advanced" for q in questions.advanced_questions)
