"""
端到端集成测试

注意：这些测试需要真实的OpenAI API密钥，会产生API调用费用
如果没有配置API密钥，测试将被跳过
"""

import pytest
import os
from src.workflow import create_resume_screening_workflow
from src.models import EvaluationResult, InterviewQuestions

# 检查是否有API密钥
HAS_API_KEY = bool(os.getenv("OPENAI_API_KEY"))
skip_without_api = pytest.mark.skipif(
    not HAS_API_KEY, reason="需要OPENAI_API_KEY环境变量才能运行集成测试"
)


@skip_without_api
@pytest.mark.asyncio
async def test_complete_workflow_with_mock_resume():
    """测试完整工作流（使用模拟简历文本）"""

    # 创建工作流
    workflow = create_resume_screening_workflow()

    # 模拟简历文本（不需要真实PDF）
    mock_resume_text = """
    张三
    量化研究员

    教育背景：
    北京大学 计算机科学与技术 硕士 2020-2023

    项目经历：
    1. CTA量化策略开发（2022.6-2023.3）
       - 开发基于动量和趋势的CTA策略
       - 使用Python和backtrader进行回测
       - 年化收益率15%，最大回撤8%
       - 使用Redis缓存行情数据，优化系统性能

    2. 多因子选股模型（2021.9-2022.5）
       - 构建包含50+因子的多因子模型
       - 使用机器学习方法进行因子筛选
       - 月度换手率控制在30%以内

    实习经历：
    某量化私募基金 量化研究实习生（2022.6-2022.12）
    - 协助开发期货套利策略
    - 优化回测系统性能，将回测速度提升3倍

    技术栈：
    - 编程语言：Python、C++
    - 量化工具：pandas、numpy、backtrader、TA-Lib
    - 机器学习：sklearn、pytorch
    - 数据库：PostgreSQL、Redis

    科研经历：
    发表论文：《基于深度学习的股票预测研究》（EI检索）

    竞赛经历：
    - 美国大学生数学建模竞赛 M奖
    - 全国量化投资策略大赛 第三名
    """

    # 准备初始状态（绕过PDF解析，直接提供文本）
    initial_state = {
        "resume_path": "mock_resume.pdf",  # 虽然不会真的解析，但需要提供
        "resume_text": mock_resume_text,  # 直接提供文本
        "threshold": 70.0,
    }

    # 运行工作流
    final_state = await workflow.ainvoke(initial_state)

    # 验证状态
    assert final_state.get("error") is None, f"工作流出错: {final_state.get('error')}"

    # 验证评估结果
    evaluation = final_state.get("evaluation")
    assert evaluation is not None, "评估结果不应为空"
    assert isinstance(evaluation, EvaluationResult), "评估结果类型错误"
    assert evaluation.candidate_name is not None, "候选人姓名不应为空"
    assert 0 <= evaluation.final_score <= 115, f"总分应在0-115之间，实际为{evaluation.final_score}"
    assert evaluation.passed_screening is not None, "初筛结果不应为空"

    # 验证评分逻辑
    base_total = (
        evaluation.base_score.project_experience.score
        + evaluation.base_score.internship_experience.score
        + evaluation.base_score.tech_stack.score
        + evaluation.base_score.research_experience.score
    )
    assert abs(base_total - evaluation.base_score.total_base_score) < 0.01, "基础分总和不一致"

    expected_final = (
        evaluation.base_score.total_base_score + evaluation.bonus_score.bonus_points
    )
    assert abs(expected_final - evaluation.final_score) < 0.01, "最终分数计算错误"

    # 如果通过初筛，应该有面试问题
    if evaluation.passed_screening:
        questions = final_state.get("questions")
        assert questions is not None, "通过初筛应该生成面试问题"
        assert isinstance(questions, InterviewQuestions), "面试问题类型错误"
        assert (
            len(questions.basic_questions) == 2
        ), f"应该有2个基础题，实际有{len(questions.basic_questions)}个"
        assert (
            2 <= len(questions.advanced_questions) <= 3
        ), f"应该有2-3个进阶题，实际有{len(questions.advanced_questions)}个"
    else:
        # 如果没通过初筛，不应该有面试问题
        questions = final_state.get("questions")
        assert questions is None, "未通过初筛不应该生成面试问题"


@skip_without_api
@pytest.mark.asyncio
async def test_workflow_with_different_thresholds():
    """测试不同阈值下的工作流行为"""

    workflow = create_resume_screening_workflow()

    mock_resume_text = """
    李四
    Python开发工程师

    教育背景：
    某普通大学 软件工程 本科 2019-2023

    项目经历：
    1. 校园二手交易平台（2022.3-2022.6）
       - 使用Django开发Web应用
       - 实现用户注册、商品发布、在线聊天功能

    技术栈：
    - Python、Django、MySQL
    """

    # 测试高阈值（应该不通过）
    high_threshold_state = {
        "resume_path": "mock_resume.pdf",
        "resume_text": mock_resume_text,
        "threshold": 80.0,
    }

    result_high = await workflow.ainvoke(high_threshold_state)
    evaluation_high = result_high.get("evaluation")

    assert evaluation_high is not None
    # 这个简历分数应该较低，不太可能通过80分阈值
    if evaluation_high.final_score < 80:
        assert not evaluation_high.passed_screening, "分数低于阈值应该不通过"
        assert result_high.get("questions") is None, "不通过初筛不应生成问题"

    # 测试低阈值（可能通过）
    low_threshold_state = {
        "resume_path": "mock_resume.pdf",
        "resume_text": mock_resume_text,
        "threshold": 40.0,
    }

    result_low = await workflow.ainvoke(low_threshold_state)
    evaluation_low = result_low.get("evaluation")

    assert evaluation_low is not None
    # 即使是弱简历，40分阈值应该能通过
    if evaluation_low.final_score >= 40:
        assert evaluation_low.passed_screening, "分数高于阈值应该通过"
        assert result_low.get("questions") is not None, "通过初筛应该生成问题"


