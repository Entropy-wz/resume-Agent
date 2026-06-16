"""
Debug test script - skip text preview
"""
import asyncio
from src import ResumeScreeningAgent
from src.nodes.parser import parse_resume_node
from src.nodes.evaluator import evaluate_resume_node


async def test_resume_debug():
    resume_path = "your_resume.pdf"

    print(f"Start analyzing resume: {resume_path}")
    print("-" * 50)

    # Step 1: Test PDF parsing
    print("\n[Step 1] Testing PDF parsing...")
    state = {"resume_path": resume_path}
    state = parse_resume_node(state)

    if state.get("error"):
        print(f"ERROR - PDF parsing failed: {state['error']}")
        return

    resume_text = state.get("resume_text", "")
    print(f"SUCCESS - PDF parsed, text length: {len(resume_text)} chars")

    # Step 2: Test evaluation
    print("\n[Step 2] Testing evaluation with API...")
    state["threshold"] = 70.0

    try:
        state = await evaluate_resume_node(state)

        if state.get("error"):
            print(f"ERROR - Evaluation failed: {state['error']}")
            return

        evaluation = state.get("evaluation")
        if not evaluation:
            print(f"ERROR - Evaluation result is None")
            return

        print(f"\nSUCCESS - Evaluation completed!")
        print(f"=" * 50)
        print(f"Candidate: {evaluation.candidate_name}")
        print(f"Total Score: {evaluation.final_score}/115")
        print(f"Passed Screening: {evaluation.passed_screening}")
        print(f"=" * 50)

        # Detailed scores
        print(f"\nDetailed Breakdown:")
        proj = evaluation.base_score.project_experience
        print(f"\n1. Projects: {proj.score}/30")
        print(f"   Reason: {proj.reasoning}")

        intern = evaluation.base_score.internship_experience
        print(f"\n2. Internship: {intern.score}/25")
        print(f"   Reason: {intern.reasoning}")

        tech = evaluation.base_score.tech_stack
        print(f"\n3. Tech Stack: {tech.score}/25")
        print(f"   Reason: {tech.reasoning}")

        research = evaluation.base_score.research_experience
        print(f"\n4. Research: {research.score}/20")
        print(f"   Reason: {research.reasoning}")

        bonus = evaluation.bonus_score
        print(f"\n5. Competition Bonus: {bonus.bonus_points}/15")
        print(f"   Competitions: {', '.join(bonus.competitions) if bonus.competitions else 'None'}")
        print(f"   Reason: {bonus.reasoning}")

    except Exception as e:
        print(f"\nERROR during evaluation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Testing Resume Screening Agent")
    print("Using Alibaba Cloud Qwen API")
    print("")
    asyncio.run(test_resume_debug())
