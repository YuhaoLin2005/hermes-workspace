#!/usr/bin/env python3
"""Log a self-model regeneration event and clean up the .self-model-stale flag.

Called by AI after regenerating self-model.md per BODY.md §奇异环再生.
This is the MECHANICAL step that replaces the prose-based "delete flag" instruction.

Usage:
  python log-regeneration.py --old v1 --new v2 --sources "2026-07-02,2026-07-01" --trigger flag

The script:
  1. VALIDATES the new self-model.md (structure + content checks)
  2. If validation passes: deletes .self-model-stale flag + writes .last-regeneration
  3. If validation fails: exits 3, flag preserved for retry next session
  4. Appends a structured JSONL record to .self-model-regeneration.jsonl

Together with quality-gate.py (writes flag) and health-check.py (SessionStart detection),
this forms the complete mechanical lifecycle of the strange-loop flag.

v2.1 (2026-07-03): Added pre-delete validation. Validate-first, delete-after.
  Exit 3 = validation failed, flag preserved. Fixes 2/3 regeneration failure rate.
"""

import os, sys, json, argparse, re
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
MEMORY = os.path.join(HOME, ".claude", "projects", "C--Users-86131", "memory")
REGENERATION_LOG = os.path.join(MEMORY, ".self-model-regeneration.jsonl")
STALE_FLAG = os.path.join(MEMORY, ".self-model-stale")
SELF_MODEL = os.path.join(MEMORY, "self-model.md")
LAST_REGENERATION = os.path.join(MEMORY, ".last-regeneration")

# ── Validation thresholds ──────────────────────────────────────
MIN_LINES = 20          # self-model must have at least 20 lines
MIN_CAPABILITIES = 3    # at least 3 capability entries (## 我擅长什么 section)
# ──────────────────────────────────────────────────────────────────


