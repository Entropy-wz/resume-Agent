# 量化岗位简历筛选Agent设计文档

**创建日期：** 2026-06-15  
**版本：** 1.0  
**目标：** 创建一个用于量化岗位招聘的简历筛选子Agent，供招聘Agent调用

## 1. 系统概述

这是一个专门针对量化岗位的简历筛选Agent，使用LangGraph编排工作流，Pydantic AI执行具体任务。系统接收PDF格式简历，输出结构化的评分结果，对于通过初筛的候选人生成个性化的面试题目。

### 1.1 核心功能

1. **多维度评分系统**
   - 项目经历（30%）
   - 实习经历（25%）
   - 技术栈（25%）
   - 科研经历（20%）
   - 基础满分：100分

2. **竞赛加分机制**
   - 独立的加分项，不计入基础权重
   - 最高15分
   - 总分上限：115分

3. **初筛判断**
   - 固定阈值机制（默认70分）
   - 达到阈值即通过初筛

4. **面试题目生成**
   - 分层出题模式
   - 基础题：2题（覆盖面广）
   - 进阶题：2-3题（针对具体项目深挖）
   - 所有题目与候选人项目经历相关

### 1.2 技术栈

- **框架：** Pydantic AI + LangChain/LangGraph
- **LLM：** OpenAI GPT-4
- **输入格式：** PDF
- **输出格式：** 结构化数据（Pydantic模型）
- **部署形式：** Python模块，供其他Agent调用

## 2. 数据模型设计

### 2.1 评分相关模型

```python
class DimensionScore(BaseModel):
    """单个维度的评分"""
    dimension: str          # 维度名称
    score: float           # 得分
    max_score: float       # 满分
    reasoning: str         # 评分理由

class BaseScore(BaseModel):
    """基础评分（100分制）"""
    project_experience: DimensionScore      # 项目经历 30分
    internship_experience: DimensionScore   # 实习经历 25分
    tech_stack: DimensionScore              # 技术栈 25分
    research_experience: DimensionScore     # 科研经历 20分
    total_base_score: float                 # 基础总分 0-100

class BonusScore(BaseModel):
    """竞赛加分"""
    competitions: List[str]    # 竞赛列表
    bonus_points: float        # 加分 0-15
    reasoning: str             # 加分理由

class EvaluationResult(BaseModel):
    """完整评估结果"""
    candidate_name: str
    base_score: BaseScore
    bonus_score: BonusScore
    final_score: float          # 总分 0-115
    passed_screening: bool      # 是否通过初筛
    timestamp: datetime
```

### 2.2 面试题目模型

```python
class InterviewQuestion(BaseModel):
    """单个面试题目"""
    level: Literal["basic", "advanced"]    # 基础/进阶
    question: str                          # 题目内容
    related_project: str                   # 关联的项目经历
    focus_area: str                        # 考察重点

class InterviewQuestions(BaseModel):
    """面试题目集"""
    candidate_name: str
    basic_questions: List[InterviewQuestion]       # 2个基础题
    advanced_questions: List[InterviewQuestion]    # 2-3个进阶题
    generation_timestamp: datetime
```

### 2.3 工作流状态模型

```python
class AgentState(TypedDict):
    """LangGraph工作流状态"""
    resume_path: str                                    # 简历PDF路径
    resume_text: str                                    # 解析后的简历文本
    evaluation: Optional[EvaluationResult]              # 评估结果
    interview_questions: Optional[InterviewQuestions]   # 面试题目
    threshold: float                                    # 初筛阈值
    error: Optional[str]                                # 错误信息
```

## 3. 工作流设计

### 3.1 状态图结构

```
START
  ↓
parse_resume (解析PDF)
  ↓
evaluate_resume (多维度评分 - Pydantic AI)
  ↓
check_threshold (判断是否通过初筛)
  ↓
[条件分支]
  ├─ passed=True → generate_questions (生成面试题 - Pydantic AI)
  │                      ↓
  │                    END
  │
  └─ passed=False → END
```

### 3.2 节点功能说明

#### 3.2.1 parse_resume 节点
- **功能：** 使用LangChain的PDF加载器解析简历
- **输入：** `resume_path`
- **输出：** `resume_text`
- **工具：** `PyPDFLoader`
- **错误处理：** PDF解析失败时设置`error`字段并终止流程

#### 3.2.2 evaluate_resume 节点
- **功能：** 使用Pydantic AI Agent进行多维度评分
- **输入：** `resume_text`
- **输出：** `evaluation` (EvaluationResult)
- **评分标准：**
  - **项目经历（30分）：** 量化策略、交易系统、回测系统等相关项目的复杂度、规模和贡献
  - **实习经历（25分）：** 量化、金融、科技公司实习的相关性和质量
  - **技术栈（25分）：** Python/C++、数据分析、机器学习、金融工具库等的掌握程度
  - **科研经历（20分）：** 论文发表、研究项目的质量和相关性
  - **竞赛加分（0-15分）：** 数学建模、量化比赛、编程竞赛等的含金量