@skip_without_api
@pytest.mark.asyncio
async def test_workflow_handles_empty_resume():
    """测试工作流处理空简历的情况"""

    workflow = create_resume_screening_workflow()

    # 空简历文本
    empty_resume_state = {
        "resume_path": "empty_resume.pdf",
        "resume_text": "",
        "threshold": 70.0,
    }

    result = await workflow.ainvoke(empty_resume_state)

    # 应该能够处理，但评分会很低
    evaluation = result.get("evaluation")
    assert evaluation is not None, "应该返回评估结果"
    assert evaluation.final_score < 20, "空简历分数应该很低"
    assert not evaluation.passed_screening, "空简历不应通过初筛"


@skip_without_api
@pytest.mark.asyncio
async def test_evaluation_score_ranges():
    """测试评分结果的范围约束"""

    workflow = create_resume_screening_workflow()

    # 优秀简历示例
    excellent_resume = """
    王五
    量化研究员

    教育背景：
    清华大学 金融工程 博士 2018-2023

    项目经历：
    1. 高频交易系统开发（2021-2023）
       - 设计并实现微秒级高频交易系统
       - 使用C++开发核心交易引擎
       - 系统延迟优化到10微秒
       - 日均处理订单百万级

    2. 机器学习因子挖掘平台（2020-2021）
       - 构建自动化因子挖掘和验证平台
       - 使用深度学习挖掘非线性因子
       - 因子IC值稳定在0.08以上

    实习经历：
    头部量化私募 量化研究员（2020.6-2021.12）
    - 独立开发多个盈利策略
    - 管理实盘策略规模500万

    技术栈：
    - C++、Python、Rust
    - 量化框架：vnpy、backtrader、zipline
    - 机器学习：pytorch、tensorflow、xgboost
    - 高性能计算：CUDA、OpenMP
    - 数据库：ClickHouse、TimescaleDB、Redis

    科研经历：
    - 发表SCI论文3篇（第一作者）
    - 国际顶会论文1篇（ICML）

    竞赛经历：
    - WorldQuant国际量化大赛 全球Top 10
    - ACM-ICPC亚洲区金牌
    - 美赛Outstanding Winner
    """

    state = {
        "resume_path": "excellent_resume.pdf",
        "resume_text": excellent_resume,
        "threshold": 70.0,
    }

    result = await workflow.ainvoke(state)
    evaluation = result.get("evaluation")

    assert evaluation is not None

    # 验证各项评分范围
    assert 0 <= evaluation.base_score.project_experience.score <= 30
    assert 0 <= evaluation.base_score.internship_experience.score <= 25
    assert 0 <= evaluation.base_score.tech_stack.score <= 25
    assert 0 <= evaluation.base_score.research_experience.score <= 20
    assert 0 <= evaluation.bonus_score.bonus_points <= 15

    # 验证总分逻辑
    assert 0 <= evaluation.base_score.total_base_score <= 100
    assert 0 <= evaluation.final_score <= 115

    # 优秀简历应该通过初筛
    assert evaluation.passed_screening, "优秀简历应该通过初筛"

    # 应该生成面试问题
    questions = result.get("questions")
    assert questions is not None
    assert len(questions.basic_questions) == 2
    assert 2 <= len(questions.advanced_questions) <= 3


@skip_without_api
@pytest.mark.asyncio
async def test_question_quality():
    """测试生成的面试问题质量"""

    workflow = create_resume_screening_workflow()

    resume_with_specific_project = """
    赵六
    量化开发工程师

    项目经历：
    1. CTA趋势跟踪策略（2023.1-2023.6）
       - 使用均线交叉和MACD指标
       - 在螺纹钢和铁矿石上测试
       - 年化收益率18%，夏普比率1.5
       - 使用Python和backtrader实现

    技术栈：
    - Python、pandas、numpy、backtrader
    - MySQL、Redis
    """

    state = {
        "resume_path": "resume.pdf",
        "resume_text": resume_with_specific_project,
        "threshold": 50.0,  # 设置较低阈值确保生成问题
    }

    result = await workflow.ainvoke(state)

    if result.get("evaluation").passed_screening:
        questions = result.get("questions")
        assert questions is not None

        # 检查基础题
        for q in questions.basic_questions:
            assert q.level == "basic"
            assert len(q.question) > 10, "问题应该有实质内容"
            assert q.related_project is not None, "应该关联具体项目"
            assert q.focus_area is not None, "应该有考察重点"

        # 检查进阶题
        for q in questions.advanced_questions:
            assert q.level == "advanced"
            assert len(q.question) > 10, "问题应该有实质内容"
            assert q.focus_area is not None, "应该有考察重点"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
