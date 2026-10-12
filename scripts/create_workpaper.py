"""
Creates the manual testing workpaper (Excel) for control CM-01.

One sheet per repository, one row per sampled change, with dropdowns for
each attribute (A1-A5). The tester fills in the results by inspecting each
pull request on GitHub.

Usage:
    python scripts\\create_workpaper.py
"""

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

SAMPLE_DIR = Path("evidence") / "sample"
OUTPUT = Path("workpapers") / "CM-01_manual_testing_workpaper.xlsx"

COLUMNS = [
    ("Sample ID", 10),
    ("PR #", 9),
    ("Title", 45),
    ("Author", 18),
    ("Author type", 12),
    ("Merged by", 18),
    ("Merged at (UTC)", 21),
    ("Approver(s)", 22),
    ("A1 Via PR", 11),
    ("A2 Approved before merge", 14),
    ("A3 Approver not author", 14),
    ("A4 Checks passed", 12),
    ("A5 No change after approval", 14),
    ("Result", 16),
    ("Evidence / notes", 60),
    ("PR link", 50),
]
ATTRIBUTE_COLS = "IJKLM"     # columns holding A1-A5
RESULT_COL = "N"


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill("solid", fgColor="1F3864")
    header_font = Font(bold=True, color="FFFFFF")

    for sample_file in sorted(SAMPLE_DIR.glob("*_sample.csv")):
        with sample_file.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sheet_name = rows[0]["repository"].split("/")[1].capitalize()
        ws = wb.create_sheet(sheet_name)

        for col, (name, width) in enumerate(COLUMNS, start=1):
            cell = ws.cell(row=1, column=col, value=name)
            cell.fill, cell.font = header_fill, header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[cell.column_letter].width = width
        ws.row_dimensions[1].height = 45
        ws.freeze_panes = "C2"

        for r, row in enumerate(rows, start=2):
            values = [
                row["sample_id"], int(row["pr_number"]), row["title"], row["author"],
                row["author_type"], row["merged_by"], row["merged_at"], "",
                "Pass", "", "", "", "", "", "", row["url"],
            ]
            for col, value in enumerate(values, start=1):
                ws.cell(row=r, column=col, value=value).alignment = Alignment(
                    wrap_text=True, vertical="top"
                )
            ws.cell(row=r, column=16).hyperlink = row["url"]

        last = len(rows) + 1
        attr = DataValidation(type="list", formula1='"Pass,Fail,Not determinable"', allow_blank=True)
        result = DataValidation(
            type="list",
            formula1='"Pass,Control exception,Explained deviation,Data limitation"',
            allow_blank=True,
        )
        ws.add_data_validation(attr)
        ws.add_data_validation(result)
        for c in ATTRIBUTE_COLS:
            attr.add(f"{c}2:{c}{last}")
        result.add(f"{RESULT_COL}2:{RESULT_COL}{last}")

    legend = wb.create_sheet("Legend", 0)
    lines = [
        ("CM-01 Manual testing workpaper", True),
        ("Control: every change merged to the default branch goes through a pull request, "
         "is approved by someone other than the author, passes automated checks, "
         "and is not changed after approval.", False),
        ("", False),
        ("A1  Change entered the default branch through a pull request", False),
        ("A2  At least one approving review before merge", False),
        ("A3  Approver is not the author (segregation of duties)", False),
        ("A4  Automated checks passed on the merged commit", False),
        ("A5  No commits pushed after the approval", False),
        ("", False),
        ("Attribute values: Pass / Fail / Not determinable", False),
        ("Result values: Pass / Control exception / Explained deviation / Data limitation", False),
        ("Bot-authored changes require at least one human approval (decision D-03).", False),
        ("Sample selected with seed 20261012 (see evidence/sample/sampling-log.json).", False),
    ]
    for i, (text, bold) in enumerate(lines, start=1):
        legend.cell(row=i, column=1, value=text).font = Font(bold=bold, size=14 if bold else 11)
    legend.column_dimensions["A"].width = 110

    wb.save(OUTPUT)
    print(f"Workpaper created: {OUTPUT}")


if __name__ == "__main__":
    main()
