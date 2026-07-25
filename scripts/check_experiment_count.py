#!/usr/bin/env python3
"""check_experiment_count.py — Mechanical gate for experiment count consistency.

Scans PAPER.md overview table, README.md claim, and dashboard.md claim.
Exit 0 if all counts match. Exit 2 if any discrepancy found.

Importers: Called standalone via `python scripts/check_experiment_count.py`.
Not imported by any other file. No API calls. No data schemas.
Reads: PAPER.md, README.md, .claude/knowledge/strategy/dashboard.md (markdown files).
Writes: stdout only.

User verbatim: "写一个 check_experiment_count.py — 扫描 PAPER.md、README.md、dashboard.md、DEV.to draft，对比实验数，不一致就 exit 2。机械门管文档一致性。"
"""

import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def count_paper_overview() -> int:
    """Count experiment rows in PAPER.md Experiment Overview table."""
    paper = REPO / "PAPER.md"
    if not paper.exists():
        print(f"ERROR: {paper} not found")
        return -1
    text = paper.read_text(encoding="utf-8")
    in_table = False
    count = 0
    for line in text.split("\n"):
        if line.startswith("## Experiment Overview"):
            in_table = True
            continue
        if in_table:
            if line.startswith("##") or line.startswith("---"):
                break
            if line.startswith("|") and not re.match(r"^\|\s*[-:]+\s*\|", line):
                if "Experiment" in line and "Design" in line:
                    continue
                count += 1
    return count

def count_readme_claim() -> int:
    """Extract experiment count from README.md."""
    readme = REPO / "README.md"
    if not readme.exists():
        print(f"ERROR: {readme} not found")
        return -1
    text = readme.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+experiments?\s+completed", text)
    return int(m.group(1)) if m else -1

def count_dashboard_claim() -> int:
    """Extract experiments.completed from dashboard.md."""
    dashboard = REPO / ".claude" / "knowledge" / "strategy" / "dashboard.md"
    if not dashboard.exists():
        print(f"ERROR: {dashboard} not found")
        return -1
    text = dashboard.read_text(encoding="utf-8")
    m = re.search(r"completed:\s*(\d+)", text)
    return int(m.group(1)) if m else -1

def main():
    fix_hint = "--fix-hint" in sys.argv
    paper_count = count_paper_overview()
    readme_count = count_readme_claim()
    dashboard_count = count_dashboard_claim()

    results = {
        "PAPER.md Experiment Overview": paper_count,
        "README.md claim": readme_count,
        "dashboard.md experiments.completed": dashboard_count,
    }

    print("=" * 60)
    print("Experiment Count Consistency Check")
    print("=" * 60)
    for source, count in results.items():
        status = "OK" if count > 0 else "MISSING"
        print(f"  {source}: {count} ({status})")

    counts = [c for c in results.values() if c > 0]
    if len(set(counts)) == 1:
        print(f"\n[PASS] All sources agree on {counts[0]} experiments.")
        return 0
    else:
        print(f"\n[FAIL] Counts disagree! {results}")
        if fix_hint:
            print()
            print("Fix hints:")
            if paper_count != readme_count:
                print(f"  PAPER.md overview has {paper_count} rows, README claims {readme_count}.")
                print(f"  → Add {readme_count - paper_count} missing experiments to PAPER.md overview, OR")
                print(f"  → Update README.md claim to {paper_count}.")
            if readme_count != dashboard_count:
                print(f"  README claims {readme_count}, dashboard says {dashboard_count}.")
                print(f"  → Sync dashboard.md experiments.completed to match.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
