# Resume-Agent 作为子Agent集成指南

## 集成场景

将 `resume-Agent` 集成到更大的 `招聘Agent` 系统中，作为简历筛选的子功能模块。

---

## 🎯 关键集成注意事项

### 1. **接口设计 - 清晰的边界**

#### ✅ 推荐：保持当前的类接口

```python
# 在招聘Agent中使用
from resume_agent import ResumeScreeningAgent

class RecruitmentAgent:
    def __init__(self, config):
        # 子Agent：简历筛选
        self.resume_screener = ResumeScreeningAgent(
            openai_api_key=config.api_key,
            threshold=config.screening_threshold
        )
        
        # 其他子Agent
        self.interview_scheduler = InterviewSchedulerAgent(...)
        self.offer_manager = OfferManagementAgent(...)
    
    async def process_candidate(self, resume_path: str):
        # Step 1: 简历筛选
        screening_result = await self.resume_screener.screen_resume(resume_path)
        
        if screening_result["error"]:
            return {"status": "failed", "reason": screening_result["error"]}
        
        if not screening_result["evaluation"].passed_screening:
            return {"status": "rejected", "score": screening_result["evaluation"].final_score}
        
        # Step 2: 安排面试
        interview = await self.interview_scheduler.schedule(
            candidate_name=screening_result["evaluation"].candidate_name,
            questions=screening_result["questions"]
        )
        
        return {"status": "interview_scheduled", "interview": interview}
```

**优点：**
- ✅ 清晰的职责边界
- ✅ 易于测试（可以单独测试resume-agent）
- ✅ 易于替换（如果需要换筛选逻辑）

---

### 2. **配置管理 - 避免冲突**

#### ⚠️ 当前问题：环境变量设置

```python
# src/__init__.py Line 28
os.environ["OPENAI_API_KEY"] = openai_api_key  # ❌ 直接修改全局环境变量
```

#### 🔴 集成风险

```python
# 场景：招聘Agent使用不同的API key
recruitment_agent = RecruitmentAgent(api_key="key-for-main-agent")

# resume-agent初始化时会覆盖环境变量！
resume_screener = ResumeScreeningAgent(api_key="key-for-screening")  
# ❌ 全局 OPENAI_API_KEY 被改成 "key-for-screening"

# 其他Agent可能受影响
other_agent.call_llm()  # ❌ 使用了错误的key
```

#### ✅ 解决方案：不修改全局环境变量

**方案A：通过参数传递（推荐）**

```python
# src/__init__.py
class ResumeScreeningAgent:
    def __init__(self, openai_api_key: str, threshold: float = 70.0):
        self.openai_api_key = openai_api_key  # 存储但不设置环境变量
        self.threshold = threshold
        
        # ❌ 移除这段
        # os.environ["OPENAI_API_KEY"] = openai_api_key
        
        self.workflow = create_resume_screening_workflow()

# src/agents/evaluator.py
def create_evaluator_agent(api_key: str):  # 接受参数
    """创建评分Agent"""
    client = AsyncOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=api_key  # 使用传入的key
    )
    return Agent(model=OpenAIModel("qwen-plus", provider=client), ...)
```

**方案B：使用配置对象**

```python
# src/config.py
class AgentConfig:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

# src/__init__.py
class ResumeScreeningAgent:
    def __init__(self, config: AgentConfig, threshold: float = 70.0):
        self.config = config
        self.threshold = threshold
```

---

### 3. **状态隔离 - 避免状态泄露**

#### ✅ 当前设计：无状态很好

```python
async def screen_resume(self, resume_path: str) -> Dict[str, Any]:
    # ✅ 每次调用都是独立的
    initial_state = {...}
    result = await self.workflow.ainvoke(initial_state)
    return result
```

**优点：**
- ✅ 线程安全
- ✅ 可以并发处理多份简历
- ✅ 不会互相干扰

---

