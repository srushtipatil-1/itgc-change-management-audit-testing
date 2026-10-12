"""
Population extraction for control CM-01 (ITGC change management).

Downloads every pull request merged into each repository during the audit
period and saves it as evidence. It also performs a completeness check:
the number of records saved must match the count GitHub reports.

Usage (Command Prompt, with the virtual environment active):
    set GITHUB_TOKEN=your_token_here
    python scripts\\extract_population.py
"""

import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---- Audit parameters (must match docs/audit-plan.md and docs/scoping-memo.md) ----
REPOSITORIES = ["prowler-cloud/prowler", "aquasecurity/trivy"]
PERIOD_START = "2026-07-01"
PERIOD_END = "2026-09-30"
OUTPUT_DIR = Path("evidence") / "population"

API = "https://api.github.com"
FIELDS = [
    "repository",
    "pr_number",
    "title",
    "author",
    "author_type",
    "created_at",
    "merged_at",
    "merged_by",
    "base_branch",
    "head_sha",
    "merge_commit_sha",
    "url",
]


def get_session() -> requests.Session:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("ERROR: GITHUB_TOKEN is not set. Run: set GITHUB_TOKEN=your_token")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    return session


def get_json(session: requests.Session, url: str, params=None):
    """GET with simple handling of GitHub rate limits."""
    for attempt in range(5):
        response = session.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        if response.status_code in (403, 429):
            reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 10)
            print(f"  Rate limit reached, waiting {wait} seconds...")
            time.sleep(wait)
            continue
        response.raise_for_status()
    sys.exit(f"ERROR: could not fetch {url} after several attempts")


def search_merged_prs(session, repo):
    """Return (reported_total, list of PR numbers) merged in the audit period."""
    query = f"repo:{repo} is:pr is:merged merged:{PERIOD_START}..{PERIOD_END}"
    numbers, page, reported_total = [], 1, None
    while True:
        data = get_json(
            session,
            f"{API}/search/issues",
            {"q": query, "per_page": 100, "page": page, "sort": "created", "order": "asc"},
        )
        if reported_total is None:
            reported_total = data["total_count"]
            if reported_total > 1000:
                sys.exit(
                    f"ERROR: {repo} has {reported_total} results; GitHub search returns at most 1000. "
                    "Split the period into smaller date ranges."
                )
        items = data.get("items", [])
        numbers.extend(item["number"] for item in items)
        if len(items) < 100:
            break
        page += 1
        time.sleep(2)  # search API allows 30 requests per minute
    return reported_total, numbers


def pr_record(session, repo, number):
    pr = get_json(session, f"{API}/repos/{repo}/pulls/{number}")
    return {
        "repository": repo,
        "pr_number": pr["number"],
        "title": pr["title"],
        "author": pr["user"]["login"],
        "author_type": pr["user"]["type"],  # "User" or "Bot"
        "created_at": pr["created_at"],
        "merged_at": pr["merged_at"],
        "merged_by": (pr.get("merged_by") or {}).get("login", ""),
        "base_branch": pr["base"]["ref"],
        "head_sha": pr["head"]["sha"],
        "merge_commit_sha": pr["merge_commit_sha"],
        "url": pr["html_url"],
    }


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    session = get_session()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = {
        "extracted_at_utc": extracted_at,
        "period": f"{PERIOD_START} to {PERIOD_END}",
        "repositories": [],
    }

    for repo in REPOSITORIES:
        print(f"\n== {repo} ==")
        reported_total, numbers = search_merged_prs(session, repo)
        print(f"GitHub reports {reported_total} merged PRs; {len(numbers)} returned by search.")

        records = []
        for i, number in enumerate(numbers, start=1):
            records.append(pr_record(session, repo, number))
            if i % 50 == 0 or i == len(numbers):
                print(f"  fetched {i}/{len(numbers)}")

        safe_name = repo.replace("/", "__")
        csv_path = OUTPUT_DIR / f"{safe_name}_population.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)

        # Completeness and accuracy checks on the population
        unique = len({r["pr_number"] for r in records})
        outside_period = [
            r["pr_number"]
            for r in records
            if not (PERIOD_START <= (r["merged_at"] or "")[:10] <= PERIOD_END)
        ]
        bots = sum(1 for r in records if r["author_type"] == "Bot")
        checks = {
            "reported_total_matches_records": reported_total == len(records),
            "no_duplicate_prs": unique == len(records),
            "all_merged_within_period": not outside_period,
        }
        print(f"Saved {len(records)} records to {csv_path}")
        print(f"Completeness checks: {checks}")
        if outside_period:
            print(f"  PRs merged outside the period: {outside_period}")

        log["repositories"].append(
            {
                "repository": repo,
                "reported_total": reported_total,
                "records_saved": len(records),
                "bot_authored": bots,
                "checks": checks,
                "file": str(csv_path).replace("\\", "/"),
                "sha256": sha256_of(csv_path),
            }
        )

    log_path = OUTPUT_DIR / "extraction-log.json"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"\nExtraction log written to {log_path}")


if __name__ == "__main__":
    main()
