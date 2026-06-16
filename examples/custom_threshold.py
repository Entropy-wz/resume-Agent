"""
自定义阈值示例：批量处理多个简历，使用不同的阈值
"""

from pathlib import Path
from src.workflow import create_resume_screening_workflow


async def process_resume(resume_path: str, threshold: float):
    """处理单个简历"""
    workflow = create_resume_screening_workflow()

    initial_state = {
        "resume_path": resume_path,  # 使用resume_path
        "threshold": threshold,
    }

    final_state = await workflow.ainvoke(initial_state)
    return final_state


async def batch_process():
    """批量处理示例"""

    # 示例1: 使用不同阈值
    resumes = [
        ("resumes/candidate1.pdf", 70.0),  # 标准阈值
        ("resumes/candidate2.pdf", 80.0),  # 高要求岗位
        ("resumes/candidate3.pdf", 60.0),  # 实习生岗位
    ]

    results = []

    for resume_path, threshold in resumes:
        print(f"处理: {resume_path} (阈值: {threshold})")
        result = await process_resume(resume_path, threshold)
        results.append((resume_path, threshold, result))

    # 输出结果
    for resume_path, threshold, result in results:
        evaluation = result.get("evaluation")
        if evaluation:
            print(f"\n{Path(resume_path).name}")
            print(f"  阈值: {threshold}")
            print(f"  得分: {evaluation.final_score}/115")
            print(f"  结果: {'通过' if evaluation.passed_screening else '未通过'}")


async def dynamic_threshold():
    """动态调整阈值示例"""

    resume_path = "resumes/candidate.pdf"

    # 先用标准阈值试试
    print(f"使用标准阈值70分评估 {resume_path}...")
    result1 = await process_resume(resume_path, 70.0)

    evaluation1 = result1.get("evaluation")
    if not evaluation1.passed_screening:
        # 如果没通过，尝试降低阈值
        print(f"\n候选人得分 {evaluation1.final_score}，未达到70分")
        print("尝试使用60分阈值重新评估...")

        result2 = await process_resume(resume_path, 60.0)
        evaluation2 = result2.get("evaluation")

        if evaluation2.passed_screening:
            print(f"使用60分阈值通过初筛")
            print("建议: 可以安排面试，但需要重点考察弱项")
        else:
            print(f"即使降低到60分也未通过")
            print("建议: 不予考虑")
    else:
        print(f"候选人得分 {evaluation1.final_score}，通过70分阈值")
        questions = result1.get("questions")
        if questions:
            print(f"\n已生成 {len(questions.basic_questions)} 个基础题")
            print(f"已生成 {len(questions.advanced_questions)} 个进阶题")


if __name__ == "__main__":
    import asyncio

    print("=== 批量处理示例 ===")
    # asyncio.run(batch_process())  # 取消注释以运行

    print("\n=== 动态阈值示例 ===")
    # asyncio.run(dynamic_threshold())  # 取消注释以运行

    print("\n注意: 请取消注释上面的代码并提供实际的PDF文件路径")