### 4. **错误处理 - 上下文传递**

#### 当前返回格式

```python
{
    "resume_path": str,
    "resume_text": str,
    "evaluation": EvaluationResult | None,
    "questions": InterviewQuestions | None,
    "error": str | None  # ✅ 简单的错误字符串
}
```

#### ⚠️ 集成时的问题

父Agent可能需要更多错误上下文：

```python
# 场景：批量处理100份简历
for resume in resumes:
    result = await screener.screen_resume(resume)
    if result["error"]:
        # ❌ 只有字符串，不知道错误类型
        # 是网络错误可以重试？还是PDF损坏应该跳过？
        logger.error(result["error"])
```

#### ✅ 建议：结构化错误

```python
# src/models.py
class AgentError(BaseModel):
    """结构化错误信息"""
    error_type: Literal["parse_error", "api_error", "validation_error", "timeout"]
    message: str
    recoverable: bool  # 是否可重试
    node: str  # 哪个节点出错
    details: Optional[dict] = None

# 返回格式
{
    ...,
    "error": AgentError | None
}
```

**父Agent可以据此决策：**

```python
if result["error"]:
    if result["error"].recoverable:
        # 重试
        result = await screener.screen_resume(resume)
    else:
        # 跳过
        continue
```

---

### 5. **性能优化 - 批量处理**

#### 当前设计：单份简历处理

```python
result = await screen_resume(resume_path)  # 一次一份
```

#### 集成需求：批量处理

```python
# 招聘Agent可能需要
results = await screen_resumes_batch([resume1, resume2, ...])
```

#### ✅ 建议：添加批量接口

```python
class ResumeScreeningAgent:
    async def screen_resumes_batch(
        self, 
        resume_paths: List[str],
        max_concurrent: int = 5  # 限制并发
    ) -> List[Dict[str, Any]]:
        """批量筛选简历"""
        import asyncio
        
        # 使用信号量限制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def screen_with_limit(path):
            async with semaphore:
                return await self.screen_resume(path)
        
        tasks = [screen_with_limit(path) for path in resume_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

### 6. **依赖管理 - 避免冲突**

#### ⚠️ 依赖冲突风险

```toml
# resume-agent/pyproject.toml
dependencies = [
    "pydantic>=2.0.0",
    "langgraph>=0.0.60",
    "openai>=1.0.0",
]

# 招聘Agent可能依赖不同版本
recruitment-agent/requirements.txt
pydantic==2.5.0  # ❌ 版本固定
langgraph==0.1.0
```

#### ✅ 解决方案

1. **使用宽松的版本约束**
   ```toml
   dependencies = [
       "pydantic>=2.0.0,<3.0.0",  # 允许2.x的任何版本
       "langgraph>=0.0.60,<1.0.0",
   ]
   ```

2. **作为可选依赖发布**
   ```toml
   [project.optional-dependencies]
   screening = ["resume-agent>=1.0.0"]
   ```

3. **使用命名空间包**
   ```
   recruitment_system/
       ├── agents/
       │   ├── screening/  # resume-agent
       │   ├── interview/
       │   └── offer/
   ```

---

### 7. **监控和追踪 - 可观测性**

#### 当前缺失：日志和追踪

```python
# 当前代码没有日志
result = await evaluate_resume(resume_text, threshold)
```

#### ✅ 建议：添加结构化日志

```python
import structlog

logger = structlog.get_logger()

async def screen_resume(self, resume_path: str) -> Dict[str, Any]:
    request_id = str(uuid.uuid4())
    
    logger.info(
        "screening_started",
        request_id=request_id,
        resume_path=resume_path,
        threshold=self.threshold
    )
    
    try:
        result = await self.workflow.ainvoke(initial_state)
        
        logger.info(
            "screening_completed",
            request_id=request_id,
            score=result["evaluation"].final_score if result["evaluation"] else None,
            passed=result["evaluation"].passed_screening if result["evaluation"] else False
        )
        
        return result
    except Exception as e:
        logger.error(
            "screening_failed",
            request_id=request_id,
            error=str(e),
            exc_info=True
        )
        raise
