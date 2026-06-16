"""
Test Resume Screening Agent - No Emoji Version
"""
import asyncio
from src import ResumeScreeningAgent


async def test_resume():
    # 1. Initialize Agent (using Alibaba Cloud Qwen API)
    agent = ResumeScreeningAgent(
        openai_api_key="sk-378c453bb0a04e6ab9a500452344d5a5",
        threshold=70.0
    )

    # 2. Specify your resume PDF path
    resume_path = "your_resume.pdf"

    print(f"Start analyzing: {resume_path}")
    print("-" * 50)

    try:
        # 3. Screen resume
        result = await agent.screen_resume(resume_path)

        # 4. Check for errors
        if result.get("error"):
            print(f"ERROR: {result['error']}")
            return

        # 5. Display evaluation results
        evaluation = result.get("evaluation")
        if not evaluation:
            print("ERROR: No evaluation result")
            return

        print(f"\n=== EVALUATION RESULTS ===")
        print(f"Candidate: {evaluation.candidate_name}")
        print(f"Total Score: {evaluation.final_score}/115")
        print(f"Passed: {'YES' if evaluation.passed_screening else 'NO'}")
        print("=" * 50)

        print(f"\n=== DETAILED SCORES ===")

        # Projects
        proj = evaluation.base_score.project_experience
        print(f"\n1. Projects: {proj.score}/{proj.max_score}")
        print(f"   Reason: {proj.reasoning}")

        # Internship
        intern = evaluation.base_score.internship_experience
        print(f"\n2. Internship: {intern.score}/{intern.max_score}")
        print(f"   Reason: {intern.reasoning}")

        # Tech Stack
        tech = evaluation.base_score.tech_stack
        print(f"\n3. Tech Stack: {tech.score}/{tech.max_score}")
        print(f"   Reason: {tech.reasoning}")

        # Research
        research = evaluation.base_score.research_experience
        print(f"\n4. Research: {research.score}/{research.max_score}")
        print(f"   Reason: {research.reasoning}")

        # Competition Bonus
        bonus = evaluation.bonus_score
        print(f"\n5. Competition Bonus: {bonus.bonus_points}/15")
        print(f"   Competitions: {', '.join(bonus.competitions) if bonus.competitions else 'None'}")
        print(f"   Reason: {bonus.reasoning}")

        # 6. Display interview questions (if any)
        if result.get("questions"):
            questions = result["questions"]
            print(f"\n\n=== INTERVIEW QUESTIONS ===")

            print(f"\nBasic Questions ({len(questions.basic_questions)}):")
            for i, q in enumerate(questions.basic_questions, 1):
                print(f"\n  {i}. {q.question}")
                print(f"     Related Project: {q.related_project}")
                print(f"     Focus Area: {q.focus_area}")

            print(f"\nAdvanced Questions ({len(questions.advanced_questions)}):")
            for i, q in enumerate(questions.advanced_questions, 1):
                print(f"\n  {i}. {q.question}")
                print(f"     Related Project: {q.related_project}")
                print(f"     Focus Area: {q.focus_area}")
        else:
            print(f"\n>>> Did not pass screening, no questions generated")

        print(f"\n{'='*50}")
        print("Analysis completed!")

    except Exception as e:
        print(f"ERROR occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_resume())
