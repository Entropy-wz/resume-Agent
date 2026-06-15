# 量化岗位简历筛选Agent实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个用于量化岗位招聘的简历筛选子Agent，使用LangGraph编排工作流，Pydantic AI执行评分和题目生成任务

**Architecture:** 
- LangGraph状态机编排工作流（PDF解析 → 评分 → 判断 → 生成题目）
- Pydantic AI Agent执行评分和题目生成
- LangChain处理PDF解析
- 结构化输出使用Pydantic模型

**Tech Stack:** 
- Python 3.10+
- Pydantic AI + LangChain + LangGraph
- OpenAI GPT-4
- PyPDF for PDF parsing
- pytest for testing

---

## 文件结构规划

```
resume-agent/
├── src/
│   ├── __init__.py              # 主接口导出
│   ├── models.py                # Pydantic数据模型
│   ├── config.py                # 配置管理
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # 评分Agent
│   │   └── question_generator.py # 题目生成Agent
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── parser.py            # PDF解析节点
│   │   ├── evaluator.py         # 评分节点
│   │   ├── checker.py           # 阈值检查节点
│   │   └── generator.py         # 题目生成节点
│   └── workflow.py              # LangGraph工作流
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_agents.py
│   ├── test_nodes.py
│   ├── test_workflow.py
│   └── fixtures/
│       └── sample_resume.pdf
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Task 1: 项目初始化和依赖配置

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "resume-agent"
version = "0.1.0"
description = "Resume screening agent for quantitative finance positions"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0.0",
    "pydantic-ai>=0.0.13",
    "langchain>=0.1.0",
    "langgraph>=0.0.60",
    "langchain-community>=0.0.38",
    "openai>=1.0.0",
    "pypdf>=3.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
```

- [ ] **Step 2: 创建 .env.example**

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Screening Configuration
DEFAULT_THRESHOLD=70.0

# Scoring Weights
WEIGHT_PROJECT=0.30
WEIGHT_INTERNSHIP=0.25
WEIGHT_TECH_STACK=0.25
WEIGHT_RESEARCH=0.20
MAX_BONUS=15.0

# Question Generation
NUM_BASIC_QUESTIONS=2
NUM_ADVANCED_QUESTIONS_MIN=2
NUM_ADVANCED_QUESTIONS_MAX=3
```

- [ ] **Step 3: 创建 .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env

# Testing
.pytest_cache/
.coverage
htmlcov/

# Superpowers
.superpowers/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 4: 创建 README.md**

```markdown
# Resume Screening Agent

量化岗位简历筛选Agent，使用LangGraph编排工作流，Pydantic AI执行评分和题目生成。

## 功能

- 多维度评分：项目经历(30%)、实习经历(25%)、技术栈(25%)、科研经历(20%)
- 竞赛加分：独立15分加分项
- 固定阈值初筛：默认70分
- 分层面试题目生成：2个基础题 + 2-3个进阶题

## 安装

```bash
pip install -e .
```

## 配置

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

## 使用

```python
from resume_agent import ResumeScreeningAgent

agent = ResumeScreeningAgent(
    openai_api_key="sk-xxx",
    threshold=70.0
)

result = await agent.screen_resume("path/to/resume.pdf")
print(result["evaluation"])
print(result["interview_questions"])
```

## 测试

```bash
pytest
```

## 架构

- LangGraph：工作流编排
- Pydantic AI：评分和题目生成Agent
- LangChain：PDF解析
- OpenAI GPT-4：大语言模型
```

- [ ] **Step 5: 创建目录结构**

```bash
mkdir -p src/agents src/nodes tests/fixtures
touch src/__init__.py src/agents/__init__.py src/nodes/__init__.py tests/__init__.py
```

- [ ] **Step 6: 安装依赖**

```bash
pip install -e ".[dev]"
```

Expected: 所有依赖成功安装

- [ ] **Step 7: 提交初始化**

```bash
git add pyproject.toml .env.example .gitignore README.md
git add src/ tests/
git commit -m "chore: initialize project structure and dependencies

- Add pyproject.toml with all dependencies
- Create .env.example for configuration
- Add .gitignore for Python project
- Create README.md with usage instructions
- Set up directory structure

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: 数据模型定义

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: 编写数据模型测试**

```python
# tests/test_models.py
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_models.py -v
```

Expected: 所有测试失败，提示 "ModuleNotFoundError: No module named 'src.models'"

- [ ] **Step 3: 实现数据模型**

```python
# src/models.py
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_models.py -v
```

Expected: 所有测试通过

- [ ] **Step 5: 提交数据模型**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: add Pydantic data models

- Add DimensionScore for individual dimension scoring
- Add BaseScore for 100-point base scoring system
- Add BonusScore for competition bonus (0-15 points)
- Add EvaluationResult for complete evaluation
- Add InterviewQuestion and InterviewQuestions models
- Add comprehensive unit tests for all models

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

## Task 3: 配置管理

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写配置测试**

```python
# tests/test_config.py
import os
from src.config import Settings


def test_settings_from_env(monkeypatch):
    """测试从环境变量加载配置"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("DEFAULT_THRESHOLD", "75.0")
    
    settings = Settings()
    assert settings.openai_api_key == "sk-test-key"
    assert settings.default_threshold == 75.0


def test_settings_defaults():
    """测试默认配置值"""
    settings = Settings(openai_api_key="sk-test")
    assert settings.openai_model == "gpt-4"
    assert settings.default_threshold == 70.0
    assert settings.weight_project == 0.30
    assert settings.weight_internship == 0.25
    assert settings.weight_tech_stack == 0.25
    assert settings.weight_research == 0.20
    assert settings.max_bonus == 15.0


def test_question_config():
    """测试题目配置"""
    settings = Settings(openai_api_key="sk-test")
    assert settings.num_basic_questions == 2
    assert settings.num_advanced_questions_min == 2
    assert settings.num_advanced_questions_max == 3
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_config.py -v
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.config'"

- [ ] **Step 3: 实现配置管理**

```python
# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI配置
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # 评分配置
    default_threshold: float = 70.0
    
    # 权重配置
    weight_project: float = 0.30
    weight_internship: float = 0.25
    weight_tech_stack: float = 0.25
    weight_research: float = 0.20
    max_bonus: float = 15.0
    
    # 题目数量配置
    num_basic_questions: int = 2
    num_advanced_questions_min: int = 2
    num_advanced_questions_max: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 全局配置实例（懒加载）
_settings = None


