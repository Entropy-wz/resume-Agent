"""
自定义阈值示例：批量处理多个简历，使用不同的阈值
"""

from pathlib import Path
from src.workflow import create_resume_screening_workflow


async def process_resume(pdf_path: str, threshold: float):
    """处理单个简历"""
    workflow = create_resume_screening_workflow()

    initial_state = {
        "pdf_path": pdf_path,
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

    print("开始批量处理简历...\n")

    results = []
    for pdf_path, threshold in resumes:
        print(f"处理: {pdf_path} (阈值: {threshold})")
        result = await process_resume(pdf_path, threshold)
        results.append((pdf_path, threshold, result))

    # 汇总结果
    print("\n" + "=" * 60)
    print("批量处理结果汇总")
    print("=" * 60)

    passed_count = 0
    for pdf_path, threshold, result in results:
        evaluation = result.get("evaluation")
        if evaluation:
            passed = evaluation.passed_screening
            passed_count += passed
            status = "✅ 通过" if passed else "❌ 未通过"
            print(f"\n{Path(pdf_path).name}")
            print(f"  候选人: {evaluation.candidate_name}")
            print(f"  总分: {evaluation.final_score}/115")
            print(f"  阈值: {threshold}")
            print(f"  结果: {status}")

    print(f"\n总计: {len(results)}份简历, {passed_count}份通过初筛")


async def dynamic_threshold():
    """动态调整阈值示例"""

    pdf_path = "resumes/candidate.pdf"

    # 先用标准阈值评估
    print("使用标准阈值(70分)评估...")
    result1 = await process_resume(pdf_path, 70.0)

    evaluation = result1.get("evaluation")
    if not evaluation:
        print("评估失败")
        return

    print(f"候选人: {evaluation.candidate_name}")
    print(f"总分: {evaluation.final_score}/115")

    # 根据分数动态调整
    if evaluation.final_score >= 90:
        print("\n候选人优秀，推荐进入高级岗位面试")
    elif evaluation.final_score >= 70:
        print("\n候选人合格，推荐进入标准面试流程")
        # 生成面试问题
        if result1.get("questions"):
            print(f"已生成{len(result1['questions'].basic_questions)}道基础题")
            print(f"已生成{len(result1['questions'].advanced_questions)}道进阶题")
    else:
        print(f"\n候选人分数较低({evaluation.final_score}分)")
        print("建议:")
        print("  1. 如果是实习生岗位，可以考虑降低阈值到60分")
        print("  2. 如果是正式岗位，建议不予考虑")

        # 尝试用实习生标准重新评估
        print("\n使用实习生标准(60分)重新评估...")
        result2 = await process_resume(pdf_path, 60.0)
        if result2.get("evaluation").passed_screening:
            print("✅ 符合实习生岗位要求")


if __name__ == "__main__":
    print("示例1: 批量处理")
    print("-" * 60)
    # asyncio.run(batch_process())

    print("\n\n示例2: 动态阈值")
    print("-" * 60)
    # asyncio.run(dynamic_threshold())

    print("\n注意: 请取消注释上面的代码并提供实际的PDF文件路径来运行")
