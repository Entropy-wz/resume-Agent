# 量化岗位简历筛选Agent - 设计文档 (Part 2: 具体实现)

## 6. 核心组件实现

### 6.1 数据模型 (src/models.py)

#### 6.1.1 设计思路

使用Pydantic实现强类型数据模型，确保：
- **类型安全**：所有字段都有明确类型
- **自动验证**：运行时自动检查数据有效性
- **业务规则**：通过validator实现业务逻辑验证

#### 6.1.2 核心模型

**DimensionScore - 单维度评分**
```python
class DimensionScore(BaseModel):
    dimension: str              # 维度名称
    score: float                # 得分 (>= 0)
    max_score: float            # 满分 (> 0)
    reasoning: str              # 评分理由 (非空)
    
    @model_validator(mode='after')
    def validate_score_range(self):
        # 验证：score <= max_score
        if self.score > self.max_score:
            raise ValueError(f"score不能超过max_score")
        return self
```

**BaseScore - 基础评分**
```python
class BaseScore(BaseModel):
    project_experience: DimensionScore      # 项目 30分
    internship_experience: DimensionScore   # 实习 25分
    tech_stack: DimensionScore              # 技术 25分
    research_experience: DimensionScore     # 科研 20分
    total_base_score: float                 # 总分 0-100
    
    @model_validator(mode='after')
    def validate_total(self):
        # 验证：总分 = 各维度之和
        calculated = sum([
            self.project_experience.score,
            self.internship_experience.score,
            self.tech_stack.score,
            self.research_experience.score
        ])
        if abs(self.total_base_score - calculated) > 0.01:
            raise ValueError(f"总分必须等于各维度之和")
        return self
```

**EvaluationResult - 完整评估结果**
```python
class EvaluationResult(BaseModel):
    candidate_name: str
    base_score: BaseScore
    bonus_score: BonusScore
    final_score: float          # 0-115
    passed_screening: bool
    timestamp: datetime
```

**InterviewQuestions - 面试题目集**
```python
class InterviewQuestions(BaseModel):
    candidate_name: str
    basic_questions: List[InterviewQuestion]      # 恰好2题
    advanced_questions: List[InterviewQuestion]   # 2-3题
    generation_timestamp: datetime
```

#### 6.1.3 验证策略

1. **字段级验证**：使用Field约束（ge, le, min_length等）
2. **模型级验证**：使用@model_validator实现跨字段验证
3. **业务规则验证**：确保数据符合业务逻辑

---

### 6.2 配置管理 (src/config.py)

#### 6.2.1 设计思路

使用pydantic-settings实现配置管理：
- 支持环境变量加载
- 支持.env文件
- 提供默认值
- 单例模式避免重复实例化

#### 6.2.2 实现

```python
class Settings(BaseSettings):
    # OpenAI配置
    openai_api_key: str                # 必填
    openai_model: str = "gpt-4"        # 默认GPT-4
    
    # 评分配置
    default_threshold: float = 70.0
    weight_project: float = 0.30
    weight_internship: float = 0.25
    weight_tech_stack: float = 0.25
    weight_research: float = 0.20
    max_bonus: float = 15.0
    
    # 题目配置
    num_basic_questions: int = 2
    num_advanced_questions_min: int = 2
    num_advanced_questions_max: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

# 单例模式
_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

---

### 6.3 Pydantic AI Agents

#### 6.3.1 评分Agent (src/agents/evaluator.py)

**核心逻辑：**
1. 接收简历文本
2. 使用GPT-4分析
3. 返回结构化的EvaluationResult

**系统提示词设计：**
```python
EVALUATOR_SYSTEM_PROMPT = """
你是一个专业的量化岗位简历评估专家。

## 评分维度和标准
### 1. 项目经历（满分30分）
- 项目与量化、金融、交易系统的相关性
- 项目复杂度和技术难度
- 候选人在项目中的角色和贡献
- 项目成果和影响力

### 2. 实习经历（满分25分）
...

## 评分原则
1. 客观公正：基于简历内容评分
2. 相关性优先：与量化岗位相关的经历给高分
3. 深度优先：有深度的项目更有价值
4. 给出理由：每个维度必须详细说明
5. 严格上限：各维度分数不能超过满分
"""
```

**实现代码：**
```python
def create_evaluator_agent() -> Agent[None, EvaluationResult]:
    settings = get_settings()
    return Agent(
        model=OpenAIModel(settings.openai_model),
        result_type=EvaluationResult,
        system_prompt=EVALUATOR_SYSTEM_PROMPT,
    )