def get_settings() -> Settings:
    """获取配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_config.py -v
```

Expected: 所有测试通过

- [ ] **Step 5: 提交配置管理**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration management

- Add Settings class using pydantic-settings
- Support loading from .env file
- Define scoring weights and thresholds
- Add question generation config
- Implement singleton pattern for settings
- Add unit tests for configuration

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Pydantic AI 评分Agent

**Files:**
- Create: `src/agents/evaluator.py`
- Create: `tests/test_agents.py`

- [ ] **Step 1: 编写评分Agent测试**

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_agents.py -v -k "test_evaluate"
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.agents.evaluator'"

- [ ] **Step 3: 实现评分Agent**

```python
# src/agents/evaluator.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from src.models import EvaluationResult, DimensionScore, BaseScore, BonusScore
from src.config import get_settings
from datetime import datetime


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
    settings = get_settings()
    
    return Agent(
        model=OpenAIModel(settings.openai_model),
        result_type=EvaluationResult,
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
    
    # 确保passed_screening正确设置
    evaluation = result.data
    evaluation.passed_screening = evaluation.final_score >= threshold
    
    return evaluation
```

- [ ] **Step 4: 运行测试（需要API key）**

```bash
# 设置测试用的API key
export OPENAI_API_KEY="sk-your-test-key"
pytest tests/test_agents.py -v -k "test_evaluate" --tb=short
```

Expected: 如果API key有效，测试应该通过；否则会有连接错误但代码结构正确

- [ ] **Step 5: 提交评分Agent**

```bash
git add src/agents/evaluator.py tests/test_agents.py
git commit -m "feat: implement Pydantic AI evaluator agent

- Create evaluator agent with detailed system prompt
- Define scoring criteria for 5 dimensions
- Implement evaluate_resume async function
- Add comprehensive tests for scoring logic
- Ensure score validation and consistency

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Pydantic AI 题目生成Agent

**Files:**
- Modify: `src/agents/question_generator.py`
- Modify: `tests/test_agents.py`

- [ ] **Step 1: 编写题目生成Agent测试**

```python
# 添加到 tests/test_agents.py
from src.agents.question_generator import generate_questions
from src.models import InterviewQuestions, EvaluationResult, BaseScore, BonusScore, DimensionScore
from datetime import datetime


@pytest.mark.asyncio
async def test_generate_questions_structure():
    """测试题目生成Agent返回结构"""
    sample_resume = """
    姓名：张三
    项目经历：开发了CTA策略和多因子选股模型
    """
    
    sample_evaluation = EvaluationResult(
        candidate_name="张三",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目经历", score=25.0, max_score=30.0, 
                reasoning="有CTA和多因子经验"
            ),
            internship_experience=DimensionScore(
                dimension="实习经历", score=20.0, max_score=25.0, reasoning="良好"
            ),
            tech_stack=DimensionScore(
                dimension="技术栈", score=20.0, max_score=25.0, reasoning="扎实"
            ),
            research_experience=DimensionScore(
                dimension="科研经历", score=15.0, max_score=20.0, reasoning="一般"
            ),
            total_base_score=80.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0.0, reasoning="无竞赛"
        ),
        final_score=80.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    
    questions = await generate_questions(sample_resume, sample_evaluation)
    
    assert isinstance(questions, InterviewQuestions)
    assert questions.candidate_name == "张三"
    assert len(questions.basic_questions) == 2
    assert 2 <= len(questions.advanced_questions) <= 3
    
    # 验证基础题
    for q in questions.basic_questions:
        assert q.level == "basic"
        assert len(q.question) > 10
        assert q.related_project
        assert q.focus_area
    
    # 验证进阶题
    for q in questions.advanced_questions:
        assert q.level == "advanced"
        assert len(q.question) > 10
        assert q.related_project
        assert q.focus_area


@pytest.mark.asyncio
async def test_generate_questions_relevance():
    """测试题目与简历相关性"""
    sample_resume = """
    姓名：李四
    项目经历：
    1. 高频交易系统延迟优化
       - 使用C++优化关键路径
       - 延迟从100微秒降至20微秒
    """
    
    sample_evaluation = EvaluationResult(
        candidate_name="李四",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目经历", score=28.0, max_score=30.0, 
                reasoning="高频交易经验丰富"
            ),
            internship_experience=DimensionScore(
                dimension="实习经历", score=15.0, max_score=25.0, reasoning="一般"
            ),
            tech_stack=DimensionScore(
                dimension="技术栈", score=23.0, max_score=25.0, reasoning="C++强"
            ),
            research_experience=DimensionScore(
                dimension="科研经历", score=10.0, max_score=20.0, reasoning="较少"
            ),
            total_base_score=76.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0.0, reasoning="无竞赛"
        ),
        final_score=76.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    
    questions = await generate_questions(sample_resume, sample_evaluation)
    
    # 验证题目与高频交易相关
    all_questions_text = " ".join([q.question for q in questions.basic_questions + questions.advanced_questions])
    
    # 至少有一道题目应该与高频、延迟、优化相关
    assert any(keyword in all_questions_text for keyword in ["高频", "延迟", "优化", "性能", "交易"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_agents.py -v -k "test_generate_questions"
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.agents.question_generator'"

- [ ] **Step 3: 实现题目生成Agent**

```python
# src/agents/question_generator.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from src.models import InterviewQuestions, EvaluationResult
from src.config import get_settings


# 题目生成Agent的系统提示词
QUESTION_GENERATOR_SYSTEM_PROMPT = """
你是一个专业的量化岗位面试官。

根据候选人的简历和评分结果，生成面试题目。

## 题目类型

### 1. 基础题（2题）
目的：
- 考察候选人对自己项目和技术的基本理解
- 覆盖面广，让候选人有机会展示不同方面的能力
- 作为面试的开场，帮助候选人进入状态

特点：
- 相对开放，让候选人自己选择切入点
- 可以是概况性的问题
- 难度适中，大部分候选人应该能够回答

示例：
- "请介绍一下你最擅长或最有成就感的量化策略项目"
- "你在项目中使用了哪些技术栈？为什么选择这些技术？"
- "请描述一个你在量化工作中遇到的技术难题，以及你是如何解决的"

### 2. 进阶题（2-3题）
目的：
- 深入考察候选人的技术能力和问题解决能力
- 针对候选人简历中的具体项目进行深挖
- 考察候选人对细节的掌握和思考深度

特点：
- 针对性强，基于候选人的具体项目经历
- 有一定技术深度
- 需要候选人给出具体的技术方案或经验

示例（针对CTA策略项目）：
- "在你的CTA策略中，如何处理信号延迟和滑点的影响？"
- "你的回测系统如何保证历史数据的准确性和完整性？"
- "如何评估和优化策略的风险收益比？"

示例（针对高频交易项目）：
- "你提到将延迟从100微秒优化到20微秒，具体采用了哪些优化手段？"
- "在高并发场景下，如何保证订单系统的正确性和一致性？"
- "如何监控和诊断生产环境中的性能问题？"

## 出题原则

1. **基于简历**：题目必须与候选人简历中提到的项目、技术相关
2. **避免超纲**：不要问候选人简历中完全没有涉及的领域
3. **有深度**：进阶题要能考察真实能力，不是简单的概念题
4. **可回答性**：题目应该是候选人能够回答的，避免过于刁钻
5. **多样性**：题目应该覆盖不同方面（策略、系统、数据、风控等）

## 输出格式

严格按照InterviewQuestions模型输出，包含：
- candidate_name: 候选人姓名
- basic_questions: 恰好2个基础题
- advanced_questions: 2-3个进阶题
- generation_timestamp: 当前时间

每个题目包含：
- level: "basic" 或 "advanced"
- question: 题目内容
- related_project: 相关的项目名称或描述
- focus_area: 考察重点（如"策略设计"、"系统架构"、"风险控制"等）
"""


def create_question_generator_agent() -> Agent[None, InterviewQuestions]:
    """创建题目生成Agent"""
    settings = get_settings()
    
    return Agent(
        model=OpenAIModel(settings.openai_model),
        result_type=InterviewQuestions,
        system_prompt=QUESTION_GENERATOR_SYSTEM_PROMPT,
    )


async def generate_questions(
    resume_text: str,
    evaluation: EvaluationResult
) -> InterviewQuestions:
    """
    生成面试题目
    
    Args:
        resume_text: 简历文本内容
        evaluation: 评估结果
        
    Returns:
        InterviewQuestions: 面试题目集
    """
    agent = create_question_generator_agent()
    
    prompt = f"""
请为以下候选人生成面试题目：

## 候选人信息
姓名：{evaluation.candidate_name}

## 简历内容
{resume_text}

## 评分结果
- 项目经历：{evaluation.base_score.project_experience.score}/{evaluation.base_score.project_experience.max_score}分
  理由：{evaluation.base_score.project_experience.reasoning}
  
- 实习经历：{evaluation.base_score.internship_experience.score}/{evaluation.base_score.internship_experience.max_score}分
  理由：{evaluation.base_score.internship_experience.reasoning}
  
- 技术栈：{evaluation.base_score.tech_stack.score}/{evaluation.base_score.tech_stack.max_score}分
  理由：{evaluation.base_score.tech_stack.reasoning}
  
- 科研经历：{evaluation.base_score.research_experience.score}/{evaluation.base_score.research_experience.max_score}分
  理由：{evaluation.base_score.research_experience.reasoning}

- 竞赛加分：{evaluation.bonus_score.bonus_points}分
  理由：{evaluation.bonus_score.reasoning}

- 总分：{evaluation.final_score}/115分

## 要求
请根据候选人的项目经历和技术背景，生成：
1. 2个基础题（覆盖面广，难度适中）
2. 2-3个进阶题（针对具体项目，有深度）

