# tests/test_nodes.py
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any


class TestParserNode:
    """测试PDF解析节点"""

    def test_parse_resume_node_success(self):
        """测试PDF解析成功"""
        from src.nodes.parser import parse_resume_node

        # Mock state with PDF path
        state = {
            "pdf_path": "test.pdf",
            "resume_text": None,
            "error": None
        }

        # Mock PyPDFLoader
        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_instance = Mock()
            mock_instance.load.return_value = [
                Mock(page_content="Page 1 content"),
                Mock(page_content="Page 2 content")
            ]
            mock_loader.return_value = mock_instance

            result = parse_resume_node(state)

            assert result["resume_text"] == "Page 1 content\nPage 2 content"
            assert result["error"] is None
            mock_loader.assert_called_once_with("test.pdf")

    def test_parse_resume_node_error(self):
        """测试PDF解析失败"""
        from src.nodes.parser import parse_resume_node

        state = {
            "pdf_path": "nonexistent.pdf",
            "resume_text": None,
            "error": None
        }

        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_loader.side_effect = Exception("File not found")

            result = parse_resume_node(state)

            assert result["resume_text"] is None
            assert "Error" in result["error"]
            assert "File not found" in result["error"]

    def test_parse_resume_node_empty_pdf(self):
        """测试空PDF"""
        from src.nodes.parser import parse_resume_node

        state = {
            "pdf_path": "empty.pdf",
            "resume_text": None,
            "error": None
        }

        with patch('src.nodes.parser.PyPDFLoader') as mock_loader:
            mock_instance = Mock()
            mock_instance.load.return_value = []
            mock_loader.return_value = mock_instance

            result = parse_resume_node(state)

            assert result["resume_text"] == ""
            assert result["error"] is None
