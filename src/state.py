"""
Workflow state type definitions

Provides type safety for LangGraph StateGraph workflow state.
"""
from typing import TypedDict, Optional
from src.models import EvaluationResult, InterviewQuestions


class WorkflowState(TypedDict, total=False):
    """
    State schema for resume screening workflow

    Type safety benefits:
    - IDE autocomplete for state keys
    - Static type checking with mypy/pyright
    - Clear documentation of state structure
    - Prevents typos in key names

    Required fields (set at workflow entry):
    - resume_path: Path to PDF file
    - threshold: Screening threshold score (0-115)

    Optional fields (set during workflow execution):
    - resume_text: Extracted text from PDF
    - evaluation: Evaluation result from LLM
    - should_generate_questions: Whether to generate interview questions
    - questions: Generated interview questions (if passed screening)
    - error: Error message (if any step failed)
    """

    # Required at workflow entry
    resume_path: str
    threshold: float

    # API configuration (passed through state to avoid env var pollution)
    api_key: str
    api_base_url: str

    # Set during workflow execution
    resume_text: Optional[str]
    evaluation: Optional[EvaluationResult]
    should_generate_questions: Optional[bool]
    questions: Optional[InterviewQuestions]
    error: Optional[str]
