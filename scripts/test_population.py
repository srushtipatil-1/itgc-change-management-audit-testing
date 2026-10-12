"""
Automated full-population test of control CM-01.

For every merged pull request in the population files, collects the review
and check-run evidence from the GitHub API and evaluates attributes A2-A5:

  A2  At least one approving review submitted before the merge
  A3  At least one of those approvals is by a human other than the author
      (bots do not count as approvers - decision D-03)
  A4  No failing check runs / statuses on the final commit of the PR
  A5  A valid approval was given on the final commit (head SHA), so no
      code was added after approval

A1 (change came through a pull request) is Pass for every record because the
population consists of merged pull requests; direct pushes are tested separately.

Usage (Command Prompt, virtual environment active):
    set GITHUB_TOKEN=your_token_here
    python scripts\\test_population.py
"""

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

POPULATION_DIR = Path("evidence") / "population"
SAMPLE_DIR = Path("evidence") / "sample"
OUTPUT_DIR = Path("evidence") / "testing"
API = "https://api.github.com"

FAILING = {"failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"}

RESULT_FIELDS = [
    "repository", "pr_number", "title", "author", "author_type", "merged_by",
    "merged_at", "head_sha", "approvers_before_merge", "valid_approvers",
    "approved_head_sha", "check_runs_total", "check_runs_failing",
    "A1", "A2", "A3", "A4", "A5", "result", "notes", "url",
]


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


def get_all(session, url, key=None):
    """Follow pagination (100 per page)."""
    items, page = [], 1
    while True:
        data = get_json(session, url, {"per_page": 100, "page": page})
        if data is None:
            return items
        batch = data.get(key, []) if key else data
        items.extend(batch)
        if len(batch) < 100:
            return items
        page += 1


def evaluate(row, reviews, check_runs, status):
    """Pure function: decide A1-A5 from the evidence. Kept separate so it can be unit-tested."""
    author, merged_at, head = row["author"], row["merged_at"], row["head_sha"]
    approvals = [
        rv for rv in reviews
        if rv.get("state") == "APPROVED" and (rv.get("submitted_at") or "") <= merged_at
    ]
    valid = [
        rv for rv in approvals
        if rv["user"] and rv["user"]["login"] != author and rv["user"].get("type") != "Bot"
    ]
    notes = []

    a2 = "Pass" if approvals else "Fail"
    a3 = "Pass" if valid else "Fail"
    if not approvals:
        notes.append("no approval before merge")
    elif not valid:
        notes.append("only approvals were by the author or a bot")

    failing = [c["name"] for c in check_runs if c.get("conclusion") in FAILING]
    status_state = (status or {}).get("state")
    status_count = len((status or {}).get("statuses", []))
    if failing or (status_count and status_state in ("failure", "error")):
        a4 = "Fail"
        if failing:
            notes.append("failing checks: " + ", ".join(sorted(set(failing))[:5]))
        else:
            notes.append(f"commit status {status_state}")
    elif check_runs or status_count:
        a4 = "Pass"
    else:
        a4 = "Not determinable"
        notes.append("no checks recorded on final commit")

    approved_head = any(rv.get("commit_id") == head for rv in valid)
    if not valid:
        a5 = "Fail"
    elif approved_head:
        a5 = "Pass"
    else:
        a5 = "Fail"
        notes.append("code changed after the last valid approval")

    attrs = ["Pass", a2, a3, a4, a5]
    if "Fail" in attrs:
        result = "Exception - to analyse"
    elif "Not determinable" in attrs:
        result = "Not determinable"
    else:
        result = "Pass"

    return {
        "approvers_before_merge": ";".join(sorted({rv["user"]["login"] for rv in approvals if rv["user"]})),
        "valid_approvers": ";".join(sorted({rv["user"]["login"] for rv in valid})),
        "approved_head_sha": "yes" if approved_head else "no",
        "check_runs_total": len(check_runs),
        "check_runs_failing": len(failing),
        "A1": "Pass", "A2": a2, "A3": a3, "A4": a4, "A5": a5,
        "result": result,
        "notes": "; ".join(notes),
    }


def main():
    session = get_session()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"tested_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "repositories": []}

    for pop_file in sorted(POPULATION_DIR.glob("*_population.csv")):
        with pop_file.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        repo = rows[0]["repository"]
        print(f"\n== {repo}: testing {len(rows)} changes ==")

        results = []
        for i, row in enumerate(rows, start=1):
            n, head = row["pr_number"], row["head_sha"]
            reviews = get_all(session, f"{API}/repos/{repo}/pulls/{n}/reviews")
            runs = get_all(session, f"{API}/repos/{repo}/commits/{head}/check-runs", key="check_runs")
            status = get_json(session, f"{API}/repos/{repo}/commits/{head}/status")
            out = {k: row[k] for k in ("repository", "pr_number", "title", "author", "author_type",
                                       "merged_by", "merged_at", "head_sha", "url")}
            out.update(evaluate(row, reviews, runs, status))
            results.append(out)
            if i % 25 == 0 or i == len(rows):
                print(f"  tested {i}/{len(rows)}")

        out_file = OUTPUT_DIR / pop_file.name.replace("_population", "_test_results")
        with out_file.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
            w.writeheader()
            w.writerows(results)

        def count(field, value, subset=results):
            return sum(1 for r in subset if r[field] == value)

        humans = [r for r in results if r["author_type"] != "Bot"]
        bots = [r for r in results if r["author_type"] == "Bot"]
        repo_summary = {
            "repository": repo,
            "tested": len(results),
            "pass": count("result", "Pass"),
            "exceptions_to_analyse": count("result", "Exception - to analyse"),
            "not_determinable": count("result", "Not determinable"),
            "attribute_failures": {a: count(a, "Fail") for a in ("A2", "A3", "A4", "A5")},
            "human_authored": {"tested": len(humans), "pass": count("result", "Pass", humans)},
            "bot_authored": {"tested": len(bots), "pass": count("result", "Pass", bots)},
            "file": str(out_file).replace("\\", "/"),
        }
        summary["repositories"].append(repo_summary)
        print(json.dumps(repo_summary, indent=2))

        # Show the results for the first 5 sampled changes, for manual re-performance
        sample_file = SAMPLE_DIR / pop_file.name.replace("_population", "_sample")
        if sample_file.exists():
            with sample_file.open(encoding="utf-8") as f:
                sample = list(csv.DictReader(f))[:5]
            by_pr = {r["pr_number"]: r for r in results}
            print("  Re-performance check - script results for S01-S05:")
            for s in sample:
                r = by_pr[s["pr_number"]]
                print(f"   {s['sample_id']} PR {r['pr_number']}: A2={r['A2']} A3={r['A3']} "
                      f"A4={r['A4']} A5={r['A5']} -> {r['result']}  approvers={r['valid_approvers']}")

    (OUTPUT_DIR / "test-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary written to {OUTPUT_DIR / 'test-summary.json'}")


if __name__ == "__main__":
    main()
