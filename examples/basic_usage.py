"""
基础使用示例：完整的简历筛选流程
"""
import asyncio
from src.workflow import create_workflow


async def main():
    # 创建工作流
    workflow = create_workflow()

    # 准备初始状态
    initial_state = {
        "pdf_path": "path/to/resume.pdf",
        "threshold": 70.0,  # 初筛阈值
    }

    # 运行工作流
    print("开始处理简历...")
    final_state = await workflow.ainvoke(initial_state)

    # 检查是否有错误
    if final_state.get("error"):
        print(f"❌ 处理失败: {final_state['error']}")
        return

    # 输出评估结果
    evaluation = final_state.get("evaluation")
    if evaluation:
        print(f"\n📊 评估结果")
        print(f"候选人: {evaluation.candidate_name}")
        print(f"总分: {evaluation.final_score}/115")
        print(f"是否通过初筛: {'✅ 是' if evaluation.passed_screening else '❌ 否'}")

        print(f"\n详细评分:")
        print(f"  项目经历: {evaluation.base_score.project_experience.score}/30")
        print(f"  实习经历: {evaluation.base_score.internship_experience.score}/25")
        print(f"  技术栈: {evaluation.base_score.tech_stack.score}/25")
        print(f"  科研经历: {evaluation.base_score.research_experience.score}/20")
        print(f"  竞赛加分: {evaluation.bonus_score.competition_bonus.score}/15")

    # 输出面试问题
    questions = final_state.get("questions")
    if questions:
        print(f"\n❓ 面试问题")

        print(f"\n基础题:")
        for i, q in enumerate(questions.basic_questions, 1):
            print(f"\n{i}. {q.question}")
            print(f"   关联项目: {q.related_project}")
            print(f"   考察重点: {q.focus_area}")

        print(f"\n进阶题:")
        for i, q in enumerate(questions.advanced_questions, 1):
            print(f"\n{i}. {q.question}")
            print(f"   关联项目: {q.related_project}")
            print(f"   考察重点: {q.focus_area}")
    else:
        print(f"\n未生成面试问题 (分数未达到阈值)")


if __name__ == "__main__":
    asyncio.run(main())