def validate_self_model():
    """Validate regenerated self-model.md structure and content.
    Returns (ok: bool, failures: list[str])."""
    failures = []

    if not os.path.exists(SELF_MODEL):
        failures.append("self-model.md not found after regeneration")
        return False, failures

    try:
        content = open(SELF_MODEL, "r", encoding="utf-8").read()
    except Exception as e:
        failures.append(f"Cannot read self-model.md: {e}")
        return False, failures

    lines = content.split("\n")

    # Check 1: Minimum line count
    if len(lines) < MIN_LINES:
        failures.append(f"Too few lines: {len(lines)} < {MIN_LINES}")

    # Check 2: name field in YAML frontmatter (non-empty)
    name_match = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if not name_match or not name_match.group(1).strip():
        failures.append("name: field empty or missing in frontmatter")
    elif name_match.group(1).strip() == "":
        failures.append("name: field is empty string")

    # Check 3: Required sections exist
    required_sections = ["## 我是谁", "## 我擅长什么"]
    for section in required_sections:
        if section not in content:
            failures.append(f"Missing required section: {section}")

    # Check 4: Capability entries (bullet points under ## 我擅长什么)
    cap_section_match = re.search(r'## 我擅长什么\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if cap_section_match:
        cap_lines = [l for l in cap_section_match.group(1).split("\n")
                     if l.strip().startswith("-")]
        if len(cap_lines) < MIN_CAPABILITIES:
            failures.append(f"Only {len(cap_lines)} capability entries (min {MIN_CAPABILITIES})")
    else:
        failures.append("Cannot parse ## 我擅长什么 section")

    # Check 5: Has a version marker
    if "v0." not in content and "version" not in content.lower():
        failures.append("No version marker found")

    return len(failures) == 0, failures


def compute_drift(old_ver, new_ver):
    """Compute drift magnitude between old and new self-model. Uses difflib (stdlib)."""
    from difflib import unified_diff
    old_path = os.path.join(MEMORY, "archive", f"self-model.{old_ver}.md")
    # Try v-prefix variant
    if not os.path.exists(old_path):
        old_path = os.path.join(MEMORY, "archive", f"self-model.v{old_ver.replace('v','')}.md")
    if not os.path.exists(old_path):
        return {"error": "old version not found", "drift_magnitude": -1}
    try:
        old_lines = open(old_path, 'r', encoding='utf-8').readlines()
        new_lines = open(SELF_MODEL, 'r', encoding='utf-8').readlines()
        diff = list(unified_diff(old_lines, new_lines))
        added = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
        removed = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
        mag = (added + removed) / max(len(old_lines), 1)
        # Count capability changes
        caps_old = sum(1 for l in old_lines if l.strip().startswith('- **') and 'L' in l)
        caps_new = sum(1 for l in new_lines if l.strip().startswith('- **') and 'L' in l)
        warnings_old = sum(1 for l in old_lines if l.strip().startswith('- **') and ('膨胀' in l or '退化' in l or '漂移' in l or '盲区' in l or '堆积' in l or '信任' in l or '泄露' in l or '过拟合' in l))
        warnings_new = sum(1 for l in new_lines if l.strip().startswith('- **') and ('膨胀' in l or '退化' in l or '漂移' in l or '盲区' in l or '堆积' in l or '信任' in l or '泄露' in l or '过拟合' in l))
        return {"lines_added": added, "lines_removed": removed, "drift_magnitude": round(mag, 3),
                "capability_count_delta": caps_new - caps_old,
                "warning_count_delta": warnings_new - warnings_old}
    except Exception as e:
        return {"error": str(e), "drift_magnitude": -1}


def check_breaker_trip(regeneration_log, memory_dir):
    """Trip circuit breaker if >=3 consecutive validation failures. Netflix ChAP pattern."""
    breaker_flag = os.path.join(memory_dir, ".circuit-breaker-open")
    try:
        if not os.path.exists(regeneration_log):
            return
        lines = open(regeneration_log, 'r', encoding='utf-8').readlines()
        consecutive = 0
        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
                if entry.get("validation") == "FAILED":
                    consecutive += 1
                else:
                    break
            except json.JSONDecodeError:
                # Carmack BUG 3: corrupted JSONL line breaks consecutive chain —
                # we can't tell if it was a failure or success, so reset count.
                # Silent skip was wrong: it could mask 2 FAILED + corrupt + 1 FAILED = 3 failures.
                consecutive = 0
                break
        if consecutive >= 3:
            breaker = {"consecutive_failures": consecutive,
                       "tripped_at": datetime.now(timezone.utc).isoformat(),
                       "action": "delete .circuit-breaker-open to reset"}
            with open(breaker_flag, 'w', encoding='utf-8') as f:
                json.dump(breaker, f, ensure_ascii=False)
            print(f"CIRCUIT_BREAKER:TRIPPED:{consecutive}_consecutive_failures", file=sys.stderr)
    except Exception:
        pass


def write_last_regeneration(version):
    """Write .last-regeneration timestamp file for cooling-period enforcement."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "version": version,
    }
    try:
        with open(LAST_REGENERATION, "w", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False))
    except OSError as e:
        print(f"REGEN:WARN: Cannot write .last-regeneration: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Log self-model regeneration event")
    parser.add_argument("--old", required=True, help="Old self-model version (e.g. v1)")
    parser.add_argument("--new", required=True, help="New self-model version (e.g. v2)")
    parser.add_argument("--sources", required=True, help="Comma-separated source file names")
    parser.add_argument("--trigger", default="flag", help="What triggered regeneration (default: flag)")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).isoformat()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]

    # ═══ STEP 1: VALIDATE regenerated self-model FIRST ═══
    valid, failures = validate_self_model()

    if not valid:
        print(f"REGEN_VALIDATE:FAIL ({len(failures)} issues):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(f"REGEN_VALIDATE:FLAG_PRESERVED — .self-model-stale retained for retry", file=sys.stderr)
        # Still log the attempt (even failed regenerations should be auditable)
        record = {
            "timestamp": timestamp,
            "trigger": args.trigger,
            "sources": sources,
            "old_version": args.old,
            "new_version": args.new,
            "flag_cleaned": False,
            "validation": "FAILED",
            "failures": failures,
        }
        try:
            with open(REGENERATION_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass
        # Check breaker: >=3 consecutive failures → trip circuit
        check_breaker_trip(REGENERATION_LOG, MEMORY)
        sys.exit(3)  # exit 3 = validation failed, flag preserved

    # ═══ STEP 1.5: Drift score (AutoLoop v0.8 — Carmack diff + Netflix Kayenta) ═══
    drift = compute_drift(args.old, args.new)

    # ═══ STEP 2: Validation passed — delete flag ═══
    flag_cleaned = False
    if os.path.exists(STALE_FLAG):
        try:
            os.remove(STALE_FLAG)
            flag_cleaned = True
            print(f"REGEN_FLAG: deleted .self-model-stale")
        except OSError as e:
            print(f"REGEN_FLAG:ERROR: {e}", file=sys.stderr)
    else:
        print(f"REGEN_FLAG: not found (already cleaned or never existed)")

    # ═══ STEP 3: Write .last-regeneration for cooling-period enforcement ═══
    write_last_regeneration(args.new)

    # ═══ STEP 4: Append to regeneration audit log ═══
    record = {
        "timestamp": timestamp,
        "trigger": args.trigger,
        "sources": sources,
        "old_version": args.old,
        "new_version": args.new,
        "flag_cleaned": flag_cleaned,
        "validation": "PASSED",
        "drift": drift,
    }
    try:
        with open(REGENERATION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"REGEN_LOG: appended (v{args.old} → v{args.new}, valid=PASSED)")
    except OSError as e:
        print(f"REGEN_LOG:ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # ═══ STEP 5: Verify log written ═══
    if os.path.exists(REGENERATION_LOG):
        print(f"REGEN_LOG: verified ({os.path.getsize(REGENERATION_LOG)} bytes)")
    else:
        print(f"REGEN_LOG:WARN: log file not found after write", file=sys.stderr)


if __name__ == "__main__":
    main()
