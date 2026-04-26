import json
import time
import os
import sys
from agent.agent import solve


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def save_answers(answers, path):
    with open(path, "w") as f:
        json.dump(answers, f, indent=2)


def run(test_path, output_path, start=0, end=None):
    data = load_data(test_path)
    if end is None:
        end = len(data)
    data = data[start:end]

    answers = []
    resume_index = 0

    if os.path.exists(output_path):
        with open(output_path) as f:
            answers = json.load(f)
        resume_index = len(answers)
        print(f"[solver] resuming from question {start + resume_index + 1}")

    for i, item in enumerate(data[resume_index:], start=resume_index):
        question = item["input"]
        print(f"\n[solver] Question {start + i + 1}/{6208}")
        try:
            answer = solve(question)
        except Exception as e:
            print(f"[solver] error: {e}")
            answer = ""
        answers.append({"output": str(answer) if answer else ""})
        if (i + 1) % 10 == 0:
            save_answers(answers, output_path)
            print(f"[solver] checkpoint saved at {start + i + 1}")
        time.sleep(0.05)

    save_answers(answers, output_path)
    print(f"\n[solver] done. saved {len(answers)} answers to {output_path}")


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 6208
    run(
        test_path="cse_476_final_project_test_data.json",
        output_path=f"answers_{start}_{end}.json",
        start=start,
        end=end
    )