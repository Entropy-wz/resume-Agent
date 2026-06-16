# src/__init__.py
from typing import Dict, Any, Optional

from src.workflow import create_resume_screening_workflow


class ResumeScreeningAgent:
    """
    简历筛选Agent主接口

    提供异步和同步两种方式来筛选简历。
    """

    def __init__(self, openai_api_key: str, threshold: float = 70.0, openai_base_url: str = None):
        """
        初始化简历筛选Agent

        Args:
            openai_api_key: OpenAI API密钥
            threshold: 筛选阈值，默认70.0
            openai_base_url: OpenAI API base URL (可选，默认从环境变量读取)
        """
        self.openai_api_key = openai_api_key
        self.threshold = threshold

        # 从环境变量读取base_url（如果未提供）
        import os
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        # 不再设置环境变量！API key通过参数传递
        # 移除: os.environ["OPENAI_API_KEY"] = openai_api_key

        # 创建工作流
        self.workflow = create_resume_screening_workflow()

    async def screen_resume(
        self, resume_path: str, threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        异步筛选简历

        Args:
            resume_path: 简历PDF文件路径
            threshold: 可选的筛选阈值，如果不提供则使用初始化时的阈值

        Returns:
            包含评估结果和面试题目（如果通过初筛）的字典
            {
                "resume_path": str,
                "resume_text": str,
                "evaluation": EvaluationResult,
                "questions": InterviewQuestions | None,
                "should_generate_questions": bool,
                "error": str | None
            }
        """
        # 使用提供的阈值或默认阈值
        final_threshold = threshold if threshold is not None else self.threshold

        # 初始化状态（包含API配置）
        initial_state = {
            "resume_path": resume_path,
            "threshold": final_threshold,
            "resume_text": None,
            "evaluation": None,
            "should_generate_questions": None,
            "questions": None,
            "error": None,
            # API配置通过state传递（避免环境变量污染）
            "api_key": self.openai_api_key,
            "api_base_url": self.openai_base_url,
        }

        # 运行工作流
        result = await self.workflow.ainvoke(initial_state)

        return result

    def screen_resume_sync(
        self, resume_path: str, threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        同步筛选简历

        Args:
            resume_path: 简历PDF文件路径
            threshold: 可选的筛选阈值，如果不提供则使用初始化时的阈值

        Returns:
            包含评估结果和面试题目（如果通过初筛）的字典
            {
                "resume_path": str,
                "resume_text": str,
                "evaluation": EvaluationResult,
                "questions": InterviewQuestions | None,
                "should_generate_questions": bool,
                "error": str | None
            }
        """
        # 使用提供的阈值或默认阈值
        final_threshold = threshold if threshold is not None else self.threshold

        # 初始化状态（包含API配置）
        initial_state = {
            "resume_path": resume_path,
            "threshold": final_threshold,
            "resume_text": None,
            "evaluation": None,
            "should_generate_questions": None,
            "questions": None,
            "error": None,
            # API配置通过state传递（避免环境变量污染）
            "api_key": self.openai_api_key,
            "api_base_url": self.openai_base_url,
        }

        # 运行工作流（同步）
        result = self.workflow.invoke(initial_state)

        return result


# 导出主要类和模型
__all__ = ["ResumeScreeningAgent"]