#### 3.2.3 check_threshold 节点
- **功能：** 判断是否通过初筛
- **输入：** `evaluation.final_score`, `threshold`
- **输出：** `evaluation.passed_screening` (bool)
- **逻辑：** `final_score >= threshold`

#### 3.2.4 generate_questions 节点
- **功能：** 使用Pydantic AI Agent生成面试题目
- **输入：** `resume_text`, `evaluation`
- **输出：** `interview_questions` (InterviewQuestions)
- **生成策略：**
  - **基础题（2题）：** 考察候选人的基础知识和项目概况，覆盖面广
  - **进阶题（2-3题）：** 针对候选人具体项目深入提问，考察技术细节、问题解决能力、系统设计能力
- **约束：** 题目必须与候选人的实际项目经历相关，避免涉及简历中未提及的领域

### 3.3 条件边逻辑

```python
def should_generate_questions(state: AgentState) -> Literal["generate_questions", "end"]:
    """决定是否生成面试题目"""
    if state.get("error"):
        return "end"
    
    if state["evaluation"].passed_screening:
        return "generate_questions"
    else:
        return "end"
```

## 4. Pydantic AI Agent设计

### 4.1 评分Agent

**Agent配置：**
```python
evaluator_agent = Agent(
    model=OpenAIModel('gpt-4'),
    result_type=EvaluationResult,
    system_prompt="""评分专家系统提示词"""
)
```

**系统提示词要点：**
- 明确五个评分维度和分值范围
- 强调量化岗位的匹配度
- 要求给出详细的评分理由
- 区分基础分（100分）和加分（15分）

**调用接口：**
```python
async def evaluate_resume(resume_text: str) -> EvaluationResult:
    result = await evaluator_agent.run(f"请评估以下简历：\n\n{resume_text}")
    return result.data
```

### 4.2 题目生成Agent

**Agent配置：**
```python
question_generator_agent = Agent(
    model=OpenAIModel('gpt-4'),
    result_type=InterviewQuestions,
    system_prompt="""面试官系统提示词"""
)
```

**系统提示词要点：**
- 定义基础题和进阶题的特点
- 要求题目与候选人项目相关
- 强调考察深度和针对性
- 提供量化岗位面试题的示例

**调用接口：**
```python
async def generate_questions(
    resume_text: str, 
    evaluation: EvaluationResult
) -> InterviewQuestions:
    prompt = f"""
    候选人简历：{resume_text}
    评分结果：{evaluation.dict()}
    请生成面试题目。
    """
    result = await question_generator_agent.run(prompt)
    return result.data
```

## 5. 项目结构

```
resume-agent/
├── src/
│   ├── __init__.py              # 主接口导出
│   ├── models.py                # Pydantic数据模型
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # 评分Agent (Pydantic AI)
│   │   └── question_generator.py # 题目生成Agent (Pydantic AI)
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── parser.py            # PDF解析节点
│   │   ├── evaluator.py         # 评分节点
│   │   ├── checker.py           # 阈值检查节点
│   │   └── generator.py         # 题目生成节点
│   ├── workflow.py              # LangGraph工作流定义
│   └── config.py                # 配置管理
├── tests/
│   ├── test_agents.py           # Agent单元测试
│   ├── test_workflow.py         # 工作流集成测试
│   └── fixtures/                # 测试用简历样本
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-06-15-resume-screening-agent-design.md
├── .env.example                 # 环境变量模板
├── pyproject.toml               # 项目依赖
└── README.md
```

## 6. 对外接口

### 6.1 主接口类

```python
class ResumeScreeningAgent:
    """简历筛选Agent - 供父Agent调用的主接口"""
    
    def __init__(self, 
                 openai_api_key: str,
                 threshold: float = 70.0):
        """初始化简历筛选Agent"""
        
    async def screen_resume(
        self, 
        resume_path: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        筛选简历（异步）
        
        Returns:
            Dict包含：
            - evaluation: EvaluationResult 评分结果
            - interview_questions: Optional[InterviewQuestions] 面试题目
            - error: Optional[str] 错误信息
        """
    
    def screen_resume_sync(
        self,
        resume_path: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """筛选简历（同步）"""
```

### 6.2 使用示例

