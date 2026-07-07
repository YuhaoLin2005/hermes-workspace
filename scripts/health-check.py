#!/usr/bin/env python3
"""SessionStart health check — disk/ram/gpu/config/growth. NEVER blocks, always exits 0.

v2.1 (2026-07-03): Added .last-regeneration cooling-period enforcement.
  Reads stdin for SessionStart source field — only triggers regeneration on "startup".
  COOLING signal when last regeneration < 24h ago.
"""

import os, sys, shutil, subprocess, glob, json
from datetime import date, timedelta, datetime, timezone

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
MEMORY = os.path.join(CLAUDE, "projects", "C--Users-86131", "memory")
STALE_FLAG = os.path.join(MEMORY, ".self-model-stale")
SELF_MODEL = os.path.join(MEMORY, "self-model.md")
GROWTH_LOG_DIR = os.path.join(MEMORY, "growth-log")
LAST_REGENERATION = os.path.join(MEMORY, ".last-regeneration")
WARN_DISK_GB = 50
BLOCK_DISK_GB = 15
WARN_TMP_FILES = 500
WARN_GPU_TEMP_C = 80
WARN_GPU_VRAM_PCT = 90
STALE_GROWTH_DAYS = 3
COOLING_HOURS = 24      # Refuse regeneration within 24h of last successful one


