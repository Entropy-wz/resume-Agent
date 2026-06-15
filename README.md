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
