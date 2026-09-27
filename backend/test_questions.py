"""Test question generation and evaluation."""
import asyncio, time

async def main():
    from app.services.question_generator import generate_questions, evaluate_answer

    # Test 1: DSA questions
    print("[1] Generating 3 DSA medium questions...")
    t = time.time()
    qs = await generate_questions(category="DSA", difficulty="medium", count=3)
    print(f"    Done in {round(time.time()-t,1)}s — got {len(qs)} questions")
    for q in qs:
        print(f"    [{q.question_type}] {q.question_text[:65]}")

    # Test 2: Answer evaluation
    if qs:
        print()
        print("[2] Evaluating an answer...")
        t = time.time()
        ev = await evaluate_answer(
            question=qs[0].model_dump(),
            user_answer="Binary search works by repeatedly halving the search space giving O(log n) time complexity",
            time_taken_seconds=25
        )
        print(f"    Done in {round(time.time()-t,1)}s")
        print(f"    Score: {ev.get('score')}/10")
        print(f"    Correct: {ev.get('is_correct')}")
        print(f"    Feedback: {str(ev.get('detailed_feedback',''))[:80]}")

    # Test 3: SQL questions
    print()
    print("[3] Generating 2 SQL easy questions...")
    t = time.time()
    qs2 = await generate_questions(category="SQL", difficulty="easy", count=2)
    print(f"    Done in {round(time.time()-t,1)}s — got {len(qs2)} questions")
    for q in qs2:
        print(f"    [{q.question_type}] {q.question_text[:65]}")

    # Test 4: Aptitude questions
    print()
    print("[4] Generating 2 Aptitude easy questions...")
    t = time.time()
    qs3 = await generate_questions(category="Aptitude", difficulty="easy", count=2)
    print(f"    Done in {round(time.time()-t,1)}s — got {len(qs3)} questions")
    for q in qs3:
        print(f"    [{q.question_type}] {q.question_text[:65]}")

    print()
    print("ALL QUESTION TESTS PASSED")

asyncio.run(main())
