import json
import time
import os
from agent.agent import solve


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def save_answers(answers, path):
    with open(path, "w") as f:
        json.dump(answers, f, indent=2)


def run(test_path, output_path):
    data = load_data(test_path)

    answers = []
    start_index = 0

    if os.path.exists(output_path):
        with open(output_path) as f:
            answers = json.load(f)
        start_index = len(answers)
        print(f"[solver] resuming from question {start_index + 1}")

    for i, item in enumerate(data[start_index:], start=start_index):
        question = item["input"]

        print(f"\n[solver] Question {i+1}/{len(data)}")

        try:
            answer = solve(question)
        except Exception as e:
            print(f"[solver] error on question {i+1}: {e}")
            answer = ""

        answers.append({"output": str(answer) if answer else ""})

        if (i + 1) % 10 == 0:
            save_answers(answers, output_path)
            print(f"[solver] saved checkpoint at {i+1}")

        time.sleep(0.1)

    save_answers(answers, output_path)
    print(f"\n[solver] done. saved {len(answers)} answers to {output_path}")


if __name__ == "__main__":
    run(
        test_path="cse_476_final_project_test_data.json",
        output_path="cse_476_final_project_answers.json"
    )