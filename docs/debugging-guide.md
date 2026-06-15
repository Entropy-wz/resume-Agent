# 量化岗位简历筛选Agent - 调试文档

## 文档信息

- **版本：** 1.0.0
- **创建日期：** 2026-06-15
- **适用范围：** 开发、测试、故障排查

---

## 1. 环境配置

### 1.1 系统要求

- **Python版本：** 3.10+
- **操作系统：** Windows/Linux/macOS
- **内存：** 建议4GB+
- **网络：** 需要访问OpenAI API

### 1.2 安装步骤

```bash
# 1. 克隆或进入项目目录
cd D:/exp_all/resume-Agent

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 验证安装
python -c "from resume_agent import ResumeScreeningAgent; print('安装成功')"
```

### 1.3 配置API Key

**方法1：环境变量（推荐）**
```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-api-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-api-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**方法2：.env文件**
```bash
# 复制模板
cp .env.example .env

# 编辑.env文件
# OPENAI_API_KEY=sk-your-api-key-here
```

**方法3：代码中直接传入**
```python
agent = ResumeScreeningAgent(
    openai_api_key="sk-your-api-key-here"
)
```

---

## 2. 快速测试

### 2.1 运行单元测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_models.py -v
pytest tests/test_config.py -v
pytest tests/test_nodes.py -v

# 运行特定测试函数
pytest tests/test_models.py::test_dimension_score_creation -v

# 显示打印输出
pytest tests/ -v -s

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 2.2 测试分类

**无需API Key的测试：**
- `test_models.py` - 数据模型测试 (8个测试)
- `test_config.py` - 配置管理测试 (3个测试)
- `test_workflow.py` - 工作流结构测试 (部分)

**需要API Key的测试：**
- `test_agents.py` - Agent测试 (4个测试)
- `test_integration.py` - 集成测试 (7个测试)
- `test_e2e.py` - 端到端测试 (5个测试)

```bash
# 只运行不需要API key的测试
pytest tests/test_models.py tests/test_config.py -v

# 运行需要API key的测试（需先设置OPENAI_API_KEY）
export OPENAI_API_KEY="sk-xxx"
pytest tests/test_agents.py -v
```

### 2.3 运行示例代码

```bash
# 设置API key
export OPENAI_API_KEY="sk-xxx"

# 运行基本示例
python examples/basic_usage.py

# 运行自定义阈值示例
python examples/custom_threshold.py
```

---

## 3. 调试技巧

### 3.1 启用调试日志

**方法1：环境变量**
```bash
export LOG_LEVEL=DEBUG
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

**方法2：代码中添加日志**
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

### 3.2 调试工作流执行

**查看工作流状态：**
```python
agent = ResumeScreeningAgent(openai_api_key="sk-xxx")

# 添加日志记录每个节点的执行
import logging
logging.basicConfig(level=logging.INFO)

result = await agent.screen_resume("resume.pdf")

# 检查最终状态
print("Error:", result.get("error"))
print("Evaluation:", result.get("evaluation"))
print("Questions:", result.get("interview_questions"))
```

**手动执行各个节点：**
```python
from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node

# 测试PDF解析
state = {"resume_path": "test.pdf"}
result = parse_resume_node(state)
print("Resume text:", result.get("resume_text")[:200])
print("Error:", result.get("error"))

# 测试评分节点
state = {
    "resume_text": "姓名：张三...",
    "threshold": 70.0
}
result = await evaluate_resume_node(state)
print("Evaluation:", result.get("evaluation"))
```

### 3.3 调试Agent输出

**检查Agent返回的原始数据：**
```python
from src.agents.evaluator import create_evaluator_agent

agent = create_evaluator_agent()
result = await agent.run("请评估以下简历：...")

# 查看完整响应
print("Raw result:", result)
print("Data:", result.data)
print("Messages:", result.messages)
```

**验证Pydantic模型：**
```python
from src.models import EvaluationResult, DimensionScore, BaseScore, BonusScore
from datetime import datetime

# 手动构造测试数据
try:
    evaluation = EvaluationResult(
        candidate_name="测试",
        base_score=BaseScore(
            project_experience=DimensionScore(
                dimension="项目", score=25, max_score=30, reasoning="优秀"
            ),
            # ... 其他维度
            total_base_score=82.0
        ),
        bonus_score=BonusScore(
            competitions=[], bonus_points=0, reasoning="无"
        ),
        final_score=82.0,
        passed_screening=True,
        timestamp=datetime.now()
    )
    print("模型验证成功")
except Exception as e:
    print("验证失败:", e)
```

---

## 4. 常见问题排查

### 4.1 问题：ModuleNotFoundError

**症状：**
```
ModuleNotFoundError: No module named 'src'
```

**原因：**
- 未安装包
- 未使用正确的Python环境

**解决方案：**
```bash
# 1. 确认在项目根目录
pwd  # 应该显示 .../resume-Agent

# 2. 重新安装
pip install -e .

# 3. 验证安装
pip list | grep resume-agent
```

