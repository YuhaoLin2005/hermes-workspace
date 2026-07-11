#!/usr/bin/env python3
"""neural-gate.py — Constraint fidelity checker.

Layer above file-system gates. File checks ask: "did info arrive at the door?"
This gate asks: "did info travel through the house?" — did constraints actually
change output behavior, not just exist on disk?

Architecture: Prose Barrier (AI architect + philosopher, 2026-07-10).
Agent generates self-narrative and output through same channel. File gates
verify INPUT to channel. This gate verifies OUTPUT — closing the causal loop.

v1: behavioral proxy — constraint keyphrase echo detection in outputs.

Stop hook. Exit 0 always.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-86131" / "memory"
BODY_PATH = Path.home() / ".claude" / "BODY.md"

# (constraint theme, regex to detect echo in outputs)
CONSTRAINTS = [
    ("自动执行", r"自动|不等批准|默认执行|直接做|不先问"),
    ("最低成本验证", r"验证|验证了|确认|核实|checked|verified|confirmed"),
    ("自审", r"自审|Completeness|Consistency|Groundedness|Honesty"),
    ("双池审查", r"双池|固定池|随机池|审查|review|audit"),
    ("Read-after-Write", r"重读|读回|read.*back|re-read|读.*刚写"),
    ("事实核验", r"事实核验|fact.check|机械验证|API.*验证"),
    ("执行铁律", r"立即执行|不拖延|写脚本.*跑|创建.*执行"),
    ("降级链", r"降级|fallback|degrad|仅查询"),
]


def extract_active_constraints() -> set[str]:
    if not BODY_PATH.exists(): return set()
    try: text = BODY_PATH.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError: return set()
    return {t for t, _ in CONSTRAINTS if t.lower() in text}


def scan_outputs() -> tuple[dict, int]:
    today = datetime.now(timezone.utc).date()
    counts = {t: 0 for t, _ in CONSTRAINTS}
    n = 0
    for f in MEMORY_DIR.rglob("*"):
        if f.suffix not in {".md", ".py"}: continue
        if "growth-log" in str(f) or f.name == "BODY.md": continue
        try:
            if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).date() != today: continue
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        n += 1
        for theme, pat in CONSTRAINTS:
            if re.search(pat, content, re.IGNORECASE):
                counts[theme] += 1
    return counts, n


def main():
    active_themes = extract_active_constraints()
    if not active_themes: return 0
    counts, n = scan_outputs()
    if n == 0: return 0

    silent = []
    echoing = []
    for theme, _ in CONSTRAINTS:
        if theme not in active_themes: continue
        c = counts.get(theme, 0)
        (echoing if c > 0 else silent).append((theme, c))

    if not silent: return 0

    lines = ["[neural-gate] Constraint fidelity:"]
    lines.append(f"  Scanned {n} files. {len(echoing)}/{len(echoing)+len(silent)} constraints echoing.")
    for t, c in echoing: lines.append(f"    ECHO  [{t}] in {c} files")
    for t, _ in silent: lines.append(f"    SILENT [{t}] — in BODY.md, no echo in outputs")
    lines.append("  -> Prose Barrier: rules in context ≠ rules shaping output.")
    lines.append("  -> May indicate compaction-induced constraint decay.")
    print("\n".join(lines), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
