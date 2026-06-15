# src/nodes/parser.py
from typing import Dict, Any
from langchain_community.document_loaders import PyPDFLoader


def parse_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    PDF解析节点：从PDF文件中提取文本内容

    Args:
        state: 工作流状态，需要包含 pdf_path

    Returns:
        更新后的状态，包含 resume_text 或 error
    """
    try:
        pdf_path = state["pdf_path"]

        # 使用LangChain的PyPDFLoader加载PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        # 合并所有页面的文本
        resume_text = "\n".join([page.page_content for page in pages])

        return {
            **state,
            "resume_text": resume_text,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "resume_text": None,
            "error": f"Error parsing PDF: {str(e)}"
        }
