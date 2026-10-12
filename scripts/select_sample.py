"""
Sample selection for control CM-01.

Selects a simple random sample of 25 changes per repository from the
population files. A fixed seed is used so anyone can re-run this script
and get exactly the same sample (re-performance).

Usage:
    python scripts\\select_sample.py
"""

import csv
import json
import random
from pathlib import Path

SEED = 20261012          # fixed seed, recorded in the sampling log
SAMPLE_SIZE = 25         # per repository, as set in the audit plan
POPULATION_DIR = Path("evidence") / "population"
SAMPLE_DIR = Path("evidence") / "sample"


def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    log = {"seed": SEED, "sample_size_per_repository": SAMPLE_SIZE, "repositories": []}

    for population_file in sorted(POPULATION_DIR.glob("*_population.csv")):
        with population_file.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        # Sort first so the result does not depend on file order
        rows.sort(key=lambda r: int(r["pr_number"]))
        rng = random.Random(SEED)
        sample = rng.sample(rows, SAMPLE_SIZE)
        sample.sort(key=lambda r: int(r["pr_number"]))

        for i, row in enumerate(sample, start=1):
            row["sample_id"] = f"S{i:02d}"

        repo = rows[0]["repository"]
        out = SAMPLE_DIR / population_file.name.replace("_population", "_sample")
        fields = ["sample_id"] + [k for k in rows[0].keys() if k != "sample_id"]
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(sample)

        bots = sum(1 for r in sample if r["author_type"] == "Bot")
        print(f"{repo}: selected {len(sample)} of {len(rows)} changes ({bots} bot-authored) -> {out}")
        log["repositories"].append(
            {
                "repository": repo,
                "population_size": len(rows),
                "sample_size": len(sample),
                "bot_authored_in_sample": bots,
                "selected_pr_numbers": [int(r["pr_number"]) for r in sample],
                "file": str(out).replace("\\", "/"),
            }
        )

    log_path = SAMPLE_DIR / "sampling-log.json"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Sampling log written to {log_path}")


if __name__ == "__main__":
    main()