所有题目必须与候选人简历中的内容相关。
"""
    
    result = await agent.run(prompt)
    return result.data
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_agents.py -v -k "test_generate_questions"
```

Expected: 测试通过（需要有效的API key）

- [ ] **Step 5: 提交题目生成Agent**

```bash
git add src/agents/question_generator.py tests/test_agents.py
git commit -m "feat: implement Pydantic AI question generator agent

- Create question generator with detailed system prompt
- Define basic and advanced question criteria
- Implement generate_questions async function
- Add tests for question structure and relevance
- Ensure questions match candidate's experience

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

## Task 6: LangGraph工作流节点 - PDF解析

**Files:**
- Create: `src/nodes/parser.py`
- Create: `tests/test_nodes.py`
- Create: `tests/fixtures/sample_resume.pdf`

- [ ] **Step 1: 创建测试用简历PDF**

手动创建一个测试用的简历PDF文件：`tests/fixtures/sample_resume.pdf`

内容示例：
```
姓名：测试候选人
教育背景：清华大学 计算机科学 本科

项目经历：
1. 量化CTA策略开发
   - 开发基于技术指标的CTA策略
   - 使用Python实现回测系统

技术栈：Python, pandas, numpy

竞赛：数学建模竞赛 一等奖
```

注：如果无法手动创建PDF，可以跳过此步骤，在后续测试中使用mock

- [ ] **Step 2: 编写PDF解析节点测试**

```python
# tests/test_nodes.py
import pytest
from typing import TypedDict, Optional
from src.nodes.parser import parse_resume_node


class MockAgentState(TypedDict):
    """测试用的状态类型"""
    resume_path: str
    resume_text: str
    evaluation: Optional[dict]
    interview_questions: Optional[dict]
    threshold: float
    error: Optional[str]


def test_parse_resume_node_success():
    """测试PDF解析成功"""
    initial_state: MockAgentState = {
        "resume_path": "tests/fixtures/sample_resume.pdf",
        "resume_text": "",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = parse_resume_node(initial_state)
    
    assert result["resume_text"]
    assert len(result["resume_text"]) > 0
    assert result["error"] is None


def test_parse_resume_node_file_not_found():
    """测试文件不存在的情况"""
    initial_state: MockAgentState = {
        "resume_path": "nonexistent.pdf",
        "resume_text": "",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = parse_resume_node(initial_state)
    
    assert result["resume_text"] == ""
    assert result["error"] is not None
    assert "失败" in result["error"] or "not found" in result["error"].lower()


def test_parse_resume_node_preserves_other_state():
    """测试节点不修改其他状态字段"""
    initial_state: MockAgentState = {
        "resume_path": "tests/fixtures/sample_resume.pdf",
        "resume_text": "",
        "evaluation": {"some": "data"},
        "interview_questions": None,
        "threshold": 75.0,
        "error": None
    }
    
    result = parse_resume_node(initial_state)
    
    assert result["threshold"] == 75.0
    assert result["evaluation"] == {"some": "data"}
```

- [ ] **Step 3: 运行测试确认失败**

```bash
pytest tests/test_nodes.py -v -k "parse_resume"
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.nodes.parser'"

- [ ] **Step 4: 实现PDF解析节点**

```python
# src/nodes/parser.py
from typing import Dict, Any
from langchain_community.document_loaders import PyPDFLoader


def parse_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析PDF简历节点
    
    Args:
        state: 工作流状态，必须包含resume_path字段
        
    Returns:
        更新后的状态，包含resume_text或error字段
    """
    try:
        resume_path = state["resume_path"]
        
        # 使用LangChain的PDF加载器
        loader = PyPDFLoader(resume_path)
        documents = loader.load()
        
        # 合并所有页面的文本
        resume_text = "\n".join([doc.page_content for doc in documents])
        
        return {
            **state,
            "resume_text": resume_text,
            "error": None
        }
    
    except FileNotFoundError:
        return {
            **state,
            "resume_text": "",
            "error": f"PDF文件未找到: {state.get('resume_path', 'unknown')}"
        }
    
    except Exception as e:
        return {
            **state,
            "resume_text": "",
            "error": f"PDF解析失败: {str(e)}"
        }
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/test_nodes.py -v -k "parse_resume"
```

Expected: 测试通过（如果有sample_resume.pdf）或部分通过

- [ ] **Step 6: 提交PDF解析节点**

```bash
git add src/nodes/parser.py tests/test_nodes.py tests/fixtures/
git commit -m "feat: implement PDF parsing node

- Add parse_resume_node using LangChain PyPDFLoader
- Handle file not found and parsing errors
- Preserve other state fields
- Add unit tests for success and error cases

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: LangGraph工作流节点 - 评分节点

**Files:**
- Create: `src/nodes/evaluator.py`
- Modify: `tests/test_nodes.py`

- [ ] **Step 1: 编写评分节点测试**

```python
# 添加到 tests/test_nodes.py
import pytest
from src.nodes.evaluator import evaluate_resume_node
from src.models import EvaluationResult


@pytest.mark.asyncio
async def test_evaluate_resume_node_success():
    """测试评分节点成功"""
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": """
        姓名：张三
        项目经历：量化CTA策略开发
        技术栈：Python, C++
        """,
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = await evaluate_resume_node(initial_state)
    
    assert result["evaluation"] is not None
    assert isinstance(result["evaluation"], EvaluationResult)
    assert result["evaluation"].candidate_name == "张三"
    assert result["error"] is None


@pytest.mark.asyncio
async def test_evaluate_resume_node_empty_text():
    """测试简历文本为空的情况"""
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = await evaluate_resume_node(initial_state)
    
    assert result["evaluation"] is None
    assert result["error"] is not None


@pytest.mark.asyncio
async def test_evaluate_resume_node_uses_threshold():
    """测试评分节点使用正确的阈值"""
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "姓名：李四\n项目：简单项目",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 80.0,
        "error": None
    }
    
    result = await evaluate_resume_node(initial_state)
    
    # 阈值应该被传递给评分函数
    # passed_screening应该根据80分阈值判断
    if result["evaluation"]:
        evaluation = result["evaluation"]
        if evaluation.final_score >= 80.0:
            assert evaluation.passed_screening is True
        else:
            assert evaluation.passed_screening is False
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_nodes.py -v -k "evaluate_resume_node"
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.nodes.evaluator'"

- [ ] **Step 3: 实现评分节点**

```python
# src/nodes/evaluator.py
from typing import Dict, Any
from src.agents.evaluator import evaluate_resume
from src.models import EvaluationResult


