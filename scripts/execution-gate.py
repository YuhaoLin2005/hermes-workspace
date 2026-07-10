#!/usr/bin/env python3
"""execution-gate.py — mechanically prevents write-without-execute spiral.

Same closed-loop pattern as self-model regeneration (4 mechanical + 1 intelligence):
  Write .py → debt++ → debt>=3 → DENY [mechanical]
  Bash runs debt file → debt-- → allow [mechanical]
  AI chooses WHAT to execute [intelligence]

This is NOT prose advice. This is exit-code enforcement.
"""
import json, os, sys, time
from pathlib import Path

STATE = Path.home() / ".claude" / "state" / "execution-debt.json"
MAX_DEBT = 3
CODE_EXTS = {".py", ".sh", ".pro", ".js", ".ts", ".rs", ".go"}
IGNORE = [str(Path.home() / ".claude"), str(Path.home() / ".config")]

def load():
    if STATE.exists():
        try: return json.loads(STATE.read_text())
        except: pass
    return {"debt": [], "max_debt": MAX_DEBT, "blocked": 0,
            "session": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def is_code(fp):
    if Path(fp).suffix.lower() not in CODE_EXTS: return False
    for pfx in IGNORE:
        if fp.startswith(pfx): return False
    return True

def match_debt(cmd, debt):
    cl = cmd.lower()
    for e in debt:
        f = e["file"].lower(); fn = Path(e["file"]).name.lower()
        if f in cl or fn in cl: return e
    return None

def main():
    try: inp = json.loads(sys.stdin.read())
    except: print(json.dumps({"decision": "allow"})); return

    tn = inp.get("tool_name", ""); ti = inp.get("tool_input", {}); s = load()

    if tn in ("Write", "Edit"):
        fp = ti.get("file_path", "")
        if not is_code(fp):
            print(json.dumps({"decision": "allow"})); return

        if len(s["debt"]) >= s["max_debt"]:
            s["blocked"] = s.get("blocked", 0) + 1; save(s)
            files = "\n".join(f"  {e['file']}" for e in s["debt"])
            print(json.dumps({"decision": "deny", "reason":
                f"[EXEC-DEBT] {len(s['debt'])} scripts unexecuted.\n{files}\n"
                "MUST run >=1 script via Bash before writing more code."})); return

        if not any(e["file"] == fp for e in s["debt"]):
            s["debt"].append({"file": fp, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        r = s["max_debt"] - len(s["debt"])
        reason = f"[EXEC-DEBT] {len(s['debt'])}/{s['max_debt']} debt. {r} writes remaining." if s["debt"] else ""
        save(s); print(json.dumps({"decision": "allow", "reason": reason})); return

    if tn == "Bash":
        cmd = ti.get("command", "")
        if not cmd: print(json.dumps({"decision": "allow"})); return
        e = match_debt(cmd, s["debt"])
        if e:
            s["debt"] = [d for d in s["debt"] if d["file"] != e["file"]]
            r = len(s["debt"])
            reason = "[EXEC-DEBT] All clear — writes re-enabled." if r == 0 else f"[EXEC-DEBT] Cleared 1. {r} remaining."
            save(s); print(json.dumps({"decision": "allow", "reason": reason})); return
        if s["debt"]:
            print(json.dumps({"decision": "allow",
                "reason": f"[EXEC-DEBT] Executed non-debt cmd. {len(s['debt'])} scripts still queued."})); return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
