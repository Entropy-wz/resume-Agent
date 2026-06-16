# src/nodes/parser.py
"""
增强的PDF解析节点

支持：
1. 文本PDF（pdfplumber - 更好的表格和布局支持）
2. 扫描PDF（OCR via pytesseract）
3. 文本清洗（页眉页脚、格式规范化）
4. 章节识别（教育背景、项目经历等）
"""
from typing import Dict, Any
import re
import pdfplumber
from PIL import Image
import io


def parse_resume_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    增强的PDF解析节点：从PDF文件中提取文本内容

    解析策略：
    1. 优先使用pdfplumber提取文本（支持表格和双栏）
    2. 如果文本太少，尝试OCR（扫描件）
    3. 清洗页眉页脚和格式
    4. 识别简历章节结构

    Args:
        state: 工作流状态，需要包含 resume_path

    Returns:
        更新后的状态，包含 resume_text 或 error
    """
    try:
        pdf_path = state["resume_path"]

        # Step 1: 尝试提取文本PDF
        text = extract_text_with_pdfplumber(pdf_path)

        # Step 2: 检测是否需要OCR（文本太少可能是扫描件）
        if not text or len(text.strip()) < 100:
            try:
                text = extract_text_with_ocr(pdf_path)
            except Exception as ocr_error:
                # OCR失败，返回原始文本（即使很少）
                if not text:
                    return {
                        **state,
                        "resume_text": None,
                        "error": f"Error: PDF appears to be scanned but OCR failed: {str(ocr_error)}"
                    }

        # Step 3: 清洗文本
        text = clean_text(text)

        # Step 4: 识别章节结构（可选，帮助LLM理解）
        text = enhance_structure(text)

        return {**state, "resume_text": text, "error": None}

    except Exception as e:
        return {**state, "resume_text": None, "error": f"Error parsing PDF: {str(e)}"}


def extract_text_with_pdfplumber(pdf_path: str) -> str:
    """
    使用pdfplumber提取文本

    优势：
    - 更好的表格提取
    - 保留布局信息
    - 支持双栏
    """
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 提取页面文本
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

            # 提取表格（如果有）
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    # 将表格转换为文本格式
                    table_text = format_table_as_text(table)
                    text_parts.append(f"\n[表格]\n{table_text}\n[/表格]\n")

    return "\n\n".join(text_parts)


def extract_text_with_ocr(pdf_path: str) -> str:
    """
    使用OCR提取扫描PDF的文本

    需要：
    - Tesseract OCR已安装
    - 中英文语言包
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path

        # 将PDF转换为图片
        images = convert_from_path(pdf_path)

        text_parts = []
        for i, image in enumerate(images):
            # OCR识别（支持中英文）
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            if text.strip():
                text_parts.append(f"[第{i+1}页]\n{text}")

        return "\n\n".join(text_parts)

    except ImportError:
        raise Exception("OCR功能需要安装: pip install pytesseract pdf2image")
    except Exception as e:
        raise Exception(f"OCR处理失败: {str(e)}")


def format_table_as_text(table: list) -> str:
    """将表格数据格式化为易读文本"""
    if not table:
        return ""

    lines = []
    for row in table:
        if row:
            # 过滤None值并合并单元格
            cells = [str(cell).strip() if cell else "" for cell in row]
            if any(cells):  # 至少有一个非空单元格
                lines.append(" | ".join(cells))

    return "\n".join(lines)


def clean_text(text: str) -> str:
    """
    清洗PDF文本

    处理：
    1. 移除常见的页眉页脚（页码、日期等）
    2. 规范化空白字符
    3. 移除过多的空行
    """
    if not text:
        return ""

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # 跳过明显的页眉页脚
        if is_header_or_footer(line):
            continue

        # 跳过空行
        if not line:
            # 保留一些空行作为段落分隔
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        cleaned_lines.append(line)

    # 合并文本
    text = "\n".join(cleaned_lines)

    # 规范化多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)  # 最多2个连续换行
    text = re.sub(r' {2,}', ' ', text)  # 多个空格变一个

    return text.strip()


def is_header_or_footer(line: str) -> bool:
    """判断是否为页眉页脚"""
    line = line.strip()

    if not line:
        return False

    # 页码模式
    if re.match(r'^第?\s*\d+\s*页?$', line):
        return True
    if re.match(r'^Page\s+\d+$', line, re.IGNORECASE):
        return True
    if re.match(r'^\d+\s*/\s*\d+$', line):  # 1/5
        return True

    # 纯数字（可能是页码）
    if line.isdigit() and len(line) <= 3:
        return True

    # 常见页眉页脚文本
    footer_keywords = ['confidential', '机密', '简历', 'resume', 'curriculum vitae']
    if any(keyword in line.lower() for keyword in footer_keywords) and len(line) < 30:
        return True

    return False


def enhance_structure(text: str) -> str:
    """
    增强文本结构，标注章节

    识别常见简历章节：
    - 基本信息/个人信息
    - 教育背景/教育经历
    - 工作经验/实习经历
    - 项目经历/项目经验
    - 技能/技术栈
    - 科研经历/论文发表
    - 竞赛获奖/荣誉奖项
    """
    # 章节标题模式
    section_patterns = {
        "基本信息": r'(个人信息|基本信息|联系方式)',
        "教育背景": r'(教育背景|教育经历|学历)',
        "工作经验": r'(工作经[验历]|实习经[验历]|工作背景)',
        "项目经历": r'(项目经[验历]|项目经历|项目经验)',
        "技能": r'(技能|技术栈|专业技能|技术能力)',
        "科研": r'(科研经[验历]|论文发表|研究经历|学术成果)',
        "竞赛": r'(竞赛获奖|获奖情况|荣誉奖项|竞赛经历)',
    }

    lines = text.split('\n')
    enhanced_lines = []

    for line in lines:
        # 检查是否为章节标题
        is_section_title = False
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                # 标注章节
                enhanced_lines.append(f"\n## {section_name}\n{line}")
                is_section_title = True
                break

        if not is_section_title:
            enhanced_lines.append(line)

    return "\n".join(enhanced_lines)