async def evaluate_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    评分节点
    
    Args:
        state: 工作流状态，必须包含resume_text和threshold字段
        
    Returns:
        更新后的状态，包含evaluation或error字段
    """
    try:
        resume_text = state.get("resume_text", "")
        
        if not resume_text or not resume_text.strip():
            return {
                **state,
                "evaluation": None,
                "error": "简历文本为空，无法评分"
            }
        
        threshold = state.get("threshold", 70.0)
        
        # 调用评分Agent
        evaluation = await evaluate_resume(resume_text, threshold)
        
        return {
            **state,
            "evaluation": evaluation,
            "error": None
        }
    
    except Exception as e:
        return {
            **state,
            "evaluation": None,
            "error": f"评分失败: {str(e)}"
        }
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_nodes.py -v -k "evaluate_resume_node"
```

Expected: 测试通过（需要有效的API key）

- [ ] **Step 5: 提交评分节点**

```bash
git add src/nodes/evaluator.py tests/test_nodes.py
git commit -m "feat: implement evaluation node

- Add evaluate_resume_node wrapping evaluator agent
- Handle empty resume text
- Pass threshold from state to agent
- Add comprehensive unit tests

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: LangGraph工作流节点 - 阈值检查和题目生成

**Files:**
- Create: `src/nodes/checker.py`
- Create: `src/nodes/generator.py`
- Modify: `tests/test_nodes.py`

- [ ] **Step 1: 编写阈值检查节点测试**

```python
# 添加到 tests/test_nodes.py
from src.nodes.checker import check_threshold_node
from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore
from datetime import datetime


def test_check_threshold_node_pass():
    """测试通过阈值的情况"""
    evaluation = EvaluationResult(
        candidate_name="张三",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=25, max_score=30, reasoning="优秀"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=20, max_score=25, reasoning="良好"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=22, max_score=25, reasoning="扎实"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=15, max_score=20, reasoning="一般"
            ),
            total_base_score=82.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=82.0,
        passed_screening=False,  # 初始值
        timestamp=datetime.now()
    )
    
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = check_threshold_node(initial_state)
    
    assert result["evaluation"].passed_screening is True


def test_check_threshold_node_fail():
    """测试未通过阈值的情况"""
    evaluation = EvaluationResult(
        candidate_name="李四",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=15, max_score=30, reasoning="一般"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=10, max_score=25, reasoning="较少"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=15, max_score=25, reasoning="基础"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=8, max_score=20, reasoning="较少"
            ),
            total_base_score=48.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=48.0,
        passed_screening=True,  # 初始值
        timestamp=datetime.now()
    )
    
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = check_threshold_node(initial_state)
    
    assert result["evaluation"].passed_screening is False


def test_check_threshold_node_boundary():
    """测试边界情况（恰好等于阈值）"""
    evaluation = EvaluationResult(
        candidate_name="王五",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=20, max_score=30, reasoning="合格"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=18, max_score=25, reasoning="合格"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=18, max_score=25, reasoning="合格"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=14, max_score=20, reasoning="合格"
            ),
            total_base_score=70.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=70.0,
        passed_screening=False,
        timestamp=datetime.now()
    )
    
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = check_threshold_node(initial_state)
    
    # 等于阈值应该通过
    assert result["evaluation"].passed_screening is True
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_nodes.py -v -k "check_threshold"
```

Expected: 测试失败 "ModuleNotFoundError"

- [ ] **Step 3: 实现阈值检查节点**

```python
# src/nodes/checker.py
from typing import Dict, Any
from src.models import EvaluationResult


def check_threshold_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查是否通过初筛阈值
    
    Args:
        state: 工作流状态，必须包含evaluation和threshold字段
        
    Returns:
        更新后的状态，evaluation.passed_screening字段被更新
    """
    evaluation: EvaluationResult = state.get("evaluation")
    
    if evaluation is None:
        return state
    
    threshold = state.get("threshold", 70.0)
    
    # 更新passed_screening字段
    evaluation.passed_screening = evaluation.final_score >= threshold
    
    return {
        **state,
        "evaluation": evaluation
    }
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_nodes.py -v -k "check_threshold"
```

Expected: 所有测试通过

- [ ] **Step 5: 编写题目生成节点测试**

```python
# 继续添加到 tests/test_nodes.py
import pytest
from src.nodes.generator import generate_questions_node


@pytest.mark.asyncio
async def test_generate_questions_node_success():
    """测试题目生成节点成功"""
    evaluation = EvaluationResult(
        candidate_name="张三",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=25, max_score=30, reasoning="CTA策略经验"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=20, max_score=25, reasoning="量化实习"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=22, max_score=25, reasoning="Python/C++"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=15, max_score=20, reasoning="机器学习研究"
            ),
            total_base_score=82.0
        ),
        bonus_score=BonusScore(
            competitions=["数学建模"], bonus_points=8, reasoning="国赛一等奖"
        ),
        final_score=90.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "姓名：张三\n项目：CTA策略开发\n技术：Python, C++",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = await generate_questions_node(initial_state)
    
    assert result["interview_questions"] is not None
    assert result["interview_questions"].candidate_name == "张三"
    assert len(result["interview_questions"].basic_questions) == 2
    assert 2 <= len(result["interview_questions"].advanced_questions) <= 3
    assert result["error"] is None


@pytest.mark.asyncio
async def test_generate_questions_node_no_evaluation():
    """测试没有评估结果的情况"""
    initial_state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = await generate_questions_node(initial_state)
    
    assert result["interview_questions"] is None
    assert result["error"] is not None
```

- [ ] **Step 6: 运行测试确认失败**

```bash
pytest tests/test_nodes.py -v -k "generate_questions_node"
```

Expected: 测试失败 "ModuleNotFoundError"

- [ ] **Step 7: 实现题目生成节点**

```python
# src/nodes/generator.py
from typing import Dict, Any
from src.agents.question_generator import generate_questions
from src.models import EvaluationResult, InterviewQuestions


