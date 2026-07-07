#!/usr/bin/env python3
"""Record three-questions completion for the three-questions-guard.py PreToolUse hook.

Run after answering Q1(概念审查)→Q2(输入一致)→Q3(非对抗终检) in conversation.
The guard reads this timestamp and allows Edit/Write/destructive Bash for 5 minutes.

Part of the dual-layer mechanical gate — soft enforcement of pre-execution quality check.
"""

import json, os, sys
from datetime import datetime

STATE_FILE = os.path.expanduser(r"~\.claude\state\three-questions-check.json")

os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump({"ts": datetime.now().isoformat(), "method": "manual"}, f)

print("✅ 三问已通过 — 5分钟内 Edit/Write/高风险Bash 免检", file=sys.stderr)
