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

Default: append one JSONL line to ~/.claude/receipts/YYYY-MM-DD.jsonl (daily
rotation, 7-day retention, target redacted against sensitive patterns).
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
from datetime import datetime, timedelta

RECEIPT_DIR = Path.home() / ".claude" / "receipts"
RECEIPT_RETENTION_DAYS = 7
# Mirrors ~/.claude/scripts/write-guard.py's sensitive-path patterns.
SENSITIVE_PATTERNS = [
    ".env", ".env.", "credentials", "secret", "token", "password", "bearer",
    "~/.ssh/", ".ssh/", "~/.aws/", ".aws/credentials",
    "id_rsa", "private.key", ".pem",
]


def _redact_target(target):
    """Strip sensitive substrings before a target hits disk. Never raises."""
    try:
        if not target:
            return target
        t_lower = target.lower()
        for p in SENSITIVE_PATTERNS:
            if p.lower() in t_lower:
                return "[redacted: %s]" % p
    except Exception:
        pass
    return target


def _receipt_path(now):
    return RECEIPT_DIR / ("%s.jsonl" % now.strftime("%Y-%m-%d"))


def _prune_receipts(now):
    """Drop receipt files older than RETENTION_DAYS. Never raises."""
    try:
        cutoff = (now - timedelta(days=RECEIPT_RETENTION_DAYS)).strftime("%Y-%m-%d")
        for f in RECEIPT_DIR.glob("*.jsonl"):
            if f.stem < cutoff:
                f.unlink()
    except OSError:
        pass


def emit_receipt(tool, target, checks, to_stdout=False):
    """Append (or print) a provenance receipt. Never raises."""
    try:
        now = datetime.now()
        # revision = hash of the exact state the gate checked
        if os.path.isfile(target):
            with open(target, 'rb') as fh:
                revision = hashlib.sha256(fh.read()).hexdigest()[:12]
        else:
            revision = hashlib.sha256(
                target.encode('utf-8', errors='replace')).hexdigest()[:12]
        target = _redact_target(target)[:80]

        record = {
            "receipt": "prose-barrier-evidence-provenance-v1",
            "ts": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "hook": "write-guard",
            "tool": tool,
            "target": target,
            "revision": revision,
            "checks": sorted(checks),
            "decision": "allow",
            "source": "mechanical",
        }
        line = json.dumps(record, ensure_ascii=False)
        if to_stdout:
            print(line)
        else:
            receipt = _receipt_path(now)
            receipt.parent.mkdir(parents=True, exist_ok=True)
            with open(receipt, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
            _prune_receipts(now)
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