### 4.2 问题：OpenAI API错误

**症状A：认证失败**
```
openai.AuthenticationError: Incorrect API key provided
```

**解决方案：**
```bash
# 检查API key格式
echo $OPENAI_API_KEY  # 应该是 sk-开头

# 重新设置
export OPENAI_API_KEY="sk-正确的key"

# 或在代码中设置
agent = ResumeScreeningAgent(openai_api_key="sk-正确的key")
```

**症状B：速率限制**
```
openai.RateLimitError: Rate limit exceeded
```

**解决方案：**
- 降低并发请求
- 增加重试延迟
- 升级API计划

**症状C：网络超时**
```
openai.APIConnectionError: Connection timeout
```

**解决方案：**
```python
# 增加超时时间（如果Pydantic AI支持）
# 或使用代理
import os
os.environ["HTTP_PROXY"] = "http://your-proxy:port"
os.environ["HTTPS_PROXY"] = "https://your-proxy:port"
```

### 4.3 问题：PDF解析失败

**症状：**
```
PDF解析失败: [Errno 2] No such file or directory: 'resume.pdf'
```

**排查步骤：**
```python
import os

# 1. 检查文件是否存在
resume_path = "path/to/resume.pdf"
print("文件存在:", os.path.exists(resume_path))

# 2. 检查文件权限
print("可读:", os.access(resume_path, os.R_OK))

# 3. 使用绝对路径
resume_path = os.path.abspath("resume.pdf")

# 4. 手动测试PDF加载
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(resume_path)
docs = loader.load()
print("页数:", len(docs))
print("内容预览:", docs[0].page_content[:200])
```

**常见原因：**
- 文件路径错误（相对路径vs绝对路径）
- 文件不存在
- 权限不足
- PDF格式损坏
- 扫描版PDF（需要OCR）

### 4.4 问题：评分结果不合理

**症状：**
- 所有候选人分数都很高/很低
- 分数分布不合理
- 评分理由不充分

**排查步骤：**

1. **检查系统提示词：**
```python
from src.agents.evaluator import EVALUATOR_SYSTEM_PROMPT
print(EVALUATOR_SYSTEM_PROMPT)
```

2. **测试单个评分：**
```python
from src.agents.evaluator import evaluate_resume

resume = """
姓名：张三
项目：简单的TODO应用
技术：Python
"""

result = await evaluate_resume(resume, threshold=70.0)
print("项目分数:", result.base_score.project_experience.score)
print("理由:", result.base_score.project_experience.reasoning)
```

3. **对比不同简历：**
```python
# 准备高质量和低质量简历样本
high_quality_resume = "..."
low_quality_resume = "..."

result_high = await evaluate_resume(high_quality_resume)
result_low = await evaluate_resume(low_quality_resume)

print("高质量:", result_high.final_score)
print("低质量:", result_low.final_score)
```

**可能的解决方案：**
- 调整系统提示词，增加更具体的评分标准
- 提供更多评分示例
- 调整温度参数（temperature）使结果更一致
- 使用多次采样求平均

### 4.5 问题：题目生成质量不佳

**症状：**
- 题目与简历无关
- 题目过于泛泛
- 题目超出候选人能力范围

**排查步骤：**

1. **检查输入数据：**
```python
from src.agents.question_generator import generate_questions

# 查看传入的数据
print("简历文本:", resume_text[:500])
print("评分结果:", evaluation.dict())
```

2. **检查系统提示词：**
```python
from src.agents.question_generator import QUESTION_GENERATOR_SYSTEM_PROMPT
print(QUESTION_GENERATOR_SYSTEM_PROMPT)
```

3. **单独测试题目生成：**
```python
questions = await generate_questions(resume_text, evaluation)

for q in questions.basic_questions:
    print(f"[基础] {q.question}")
    print(f"  关联项目: {q.related_project}")
    print(f"  考察点: {q.focus_area}")
```

### 4.6 问题：数据验证错误

**症状：**
```
ValidationError: 1 validation error for EvaluationResult
total_base_score
  总分必须等于各维度之和 (type=value_error)
```

**原因：**
- Pydantic模型验证失败
- LLM返回的数据不符合约束

**排查步骤：**

1. **查看原始LLM输出：**
```python
agent = create_evaluator_agent()
result = await agent.run(prompt)

# 在验证失败前查看原始数据
print("Raw data:", result.data)
```

2. **临时禁用验证测试：**
```python
# 在models.py中临时注释掉validator
# @model_validator(mode='after')
# def validate_total(self):
#     ...
```

3. **调整提示词强调约束：**
```python
prompt = f"""
请确保：
1. total_base_score必须等于四个维度之和
2. score不能超过max_score
3. 所有reasoning字段不能为空

请评估以下简历：...
"""
```

---

## 5. 性能调试

### 5.1 测量执行时间

