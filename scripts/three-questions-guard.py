#!/usr/bin/env python3
"""PreToolUse hook: enforce three-questions warmup before Edit/Write/destructive Bash.

Checks ~/.claude/state/three-questions-check.json timestamp.
If older than TIMEOUT_MINUTES → exit 2 with instructions to complete Q1/Q2/Q3.
Non-destructive Bash (read-only, three-questions-pass.py itself) always passes through.

Part of the dual-layer mechanical gate — soft enforcement of pre-execution quality check.
Paired with: three-questions-pass.py (writes timestamp after Q1/Q2/Q3 answered)
"""

import json, os, sys
from datetime import datetime

STATE_FILE = os.path.expanduser(r"~\.claude\state\three-questions-check.json")
TIMEOUT_MINUTES = 5

# Bash command patterns that trigger three-questions check.
# Only destructive/write operations — read-only commands pass through.
DESTRUCTIVE_PATTERNS = [
    "rm ", "rmdir", "del ",
    "mv ", "rename ",
    "chmod", "chown", "chattr",
    "git push", "git commit", "git tag",
    "pip install", "pip3 install", "npm install -g", "npm i -g",
    "pip uninstall", "pip3 uninstall", "npm uninstall -g",
    "conda install", "conda remove",
    "cargo install", "cargo uninstall",
    "curl ", "wget ",
    "> /dev/", "dd if=", "mkfs", "format ",
]


def is_destructive(cmd):
    """Check if a Bash command requires three-questions verification."""
    cmd_lower = cmd.lower()
    # curl/wget pipe to bash/sh is always dangerous
    if ("curl" in cmd_lower or "wget" in cmd_lower) and \
       ("| bash" in cmd_lower or "| sh" in cmd_lower or "| sudo" in cmd_lower):
        return True
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern in cmd_lower:
            return True
    return False


def check_timestamp():
    """Return True if three-questions were completed within TIMEOUT_MINUTES."""
    try:
        if not os.path.exists(STATE_FILE):
            return False
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        last_ts = datetime.fromisoformat(state.get("ts", "2000-01-01T00:00:00"))
        elapsed = (datetime.now() - last_ts).total_seconds()
        return elapsed < TIMEOUT_MINUTES * 60
    except (ValueError, KeyError, OSError, json.JSONDecodeError):
        return False


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
        tool_name = data.get("tool_name", "")
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Fail open — never block on parse errors

    # Only enforce on Edit/Write/Bash
    if tool_name not in ("Edit", "Write", "Bash"):
        sys.exit(0)

    # For Bash, only check destructive commands
    if tool_name == "Bash":
        tool_input = data.get("tool_input", {})
        cmd = tool_input.get("command", "")
        if not cmd or not is_destructive(cmd):
            sys.exit(0)

    # Check three-questions freshness
    if check_timestamp():
        sys.exit(0)

    # Block: three-questions expired or never completed
    print(
        "[三问守卫] ⛔ 请先完成强制三问: "
        "Q1概念审查→Q2输入一致→Q3非对抗终检",
        file=sys.stderr,
    )
    print(
        "[三问守卫] 三问逐条回答后运行: "
        'python ~/.claude/scripts/three-questions-pass.py',
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
