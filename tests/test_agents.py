# tests/test_agents.py
import pytest
from src.agents.evaluator import evaluate_resume
from src.models import EvaluationResult


@pytest.mark.asyncio
async def test_evaluate_resume_structure():
    """测试评分Agent返回结构"""
    sample_resume = """
    姓名：张三
    教育背景：清华大学 计算机科学与技术 本科

    项目经历：
    1. 量化CTA策略开发（2023.06-2023.12）
       - 开发基于技术指标的CTA策略
       - 使用Python实现回测系统
       - 年化收益率15%，最大回撤8%

    实习经历：
    1. XX量化投资公司 量化研究实习生（2023.01-2023.06）
       - 协助开发多因子选股模型
       - 数据清洗和特征工程

    技术栈：
    - 编程语言：Python, C++
    - 量化工具：pandas, numpy, backtrader
    - 机器学习：sklearn, pytorch

    竞赛经历：
    - 全国大学生数学建模竞赛 一等奖
    """

    result = await evaluate_resume(sample_resume)

    assert isinstance(result, EvaluationResult)
    assert result.candidate_name
    assert 0 <= result.base_score.total_base_score <= 100
    assert 0 <= result.bonus_score.bonus_points <= 15
    assert 0 <= result.final_score <= 115
    assert isinstance(result.passed_screening, bool)


@pytest.mark.asyncio
async def test_evaluate_resume_scoring_logic():
    """测试评分逻辑合理性"""
    sample_resume = """
    姓名：李四
    教育背景：北京大学 数学系 硕士

    项目经历：
    1. 高频交易系统优化（2024.01-2024.06）
       - 将系统延迟从100微秒优化到20微秒
       - 使用C++重写关键路径

    技术栈：Python, C++, Redis, Kafka
    """

    result = await evaluate_resume(sample_resume)

    # 验证各维度分数在合理范围内
    assert result.base_score.project_experience.score <= 30
    assert result.base_score.internship_experience.score <= 25
    assert result.base_score.tech_stack.score <= 25
    assert result.base_score.research_experience.score <= 20

    # 验证总分等于各维度之和
    total = (
        result.base_score.project_experience.score +
        result.base_score.internship_experience.score +
        result.base_score.tech_stack.score +
        result.base_score.research_experience.score
    )
    assert abs(result.base_score.total_base_score - total) < 0.1

    # 验证最终分数
    expected_final = result.base_score.total_base_score + result.bonus_score.bonus_points
    assert abs(result.final_score - expected_final) < 0.1