```python
import time

start = time.time()
result = await agent.screen_resume("resume.pdf")
end = time.time()

print(f"总耗时: {end - start:.2f}秒")

# 分解各环节时间
times = {}

# PDF解析
start = time.time()
state = parse_resume_node({"resume_path": "resume.pdf"})
times["parse"] = time.time() - start

# 评分
start = time.time()
state = await evaluate_resume_node(state)
times["evaluate"] = time.time() - start

# 题目生成
start = time.time()
state = await generate_questions_node(state)
times["generate"] = time.time() - start

print("时间分解:", times)
```

### 5.2 监控Token使用

```python
# Pydantic AI会在result中返回usage信息
agent = create_evaluator_agent()
result = await agent.run(prompt)

# 查看token使用
if hasattr(result, 'usage'):
    print(f"Tokens使用: {result.usage}")
```

### 5.3 批量处理优化

```python
import asyncio

async def process_batch(resume_paths, agent):
    """批量处理简历"""
    tasks = [
        agent.screen_resume(path)
        for path in resume_paths
    ]
    
    # 并发执行（注意API速率限制）
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

# 使用
agent = ResumeScreeningAgent(openai_api_key="sk-xxx")
resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
results = await process_batch(resumes, agent)
```

---

## 6. 测试数据准备

### 6.1 创建测试简历

**高质量简历示例：**
```python
high_quality_resume = """
姓名：张三
教育背景：清华大学 计算机科学 本科

项目经历：
1. 高频交易系统开发（2023.06-2024.01）
   - 使用C++开发低延迟交易系统
   - 将延迟从100微秒优化到15微秒
   - 处理每秒10万笔订单

2. 多因子选股策略（2023.01-2023.06）
   - 构建包含50+因子的量化模型
   - 使用机器学习进行因子筛选
   - 年化超额收益12%

实习经历：
1. XX量化投资公司 量化研究员（2022.07-2022.12）
   - 开发和维护量化交易策略
   - 参与实盘交易和风控

技术栈：
- 编程：Python, C++, SQL
- 量化：pandas, numpy, backtrader, zipline
- 机器学习：sklearn, xgboost, pytorch

科研经历：
- 发表论文："基于深度学习的股票价格预测"（ICML 2023）

竞赛：
- 全国大学生数学建模竞赛 国家一等奖
- WorldQuant量化挑战赛 Top 10%
"""
```

**低质量简历示例：**
```python
low_quality_resume = """
姓名：李四
教育：某大学 本科

项目：
- 做过一个网站
- 学过Python

技能：
- Python
- Excel
"""
```

### 6.2 创建测试PDF

使用Python生成测试PDF：
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf(text, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # 添加文本
    y = 750
    for line in text.split('\n'):
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    
    c.save()

# 生成测试PDF
create_test_pdf(high_quality_resume, "tests/fixtures/high_quality.pdf")
create_test_pdf(low_quality_resume, "tests/fixtures/low_quality.pdf")
```

---

## 7. 开发建议

### 7.1 本地开发工作流

```bash
# 1. 修改代码
vim src/models.py

# 2. 运行相关测试
pytest tests/test_models.py -v

# 3. 代码格式化
black src/models.py

# 4. 代码检查
ruff check src/models.py

# 5. 提交更改
git add src/models.py tests/test_models.py
git commit -m "feat: update model validation"
```

### 7.2 添加新功能

**步骤：**
1. 先写测试（TDD）
2. 实现功能
3. 运行测试确保通过
4. 更新文档
5. 提交代码

**示例：添加新的评分维度**
```python
# 1. 先在tests/test_models.py添加测试
def test_new_dimension():
    score = NewDimensionScore(...)
    assert score.value == expected

# 2. 在src/models.py实现
class NewDimensionScore(BaseModel):
    ...

# 3. 运行测试
pytest tests/test_models.py::test_new_dimension -v

# 4. 提交
git commit -m "feat: add new scoring dimension"
```

### 7.3 调试最佳实践

1. **使用小数据集测试**：不要一开始就用大量简历
2. **隔离问题**：单独测试每个组件
3. **保存中间结果**：在文件中保存state便于分析
4. **使用pytest fixtures**：准备可复用的测试数据
5. **Mock外部依赖**：在单元测试中mock LLM调用

---

## 8. 故障排查检查清单

当遇到问题时，按此顺序检查：

- [ ] Python版本是否>=3.10
- [ ] 依赖是否正确安装 (`pip list`)
- [ ] OPENAI_API_KEY是否设置且有效
- [ ] 文件路径是否正确（绝对路径vs相对路径）
- [ ] PDF文件是否存在且可读
- [ ] 网络是否可以访问OpenAI API
- [ ] 简历内容是否足够详细（空简历会导致低分）
- [ ] 测试时使用的API key是否有足够余额
- [ ] 日志输出中是否有错误信息
- [ ] Pydantic验证是否通过

---

## 9. 联系支持

如果以上方法都无法解决问题：

1. 查看GitHub Issues
2. 运行诊断脚本收集信息
3. 提供完整错误日志
4. 说明复现步骤
