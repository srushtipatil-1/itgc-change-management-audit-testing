"""
First-pass analysis of the exceptions found by test_population.py.

Groups the exceptions so the auditor can see patterns before judging them:
  - which attributes failed together
  - which check names caused A4 failures (and how often)
  - how many A5 failures there are

Usage:
    python scripts\\analyse_exceptions.py
"""

import csv
from collections import Counter
from pathlib import Path

TESTING_DIR = Path("evidence") / "testing"


def main():
    for results_file in sorted(TESTING_DIR.glob("*_test_results.csv")):
        with results_file.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        repo = rows[0]["repository"]
        exceptions = [r for r in rows if r["result"] != "Pass"]
        print(f"\n===== {repo}: {len(exceptions)} exceptions out of {len(rows)} =====")

        patterns = Counter(
            "+".join(a for a in ("A2", "A3", "A4", "A5") if r[a] == "Fail") for r in exceptions
        )
        print("\nFailed attributes (pattern -> count):")
        for pattern, n in patterns.most_common():
            print(f"  {pattern:15} {n}")

        check_names = Counter()
        for r in exceptions:
            if r["A4"] == "Fail" and "failing checks:" in r["notes"]:
                part = r["notes"].split("failing checks:")[1].split(";")[0]
                for name in part.split(","):
                    check_names[name.strip()] += 1
        if check_names:
            print("\nChecks most often failing (A4):")
            for name, n in check_names.most_common(10):
                print(f"  {n:4}  {name}")

        only_a4 = [r for r in exceptions if patterns and
                   [a for a in ("A2", "A3", "A4", "A5") if r[a] == "Fail"] == ["A4"]]
        print(f"\nExceptions where ONLY A4 failed (approval was fine): {len(only_a4)}")

        print("\nExamples to inspect by hand (first 3 of each pattern):")
        shown = Counter()
        for r in exceptions:
            pattern = "+".join(a for a in ("A2", "A3", "A4", "A5") if r[a] == "Fail")
            if shown[pattern] < 3:
                shown[pattern] += 1
                print(f"  [{pattern}] PR {r['pr_number']} by {r['author']} -> {r['url']}")
                if r["notes"]:
                    print(f"        notes: {r['notes'][:150]}")


if __name__ == "__main__":
    main()
