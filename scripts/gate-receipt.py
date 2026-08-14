#!/usr/bin/env python3
"""Evidence-provenance receipt — the provenance-side contract from the paper.

Standalone, publicly-viewable copy of the receipt logic that runs in the
production L1 mechanical gate (~/.claude/scripts/write-guard.py). It binds a
gate pass to the exact state the gate checked: a pass without a bound revision
hash and an explicit coverage list is not a valid receipt by construction.

Usage:
  python gate_receipt.py Write C:/path/file.txt --stdout
  python gate_receipt.py Bash "echo hello"
  python gate_receipt.py Bash "rm -rf /" --checks dangerous-cmd,disk

Default: append one JSONL line to ~/.claude/receipts.jsonl.
With --stdout: print the receipt and write nothing.

Why it exists: the three-questions gate died because its evidence (a ritual)
was not bound to any artifact — a `pass.py` could satisfy it with zero
connection to the work. Binding the decision to a revision hash + coverage list
makes the cheapest bypass stop being "emit a marker" and become "actually
produce that state" — which is the work. Wrong-revision acceptance (a gate
passing a result from before a later edit) becomes a non-receipt by
construction. Standard library only, no network, never raises.
"""

import sys, os, json, hashlib
from pathlib import Path
from datetime import datetime

RECEIPT_LOG = Path.home() / ".claude" / "receipts.jsonl"


def emit_receipt(tool, target, checks, to_stdout=False):
    """Append (or print) a provenance receipt. Never raises."""
    try:
        # revision = hash of the exact state the gate checked
        if os.path.isfile(target):
            with open(target, 'rb') as fh:
                revision = hashlib.sha256(fh.read()).hexdigest()[:12]
        else:
            revision = hashlib.sha256(
                target.encode('utf-8', errors='replace')).hexdigest()[:12]

        record = {
            "receipt": "prose-barrier-evidence-provenance-v1",
            "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "hook": "write-guard",
            "tool": tool,
            "target": target[:80],
            "revision": revision,
            "checks": sorted(checks),
            "decision": "allow",
            "source": "mechanical",
        }
        line = json.dumps(record, ensure_ascii=False)
        if to_stdout:
            print(line)
        else:
            RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(RECEIPT_LOG, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        return record
    except OSError:
        return None


def parse_args(argv):
    tool = "Bash"
    target = "echo hello"
    checks = ["dangerous-cmd", "disk", "exec-debt",
              "sensitive-path", "session-health"]
    to_stdout = False
    for i, a in enumerate(argv):
        if a == "--stdout":
            to_stdout = True
        elif a == "--checks" and i + 1 < len(argv):
            checks = [c.strip() for c in argv[i + 1].split(',') if c.strip()]
        elif a in ("Write", "Edit", "Bash", "Agent"):
            tool = a
        elif not a.startswith("-"):
            target = a
    return tool, target, checks, to_stdout


if __name__ == "__main__":
    tool, target, checks, to_stdout = parse_args(sys.argv[1:])
    r = emit_receipt(tool, target, checks, to_stdout=to_stdout)
    if r is None:
        sys.exit(2)
    sys.exit(0)