```python
from resume_agent import ResumeScreeningAgent

# 初始化Agent
screening_agent = ResumeScreeningAgent(
    openai_api_key="sk-xxx",
    threshold=70.0
)

# 筛选简历
result = await screening_agent.screen_resume(
    resume_path="./candidates/张三.pdf"
)

# 处理结果
if result["error"]:
    print(f"错误: {result['error']}")
else:
    evaluation = result["evaluation"]
    print(f"候选人: {evaluation.candidate_name}")
    print(f"总分: {evaluation.final_score}")
    print(f"通过初筛: {evaluation.passed_screening}")
    
    if result["interview_questions"]:
        questions = result["interview_questions"]
        print("\n面试题目:")
        for q in questions.basic_questions:
            print(f"[基础] {q.question}")
        for q in questions.advanced_questions:
            print(f"[进阶] {q.question}")
```

## 7. 配置管理

### 7.1 配置项

```python
class Settings(BaseSettings):
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
    
    class Config:
        env_file = ".env"
```

### 7.2 环境变量

创建 `.env` 文件：
```
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4
DEFAULT_THRESHOLD=70.0
```

## 8. 依赖项

### 8.1 核心依赖

```toml
[project]
name = "resume-agent"
version = "0.1.0"
description = "Resume screening agent for quantitative finance positions"
requires-python = ">=3.10"

dependencies = [
    "pydantic>=2.0.0",
    "pydantic-ai>=0.0.1",
    "langchain>=0.1.0",
    "langgraph>=0.0.1",
    "langchain-community>=0.0.1",
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
```

## 9. 测试策略

### 9.1 单元测试

- **Agent测试：** 测试评分Agent和题目生成Agent的输出格式和质量
- **节点测试：** 测试各个节点的输入输出正确性
- **工具测试：** 测试PDF解析、条件判断等工具函数

### 9.2 集成测试

- **端到端测试：** 使用真实简历样本测试完整工作流
- **边界测试：** 测试极端情况（空简历、格式错误、阈值边界等）
- **性能测试：** 测试处理速度和并发能力

### 9.3 测试数据

准备多种简历样本：
- 高分候选人（>80分）
- 及格候选人（70-80分）
- 不及格候选人（<70分）
- 边界情况（恰好70分）
- 异常情况（格式错误、内容缺失）

## 10. 扩展性考虑

### 10.1 未来可能的扩展

1. **多岗位支持：** 支持不同类型的量化岗位，每个岗位有不同的评分权重
2. **自定义维度：** 允许用户自定义评分维度
3. **批量处理：** 支持批量处理多份简历并生成排序
4. **简历去重：** 检测重复投递的简历
5. **候选人排序：** 对通过初筛的候选人按分数排序
6. **评分解释：** 生成更详细的评分解释报告
7. **反馈学习：** 根据面试结果调整评分模型

### 10.2 架构优势

- **模块化设计：** 各组件独立，易于替换和升级
- **状态机模式：** LangGraph状态机易于添加新节点
- **类型安全：** Pydantic模型保证数据一致性
- **异步支持：** 支持高并发处理

## 11. 部署说明

### 11.1 作为子Agent使用

```python
# 在父Agent中集成
class RecruitmentAgent:
    def __init__(self):
        self.screening_agent = ResumeScreeningAgent(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def process_candidate(self, resume_path: str):
        # 调用简历筛选子Agent
        result = await self.screening_agent.screen_resume(resume_path)
        
        # 处理筛选结果
        if result["evaluation"].passed_screening:
            # 安排面试
            await self.schedule_interview(
                candidate=result["evaluation"].candidate_name,
                questions=result["interview_questions"]
            )
```

### 11.2 独立使用

```python
# 也可以独立使用
if __name__ == "__main__":
    agent = ResumeScreeningAgent(openai_api_key="sk-xxx")
    result = agent.screen_resume_sync("./resume.pdf")
    print(result)
```

## 12. 注意事项

### 12.1 API成本

- 每份简历需要调用2次GPT-4（评分 + 题目生成）
- 建议监控API使用量和成本
- 可以考虑对于低分简历只调用评分Agent，不生成题目

### 12.2 隐私和安全

- 简历包含个人隐私信息，注意数据保护
- 不要将简历内容记录到日志
- API调用使用HTTPS加密

### 12.3 评分公平性

- 定期审查评分结果，避免偏见
- 评分标准应该透明且一致
- 保留评分理由以便审计

### 12.4 PDF解析限制

- 支持标准PDF格式
- 扫描版PDF可能需要OCR预处理
- 建议候选人使用标准格式简历

## 13. 总结

本设计文档描述了一个完整的量化岗位简历筛选Agent系统，采用LangGraph编排工作流，Pydantic AI执行具体任务的架构。系统具有以下特点：

- **结构化输出：** 使用Pydantic模型保证数据质量
- **模块化设计：** 各组件独立，易于测试和维护
- **易于集成：** 作为Python模块供父Agent调用
- **扩展性强：** 基于状态机的架构易于添加新功能
- **类型安全：** 完整的类型标注和验证

系统已准备好进入实现阶段。