async def generate_questions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成面试题目节点
    
    Args:
        state: 工作流状态，必须包含resume_text和evaluation字段
        
    Returns:
        更新后的状态，包含interview_questions或error字段
    """
    try:
        evaluation: EvaluationResult = state.get("evaluation")
        resume_text = state.get("resume_text", "")
        
        if evaluation is None:
            return {
                **state,
                "interview_questions": None,
                "error": "缺少评估结果，无法生成题目"
            }
        
        if not resume_text or not resume_text.strip():
            return {
                **state,
                "interview_questions": None,
                "error": "简历文本为空，无法生成题目"
            }
        
        # 调用题目生成Agent
        questions = await generate_questions(resume_text, evaluation)
        
        return {
            **state,
            "interview_questions": questions,
            "error": None
        }
    
    except Exception as e:
        return {
            **state,
            "interview_questions": None,
            "error": f"题目生成失败: {str(e)}"
        }
```

- [ ] **Step 8: 运行测试**

```bash
pytest tests/test_nodes.py -v -k "generate_questions_node"
```

Expected: 测试通过（需要有效的API key）

- [ ] **Step 9: 提交阈值检查和题目生成节点**

```bash
git add src/nodes/checker.py src/nodes/generator.py tests/test_nodes.py
git commit -m "feat: implement checker and generator nodes

- Add check_threshold_node for screening decision
- Add generate_questions_node wrapping question agent
- Handle missing evaluation and empty text
- Add comprehensive tests for all cases including boundary

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

## Task 9: LangGraph工作流组装

**Files:**
- Create: `src/workflow.py`
- Create: `tests/test_workflow.py`

- [ ] **Step 1: 编写工作流测试**

```python
# tests/test_workflow.py
import pytest
from src.workflow import create_resume_screening_workflow, should_generate_questions
from typing import TypedDict, Optional
from src.models import EvaluationResult, BaseScore, BonusScore, DimensionScore
from datetime import datetime


class MockAgentState(TypedDict):
    """测试用的状态类型"""
    resume_path: str
    resume_text: str
    evaluation: Optional[EvaluationResult]
    interview_questions: Optional[dict]
    threshold: float
    error: Optional[str]


def test_should_generate_questions_with_error():
    """测试有错误时的条件判断"""
    state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": "某个错误"
    }
    
    result = should_generate_questions(state)
    assert result == "end"


def test_should_generate_questions_passed():
    """测试通过初筛时的条件判断"""
    evaluation = EvaluationResult(
        candidate_name="张三",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=25, max_score=30, reasoning="优秀"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=20, max_score=25, reasoning="良好"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=22, max_score=25, reasoning="扎实"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=15, max_score=20, reasoning="一般"
            ),
            total_base_score=82.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=82.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    
    state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = should_generate_questions(state)
    assert result == "generate_questions"


def test_should_generate_questions_failed():
    """测试未通过初筛时的条件判断"""
    evaluation = EvaluationResult(
        candidate_name="李四",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=15, max_score=30, reasoning="一般"
            ),
            internship_experience=DimensionScore(
                dimension="实习", score=10, max_score=25, reasoning="较少"
            ),
            tech_stack=DimensionScore(
                dimension="技术", score=15, max_score=25, reasoning="基础"
            ),
            research_experience=DimensionScore(
                dimension="科研", score=8, max_score=20, reasoning="较少"
            ),
            total_base_score=48.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=48.0,
        passed_screening=False,
        timestamp=datetime.now()
    )
    
    state: MockAgentState = {
        "resume_path": "test.pdf",
        "resume_text": "test",
        "evaluation": evaluation,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = should_generate_questions(state)
    assert result == "end"


def test_create_workflow():
    """测试工作流创建"""
    workflow = create_resume_screening_workflow()
    
    # 验证工作流对象存在
    assert workflow is not None
    
    # 验证工作流是已编译的
    # LangGraph编译后的workflow有invoke方法
    assert hasattr(workflow, "invoke") or hasattr(workflow, "ainvoke")


@pytest.mark.asyncio
async def test_workflow_integration_success():
    """测试完整工作流（需要真实PDF和API key）"""
    # 这个测试需要真实的环境，标记为integration测试
    pytest.skip("需要真实PDF和API key，作为集成测试运行")
    
    workflow = create_resume_screening_workflow()
    
    initial_state = {
        "resume_path": "tests/fixtures/sample_resume.pdf",
        "resume_text": "",
        "evaluation": None,
        "interview_questions": None,
        "threshold": 70.0,
        "error": None
    }
    
    result = await workflow.ainvoke(initial_state)
    
    assert result["resume_text"]
    assert result["evaluation"] is not None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_workflow.py -v
```

Expected: 测试失败 "ModuleNotFoundError: No module named 'src.workflow'"

- [ ] **Step 3: 实现工作流组装**

```python
# src/workflow.py
from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END
from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node
from src.nodes.checker import check_threshold_node
from src.nodes.generator import generate_questions_node


def should_generate_questions(state: Dict[str, Any]) -> Literal["generate_questions", "end"]:
    """
    决定是否生成面试题目的条件函数
    
    Args:
        state: 工作流状态
        
    Returns:
        "generate_questions" 如果通过初筛，否则 "end"
    """
    # 如果有错误，直接结束
    if state.get("error"):
        return "end"
    
    # 如果没有评估结果，直接结束
    evaluation = state.get("evaluation")
    if evaluation is None:
        return "end"
    
    # 根据是否通过初筛决定
    if evaluation.passed_screening:
        return "generate_questions"
    else:
        return "end"


def create_resume_screening_workflow():
    """
    创建简历筛选工作流
    
    Returns:
        编译后的LangGraph工作流
    """
    # 创建状态图
    # 注意：我们使用Dict[str, Any]而不是严格的TypedDict
    # 因为LangGraph需要更灵活的状态类型
    workflow = StateGraph(dict)
    
    # 添加节点
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("evaluate_resume", evaluate_resume_node)
    workflow.add_node("check_threshold", check_threshold_node)
    workflow.add_node("generate_questions", generate_questions_node)
    
    # 设置入口点
    workflow.set_entry_point("parse_resume")
    
    # 添加边：parse -> evaluate
    workflow.add_edge("parse_resume", "evaluate_resume")
    
    # 添加边：evaluate -> check
    workflow.add_edge("evaluate_resume", "check_threshold")
    
    # 添加条件边：check -> generate_questions 或 END
    workflow.add_conditional_edges(
        "check_threshold",
        should_generate_questions,
        {
            "generate_questions": "generate_questions",
            "end": END
        }
    )
    
    # 添加边：generate_questions -> END
    workflow.add_edge("generate_questions", END)
    
    # 编译工作流
    return workflow.compile()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_workflow.py -v
```

Expected: 除了integration测试外，其他测试通过

- [ ] **Step 5: 提交工作流**

```bash
git add src/workflow.py tests/test_workflow.py
git commit -m "feat: implement LangGraph workflow

- Create StateGraph with 4 nodes
- Add parse -> evaluate -> check -> generate flow
- Implement conditional edge for screening decision
- Add comprehensive tests for workflow logic
- Skip integration test for CI

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: 主接口实现

**Files:**
- Modify: `src/__init__.py`
- Create: `tests/test_integration.py`

- [ ] **Step 1: 编写主接口测试**

```python
# tests/test_integration.py
import pytest
from src import ResumeScreeningAgent


def test_resume_screening_agent_initialization():
    """测试Agent初始化"""
    agent = ResumeScreeningAgent(
        openai_api_key="sk-test-key",
        threshold=75.0
    )
    
    assert agent.openai_api_key == "sk-test-key"
    assert agent.threshold == 75.0
    assert agent.workflow is not None


@pytest.mark.asyncio
async def test_screen_resume_async():
    """测试异步筛选接口（集成测试）"""
    pytest.skip("需要真实PDF和API key")
    
    agent = ResumeScreeningAgent(
        openai_api_key="sk-real-key",
        threshold=70.0
    )
    
    result = await agent.screen_resume("tests/fixtures/sample_resume.pdf")
    
    assert "evaluation" in result
    assert "interview_questions" in result
    assert "error" in result
    
    if result["error"] is None:
        assert result["evaluation"] is not None
        assert result["evaluation"].candidate_name


def test_screen_resume_sync():
    """测试同步筛选接口（集成测试）"""
    pytest.skip("需要真实PDF和API key")
    
    agent = ResumeScreeningAgent(
        openai_api_key="sk-real-key",
        threshold=70.0
    )
    
    result = agent.screen_resume_sync("tests/fixtures/sample_resume.pdf")
    
    assert "evaluation" in result
    assert result["evaluation"] is not None


@pytest.mark.asyncio
async def test_screen_resume_custom_threshold():
    """测试自定义阈值"""
    pytest.skip("需要真实PDF和API key")
    
    agent = ResumeScreeningAgent(
        openai_api_key="sk-real-key",
        threshold=70.0
    )
    
    # 使用自定义阈值80
    result = await agent.screen_resume(
        "tests/fixtures/sample_resume.pdf",
        threshold=80.0
    )
    
    if result["evaluation"]:
        # 验证使用了80分阈值
        if result["evaluation"].final_score >= 80:
            assert result["evaluation"].passed_screening is True
        else:
            assert result["evaluation"].passed_screening is False


@pytest.mark.asyncio
async def test_screen_resume_file_not_found():
    """测试文件不存在的错误处理"""
    agent = ResumeScreeningAgent(
        openai_api_key="sk-test-key",
        threshold=70.0
    )
    
    result = await agent.screen_resume("nonexistent.pdf")
    
    assert result["error"] is not None
    assert result["evaluation"] is None
    assert result["interview_questions"] is None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_integration.py -v
```

Expected: 测试失败 "ImportError: cannot import name 'ResumeScreeningAgent'"

- [ ] **Step 3: 实现主接口**

```python
# src/__init__.py
import asyncio
from typing import Dict, Any, Optional
from src.workflow import create_resume_screening_workflow


class ResumeScreeningAgent:
    """
    简历筛选Agent - 供父Agent调用的主接口
    
    使用LangGraph编排工作流，Pydantic AI执行评分和题目生成。
    """
    
    def __init__(
        self,
        openai_api_key: str,
        threshold: float = 70.0
    ):
        """
        初始化简历筛选Agent
        
        Args:
            openai_api_key: OpenAI API密钥
            threshold: 初筛阈值，默认70分
        """
        self.openai_api_key = openai_api_key
        self.threshold = threshold
        
        # 设置环境变量供Agent使用
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # 创建工作流
        self.workflow = create_resume_screening_workflow()
    
    async def screen_resume(
        self,
        resume_path: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        筛选简历（异步）
        
        Args:
            resume_path: PDF简历文件路径
            threshold: 可选的自定义阈值，覆盖默认值
            
        Returns:
            Dict包含：
            - evaluation: EvaluationResult 评分结果
            - interview_questions: Optional[InterviewQuestions] 面试题目（通过初筛才有）
            - error: Optional[str] 错误信息
        """
        # 初始化状态
        initial_state = {
            "resume_path": resume_path,
            "resume_text": "",
            "evaluation": None,
            "interview_questions": None,
            "threshold": threshold if threshold is not None else self.threshold,
            "error": None
        }
        
        # 运行工作流
        final_state = await self.workflow.ainvoke(initial_state)
        
        # 返回结果
        return {
            "evaluation": final_state.get("evaluation"),
            "interview_questions": final_state.get("interview_questions"),
            "error": final_state.get("error")
        }
    
    def screen_resume_sync(
        self,
        resume_path: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        筛选简历（同步）
        
        Args:
            resume_path: PDF简历文件路径
            threshold: 可选的自定义阈值，覆盖默认值
            
        Returns:
            Dict包含：
            - evaluation: EvaluationResult 评分结果
            - interview_questions: Optional[InterviewQuestions] 面试题目
            - error: Optional[str] 错误信息
        """
        return asyncio.run(self.screen_resume(resume_path, threshold))


# 导出主接口
__all__ = ["ResumeScreeningAgent"]
```

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_integration.py -v
```

Expected: 非集成测试通过，集成测试被跳过

- [ ] **Step 5: 提交主接口**

```bash
git add src/__init__.py tests/test_integration.py
git commit -m "feat: implement main ResumeScreeningAgent interface

- Add ResumeScreeningAgent class with async/sync methods
- Support custom threshold per request
- Handle API key configuration
- Return structured results with evaluation and questions
- Add comprehensive integration tests

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: 更新nodes的__init__.py导出

**Files:**
- Modify: `src/nodes/__init__.py`
- Modify: `src/agents/__init__.py`

- [ ] **Step 1: 更新nodes导出**

```python
# src/nodes/__init__.py
from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node
from src.nodes.checker import check_threshold_node
from src.nodes.generator import generate_questions_node

__all__ = [
    "parse_resume_node",
    "evaluate_resume_node",
    "check_threshold_node",
    "generate_questions_node",
]
```

- [ ] **Step 2: 更新agents导出**

```python
# src/agents/__init__.py
from src.agents.evaluator import evaluate_resume, create_evaluator_agent
from src.agents.question_generator import generate_questions, create_question_generator_agent

__all__ = [
    "evaluate_resume",
    "create_evaluator_agent",
    "generate_questions",
    "create_question_generator_agent",
]
```

- [ ] **Step 3: 测试导入**

```bash
python -c "from src.nodes import parse_resume_node, evaluate_resume_node, check_threshold_node, generate_questions_node; print('nodes导入成功')"
python -c "from src.agents import evaluate_resume, generate_questions; print('agents导入成功')"
python -c "from src import ResumeScreeningAgent; print('主接口导入成功')"
```

Expected: 所有导入成功

- [ ] **Step 4: 提交导出更新**

```bash
git add src/nodes/__init__.py src/agents/__init__.py
git commit -m "chore: add __init__.py exports for nodes and agents

- Export all node functions from src.nodes
- Export all agent functions from src.agents
- Improve package organization

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: 添加使用示例和文档

**Files:**
- Create: `examples/basic_usage.py`
- Create: `examples/custom_threshold.py`
- Modify: `README.md`

- [ ] **Step 1: 创建基本使用示例**

```python
# examples/basic_usage.py
"""
基本使用示例
"""
import asyncio
from src import ResumeScreeningAgent


async def main():
    # 初始化Agent
    agent = ResumeScreeningAgent(
        openai_api_key="sk-your-api-key-here",
        threshold=70.0
    )
    
    # 筛选简历
    result = await agent.screen_resume("path/to/resume.pdf")
    
    # 处理结果
    if result["error"]:
        print(f"错误: {result['error']}")
        return
    
    # 打印评分结果
    evaluation = result["evaluation"]
    print(f"候选人: {evaluation.candidate_name}")
    print(f"总分: {evaluation.final_score}/115")
    print(f"通过初筛: {evaluation.passed_screening}")
    
    print("\n评分详情:")
    print(f"- 项目经历: {evaluation.base_score.project_experience.score}/{evaluation.base_score.project_experience.max_score}")
    print(f"  理由: {evaluation.base_score.project_experience.reasoning}")
    
    print(f"- 实习经历: {evaluation.base_score.internship_experience.score}/{evaluation.base_score.internship_experience.max_score}")
    print(f"  理由: {evaluation.base_score.internship_experience.reasoning}")
    
    print(f"- 技术栈: {evaluation.base_score.tech_stack.score}/{evaluation.base_score.tech_stack.max_score}")
    print(f"  理由: {evaluation.base_score.tech_stack.reasoning}")
    
    print(f"- 科研经历: {evaluation.base_score.research_experience.score}/{evaluation.base_score.research_experience.max_score}")
    print(f"  理由: {evaluation.base_score.research_experience.reasoning}")
    
    print(f"- 竞赛加分: {evaluation.bonus_score.bonus_points}/15")
    print(f"  理由: {evaluation.bonus_score.reasoning}")
    
    # 打印面试题目（如果有）
    if result["interview_questions"]:
        questions = result["interview_questions"]
        print(f"\n面试题目 for {questions.candidate_name}:")
        
        print("\n基础题:")
        for i, q in enumerate(questions.basic_questions, 1):
            print(f"{i}. {q.question}")
            print(f"   关联项目: {q.related_project}")
            print(f"   考察重点: {q.focus_area}")
        
        print("\n进阶题:")
        for i, q in enumerate(questions.advanced_questions, 1):
            print(f"{i}. {q.question}")
            print(f"   关联项目: {q.related_project}")
            print(f"   考察重点: {q.focus_area}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 创建自定义阈值示例**

```python
# examples/custom_threshold.py
"""
自定义阈值示例
"""
import asyncio
from src import ResumeScreeningAgent


async def main():
    # 初始化Agent（默认阈值70）
    agent = ResumeScreeningAgent(
        openai_api_key="sk-your-api-key-here",
        threshold=70.0
    )
    
    # 对于高级岗位，使用更高的阈值
    print("高级岗位筛选（阈值80分）:")
    result_senior = await agent.screen_resume(
        "path/to/senior_resume.pdf",
        threshold=80.0
    )
    
    if result_senior["evaluation"]:
        eval_senior = result_senior["evaluation"]
        print(f"候选人: {eval_senior.candidate_name}")
        print(f"分数: {eval_senior.final_score}")
        print(f"通过: {eval_senior.passed_screening}")
    
    # 对于实习生，使用较低的阈值
    print("\n实习生岗位筛选（阈值55分）:")
    result_intern = await agent.screen_resume(
        "path/to/intern_resume.pdf",
        threshold=55.0
    )
    
    if result_intern["evaluation"]:
        eval_intern = result_intern["evaluation"]
        print(f"候选人: {eval_intern.candidate_name}")
        print(f"分数: {eval_intern.final_score}")
        print(f"通过: {eval_intern.passed_screening}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 3: 创建示例目录**

```bash
mkdir -p examples
```

- [ ] **Step 4: 更新README.md**

在README.md的"使用"部分添加更详细的说明：

```markdown
## 使用

### 快速开始

```python
import asyncio
from resume_agent import ResumeScreeningAgent

async def main():
    # 初始化Agent
    agent = ResumeScreeningAgent(
        openai_api_key="sk-xxx",
        threshold=70.0
    )
    
    # 筛选简历
    result = await agent.screen_resume("path/to/resume.pdf")
    
    # 查看结果
    if result["error"]:
        print(f"错误: {result['error']}")
    else:
        print(f"候选人: {result['evaluation'].candidate_name}")
        print(f"总分: {result['evaluation'].final_score}")
        print(f"通过初筛: {result['evaluation'].passed_screening}")

asyncio.run(main())
```

### 同步API

```python
from resume_agent import ResumeScreeningAgent

agent = ResumeScreeningAgent(openai_api_key="sk-xxx")
result = agent.screen_resume_sync("path/to/resume.pdf")
```

### 自定义阈值

```python
# 默认阈值70分
agent = ResumeScreeningAgent(openai_api_key="sk-xxx", threshold=70.0)

# 对不同岗位使用不同阈值
result_senior = await agent.screen_resume("senior.pdf", threshold=80.0)
result_intern = await agent.screen_resume("intern.pdf", threshold=55.0)
```

### 更多示例

查看 `examples/` 目录获取更多使用示例：
- `basic_usage.py` - 基本使用
- `custom_threshold.py` - 自定义阈值
```

- [ ] **Step 5: 测试示例代码语法**

```bash
python -m py_compile examples/basic_usage.py
python -m py_compile examples/custom_threshold.py
```

Expected: 无语法错误

- [ ] **Step 6: 提交示例和文档**

```bash
git add examples/ README.md
git commit -m "docs: add usage examples and update README

- Add basic_usage.py example
- Add custom_threshold.py example
- Update README with detailed usage instructions
- Document sync and async APIs
- Add custom threshold examples

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```


## Task 13: 端到端集成测试

**Files:**
- Create: `tests/test_e2e.py`
- Create: `tests/fixtures/create_sample_pdf.py`

- [ ] **Step 1: 创建PDF生成脚本**

```python
# tests/fixtures/create_sample_pdf.py
"""
创建测试用的样本PDF简历
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


def create_sample_resume():
    """创建一个测试用的量化岗位简历PDF"""
    filename = "tests/fixtures/sample_resume.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # 标题
    title = Paragraph("<b>张三 - 量化研究员</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # 基本信息
    info = Paragraph("""
    <b>联系方式:</b> zhangsan@example.com | 138-0000-0000<br/>
    <b>教育背景:</b> 清华大学 计算机科学与技术 本科 (2019-2023)
    """, styles['Normal'])
    story.append(info)
    story.append(Spacer(1, 0.3*inch))
    
    # 项目经历
    project_title = Paragraph("<b>项目经历</b>", styles['Heading2'])
    story.append(project_title)
    
    project1 = Paragraph("""
    <b>1. 量化CTA策略开发与回测系统</b> (2023.06 - 2023.12)<br/>
    - 开发基于技术指标(MACD, RSI, Bollinger Bands)的趋势跟踪CTA策略<br/>
    - 使用Python实现完整的回测系统，支持滑点、手续费等真实交易成本模拟<br/>
    - 策略在回测中年化收益率15%，最大回撤8%，夏普比率1.8<br/>
    - 技术栈: Python, pandas, numpy, backtrader, matplotlib
    """, styles['Normal'])
    story.append(project1)
    story.append(Spacer(1, 0.2*inch))
    
    project2 = Paragraph("""
    <b>2. 多因子选股模型</b> (2023.01 - 2023.06)<br/>
    - 构建包含价值、成长、动量等20+因子的多因子选股模型<br/>
    - 使用机器学习方法(XGBoost)进行因子组合优化<br/>
    - 实现因子IC分析、因子正交化等特征工程<br/>
    - 在A股市场回测，年化超额收益10%<br/>
    - 技术栈: Python, sklearn, XGBoost, SQL
    """, styles['Normal'])
    story.append(project2)
    story.append(Spacer(1, 0.3*inch))
    
    # 实习经历
    intern_title = Paragraph("<b>实习经历</b>", styles['Heading2'])
    story.append(intern_title)
    
    intern = Paragraph("""
    <b>XX量化投资公司 - 量化研究实习生</b> (2022.07 - 2022.12)<br/>
    - 协助开发和维护量化交易策略<br/>
    - 进行金融数据清洗、特征工程和因子挖掘<br/>
    - 参与策略回测和实盘监控<br/>
    - 使用Python进行数据分析和可视化
    """, styles['Normal'])
    story.append(intern)
    story.append(Spacer(1, 0.3*inch))
    
    # 技术栈
    tech_title = Paragraph("<b>技术栈</b>", styles['Heading2'])
    story.append(tech_title)
    
    tech = Paragraph("""
    <b>编程语言:</b> Python (熟练), C++ (了解)<br/>
    <b>量化工具:</b> pandas, numpy, backtrader, zipline, QuantLib<br/>
    <b>机器学习:</b> sklearn, XGBoost, pytorch<br/>
    <b>数据库:</b> MySQL, Redis<br/>
    <b>其他:</b> Git, Linux, Jupyter
    """, styles['Normal'])
    story.append(tech)
    story.append(Spacer(1, 0.3*inch))
    
    # 科研经历
    research_title = Paragraph("<b>科研经历</b>", styles['Heading2'])
    story.append(research_title)
    
    research = Paragraph("""
    <b>机器学习在量化投资中的应用研究</b> (2022.09 - 2023.06)<br/>
    - 研究深度学习方法在股票价格预测中的应用<br/>
    - 发表论文: "基于LSTM的股票价格预测模型" (校级学术会议)
    """, styles['Normal'])
    story.append(research)
    story.append(Spacer(1, 0.3*inch))
    
    # 竞赛经历
    competition_title = Paragraph("<b>竞赛经历</b>", styles['Heading2'])
    story.append(competition_title)
    
    competition = Paragraph("""
    - 全国大学生数学建模竞赛 <b>国家一等奖</b> (2022)<br/>
    - 美国大学生数学建模竞赛 (MCM) <b>Honorable Mention</b> (2021)<br/>
    - LeetCode 周赛 Rating: 1850+
    """, styles['Normal'])
    story.append(competition)
    
    # 生成PDF
    doc.build(story)
    print(f"Sample resume created: {filename}")


if __name__ == "__main__":
    create_sample_resume()
```

- [ ] **Step 2: 安装reportlab并生成PDF**

```bash
pip install reportlab
python tests/fixtures/create_sample_pdf.py
```

Expected: 生成 `tests/fixtures/sample_resume.pdf`

- [ ] **Step 3: 编写端到端测试**

```python
# tests/test_e2e.py
"""
端到端集成测试

需要真实的OpenAI API key和sample_resume.pdf才能运行
"""
import pytest
import os
from src import ResumeScreeningAgent


@pytest.mark.skipif(
    not os.path.exists("tests/fixtures/sample_resume.pdf"),
    reason="需要sample_resume.pdf"
)
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-test"),
    reason="需要真实的OPENAI_API_KEY"
)
@pytest.mark.asyncio
async def test_e2e_passed_screening():
    """端到端测试：候选人通过初筛"""
    agent = ResumeScreeningAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        threshold=70.0
    )
    
    result = await agent.screen_resume("tests/fixtures/sample_resume.pdf")
    
    # 验证无错误
    assert result["error"] is None
    
    # 验证评分结果
    evaluation = result["evaluation"]
    assert evaluation is not None
    assert evaluation.candidate_name == "张三"
    assert 0 <= evaluation.final_score <= 115
    assert 0 <= evaluation.base_score.total_base_score <= 100
    assert 0 <= evaluation.bonus_score.bonus_points <= 15
    
    # 验证各维度评分
    assert 0 <= evaluation.base_score.project_experience.score <= 30
    assert 0 <= evaluation.base_score.internship_experience.score <= 25
    assert 0 <= evaluation.base_score.tech_stack.score <= 25
    assert 0 <= evaluation.base_score.research_experience.score <= 20
    
    # 验证评分理由存在
    assert evaluation.base_score.project_experience.reasoning
    assert evaluation.base_score.internship_experience.reasoning
    assert evaluation.base_score.tech_stack.reasoning
    assert evaluation.base_score.research_experience.reasoning
    
    # 这个简历应该能通过70分阈值
    # 因为有丰富的项目、实习、技术栈和竞赛经历
    print(f"\n候选人: {evaluation.candidate_name}")
    print(f"总分: {evaluation.final_score}/115")
    print(f"通过初筛: {evaluation.passed_screening}")
    
    # 如果通过初筛，应该有面试题目
    if evaluation.passed_screening:
        questions = result["interview_questions"]
        assert questions is not None
        assert questions.candidate_name == "张三"
        
        # 验证题目数量
        assert len(questions.basic_questions) == 2
        assert 2 <= len(questions.advanced_questions) <= 3
        
        # 验证题目质量
        for q in questions.basic_questions:
            assert q.level == "basic"
            assert len(q.question) > 10
            assert q.related_project
            assert q.focus_area
        
        for q in questions.advanced_questions:
            assert q.level == "advanced"
            assert len(q.question) > 10
            assert q.related_project
            assert q.focus_area
        
        print(f"\n生成了{len(questions.basic_questions)}个基础题和{len(questions.advanced_questions)}个进阶题")


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-test"),
    reason="需要真实的OPENAI_API_KEY"
)
@pytest.mark.asyncio
async def test_e2e_file_not_found():
    """端到端测试：文件不存在的错误处理"""
    agent = ResumeScreeningAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        threshold=70.0
    )
    
    result = await agent.screen_resume("nonexistent_file.pdf")
    
    # 应该有错误信息
    assert result["error"] is not None
    assert "未找到" in result["error"] or "not found" in result["error"].lower()
    
    # 不应该有评分和题目
    assert result["evaluation"] is None
    assert result["interview_questions"] is None


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-test"),
    reason="需要真实的OPENAI_API_KEY"
)
def test_e2e_sync_api():
    """端到端测试：同步API"""
    pytest.skip("需要sample_resume.pdf且耗时较长")
    
    agent = ResumeScreeningAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        threshold=70.0
    )
    
    result = agent.screen_resume_sync("tests/fixtures/sample_resume.pdf")
    
    assert result["error"] is None
    assert result["evaluation"] is not None