```

**父Agent可以关联追踪：**

```python
# 招聘Agent
async def process_candidate(self, candidate_id: str, resume_path: str):
    with logger.bind(candidate_id=candidate_id):
        # resume-agent的日志会包含candidate_id
        result = await self.resume_screener.screen_resume(resume_path)
```

---

### 8. **版本兼容 - API稳定性**

#### ✅ 建议：语义化版本 + 弃用警告

```python
# src/__init__.py
__version__ = "1.0.0"

class ResumeScreeningAgent:
    def __init__(self, openai_api_key: str, threshold: float = 70.0):
        # 如果未来要改变接口
        warnings.warn(
            "Passing openai_api_key directly is deprecated. "
            "Use config object instead. "
            "This will be removed in version 2.0.0",
            DeprecationWarning,
            stacklevel=2
        )
```

---

### 9. **测试支持 - Mock友好**

#### ✅ 当前设计：易于Mock

```python
# 在招聘Agent的测试中
from unittest.mock import AsyncMock, MagicMock

async def test_recruitment_process():
    # Mock resume-agent
    mock_screener = AsyncMock(spec=ResumeScreeningAgent)
    mock_screener.screen_resume.return_value = {
        "evaluation": MagicMock(passed_screening=True, final_score=85),
        "questions": MagicMock(),
        "error": None
    }
    
    recruitment_agent = RecruitmentAgent(resume_screener=mock_screener)
    
    result = await recruitment_agent.process_candidate("resume.pdf")
    assert result["status"] == "interview_scheduled"
```

---

### 10. **资源管理 - 清理和释放**

#### ⚠️ 当前缺失：资源清理

```python
class ResumeScreeningAgent:
    def __init__(self, ...):
        self.workflow = create_resume_screening_workflow()
        # ❓ workflow持有什么资源？需要清理吗？
```

#### ✅ 建议：添加上下文管理器

```python
class ResumeScreeningAgent:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 清理资源
        if hasattr(self, 'client'):
            await self.client.close()
        return False

# 使用
async with ResumeScreeningAgent(api_key=...) as screener:
    result = await screener.screen_resume("resume.pdf")
# 自动清理
```

---

## 📋 集成检查清单

### 必须修复（P0）
- [ ] **移除全局环境变量设置**（避免key冲突）
- [ ] **添加结构化错误类型**（方便父Agent处理）
- [ ] **验证线程安全性**（确保可并发）

### 强烈建议（P1）
- [ ] **添加批量处理接口**
- [ ] **添加结构化日志**
- [ ] **添加追踪ID支持**
- [ ] **版本化API**

### 可选优化（P2）
- [ ] **添加上下文管理器**
- [ ] **添加性能指标（处理时间、API调用次数）**
- [ ] **添加配置验证**

---

## 🎯 推荐的集成架构

```
招聘Agent (RecruitmentAgent)
├── 简历筛选子Agent (ResumeScreeningAgent)  ← 你的项目
├── 面试安排子Agent (InterviewSchedulerAgent)
├── 候选人沟通子Agent (CommunicationAgent)
└── Offer管理子Agent (OfferManagementAgent)

通信方式：
- 接口：类方法调用
- 配置：配置对象传递（不污染环境变量）
- 状态：无状态设计（每次调用独立）
- 错误：结构化错误对象
- 追踪：统一的request_id
```

---

## 🚀 下一步建议

要我现在实现这些关键修复吗？优先级建议：

1. **移除环境变量污染**（5分钟）
2. **添加结构化错误**（15分钟）
3. **添加批量处理**（10分钟）
4. **添加日志和追踪**（20分钟）

这些修改完成后，你的resume-agent将非常适合作为子Agent集成！
