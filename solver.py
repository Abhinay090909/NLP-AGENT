import json
import time
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

    for i, item in enumerate(data):
        question = item["input"]
        domain = item.get("domain", None)

        print(f"\n[solver] Question {i+1}/{len(data)}")

        try:
            answer = solve(question, domain=domain)
        except Exception as e:
            print(f"[solver] error on question {i+1}: {e}")
            answer = ""

        answers.append({"output": answer})
        time.sleep(0.3)

    save_answers(answers, output_path)
    print(f"\n[solver] done. saved {len(answers)} answers to {output_path}")


if __name__ == "__main__":
    run(
        test_path="cse_476_final_project_test_data.json",
        output_path="cse_476_final_project_answers.json"
    )