@pytest.mark.skipif(
    not os.path.exists("tests/fixtures/sample_resume.pdf"),
    reason="需要sample_resume.pdf"
)
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-test"),
    reason="需要真实的OPENAI_API_KEY"
)
@pytest.mark.asyncio
async def test_e2e_custom_threshold():
    """端到端测试：自定义阈值"""
    agent = ResumeScreeningAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        threshold=70.0
    )
    
    # 使用高阈值
    result_high = await agent.screen_resume(
        "tests/fixtures/sample_resume.pdf",
        threshold=85.0
    )
    
    if result_high["evaluation"]:
        evaluation = result_high["evaluation"]
        if evaluation.final_score >= 85.0:
            assert evaluation.passed_screening is True
        else:
            assert evaluation.passed_screening is False
        
        print(f"\n高阈值(85分)测试:")
        print(f"分数: {evaluation.final_score}")
        print(f"通过: {evaluation.passed_screening}")
    
    # 使用低阈值
    result_low = await agent.screen_resume(
        "tests/fixtures/sample_resume.pdf",
        threshold=50.0
    )
    
    if result_low["evaluation"]:
        evaluation = result_low["evaluation"]
        # 低阈值应该更容易通过
        if evaluation.final_score >= 50.0:
            assert evaluation.passed_screening is True
        
        print(f"\n低阈值(50分)测试:")
        print(f"分数: {evaluation.final_score}")
        print(f"通过: {evaluation.passed_screening}")