async def evaluate_resume(resume_text: str, threshold: float = 70.0) -> EvaluationResult:
    agent = create_evaluator_agent()
    
    prompt = f"""
    请评估以下简历：
    {resume_text}
    
    初筛阈值为{threshold}分，请在passed_screening字段中标明是否通过。
    """
    
    result = await agent.run(prompt)
    evaluation = result.data
    
    # 确保passed_screening正确设置
    evaluation.passed_screening = evaluation.final_score >= threshold
    
    return evaluation
```

**关键设计点：**
- ✅ 使用Pydantic AI的`result_type`强制结构化输出
- ✅ 系统提示词包含详细的评分标准和示例
- ✅ 在代码中二次确认passed_screening逻辑

#### 6.3.2 题目生成Agent (src/agents/question_generator.py)

**核心逻辑：**
1. 接收简历文本和评分结果
2. 使用GPT-4生成题目
3. 返回结构化的InterviewQuestions

**系统提示词设计：**
```python
QUESTION_GENERATOR_SYSTEM_PROMPT = """
你是一个专业的量化岗位面试官。

## 题目类型
### 1. 基础题（2题）
目的：考察基本理解和项目概况
特点：覆盖面广、难度适中、相对开放

### 2. 进阶题（2-3题）
目的：深入考察技术能力和问题解决能力
特点：针对性强、有技术深度、基于具体项目

## 出题原则
1. 基于简历：题目必须与简历内容相关
2. 避免超纲：不问简历中未涉及的领域
3. 有深度：能考察真实能力
4. 可回答性：候选人能够回答
5. 多样性：覆盖不同方面
"""
```

**实现代码：**
```python
async def generate_questions(
    resume_text: str,
    evaluation: EvaluationResult
) -> InterviewQuestions:
    agent = create_question_generator_agent()
    
    prompt = f"""
    ## 候选人信息
    姓名：{evaluation.candidate_name}
    
    ## 简历内容
    {resume_text}
    
    ## 评分结果
    - 项目经历：{evaluation.base_score.project_experience.score}/30分
      理由：{evaluation.base_score.project_experience.reasoning}
    ...
    
    请根据候选人的项目经历和技术背景生成面试题目。
    """
    
    result = await agent.run(prompt)
    return result.data
