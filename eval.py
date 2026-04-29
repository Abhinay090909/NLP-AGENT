import json
import random
import sys
from agent.agent import solve

def load_dev_data(path):
    with open(path) as f:
        return json.load(f)

def score(predicted, expected):
    predicted = str(predicted).strip().lower()
    expected = str(expected).strip().lower()
    if not predicted:
        return False
    if predicted == expected:
        return True
    if expected in predicted or predicted in expected:
        return True
    return False

def eval_agent(dev_path, domain_filter=None, n_per_domain=10, seed=42):
    data = load_dev_data(dev_path)
    random.seed(seed)

    by_domain = {}
    for item in data:
        d = item["domain"]
        if d not in by_domain:
            by_domain[d] = []
        by_domain[d].append(item)

    if domain_filter:
        if domain_filter not in by_domain:
            print(f"Domain '{domain_filter}' not found. Available: {list(by_domain.keys())}")
            return
        by_domain = {domain_filter: by_domain[domain_filter]}

    results = {}
    log_lines = []

    for domain, items in by_domain.items():
        sample = random.sample(items, min(n_per_domain, len(items)))
        correct = 0

        header = f"\n{'='*50}\nDomain: {domain} ({len(sample)} questions)\n{'='*50}"
        print(header)
        log_lines.append(header)

        for item in sample:
            question = item["input"]
            expected = item["output"]
            try:
                predicted = solve(question, domain=domain)
            except Exception as e:
                predicted = ""
                err = f"  ERROR: {e}"
                print(err)
                log_lines.append(err)

            ok = score(predicted, expected)
            correct += int(ok)

            lines = [
                f"  {'OK' if ok else 'FAIL'}",
                f"  Q: {question[:80]}...",
                f"  Expected : {str(expected)[:80]}",
                f"  Predicted: {str(predicted)[:80]}",
                ""
            ]
            for l in lines:
                print(l)
                log_lines.append(l)

        acc = correct / len(sample) * 100
        results[domain] = acc
        summary = f"  Accuracy: {correct}/{len(sample)} = {acc:.0f}%"
        print(summary)
        log_lines.append(summary)

    print(f"\n{'='*50}\nSUMMARY\n{'='*50}")
    log_lines.append(f"\n{'='*50}\nSUMMARY\n{'='*50}")
    for domain, acc in results.items():
        line = f"  {domain:<20} {acc:.0f}%"
        print(line)
        log_lines.append(line)
    overall = sum(results.values()) / len(results)
    ov = f"  {'overall':<20} {overall:.0f}%"
    print(ov)
    log_lines.append(ov)

    tag = domain_filter if domain_filter else "all"
    out_path = f"eval_{tag}.txt"
    with open(out_path, "w") as f:
        f.write("\n".join(log_lines))
    print(f"\n[eval] saved to {out_path}")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else None
    eval_agent("cse476_final_project_dev_data.json", domain_filter=domain, seed=777)