```

- [ ] **Step 4: 运行端到端测试（需要API key）**

```bash
# 设置真实的API key
export OPENAI_API_KEY="sk-your-real-key"

# 运行端到端测试
pytest tests/test_e2e.py -v -s
```

Expected: 如果有有效的API key和PDF，测试应该通过

- [ ] **Step 5: 提交端到端测试**

```bash
git add tests/test_e2e.py tests/fixtures/create_sample_pdf.py tests/fixtures/sample_resume.pdf
git commit -m "test: add end-to-end integration tests

- Add script to generate sample resume PDF
- Add comprehensive e2e tests for full workflow
- Test passed screening with question generation
- Test custom threshold functionality
- Test error handling for missing files
- Add sync API test

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: 代码质量和格式化

**Files:**
- All Python files

- [ ] **Step 1: 运行black格式化**

```bash
black src/ tests/ examples/
```

Expected: 所有Python文件格式化完成

- [ ] **Step 2: 运行ruff检查**

```bash
ruff check src/ tests/ examples/
```

Expected: 无严重错误（可以有一些warning）

- [ ] **Step 3: 如果有错误，修复**

根据ruff的提示修复代码问题，常见的：
- 未使用的导入
- 未使用的变量
- 过长的行

- [ ] **Step 4: 再次运行所有测试**

