"""
Refines attribute A4 (automated checks passed) and adds branch scope.

Why: the first test counted ANY failing check as an A4 failure. Many failing
checks are informational (coverage reports, changelog reminders, title-format
checks) and do not test whether the software works. This script separates
blocking checks from informational ones (decision D-07) and re-evaluates A4.

It also labels each change as default-branch or release-branch (decision D-05).

Only changes that failed A4 are re-queried, so this is much faster than the
full test.

Usage (Command Prompt, virtual environment active):
    set GITHUB_TOKEN=your_token_here
    python scripts\\refine_a4.py
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

TESTING_DIR = Path("evidence") / "testing"
POPULATION_DIR = Path("evidence") / "population"
API = "https://api.github.com"

# Decision D-07: checks treated as informational (they do not test functionality or security)
INFORMATIONAL_PATTERNS = [
    r"^codecov",                 # test-coverage percentage reports
    r"changelog",                # changelog reminders
    r"conventional-commit",      # commit/PR title format
    r"validate pr title",        # PR title format
    r"semantic",                 # title format (semantic PR)
    r"label",                    # labelling bots
]
# Conclusions counted as a failure. "cancelled" and "skipped" are not counted:
# runs are usually cancelled when a newer run replaces them.
FAILED = {"failure", "timed_out", "action_required", "startup_failure"}


def is_informational(name: str) -> bool:
    return any(re.search(p, name.lower()) for p in INFORMATIONAL_PATTERNS)


def get_session():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("ERROR: GITHUB_TOKEN is not set. Run: set GITHUB_TOKEN=your_token")
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return s


def get_json(session, url, params=None):
    for _ in range(5):
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (403, 429):
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 10)
            print(f"  Rate limit reached, waiting {wait} seconds...")
            time.sleep(wait)
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
    sys.exit(f"ERROR: could not fetch {url}")


def failing_checks(session, repo, sha):
    """Return the names of failing check runs and commit statuses on a commit."""
    names, page = [], 1
    while True:
        data = get_json(session, f"{API}/repos/{repo}/commits/{sha}/check-runs",
                        {"per_page": 100, "page": page, "filter": "latest"}) or {}
        runs = data.get("check_runs", [])
        names += [c["name"] for c in runs if c.get("conclusion") in FAILED]
        if len(runs) < 100:
            break
        page += 1
    status = get_json(session, f"{API}/repos/{repo}/commits/{sha}/status") or {}
    names += [s["context"] for s in status.get("statuses", []) if s.get("state") in ("failure", "error")]
    return sorted(set(names))


def classify(row, names):
    """Pure function: re-evaluate A4 and the overall result. Unit-testable."""
    blocking = [n for n in names if not is_informational(n)]
    informational = [n for n in names if is_informational(n)]
    a4 = "Fail" if blocking else "Pass"
    attrs = [row["A2"], row["A3"], a4, row["A5"]]
    result = "Exception" if "Fail" in attrs else ("Not determinable" if "Not determinable" in attrs else "Pass")
    return {
        "A4_refined": a4,
        "blocking_failures": ", ".join(blocking),
        "informational_failures": ", ".join(informational),
        "result_refined": result,
    }


def main():
    session = get_session()
    summary = {"decision": "D-07 informational patterns: " + "; ".join(INFORMATIONAL_PATTERNS),
               "repositories": []}

    for results_file in sorted(TESTING_DIR.glob("*_test_results.csv")):
        with results_file.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        repo = rows[0]["repository"]
        default_branch = get_json(session, f"{API}/repos/{repo}")["default_branch"]

        pop_file = POPULATION_DIR / results_file.name.replace("_test_results", "_population")
        with pop_file.open(encoding="utf-8") as f:
            base = {r["pr_number"]: r["base_branch"] for r in csv.DictReader(f)}

        to_check = [r for r in rows if r["A4"] == "Fail"]
        print(f"\n== {repo} (default branch: {default_branch}): re-checking {len(to_check)} A4 failures ==")

        done = 0
        for row in rows:
            row["base_branch"] = base.get(row["pr_number"], "")
            row["branch_type"] = "default" if row["base_branch"] == default_branch else "release/other"
            names = []
            if row["A4"] == "Fail":
                names = failing_checks(session, repo, row["head_sha"])
                done += 1
                if done % 25 == 0 or done == len(to_check):
                    print(f"  re-checked {done}/{len(to_check)}")
            row.update(classify(row, names))

        out = TESTING_DIR / results_file.name.replace("_test_results", "_test_results_refined")
        fields = list(rows[0].keys())
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

        def tally(subset):
            return {
                "tested": len(subset),
                "pass": sum(r["result_refined"] == "Pass" for r in subset),
                "exceptions": sum(r["result_refined"] == "Exception" for r in subset),
                "attribute_failures": {
                    "A2_no_approval": sum(r["A2"] == "Fail" for r in subset),
                    "A3_no_independent_human_approval": sum(r["A3"] == "Fail" for r in subset),
                    "A4_blocking_check_failed": sum(r["A4_refined"] == "Fail" for r in subset),
                    "A5_changed_after_approval": sum(r["A5"] == "Fail" for r in subset),
                },
            }

        repo_summary = {
            "repository": repo,
            "default_branch": default_branch,
            "all_changes": tally(rows),
            "default_branch_changes": tally([r for r in rows if r["branch_type"] == "default"]),
            "release_or_other_branch_changes": tally([r for r in rows if r["branch_type"] != "default"]),
            "human_authored": tally([r for r in rows if r["author_type"] != "Bot"]),
            "bot_authored": tally([r for r in rows if r["author_type"] == "Bot"]),
            "a4_moved_to_pass_after_refinement": sum(
                r["A4"] == "Fail" and r["A4_refined"] == "Pass" for r in rows),
            "file": str(out).replace("\\", "/"),
        }
        summary["repositories"].append(repo_summary)
        print(json.dumps(repo_summary, indent=2))

    (TESTING_DIR / "refined-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nRefined summary written to {TESTING_DIR / 'refined-summary.json'}")


if __name__ == "__main__":
    main()
