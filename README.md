# Resume Screening Agent

量化岗位简历筛选Agent，使用LangGraph编排工作流，Pydantic AI执行评分和题目生成。

## 功能特点

- **多维度评分系统**：项目经历(30分)、实习经历(25分)、技术栈(25分)、科研经历(20分)
- **竞赛加分机制**：独立15分加分项
- **智能阈值筛选**：默认70分，可自定义
- **针对性面试题目**：2个基础题 + 2-3个进阶题，基于简历内容生成
- **完整工作流**：PDF解析 → 评分 → 阈值检查 → 题目生成

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

### 3. 基础使用

```python
import asyncio
from src.workflow import create_workflow

async def main():
    # 创建工作流
    workflow = create_workflow()
    
    # 准备初始状态
    initial_state = {
        "pdf_path": "path/to/resume.pdf",
        "threshold": 70.0,
    }
    
    # 运行工作流
    final_state = await workflow.ainvoke(initial_state)
    
    # 获取结果
    evaluation = final_state.get("evaluation")
    questions = final_state.get("questions")
    
    print(f"候选人: {evaluation.candidate_name}")
    print(f"总分: {evaluation.final_score}/115")
    print(f"是否通过: {evaluation.passed_screening}")

if __name__ == "__main__":
    asyncio.run(main())
```

更多示例请查看 `examples/` 目录：
- `basic_usage.py` - 完整的使用示例
- `custom_threshold.py` - 自定义阈值和批量处理

## 项目结构

```
resume-Agent/
├── src/
│   ├── agents/           # Pydantic AI agents
│   │   ├── evaluator.py           # 简历评分Agent
│   │   └── question_generator.py  # 问题生成Agent
│   ├── nodes/            # LangGraph节点
│   │   ├── parser.py              # PDF解析节点
│   │   ├── evaluator.py           # 评分节点
│   │   ├── checker.py             # 阈值检查节点
│   │   └── generator.py           # 问题生成节点
│   ├── models.py         # Pydantic数据模型
│   ├── config.py         # 配置管理
│   └── workflow.py       # LangGraph工作流
├── tests/                # 测试文件
├── examples/             # 使用示例
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目配置
└── README.md
```

## 评分标准

### 基础评分（100分）

1. **项目经历（30分）**
   - 量化/金融相关项目的深度和复杂度
   - 技术难度和创新性
   - 个人贡献和项目影响力

2. **实习经历（25分）**
   - 公司和岗位的相关性
   - 实习时长和深度
   - 具体工作内容和成果

3. **技术栈（25分）**
   - 编程语言：Python、C++等
   - 量化工具：pandas、numpy、backtrader等
   - 机器学习：sklearn、pytorch等
   - 数据库和中间件

4. **科研经历（20分）**
   - 论文发表（顶会、SCI）
   - 研究项目质量
   - 与量化/金融的相关性

### 加分项（15分）

- 数学建模竞赛（美赛、国赛）
- 量化投资比赛（宽客、WorldQuant）
- 编程竞赛（ACM、LeetCode）
- 金融科技比赛

## 测试

运行所有测试：

```bash
pytest tests/ -v
```

运行特定测试：

```bash
# 单元测试
pytest tests/test_models.py -v
pytest tests/test_workflow.py -v

# 集成测试（需要API key）
pytest tests/test_e2e.py -v
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
# 格式化代码
black src/ tests/ examples/

# 代码检查
ruff check src/ tests/ examples/ --fix
```

### 运行测试

```bash
pytest tests/ -v --cov=src
```

## 技术栈

- **LangGraph**: 工作流编排和状态管理
- **Pydantic AI**: 结构化输出的AI Agent
- **LangChain**: PDF文档解析
- **OpenAI GPT-4**: 大语言模型
- **Pydantic**: 数据验证和模型定义

## License

MIT License