```bash
pytest tests/ -v --tb=short
```

Expected: 所有非集成测试通过

- [ ] **Step 5: 提交格式化**

```bash
git add -A
git commit -m "style: format code with black and fix ruff issues

- Run black on all Python files
- Fix ruff warnings and errors
- Ensure code style consistency

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: 最终文档和清理

**Files:**
- Modify: `README.md`
- Create: `CHANGELOG.md`
- Create: `LICENSE`

- [ ] **Step 1: 完善README.md**

在README.md添加更多内容：

```markdown
## 项目结构

```
resume-agent/
├── src/                    # 源代码
│   ├── models.py           # Pydantic数据模型
│   ├── config.py           # 配置管理
│   ├── agents/             # Pydantic AI agents
│   │   ├── evaluator.py    # 评分Agent
│   │   └── question_generator.py  # 题目生成Agent
│   ├── nodes/              # LangGraph节点
│   │   ├── parser.py       # PDF解析
│   │   ├── evaluator.py    # 评分节点
│   │   ├── checker.py      # 阈值检查
│   │   └── generator.py    # 题目生成
│   └── workflow.py         # LangGraph工作流
├── tests/                  # 测试
│   ├── test_models.py      # 模型测试
│   ├── test_agents.py      # Agent测试
│   ├── test_nodes.py       # 节点测试
│   ├── test_workflow.py    # 工作流测试
│   └── test_e2e.py         # 端到端测试
├── examples/               # 使用示例
└── docs/                   # 文档
```

## 评分标准

### 基础分（100分）

- **项目经历（30分）**：量化策略、交易系统、回测系统等相关项目
- **实习经历（25分）**：量化、金融科技公司实习经历
- **技术栈（25分）**：Python/C++、量化工具、机器学习等
- **科研经历（20分）**：论文发表、研究项目

### 竞赛加分（0-15分）

- 数学建模竞赛
- 量化投资比赛
- 编程竞赛
- 金融科技比赛

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py -v

# 运行端到端测试（需要API key）
export OPENAI_API_KEY="sk-xxx"
pytest tests/test_e2e.py -v -s
```

### 代码格式化

```bash
# 格式化代码
black src/ tests/ examples/

# 检查代码质量
ruff check src/ tests/ examples/
```

## 限制和注意事项

- 仅支持PDF格式简历
- 需要OpenAI API key
- API调用有成本（每份简历约2次GPT-4调用）
- 简历文本提取依赖PDF格式质量
- 评分结果仅供参考，不应作为唯一筛选标准

## 许可证

MIT License
```

- [ ] **Step 2: 创建CHANGELOG.md**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-15

### Added
- Initial release
- Multi-dimensional scoring system for quantitative finance positions
- Five scoring dimensions: projects (30%), internships (25%), tech stack (25%), research (20%)
- Competition bonus points (0-15 points)
- Fixed threshold screening (default 70 points)
- Layered interview question generation (2 basic + 2-3 advanced questions)
- LangGraph workflow orchestration
- Pydantic AI agents for evaluation and question generation
- PDF resume parsing with LangChain
- Async and sync API interfaces
- Comprehensive test suite
- Usage examples and documentation

### Technical Stack
- Python 3.10+
- Pydantic AI for structured LLM outputs
- LangChain for PDF processing
- LangGraph for workflow orchestration
- OpenAI GPT-4 for resume analysis

[0.1.0]: https://github.com/yourusername/resume-agent/releases/tag/v0.1.0
```

- [ ] **Step 3: 创建LICENSE**

```text
MIT License

Copyright (c) 2026 Resume Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 4: 检查.gitignore是否完整**

确保.gitignore包含：
```
__pycache__/
*.pyc
.env
.pytest_cache/
dist/
build/
*.egg-info/
.superpowers/
```

- [ ] **Step 5: 最终提交**

```bash
git add README.md CHANGELOG.md LICENSE
git commit -m "docs: add final documentation and license

- Complete README with project structure and development guide
- Add CHANGELOG for version 0.1.0
- Add MIT License
- Document limitations and best practices

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## 实现完成 - 验证清单

完成所有任务后，验证以下内容：

- [ ] **所有测试通过**
```bash
pytest tests/ -v
```

- [ ] **代码格式正确**
```bash
black --check src/ tests/ examples/
ruff check src/ tests/ examples/
```

- [ ] **示例可以运行**
```bash
python -m py_compile examples/*.py
```

- [ ] **导入正常**
```bash
python -c "from src import ResumeScreeningAgent; print('OK')"
```

- [ ] **文档完整**
- [ ] README.md 有使用说明
- [ ] 有使用示例
- [ ] 有测试说明

- [ ] **Git历史清晰**
```bash
git log --oneline
```

应该看到15个清晰的commit，每个对应一个任务

---

## 后续扩展建议

实现完成后，可以考虑以下扩展：

1. **批量处理**：支持批量处理多份简历并生成排序
2. **简历去重**：检测重复投递的简历
3. **Web UI**：添加简单的Web界面供HR使用
4. **报告生成**：生成PDF或HTML格式的评估报告
5. **数据库集成**：将评估结果存储到数据库
6. **多岗位支持**：支持不同类型量化岗位的不同评分权重
7. **反馈学习**：根据面试结果优化评分模型
8. **OCR支持**：支持扫描版PDF简历
