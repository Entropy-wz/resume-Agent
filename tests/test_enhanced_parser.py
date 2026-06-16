"""
Test enhanced PDF parser
"""
import pytest
from src.nodes.parser import (
    parse_resume_node,
    clean_text,
    is_header_or_footer,
    format_table_as_text,
    enhance_structure
)


def test_clean_text_removes_multiple_spaces():
    """测试：清洗多余空格"""
    text = "Hello    world\nTest    line"
    cleaned = clean_text(text)
    assert "    " not in cleaned
    assert "Hello world" in cleaned


def test_clean_text_removes_excessive_newlines():
    """测试：清洗过多换行"""
    text = "Line1\n\n\n\n\nLine2"
    cleaned = clean_text(text)
    assert "\n\n\n" not in cleaned
    assert "Line1\n\nLine2" in cleaned


def test_is_header_or_footer_detects_page_numbers():
    """测试：识别页码"""
    assert is_header_or_footer("第1页") is True
    assert is_header_or_footer("Page 1") is True
    assert is_header_or_footer("1/5") is True
    assert is_header_or_footer("3") is True
    assert is_header_or_footer("真实内容") is False


def test_is_header_or_footer_detects_common_footers():
    """测试：识别常见页脚"""
    assert is_header_or_footer("Confidential") is True
    assert is_header_or_footer("简历") is True
    assert is_header_or_footer("Resume") is True
    assert is_header_or_footer("我的项目经历很丰富") is False


def test_format_table_as_text():
    """测试：表格格式化"""
    table = [
        ["姓名", "年龄", "学校"],
        ["张三", "25", "清华大学"],
        ["李四", "24", "北京大学"],
    ]
    result = format_table_as_text(table)

    assert "姓名 | 年龄 | 学校" in result
    assert "张三 | 25 | 清华大学" in result
    assert "李四 | 24 | 北京大学" in result


def test_format_table_handles_none_values():
    """测试：处理表格中的None值"""
    table = [
        ["Name", None, "School"],
        ["Alice", "25", None],
    ]
    result = format_table_as_text(table)

    assert "Name |  | School" in result
    assert "Alice | 25 | " in result


def test_enhance_structure_marks_sections():
    """测试：标注章节结构"""
    text = """
    张三的简历

    教育背景
    清华大学 计算机科学

    项目经历
    量化交易系统开发

    技术栈
    Python, C++
    """

    enhanced = enhance_structure(text)

    # 应该标注章节
    assert "## 教育背景" in enhanced
    assert "## 项目经历" in enhanced
    assert "## 技能" in enhanced


def test_enhance_structure_handles_variations():
    """测试：识别章节标题的不同写法"""
    text = "实习经验\n某公司实习\n\n竞赛获奖\n数学建模一等奖"
    enhanced = enhance_structure(text)

    assert "## 工作经验" in enhanced  # 实习经验 -> 工作经验
    assert "## 竞赛" in enhanced


@pytest.mark.asyncio
async def test_parse_resume_node_with_valid_pdf():
    """测试：解析有效的PDF文件"""
    state = {"resume_path": "test_pass_resume.pdf"}

    result = parse_resume_node(state)

    # 应该成功解析
    assert result.get("error") is None
    assert result.get("resume_text") is not None
    assert len(result["resume_text"]) > 100  # 应该有足够的文本


def test_parse_resume_node_with_invalid_path():
    """测试：处理无效的PDF路径"""
    state = {"resume_path": "nonexistent_file.pdf"}

    result = parse_resume_node(state)

    # 应该返回错误
    assert result.get("error") is not None
    assert result.get("resume_text") is None
    assert "Error parsing PDF" in result["error"]


def test_clean_text_preserves_paragraph_structure():
    """测试：保留段落结构"""
    text = """
    第一段内容

    第二段内容


    第三段内容
    """

    cleaned = clean_text(text)

    # 应该保留段落分隔，但不超过2个换行
    assert "第一段内容\n\n第二段内容" in cleaned
    assert "\n\n\n" not in cleaned


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
