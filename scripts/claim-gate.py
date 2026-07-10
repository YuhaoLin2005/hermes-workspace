#!/usr/bin/env python3
"""claim-gate.py v2 — AI declares success criteria in YAML frontmatter, gate verifies.

Falsification gate: PASS means "claims not disproven", not "task complete."
File exists ≠ task done. But file NOT existing = task definitely NOT done.

YAML frontmatter:
  ---
  verify:
    - type: exists
      path: paper-trial-results.md
    - type: count
      path: paper-trial-results.md
      pattern: "PASS"
      min: 5
    - type: lines
      path: paper-trial-results.md
      min: 15
    - type: contains
      path: results.md
      text: "Fisher exact p"
    - type: modified
      path: paper-trial-results.md
    - type: unchanged
      path: production-config.json
  ---

Stop hook. Exit 2 on any FAIL (claims are commitments).
Exit 0 only when all claims pass or no claims exist.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try: import yaml
except ImportError: yaml = None

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-86131" / "memory"
SCRIPTS_DIR = Path.home() / ".claude" / "scripts"
SCAN_DIRS = [MEMORY_DIR, SCRIPTS_DIR]
SKIP_DIRS = {"growth-log", "archive", "decisions", "__pycache__", ".git"}
VERIFY_RE = re.compile(r'@verify:\s*(\w+)\s+(.+?)(?:\s*$)', re.MULTILINE)
CLAIM_RE = re.compile(r'<!--\s*claim-gate:(\w+):(.+?)\s*-->')


def resolve_path(path_str: str, origin_file: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute(): return p
    return (origin_file.parent / p).resolve()


def has_skip(file_path: Path) -> bool:
    try:
        head = "\n".join(file_path.read_text(encoding="utf-8", errors="ignore").split("\n")[:5])
        return "# claim-gate:skip" in head
    except OSError:
        return True


def should_scan(path: Path) -> bool:
    return not any(p in SKIP_DIRS for p in path.parts)


def parse_html_comments(file_path: Path) -> list[dict]:
    """Extract <!-- claim-gate:type:params --> HTML comments (linter-proof)."""
    try: content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError: return []
    checks = []
    for m in CLAIM_RE.finditer(content):
        ct = m.group(1).strip()
        params_str = m.group(2).strip()
        # Convert colon-delimited params to dict
        parts = params_str.split(":")
        if ct == "exists":
            params = parts[0] if parts else ""
        elif ct == "modified" or ct == "unchanged":
            params = parts[0] if parts else ""
        elif ct == "lines":
            params = {"path": parts[0], "min": int(parts[1])} if len(parts) >= 2 else params_str
        elif ct == "contains":
            params = {"path": parts[0], "text": ":".join(parts[1:])} if len(parts) >= 2 else params_str
        elif ct == "count":
            params = {"path": parts[0], "pattern": parts[1], "min": int(parts[2])} if len(parts) >= 3 else params_str
        else:
            params = params_str
        checks.append({"type": ct, "params": params, "file": str(file_path), "line": content[:m.start()].count("\n") + 1})
    return checks


def parse_frontmatter(file_path: Path) -> list[dict]:
    """Extract verify claims from YAML frontmatter (secondary format)."""
    try: content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError: return []
    if not content.startswith("---"): return []
    end = content.find("\n---", 3)
    if end == -1 or yaml is None: return []
    try: fm = yaml.safe_load(content[4:end])
    except yaml.YAMLError: return []
    if not isinstance(fm, dict): return []
    # Check top-level and metadata-nested verify
    vl = fm.get("verify") or fm.get("metadata", {}).get("verify")
    if not vl or not isinstance(vl, list):
        return []
    return [{"type": str(e.get("type", "")), "params": e, "file": str(file_path), "line": 1}
            for e in vl if isinstance(e, dict) and "type" in e]


def parse_legacy(file_path: Path) -> list[dict]:
    try: content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError: return []
    checks = []
    for m in VERIFY_RE.finditer(content):
        ct = m.group(1).strip()
        if ct == "hook": continue  # removed — hook-audit covers this
        checks.append({"type": ct, "params": m.group(2).strip(),
                       "file": str(file_path), "line": content[:m.start()].count("\n") + 1})
    return checks


def parse_checks(file_path: Path) -> list[dict]:
    c = parse_html_comments(file_path)
    if c: return c
    c = parse_frontmatter(file_path)
    return c if c else parse_legacy(file_path)


# --- Handlers ---

def _path(params, origin: Path) -> str:
    return params if isinstance(params, str) else params.get("path", "")


def check_exists(params, origin: Path) -> tuple[bool, str]:
    path = resolve_path(_path(params, origin), origin)
    ok = path.exists()
    return ok, f"{'PASS' if ok else 'FILE NOT FOUND'}: {path}"


def check_modified(params, origin: Path, plan_mtime: float) -> tuple[bool, str]:
    path = resolve_path(_path(params, origin), origin)
    if not path.exists(): return False, f"FILE NOT FOUND: {path}"
    try:
        ok = path.stat().st_mtime > plan_mtime
        return ok, f"{'PASS' if ok else 'NOT MODIFIED AFTER PLAN'}: {path}"
    except OSError: return False, f"UNREADABLE: {path}"


def check_unchanged(params, origin: Path, plan_mtime: float) -> tuple[bool, str]:
    path = resolve_path(_path(params, origin), origin)
    if not path.exists(): return False, f"FILE NOT FOUND: {path}"
    try:
        ok = path.stat().st_mtime <= plan_mtime
        return ok, f"{'PASS' if ok else 'WAS MODIFIED (regression risk)'}: {path}"
    except OSError: return False, f"UNREADABLE: {path}"


def check_lines(params, origin: Path) -> tuple[bool, str]:
    if isinstance(params, dict):
        ps, mn = params.get("path", ""), params.get("min", 0)
    else:
        parts = params.split(">=")
        if len(parts) != 2: return False, f"INVALID FORMAT: {params}"
        ps = parts[0].strip()
        try: mn = int(parts[1].strip())
        except ValueError: return False, f"INVALID NUMBER"
    path = resolve_path(ps, origin)
    if not path.exists(): return False, f"FILE NOT FOUND: {path}"
    try:
        actual = len(path.read_text(encoding="utf-8", errors="ignore").split("\n"))
        ok = actual >= mn
        return ok, f"{'PASS' if ok else f'TOO SHORT ({actual} < {mn})'}: {path}"
    except OSError: return False, f"UNREADABLE: {path}"


def check_contains(params, origin: Path) -> tuple[bool, str]:
    if isinstance(params, dict):
        ps, needle = params.get("path", ""), params.get("text", "")
    else:
        parts = params.split(" ", 1)
        if len(parts) != 2: return False, f"INVALID FORMAT: {params}"
        ps = parts[0].strip()
        needle = parts[1].strip()
        if len(needle) >= 2 and needle[0] == needle[-1] and needle[0] in ('"', "'"):
            needle = needle[1:-1]
    path = resolve_path(ps, origin)
    if not path.exists(): return False, f"FILE NOT FOUND: {path}"
    try:
        ok = needle in path.read_text(encoding="utf-8", errors="ignore")
        return ok, f"{'PASS' if ok else 'PATTERN NOT FOUND'}: {path}"
    except OSError: return False, f"UNREADABLE: {path}"


def check_count(params, origin: Path) -> tuple[bool, str]:
    if isinstance(params, dict):
        ps, pat, mn = params.get("path", ""), params.get("pattern", ""), params.get("min", 1)
    else:
        return False, f"YAML format required for count"

    path = resolve_path(ps, origin)
    if not path.exists(): return False, f"FILE NOT FOUND: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        actual = content.count(pat)
        ok = actual >= mn
        return ok, f"{'PASS' if ok else f'TOO FEW ({actual} < {mn})'}: found {actual}x in {path}"
    except OSError: return False, f"UNREADABLE: {path}"


HANDLERS = {
    "exists": lambda p, o, m: check_exists(p, o),
    "modified": lambda p, o, m: check_modified(p, o, m),
    "unchanged": lambda p, o, m: check_unchanged(p, o, m),
    "lines": lambda p, o, m: check_lines(p, o),
    "contains": lambda p, o, m: check_contains(p, o),
    "count": lambda p, o, m: check_count(p, o),
}


def run_check(check: dict, plan_mtime: float) -> dict:
    ctype, params, origin = check["type"], check["params"], Path(check["file"])
    handler = HANDLERS.get(ctype)
    if handler is None:
        return {**check, "ok": False, "msg": f"UNKNOWN TYPE: {ctype}"}
    try:
        ok, msg = handler(params, origin, plan_mtime)
    except Exception as e:
        ok, msg = False, f"ERROR: {e}"
    return {**check, "ok": ok, "msg": msg}


def main():
    today = datetime.now(timezone.utc).date()
    candidates = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists(): continue
        for f in scan_dir.rglob("*.md"):
            if not should_scan(f) or has_skip(f): continue
            try:
                if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).date() == today:
                    candidates.append(f)
            except OSError: continue

    if not candidates: return 0

    all_checks = []
    plan_mtimes = {}
    for f in candidates:
        try: plan_mtimes[str(f)] = f.stat().st_mtime
        except OSError: plan_mtimes[str(f)] = 0
        all_checks.extend(parse_checks(f))

    if not all_checks: return 0

    results = [run_check(c, plan_mtimes.get(c["file"], 0)) for c in all_checks]
    passed = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]

    lines = ["[claim-gate] falsification gate:"]
    lines.append(f"  {len(results)} claims from {len(candidates)} files")
    for r in passed:
        lines.append(f"  PASS [{r['type']}] {r['msg']} ({Path(r['file']).name})")
    for r in failed:
        lines.append(f"  FAIL [{r['type']}] {r['msg']} ({Path(r['file']).name})")

    if failed:
        lines.append(f"  -> {len(failed)}/{len(results)} FAILED.")
        lines.append("  -> Fulfill claim or update/remove verify declaration.")
        lines.append("  -> NB: PASS = 'not disproven', not 'task complete'.")
        print("\n".join(lines), file=sys.stderr)
        return 2

    lines.append(f"  -> All {len(passed)} passed (not disproven).")
    print("\n".join(lines), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
