from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    """单个维度的评分"""
    dimension: str = Field(description="维度名称")
    score: float = Field(ge=0, description="得分")
    max_score: float = Field(gt=0, description="满分")
    reasoning: str = Field(description="评分理由")


class BaseScore(BaseModel):
    """基础评分（100分制）"""
    project_experience: DimensionScore = Field(description="项目经历 30分")
    internship_experience: DimensionScore = Field(description="实习经历 25分")
    tech_stack: DimensionScore = Field(description="技术栈 25分")
    research_experience: DimensionScore = Field(description="科研经历 20分")
    total_base_score: float = Field(ge=0, le=100, description="基础总分 0-100")


class BonusScore(BaseModel):
    """竞赛加分"""
    competitions: List[str] = Field(default_factory=list, description="竞赛列表")
    bonus_points: float = Field(ge=0, le=15, description="加分 0-15")
    reasoning: str = Field(description="加分理由")


class EvaluationResult(BaseModel):
    """完整评估结果"""
    candidate_name: str = Field(description="候选人姓名")
    base_score: BaseScore = Field(description="基础评分")
    bonus_score: BonusScore = Field(description="竞赛加分")
    final_score: float = Field(ge=0, le=115, description="总分 0-115")
    passed_screening: bool = Field(description="是否通过初筛")
    timestamp: datetime = Field(default_factory=datetime.now, description="评估时间")


class InterviewQuestion(BaseModel):
    """单个面试题目"""
    level: Literal["basic", "advanced"] = Field(description="基础/进阶")
    question: str = Field(min_length=1, description="题目内容")
    related_project: str = Field(description="关联的项目经历")
    focus_area: str = Field(description="考察重点")


class InterviewQuestions(BaseModel):
    """面试题目集"""
    candidate_name: str = Field(description="候选人姓名")
    basic_questions: List[InterviewQuestion] = Field(
        min_length=2, max_length=2, description="2个基础题"
    )
    advanced_questions: List[InterviewQuestion] = Field(
        min_length=2, max_length=3, description="2-3个进阶题"
    )
    generation_timestamp: datetime = Field(
        default_factory=datetime.now, description="生成时间"
    )
