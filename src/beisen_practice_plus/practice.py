from __future__ import annotations

import random

from .models import Question


def run_practice(questions: list[Question], category: str | None = None, count: int = 10) -> int:
    pool = [q for q in questions if (category is None or q.category == category) and q.answer in q.options]
    if not pool:
        print("No valid questions available for this category.")
        return 1

    chosen = random.sample(pool, min(count, len(pool)))
    correct = 0
    for index, q in enumerate(chosen, 1):
        print(f"\n[{index}/{len(chosen)}] {q.id} · {q.tag}")
        print(q.stem)
        if q.images:
            print("Images:", ", ".join(q.images))
        for key in "ABCD":
            print(f"  {key}. {q.options.get(key, '')}")

        while True:
            answer = input("Your answer (A-D, q to quit): ").strip().upper()
            if answer == "Q":
                print(f"Score: {correct}/{index-1}")
                return 0
            if answer in "ABCD":
                break

        if answer == q.answer:
            correct += 1
            print("Correct.")
        else:
            print(f"Incorrect. Correct answer: {q.answer}")
        if q.analysis:
            print("Analysis:", q.analysis)

    print(f"\nFinished. Score: {correct}/{len(chosen)}")
    return 0
