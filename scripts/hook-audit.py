#!/usr/bin/env python3
"""hook-audit.py — Mechanized detection of the "Standalone Capability → Pipeline Checkpoint" meta-pattern.

Scans ~/.claude/scripts/*.py, cross-references settings.json hooks, reports unwired scripts.
Exit 0 always (soft monitoring). Writes to stderr so hook output is visible.

Meta: this script itself must be wired (SessionStart) to close the self-referential loop.
This is instance #5 of the pattern it detects.
"""

import json
import os
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path.home() / ".claude" / "scripts"
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

# Known manual-only scripts (no recurring trigger, deliberately unwired)
MANUAL_ONLY = {
    "ocr.py",
    "three-questions-pass.py",
    "session-cost.py",
    "trial-tick.py",
}

# Known library/utility modules (imported by wired scripts)
KNOWN_LIBRARIES = {
    "_ocr_engine.py",
    "fact-check.py",
    "log-regeneration.py",
    "version-rotate.py",
    "statusline.py",
    "desensitize.py",
    "memory-curator.py",
    "config-usage-tracker.py",
    "review-budget-guard.py",
    "review-classifier.py",
    "session-snapshot.sh",
}


def get_script_names(scripts_dir: Path) -> set[str]:
    scripts = set()
    if not scripts_dir.exists():
        return scripts
    for f in scripts_dir.iterdir():
        if f.is_file() and f.suffix == ".py" and f.name != "__init__.py":
            if f.parent != scripts_dir:
                continue
            scripts.add(f.name)
    return scripts


def get_wired_scripts(settings_path: Path) -> set[str]:
    wired = set()
    if not settings_path.exists():
        return wired
    try:
        with open(settings_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return wired

    hooks = data.get("hooks", {})
    for entries in hooks.values():
        for entry in entries:
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                matches = re.findall(r'scripts[/\\]([a-zA-Z0-9_-]+\.py)', cmd)
                wired.update(matches)
    return wired


def is_imported_by_wired(script_name: str, wired_scripts: set[str], scripts_dir: Path) -> bool:
    module_name = script_name.replace(".py", "").replace("-", "_")
    for wired_name in wired_scripts:
        wired_path = scripts_dir / wired_name
        if not wired_path.exists():
            continue
        try:
            content = wired_path.read_text(encoding="utf-8", errors="ignore")
            patterns = [
                rf'import\s+{re.escape(module_name)}',
                rf'from\s+{re.escape(module_name)}\s+import',
            ]
            for pat in patterns:
                if re.search(pat, content):
                    return True
        except Exception:
            continue
    return False


def has_manual_only_annotation(script_path: Path) -> bool:
    try:
        content = script_path.read_text(encoding="utf-8", errors="ignore")
        head = "\n".join(content.split("\n")[:20])
        return "# MANUAL_ONLY" in head
    except Exception:
        return False


def main():
    scripts = get_script_names(SCRIPTS_DIR)
    wired = get_wired_scripts(SETTINGS_PATH)

    unwired = []
    unknown_category = []

    for script in sorted(scripts):
        if script in wired:
            continue

        script_path = SCRIPTS_DIR / script

        if has_manual_only_annotation(script_path):
            continue

        if is_imported_by_wired(script, wired, SCRIPTS_DIR):
            continue

        if script in KNOWN_LIBRARIES:
            continue

        if script in MANUAL_ONLY:
            continue

        try:
            first_line = script_path.read_text(encoding="utf-8", errors="ignore").split("\n")[0].strip()
        except Exception:
            first_line = ""

        if first_line.startswith("#!") or first_line.startswith('"""') or first_line.startswith("'''"):
            unwired.append(script)
        else:
            unknown_category.append(script)

    if not unwired and not unknown_category:
        return

    lines = ["[hook-audit] Scripts vs hooks cross-reference:"]

    if unwired:
        lines.append(f"  UNWIRED ({len(unwired)}): scripts exist but not referenced in any hook:")
        for s in unwired:
            lines.append(f"    - scripts/{s}")

    if unknown_category:
        lines.append(f"  UNKNOWN ({len(unknown_category)}): no clear entry point, may be libraries:")
        for s in unknown_category:
            lines.append(f"    - scripts/{s}")

    if unwired:
        lines.append("  -> Meta-pattern active: Standalone Capability -> Pipeline Checkpoint")
        lines.append("  -> Fix: register in settings.json hook, or add '# MANUAL_ONLY' annotation")

    print("\n".join(lines), file=sys.stderr)

    # Write machine-readable flag for health-check consumption
    flag_path = Path.home() / ".claude" / "state" / ".unwired-scripts"
    try:
        flag_path.parent.mkdir(parents=True, exist_ok=True)
        if unwired:
            flag_path.write_text("\n".join(unwired))
        elif flag_path.exists():
            flag_path.unlink()
    except OSError:
        pass


if __name__ == "__main__":
    sys.exit(main() or 0)