```

---

### 6.4 LangGraph工作流节点

#### 6.4.1 节点设计模式

所有节点遵循统一模式：
```python
def node_function(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 1. 从state获取输入
        input_data = state.get("input_key")
        
        # 2. 验证输入
        if input_data is None:
            return {**state, "error": "Missing input"}
        
        # 3. 执行处理
        result = process(input_data)
        
        # 4. 返回更新后的state
        return {
            **state,
            "output_key": result,
            "error": None
        }
    except Exception as e:
        # 5. 错误处理
        return {
            **state,
            "error": f"Error: {str(e)}"
        }
```

#### 6.4.2 PDF解析节点 (src/nodes/parser.py)

```python
def parse_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        resume_path = state["resume_path"]
        
        # 使用LangChain的PyPDFLoader
        loader = PyPDFLoader(resume_path)
        documents = loader.load()
        
        # 合并所有页面文本
        resume_text = "\n".join([doc.page_content for doc in documents])
        
        return {
            **state,
            "resume_text": resume_text,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "resume_text": "",
            "error": f"PDF解析失败: {str(e)}"
        }
```

**关键点：**
- 使用LangChain的PyPDFLoader处理PDF
- 合并多页内容为单一文本
- 错误时设置空文本和错误信息

#### 6.4.3 评分节点 (src/nodes/evaluator.py)

```python
async def evaluate_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        resume_text = state.get("resume_text", "")
        
        if not resume_text.strip():
            return {
                **state,
                "evaluation": None,
                "error": "简历文本为空"
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

#### 6.4.4 阈值检查节点 (src/nodes/checker.py)

```python
def check_threshold_node(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        evaluation = state.get("evaluation")
        
        if evaluation is None:
            return {
                **state,
                "should_generate_questions": False,
                "error": "评估结果为空"
            }
        
        # 检查是否通过初筛
        should_generate = evaluation.passed_screening
        
        return {
            **state,
            "should_generate_questions": should_generate,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "should_generate_questions": False,
            "error": f"阈值检查失败: {str(e)}"
        }
```

**关键设计：**
- 设置`should_generate_questions`标志
- 此标志用于条件边判断
- **这里实现了成本优化：未通过不生成题目**

#### 6.4.5 题目生成节点 (src/nodes/generator.py)

```python
async def generate_questions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        evaluation = state.get("evaluation")
        resume_text = state.get("resume_text", "")
        
        if evaluation is None or not resume_text.strip():
            return {
                **state,
                "interview_questions": None,
                "error": "缺少必要数据"
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

---

### 6.5 LangGraph工作流 (src/workflow.py)

#### 6.5.1 条件判断函数

```python
def should_generate_questions(state: Dict[str, Any]) -> Literal["generate_questions", "end"]:
    """
    根据should_generate_questions字段决定下一步
    """
    if state.get("should_generate_questions", False):
        return "generate_questions"
    return "end"
```

**关键设计：**
- 返回值为字面量类型，用于路由
- `should_generate_questions=True` → 生成题目
- `should_generate_questions=False` → 直接结束（**节省tokens**）

#### 6.5.2 工作流构建

```python
def create_resume_screening_workflow():
    # 1. 创建StateGraph
    workflow = StateGraph(dict)
    
    # 2. 添加节点
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("evaluate_resume", evaluate_resume_node)
    workflow.add_node("check_threshold", check_threshold_node)
    workflow.add_node("generate_questions", generate_questions_node)
    
    # 3. 设置入口点
    workflow.set_entry_point("parse_resume")
    
    # 4. 添加顺序边
    workflow.add_edge("parse_resume", "evaluate_resume")
    workflow.add_edge("evaluate_resume", "check_threshold")
    
    # 5. 添加条件边（关键！）
    workflow.add_conditional_edges(
        "check_threshold",
        should_generate_questions,
        {
            "generate_questions": "generate_questions",
            "end": END
        }
    )
    
    # 6. 最终边
    workflow.add_edge("generate_questions", END)
    
    # 7. 编译工作流
    return workflow.compile()
```

**执行路径：**

路径A（通过初筛）：
```
parse → evaluate → check → generate_questions → END
```

路径B（未通过初筛）：
```
parse → evaluate → check → END
```

---

### 6.6 主接口 (src/__init__.py)

#### 6.6.1 ResumeScreeningAgent类

```python
class ResumeScreeningAgent:
    def __init__(self, openai_api_key: str, threshold: float = 70.0):
        # 设置API key
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
        # 初始化状态
        initial_state = {
            "resume_path": resume_path,
            "resume_text": "",
            "evaluation": None,
            "interview_questions": None,
            "threshold": threshold or self.threshold,
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
        # 同步包装
        import asyncio
        return asyncio.run(self.screen_resume(resume_path, threshold))
```

#### 6.6.2 使用示例

```python
# 异步使用
agent = ResumeScreeningAgent(
    openai_api_key="sk-xxx",
    threshold=70.0
)

result = await agent.screen_resume("resume.pdf")

# 同步使用
result = agent.screen_resume_sync("resume.pdf")

# 自定义阈值
result = await agent.screen_resume("resume.pdf", threshold=80.0)
```
