"""
生成一份高分测试简历PDF
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


def create_high_score_resume():
    """创建一份能通过70分阈值的测试简历"""

    output_file = "test_pass_resume.pdf"
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    # 尝试使用中文字体（如果有的话）
    try:
        # Windows系统字体路径
        font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            c.setFont('SimHei', 12)
        else:
            c.setFont('Helvetica', 12)
    except:
        c.setFont('Helvetica', 12)

    y = height - 50
    line_height = 20

    def write_line(text, size=12, bold=False):
        nonlocal y
        if bold:
            c.setFont('Helvetica-Bold', size)
        else:
            try:
                c.setFont('SimHei', size)
            except:
                c.setFont('Helvetica', size)
        c.drawString(50, y, text)
        y -= line_height

    # 标题
    write_line("Zhang Wei - Quantitative Finance Resume", 16, True)
    y -= 10

    # 基本信息
    write_line("Email: zhangwei@example.com | Phone: +86 138-0000-0000", 10)
    write_line("GitHub: github.com/zhangwei | Location: Shanghai, China", 10)
    y -= 10

    # 教育背景
    write_line("EDUCATION", 14, True)
    write_line("Tsinghua University, Beijing, China", 11)
    write_line("Bachelor of Science in Computer Science, GPA: 3.8/4.0", 10)
    write_line("Expected Graduation: June 2025", 10)
    y -= 10

    # 项目经历（30分满分目标：28分）
    write_line("PROJECT EXPERIENCE", 14, True)
    write_line("1. Multi-Factor Stock Selection Strategy (2023.06 - 2024.01)", 11, True)
    write_line("   - Developed 50+ alpha factors including momentum, value, quality factors", 10)
    write_line("   - Implemented backtesting system using Python/pandas/numpy", 10)
    write_line("   - Achieved annual return 18%, max drawdown 6%, Sharpe ratio 2.1", 10)
    write_line("   - Used machine learning (XGBoost) for factor selection", 10)
    y -= 5

    write_line("2. CTA Trend Following Strategy (2023.01 - 2023.06)", 11, True)
    write_line("   - Developed CTA strategy based on technical indicators (MA, MACD, RSI)", 10)
    write_line("   - Backtested on futures data (commodity, equity index, bond)", 10)
    write_line("   - Annual return 22%, max drawdown 8%, implemented real-time monitoring", 10)
    write_line("   - Optimized execution with TWAP/VWAP algorithms to reduce slippage", 10)
    y -= 5

    write_line("3. High-Frequency Market Making System (2022.09 - 2022.12)", 11, True)
    write_line("   - Built low-latency trading system using C++ (latency <50 microseconds)", 10)
    write_line("   - Implemented order book analysis and inventory management", 10)
    write_line("   - Achieved daily profit 0.5% with minimal risk", 10)
    y -= 10

    # 实习经历（25分满分目标：22分）
    write_line("INTERNSHIP EXPERIENCE", 14, True)
    write_line("Quantitative Research Intern | ABC Quantitative Investment (2023.07-2024.01)", 11, True)
    write_line("   - Developed and maintained multi-factor stock selection models", 10)
    write_line("   - Participated in strategy research, factor mining, and backtesting", 10)
    write_line("   - Improved factor IC from 0.03 to 0.05 through feature engineering", 10)
    write_line("   - Worked with senior quants on live trading strategies (AUM 500M RMB)", 10)
    y -= 10

    # 技术栈（25分满分目标：23分）
    write_line("TECHNICAL SKILLS", 14, True)
    write_line("Programming: Python (proficient), C++ (proficient), SQL", 10)
    write_line("Quant Tools: pandas, numpy, scipy, statsmodels, backtrader, zipline", 10)
    write_line("Machine Learning: scikit-learn, XGBoost, LightGBM, PyTorch", 10)
    write_line("Database: MySQL, Redis, TimescaleDB, InfluxDB", 10)
    write_line("Financial Data: Wind API, Tushare, AKShare, Bloomberg Terminal", 10)
    write_line("Other: Git, Docker, Linux, Jupyter, Matplotlib, Seaborn", 10)
    y -= 10

    # 科研经历（20分满分目标：0分 - 为了刚好过线）
    # 不添加科研经历

    # 竞赛经历（15分加分目标：10分）
    write_line("COMPETITION & AWARDS", 14, True)
    write_line("- Mathematical Contest in Modeling (MCM), Honorable Mention (2023)", 10)
    write_line("- China Undergraduate Mathematical Contest in Modeling, Provincial 1st Prize (2022)", 10)
    write_line("- WorldQuant Brain Quantitative Challenge, Top 15% (2023)", 10)

    c.save()
    print(f"High-score resume created: {output_file}")
    print("\nExpected Score Breakdown:")
    print("- Projects: 28/30 (3 high-quality quant projects)")
    print("- Internship: 22/25 (6-month quant research intern)")
    print("- Tech Stack: 23/25 (comprehensive quant tech stack)")
    print("- Research: 0/20 (no research experience)")
    print("- Competition: 10/15 (math modeling + quant competitions)")
    print("=" * 50)
    print("Expected Total: 83/115 (PASS - above 70 threshold)")


if __name__ == "__main__":
    create_high_score_resume()
