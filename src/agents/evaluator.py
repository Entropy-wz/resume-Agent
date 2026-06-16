# src/agents/evaluator.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from src.models import EvaluationResult
from src.config import get_settings

# 评分Agent的系统提示词
EVALUATOR_SYSTEM_PROMPT = """
你是一个专业的量化岗位简历评估专家。

你的任务是对候选人简历进行多维度评分：

## 评分维度和标准

### 1. 项目经历（满分30分）
评分要点：
- 项目与量化、金融、交易系统的相关性
- 项目复杂度和技术难度
- 候选人在项目中的角色和贡献
- 项目成果和影响力

量化相关项目包括：
- 量化交易策略开发（CTA、多因子、统计套利等）
- 交易系统、回测系统、风控系统
- 高频交易、算法交易
- 金融数据分析和建模

### 2. 实习经历（满分25分）
评分要点：
- 实习公司的行业相关性（量化、金融科技优先）
- 实习岗位与量化工作的匹配度
- 实习时长和深度
- 实习期间的具体工作内容和成果

### 3. 技术栈（满分25分）
评分要点：
- 编程语言：Python（必备）、C++（加分）
- 量化工具：pandas、numpy、backtrader、zipline等
- 机器学习：sklearn、pytorch、tensorflow等
- 数据库和中间件：Redis、Kafka、TimescaleDB等
- 金融数据接口：Wind、Tushare、akshare等

### 4. 科研经历（满分20分）
评分要点：
- 论文发表（顶会、SCI优先）
- 研究项目的质量和创新性
- 与量化、金融、机器学习的相关性
- 研究成果的实际应用价值

### 5. 竞赛加分（满分15分，独立加分项）
评分要点：
- 数学建模竞赛（美赛、国赛等）
- 量化投资比赛（宽客、WorldQuant等）
- 编程竞赛（ACM、LeetCode等）
- 金融科技比赛
- 获奖等级和含金量

## 评分原则

1. 客观公正：基于简历内容评分，不做主观臆断
2. 相关性优先：与量化岗位相关的经历给高分
3. 深度优先：有深度的项目比数量多但浅显的项目更有价值
4. 给出理由：每个维度必须给出详细的评分理由
5. 严格上限：各维度分数不能超过满分

## 输出格式

严格按照EvaluationResult模型输出，包含：
- candidate_name: 从简历中提取候选人姓名
- base_score: 四个维度的详细评分和理由
- bonus_score: 竞赛加分和理由
- final_score: 基础分 + 加分
- passed_screening: 根据final_score判断（需要外部阈值）
- timestamp: 当前时间

注意：
- 基础分total_base_score必须等于四个维度之和
- final_score必须等于total_base_score + bonus_points
- 所有分数必须在规定范围内
"""


def create_evaluator_agent() -> Agent[None, EvaluationResult]:
    """创建评分Agent"""
    import os
    settings = get_settings()

    # 设置环境变量供OpenAI SDK使用
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    os.environ["OPENAI_BASE_URL"] = settings.openai_base_url

    return Agent(
        model=OpenAIModel(settings.openai_model),
        output_type=EvaluationResult,
        system_prompt=EVALUATOR_SYSTEM_PROMPT,
    )


async def evaluate_resume(resume_text: str, threshold: float = 70.0) -> EvaluationResult:
    """
    评估简历

    Args:
        resume_text: 简历文本内容
        threshold: 初筛阈值

    Returns:
        EvaluationResult: 评估结果
    """
    agent = create_evaluator_agent()

    prompt = f"""
请评估以下简历：

{resume_text}

请严格按照评分标准进行打分，并给出详细理由。
初筛阈值为{threshold}分，请在passed_screening字段中标明是否通过。
"""

    result = await agent.run(prompt)

    # 获取结构化输出数据
    evaluation = result.output
    evaluation.passed_screening = evaluation.final_score >= threshold

    return evaluation