def read_stdin():
    """Read SessionStart hook payload to get source field."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except Exception:
        pass
    return {}


def check_disk():
    usage = shutil.disk_usage(HOME)
    free_gb = usage.free // (1024 ** 3)
    if free_gb < BLOCK_DISK_GB:
        print(f"DISK:{free_gb}GB:REFUSE", file=sys.stderr)
    elif free_gb < WARN_DISK_GB:
        print(f"DISK:{free_gb}GB:WARN", file=sys.stderr)
    else:
        print(f"DISK:{free_gb}GB:OK", file=sys.stderr)
    return free_gb


def check_tmp():
    tmp = os.path.join(HOME, "AppData", "Local", "Temp")
    try:
        count = len(os.listdir(tmp))
    except OSError:
        count = 0
    if count > WARN_TMP_FILES:
        print(f"TMP:{count}:WARN", file=sys.stderr)
    return count


def check_ram():
    try:
        out = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:list"],
            capture_output=True, text=True, timeout=10
        )
        lines = out.stdout.strip().split("\n")
        total_kb = free_kb = None
        for line in lines:
            line = line.strip()
            if "TotalVisibleMemorySize" in line:
                total_kb = int(line.split("=")[-1].strip())
            elif "FreePhysicalMemory" in line:
                free_kb = int(line.split("=")[-1].strip())
        if total_kb and free_kb:
            pct = 100 - (free_kb * 100 // total_kb)
            print(f"RAM:{pct}%:{free_kb//1024}MB:{total_kb//1024}MB", file=sys.stderr)
    except Exception:
        pass


def check_gpu():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        parts = out.stdout.strip().split(",")
        if len(parts) >= 4:
            temp = int(parts[0].strip())
            gpu_pct = int(parts[1].strip())
            vram_used = int(parts[2].strip())
            vram_total = int(parts[3].strip())
            vram_pct = vram_used * 100 // vram_total
            state = "WARN" if temp > WARN_GPU_TEMP_C or vram_pct > WARN_GPU_VRAM_PCT else "OK"
            print(f"GPU:{temp}C:{gpu_pct}%:{vram_used}/{vram_total}MB:{state}", file=sys.stderr)
    except Exception:
        pass


def check_config():
    """Verify core config files exist and are readable.
    Returns: dict mapping filename -> severity (FATAL/SEVERE/MEDIUM/MINOR) for MISSING files.
    Only missing files are included; present files are omitted."""
    # Degradation chain severity levels (matches BODY.md §配置降级链).
    # FATAL  = session cannot proceed safely (no behavioral calibration or hooks)
    # SEVERE = session can proceed but with degraded quality
    # MEDIUM = session identity/goals unavailable
    # MINOR  = non-critical, session proceeds normally
    DEGRADE = {
        "settings.json": "FATAL",    # hooks/permissions/MCP — mechanical safety net
        "INTERFACE.md": "FATAL",     # behavioral calibration — "致命" per BODY.md
        "CLAUDE.md":     "FATAL",    # root instruction file — startup sequence itself
        "BODY.md":       "SEVERE",   # process rules — "严重" per BODY.md
        "SOUL.md":       "MEDIUM",   # identity — "中等" per BODY.md
        "assumption.md": "MINOR",    # shared premises — "轻微" per BODY.md
        "RTK.md":        "MINOR",    # runtime knowledge — optional
    }
    missing = {}
    for f, severity in DEGRADE.items():
        if not os.path.exists(os.path.join(CLAUDE, f)):
            missing[f] = severity
            print(f"DEGRADE:{severity}:MISSING:{f}", file=sys.stderr)

    if not missing:
        print("CONFIG:ALL:OK", file=sys.stderr)
    return missing


def check_memory_config():
    """Verify memory-resident config files (self-model, persona-pool, MEMORY.md).
    Returns: dict mapping filename -> severity."""
    DEGRADE = {
        "self-model.md":   "MINOR",   # can use cached version or regenerate
        "persona-pool.md": "MEDIUM",  # dual-pool unavailable, fallback to 3x code-reviewer
        "MEMORY.md":       "MEDIUM",  # memory index — gateway to all memories
    }
    missing = {}
    for f, severity in DEGRADE.items():
        if not os.path.exists(os.path.join(MEMORY, f)):
            missing[f] = severity
            print(f"DEGRADE:{severity}:MISSING:memory/{f}", file=sys.stderr)
    return missing


def check_degradation_gate(root_missing, memory_missing):
    """Apply degradation severity gates.
    FATAL  → exit 2 (block session start)
    SEVERE → write .degraded-session flag for Stop hooks to read
    Returns True if session should proceed, False if blocked."""
    all_missing = {**root_missing, **memory_missing}

    # FATAL gate: session cannot proceed
    fatals = [f for f, s in all_missing.items() if s == "FATAL"]
    if fatals:
        print(f"DEGRADE:GATE:FATAL:{','.join(fatals)}:session_blocked", file=sys.stderr)
        return False

    # SEVERE gate: write flag for Stop hooks
    severes = [f for f, s in all_missing.items() if s == "SEVERE"]
    if severes:
        flag_path = os.path.join(MEMORY, ".degraded-session")
        with open(flag_path, "w") as f:
            f.write(f"degraded:{','.join(severes)}\n")
        print(f"DEGRADE:GATE:SEVERE:{','.join(severes)}:flag_written", file=sys.stderr)

    # MEDIUM/MINOR: informational only
    for f, s in all_missing.items():
        if s in ("MEDIUM", "MINOR"):
            print(f"DEGRADE:GATE:{s}:{f}:proceeding", file=sys.stderr)

    return True


def check_growth():
    """Check if growth-log has recent entries."""
    growth_dir = os.path.join(MEMORY, "growth-log")
    if not os.path.isdir(growth_dir):
        print("GROWTH:NO_DIR", file=sys.stderr)
        return
    today = date.today()
    latest = None
    for f in os.listdir(growth_dir):
        if f.endswith(".md"):
            try:
                d = date.fromisoformat(f[:10])
                if latest is None or d > latest:
                    latest = d
            except ValueError:
                continue
    if latest:
        days = (today - latest).days
        state = "WARN" if days > STALE_GROWTH_DAYS else "OK"
        print(f"GROWTH:{latest}:{days}d:{state}", file=sys.stderr)
    else:
        print("GROWTH:EMPTY:WARN", file=sys.stderr)


def check_skills():
    """Count active skills."""
    skills_dir = os.path.join(CLAUDE, "skills")
    count = 0
    if os.path.isdir(skills_dir):
        for name in os.listdir(skills_dir):
            if os.path.isdir(os.path.join(skills_dir, name)) and \
               os.path.exists(os.path.join(skills_dir, name, "SKILL.md")):
                count += 1
    print(f"SKILLS:{count}:OK", file=sys.stderr)


def check_cooling_period():
    """Check if regeneration cooling period is active.
    Returns (is_cooling: bool, hours_remaining: float)."""
    if not os.path.exists(LAST_REGENERATION):
        return False, 0

    try:
        data = json.loads(open(LAST_REGENERATION, "r", encoding="utf-8").read())
        last_ts = data.get("ts", "")
        if not last_ts:
            return False, 0
        last_dt = datetime.fromisoformat(last_ts)
        # Normalize: strip tzinfo, treat all timestamps as UTC.
        # log-regeneration.py writes UTC; manual edits may introduce local time.
        # Stripping tzinfo avoids TypeError on naive-vs-aware subtraction.
        if last_dt.tzinfo is not None:
            last_dt = last_dt.replace(tzinfo=None)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        hours_since = (now - last_dt).total_seconds() / 3600
        if hours_since < COOLING_HOURS:
            return True, COOLING_HOURS - hours_since
        return False, 0
    except Exception:
        return False, 0


def check_self_model_flag(source):
    """Check .self-model-stale flag consistency at session start.

    Lifecycle:
      1. Flag exists + self-model stale + not cooling → REGENERATE_NEEDED
      2. Flag exists + self-model stale + cooling active → COOLING (skip)
      3. Flag exists + self-model fresh → CLEANED_ORPHAN (auto-delete flag)
      4. No flag → nothing

    Only triggers regeneration on source="startup" (not compact/clear).
    """
    if not os.path.exists(STALE_FLAG):
        return None

    # Only trigger regeneration on fresh session start
    if source and source not in ("startup", ""):
        print(f"SELF_MODEL:SKIP:source={source}", file=sys.stderr)
        return "skip"

    flag_mtime = datetime.fromtimestamp(os.path.getmtime(STALE_FLAG), tz=timezone.utc)

    if not os.path.exists(SELF_MODEL):
        # Check cooling before signaling
        cooling, hours_left = check_cooling_period()
        if cooling:
            print(f"SELF_MODEL:COOLING:{hours_left:.1f}h_remaining:model_missing", file=sys.stderr)
            print(f"SELF_MODEL:JSON:{json.dumps({'action': 'wait', 'reason': f'cooling period: {hours_left:.1f}h remaining', 'trigger': 'flag'})}", file=sys.stderr)
            return "cooling"

        print(f"SELF_MODEL:REGENERATE_NEEDED:model_missing", file=sys.stderr)
        print(f"SELF_MODEL:JSON:{json.dumps({'action': 'regenerate', 'reason': 'self-model.md missing', 'trigger': 'flag'})}", file=sys.stderr)
        return "regenerate"

    model_mtime = datetime.fromtimestamp(os.path.getmtime(SELF_MODEL), tz=timezone.utc)

    # Find growth-log entries newer than self-model
    newer_logs = []
    if os.path.isdir(GROWTH_LOG_DIR):
        for f in os.listdir(GROWTH_LOG_DIR):
            if f.endswith(".md"):
                fpath = os.path.join(GROWTH_LOG_DIR, f)
                if datetime.fromtimestamp(os.path.getmtime(fpath), tz=timezone.utc) > model_mtime:
                    newer_logs.append(f.replace(".md", ""))

    if newer_logs:
        # Legitimate: flag exists AND self-model IS stale
        # But first: check cooling period
        cooling, hours_left = check_cooling_period()
        if cooling:
            newer_logs.sort()
            print(f"SELF_MODEL:COOLING:{hours_left:.1f}h_remaining:growth_logs_newer({len(newer_logs)}):{','.join(newer_logs[:3])}", file=sys.stderr)
            payload = json.dumps({
                "action": "wait",
                "reason": f"cooling period active: {hours_left:.1f}h remaining. {len(newer_logs)} newer growth-logs waiting.",
                "trigger": "flag",
                "sources": newer_logs,
                "hours_remaining": round(hours_left, 1)
            })
            print(f"SELF_MODEL:JSON:{payload}", file=sys.stderr)
            return "cooling"

        newer_logs.sort()
        print(f"SELF_MODEL:REGENERATE_NEEDED:growth_logs_newer({len(newer_logs)}):{','.join(newer_logs[:5])}", file=sys.stderr)
        payload = json.dumps({
            "action": "regenerate",
            "reason": f"growth-log entries newer than self-model: {', '.join(newer_logs)}",
            "trigger": "flag",
            "sources": newer_logs
        })
        print(f"SELF_MODEL:JSON:{payload}", file=sys.stderr)
        return "regenerate"
    else:
        # Orphaned: flag exists BUT self-model is already fresh
        try:
            os.remove(STALE_FLAG)
        except OSError:
            pass
        print(f"SELF_MODEL:CLEANED_ORPHAN:model_fresh:flag_was_{flag_mtime.strftime('%Y-%m-%dT%H:%M:%S')}", file=sys.stderr)
        return "cleaned"


CIRCUIT_BREAKER = os.path.join(MEMORY, ".circuit-breaker-open")
REVIEW_NEEDED = os.path.join(MEMORY, ".review-needed")
FIX_QUEUE = os.path.join(MEMORY, ".pending-fixes.json")
CURATION_NEEDED = os.path.join(MEMORY, ".curation-needed")


def check_circuit_breaker():
    """Netflix ChAP pattern: halt regeneration pipeline if >=3 consecutive failures.
    Runs BEFORE check_self_model_flag to prevent regeneration signaling."""
    if not os.path.exists(CIRCUIT_BREAKER):
        return None
    try:
        data = json.loads(open(CIRCUIT_BREAKER, "r", encoding="utf-8").read())
        failures = data.get("consecutive_failures", 0)
        tripped = data.get("tripped_at", "unknown")
    except Exception:
        failures = 0; tripped = "unknown"

    print(f"CIRCUIT_BREAKER:OPEN:{failures}_consecutive_failures:tripped_{tripped}", file=sys.stderr)
    print(f"CIRCUIT_BREAKER:ACTION:delete .circuit-breaker-open and .self-model-stale to reset", file=sys.stderr)

    # Clear stale flag to break regeneration loop
    if os.path.exists(STALE_FLAG):
        try:
            os.remove(STALE_FLAG)
            print("CIRCUIT_BREAKER:cleared .self-model-stale", file=sys.stderr)
        except OSError:
            pass
    return "open"


def check_auto_signals():
    """Detect review-needed, pending-fixes, curation-needed flags.
    Auto-loop v0.8: Gene Kim pattern — amplify weak signals at SessionStart."""
    signals = []

    if os.path.exists(REVIEW_NEEDED):
        try:
            data = json.loads(open(REVIEW_NEEDED, "r", encoding="utf-8").read())
            reason = data.get("reason", "unknown")
            tier = data.get("suggested_tier", "T2")
            signals.append(f"REVIEW_NEEDED:{reason}:{tier}")
        except Exception:
            signals.append("REVIEW_NEEDED:flag_exists")

    if os.path.exists(FIX_QUEUE):
        try:
            data = json.loads(open(FIX_QUEUE, "r", encoding="utf-8").read())
            count = len(data.get("violations", []))
            signals.append(f"FIX_QUEUE:{count}_violations")
        except Exception:
            signals.append("FIX_QUEUE:flag_exists")

    if os.path.exists(CURATION_NEEDED):
        try:
            data = json.loads(open(CURATION_NEEDED, "r", encoding="utf-8").read())
            since = data.get("sessions_since", "?")
            signals.append(f"CURATION_NEEDED:{since}_sessions")
        except Exception:
            signals.append("CURATION_NEEDED:flag_exists")

    if signals:
        print(f"AUTOLOOP:{';'.join(signals)}", file=sys.stderr)
    return signals


def main():
    # Read SessionStart payload for source field
    payload = read_stdin()
    source = payload.get("source", "")

    print("--- health ---", file=sys.stderr)
    check_disk()
    check_ram()
    check_gpu()
    check_tmp()
    root_missing = check_config()
    memory_missing = check_memory_config()
    check_growth()
    check_skills()

    # Auto-loop: circuit breaker BEFORE regeneration signal (Netflix ChAP pattern)
    breaker = check_circuit_breaker()
    if breaker != "open":
        check_self_model_flag(source)

    # Auto-loop: amplify weak signals at SessionStart (Gene Kim pattern)
    check_auto_signals()

    # Degradation severity gate
    if not check_degradation_gate(root_missing, memory_missing):
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
