#!/usr/bin/env python3
"""
Stop hook: quality gate with delivery check.
Detects incomplete work, stale learning logs, and low disk space.
Blocks Claude from stopping when a complex task completed without learning capture.

Install: cp this file to ~/.claude/scripts/quality-gate.py
Configure: Add to settings.json hooks.Stop
"""
from __future__ import annotations

import sys
import os
import re
import json
import datetime
import shutil
import logging
from typing import Optional

# ---- Configuration ----
# Patterns that indicate rationalized incompleteness
RATIONALIZE = [
    r'(?:this|that)\s+is\s+a\s+pre[- ]existing\s+(?:issue|bug)\b(?!\s+(?:that|which|and))',
    r'skipping\s+(?:tests?|lint|coverage|type[- ]check)\s+for\s+now',
    r'(?:tests?|coverage)\s+(?:are|is)\s+(?:failing|broken)\s+but\s+(?:I|we)\'ll\s+(?:fix|address)',
    r'(?:not\s+addressing|won\'t\s+fix|leaving)\s+the\s+(?:failing|broken)\s+(?:test|build)',
]

# Files to check for today's updates (relative to project memory dir)
# Customize these to match your learning-capture workflow
LIBS = {
    'ratings-tracker': 'ratings-tracker.md',
    'decisions-log': 'decisions/log.md',
    'growth-log': 'growth-log/',          # directory — any file updated today counts
    'output-index': 'output-index.md',
    'tooling-capabilities': 'tooling_capabilities.md',
}

MIN_CHARS = 40          # minimum transcript length to trigger checks
COMPLEX_THRESHOLD = 3   # Edit/Write calls to classify as "complex task"
DISK_REMIND_GB = 50     # remind when free space below this
DISK_WARN_GB = 30       # warn when free space below this
DISK_CRIT_GB = 15       # block stop when below this
# ---- End Configuration ----

# Configure stderr logger per coding guidelines
logging.basicConfig(
    stream=sys.stderr,
    format='%(levelname)s: %(message)s',
    level=logging.INFO,  # INFO for DISK_REMIND; warnings still emitted
)
log = logging.getLogger('quality-gate')


def get_project_memory_dir() -> Optional[str]:
    """Find the current project's memory directory.
    Returns None if no memory directory exists for this project.
    Does NOT fall back to other projects (privacy boundary)."""
    cwd = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    safe = cwd.replace(':', '-').replace('\\', '-').replace('/', '-')
    mem = os.path.expanduser(f'~/.claude/projects/{safe}/memory')
    log.info('Looking for memory dir: cwd=%s -> %s', cwd, mem)
    if os.path.isdir(mem):
        return mem
    return None


def check_disk() -> Optional[int]:
    """Check free space on the disk containing the home directory.
    Works cross-platform: macOS, Linux, Windows.
    Returns free GB, or None if the home directory is unavailable
    (e.g. on a headless CI runner without a real home dir)."""
    try:
        home = os.path.expanduser('~')
        free_gb = shutil.disk_usage(home).free // (2**30)
        return free_gb
    except (FileNotFoundError, PermissionError, OSError):
        # Home dir not accessible — log and continue without disk check
        log.warning('cannot check disk space (home dir inaccessible)')
        return None


def check_stale_libs(mem_dir: str) -> list[str]:
    """Return list of library names not updated today.
    Per-file OSError handling: individual unreadable files are skipped,
    but the scan continues for remaining libraries. Only returns empty
    list when the entire memory directory is inaccessible."""
    today = datetime.date.today()
    stale: list[str] = []
    for name, path in LIBS.items():
        full = os.path.join(mem_dir, path)
        try:
            if os.path.isdir(full):
                has_today = False
                # Use os.walk to handle nested subdirectories (e.g. growth-log/2026/06-26.md)
                for dirpath, _dirnames, filenames in os.walk(full):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            mt = datetime.datetime.fromtimestamp(os.path.getmtime(fp)).date()
                            if mt == today:
                                has_today = True
                                break
                        except OSError:
                            continue  # skip unreadable individual files
                    if has_today:
                        break
                if not has_today:
                    stale.append(name)
            elif os.path.exists(full):
                try:
                    mt = datetime.datetime.fromtimestamp(os.path.getmtime(full)).date()
                    if mt != today:
                        stale.append(name)
                except OSError:
                    stale.append(name)  # can't check → treat as stale
            else:
                stale.append(name)
        except OSError as e:
            # Individual lib path inaccessible — log and treat as stale
            log.warning('cannot access lib %s: %s', name, e)
            stale.append(name)
    return stale


def check_self_model(mem_dir: str) -> Optional[str]:
    """Check if self-model.md is older than latest growth-log entry.
    Writes .self-model-stale flag for next session startup if stale.
    Different from check_stale_libs: freshness is measured against
    the most recent growth-log, not against 'today'.

    Returns 'self-model' if stale, None if fresh or if self-model
    doesn't exist yet (first-run — flag written, trigger at startup)."""
    self_model = os.path.join(mem_dir, 'self-model.md')
    growth_log_dir = os.path.join(mem_dir, 'growth-log')
    flag_file = os.path.join(mem_dir, '.self-model-stale')

    # Find latest growth-log mtime first (needed for comparison)
    latest_gl = 0.0
    if os.path.isdir(growth_log_dir):
        for dirpath, _dirnames, filenames in os.walk(growth_log_dir):
            for f in filenames:
                if f.endswith('.md'):
                    try:
                        mt = os.path.getmtime(os.path.join(dirpath, f))
                        if mt > latest_gl:
                            latest_gl = mt
                    except OSError:
                        continue

    if latest_gl == 0.0:
        return None  # No growth-logs at all — nothing to synthesize

    try:
        sm_mtime = os.path.getmtime(self_model)
    except OSError:
        # self-model.md doesn't exist or is unreadable
        try:
            with open(flag_file, 'w') as f:
                f.write(datetime.datetime.now().isoformat())
        except OSError:
            pass
        return 'self-model'

    if latest_gl > sm_mtime:
        try:
            with open(flag_file, 'w') as f:
                f.write(datetime.datetime.now().isoformat())
        except OSError:
            pass
        return 'self-model'

    # self-model is fresh — clean up stale flag if present
    if os.path.exists(flag_file):
        try:
            os.remove(flag_file)
        except OSError:
            pass
    return None


# ---- Agent misuse detection ----
# Two-step logic (same as pre-agent-guard.py):
# (1) matches a search verb phrase → (2) no semantic verb → suspicious
AGENT_SEARCH_PATTERNS = [
    r"\bsearch\s+(?:for|in|through)\b",
    r"\bfind\s+(?:all\s+)?(?:files?|occurrences?|matches?|patterns?|sessions?)\b",
    r"\bcount\s+(?:how\s+many\s+)?(?:occurrences?|files?|matches?|sessions?)\b",
    r"\blist\s+(?:all\s+)?(?:files?|sessions?|directories?|matches?)\b",
    r"\bgrep\s+(?:for|pattern)\b",
    r"\blocate\s+(?:all\s+)?(?:files?|matches?)\b",
]
AGENT_SEMANTIC_STEMS = [
    "analyz", "understand", "review", "reason", "investigat",
    "explain", "summariz", "evaluat", "assess", "compar",
    "interpret", "determine whether", "check if", "decid",
    "design", "implement", "fix", "debug", "refactor",
    "propos", "recommend", "suggest", "research",
    "verif", "validat", "transform", "convert",
    "extract", "generat", "compos", "write",
]


def count_edits(text: str) -> int:
    """Count Edit/Write tool invocations in the current session tail.
    Matches structured tool-call JSON patterns to avoid false-positives
    from ordinary English prose (e.g., 'Edit the file' in conversation).

    Scopes to the last 20000 characters of the transcript — the approximate
    window of the most recent task/turn. Scanning the full cumulative
    transcript causes permanent false-positives: a session with 50+ total
    edits from earlier tasks is not necessarily "complex" right now.
    COMPLEX_THRESHOLD (default 3) is per-task, not per-lifetime.
    """
    tail = text[-20000:] if len(text) > 20000 else text
    return len(re.findall(r'"name":\s*"(?:Edit|Write)"', tail))


def check_evidence_staleness(mem_dir: str) -> list[str]:
    """Parse ratings-tracker.md for dimensions with confidence=low + evidence > 90d.
    Returns list of dimension names. Warn if >=3 — self-model accuracy is degrading."""
    ratings_file = os.path.join(mem_dir, 'ratings-tracker.md')
    if not os.path.exists(ratings_file):
        return []

    try:
        with open(ratings_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        return []

    # Match evidence lines: - **证据**: type | link | YYYY-MM-DD | confidence=level
    evidence_re = re.compile(
        r'###\s+(.+?)：.+?\n.*?'
        r'\*\*证据\*\*:\s*(?:self_report|output_artifact|external_review|benchmark|peer_comparison)'
        r'\s*\|\s*.+?\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*confidence=(\w+)',
        re.DOTALL,
    )

    today = datetime.date.today()
    stale_dims: list[str] = []

    for m in evidence_re.finditer(content):
        dim_name = m.group(1).strip().split('\n')[0].strip()
        evidence_date_str = m.group(2)
        confidence = m.group(3)

        if confidence != 'low':
            continue

        try:
            evidence_date = datetime.date.fromisoformat(evidence_date_str)
        except ValueError:
            continue

        age_days = (today - evidence_date).days
        if age_days > 90:
            stale_dims.append(f'{dim_name}({age_days}d)')

    return stale_dims


def check_agent_misuse(transcript: str) -> list[str]:
    """Find Agent calls that should have been grep/Bash instead.
    Matches the same heuristics as pre-agent-guard.py (mechanical double-check).
    Returns list of offending descriptions (for warning only — pre-agent hook blocks).

    Scopes to the last 20000 characters of the transcript — the approximate
    window of the most recent task/turn. Scanning the full cumulative
    transcript causes permanent false-positives (same bug class as count_edits)."""
    # Tail-scope to avoid re-scanning every Agent call from entire session history
    tail = transcript[-20000:] if len(transcript) > 20000 else transcript
    suspicious: list[str] = []
    # Find Agent tool calls with their descriptions
    for m in re.finditer(r'"name":\s*"Agent"[^}]*"description":\s*"([^"]+)"', tail):
        desc = m.group(1)
        desc_lower = desc.lower()
        # Safe override: semantic verbs → skip
        has_semantic = any(stem in desc_lower for stem in AGENT_SEMANTIC_STEMS)
        if has_semantic:
            continue
        # Check for pure search patterns
        for pat in AGENT_SEARCH_PATTERNS:
            if re.search(pat, desc_lower):
                suspicious.append(desc[:80])
                break
    return suspicious


def main() -> None:
    raw = sys.stdin.read()

    # Stop-hook contract: echo stdin to stdout so the harness can forward the payload
    sys.stdout.write(raw)

    # Resolve transcript: Stop hooks may receive raw text OR JSON with transcript_path.
    # Handle both so the gate works regardless of Claude Code version/configuration.
    transcript = raw
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict) and 'transcript_path' in payload:
            tp = os.path.expanduser(payload['transcript_path'])
            if os.path.exists(tp):
                with open(tp, 'r', encoding='utf-8') as f:
                    transcript = f.read()
            else:
                log.warning('transcript_path %s not found, falling back to raw stdin', tp)
    except (json.JSONDecodeError, TypeError, OSError):
        pass  # Not JSON or unreadable — use raw stdin as transcript

    # 1. Disk check — three-level: remind / warn / block
    disk_free = check_disk()
    if disk_free is not None:
        if disk_free < DISK_CRIT_GB:
            log.warning('Blocked: disk space at %dGB (<%dGB). Free space before continuing.',
                        disk_free, DISK_CRIT_GB)
            sys.exit(2)
        if disk_free < DISK_WARN_GB:
            log.warning('WARN: disk space at %dGB (<%dGB)', disk_free, DISK_WARN_GB)
        elif disk_free < DISK_REMIND_GB:
            log.info('Reminder: disk space at %dGB (<%dGB)', disk_free, DISK_REMIND_GB)

    # 2. Short session — skip remaining checks
    if len(transcript) < MIN_CHARS:
        sys.exit(0)

    tail = transcript[-8000:]

    # 3. Rationalization pattern detection
    hits = []
    for p in RATIONALIZE:
        m = re.search(p, tail, re.IGNORECASE)
        if m:
            hits.append(m.group(0)[:80])
    if hits:
        log.warning('quality-gate: %s', hits)

    # 4. Learning capture check
    mem_dir = get_project_memory_dir()
    edit_count = count_edits(transcript)
    is_complex = edit_count >= COMPLEX_THRESHOLD

    if mem_dir:
        stale = check_stale_libs(mem_dir)
        # self-model: separate check (vs latest growth-log, not vs today)
        # stale flag written to .self-model-stale for next session startup
        sm_stale = check_self_model(mem_dir)
        if sm_stale:
            stale.append(sm_stale)
        # Evidence staleness: low-confidence + >90d evidence = self-model drift risk
        evidence_stale = check_evidence_staleness(mem_dir)
        if evidence_stale:
            log.warning(
                'Evidence staleness: %d dimension(s) with low-confidence evidence >90d:\n  %s',
                len(evidence_stale),
                '\n  '.join(evidence_stale),
            )
            if len(evidence_stale) >= 3:
                log.warning(
                    '≥3 low-confidence stale dimensions — self-model accuracy is degrading. '
                    'Re-verify or update evidence dates for: %s',
                    ', '.join(e.split('(')[0] for e in evidence_stale),
                )
    else:
        # No memory dir — setup incomplete.
        # Warn but DO NOT block: blocking here deadlocks new users
        # who haven't created the memory directory yet.
        if is_complex:
            log.warning('No project memory directory found — cannot verify learning capture.')
            log.warning('Set up memory/ per delivery-gate SKILL.md to enable enforcement.')
        stale = []

    # Build warning message
    parts = []
    if is_complex:
        status_icons = ['X' if s in stale else 'O' for s in LIBS]
        parts.append(
            f'\n  Complex task ({edit_count} edits). '
            f'Check: [{"][".join(f"{k}:{v}" for k,v in zip(LIBS.keys(), status_icons))}]'
        )
    if stale:
        parts.append(f'  Stale ({len(stale)}): {", ".join(stale)}')

    if parts:
        log.warning('\n'.join(parts))

    # 4.5. Agent misuse audit — detect Agent calls that should have been grep
    # This is the DETECTION layer (pre-agent-guard.py is the PREVENTION layer).
    # If both layers miss the same call, there's a bug in the patterns.
    agent_suspicious = check_agent_misuse(transcript)
    if agent_suspicious:
        log.warning(
            'Agent misuse detected (%d call(s)) — should have used grep/Bash:\n  %s',
            len(agent_suspicious),
            '\n  '.join(agent_suspicious),
        )

    # 5. Block if complex task completed without learning capture
    # Previously blocked only if ALL 5 libraries stale — too lenient.
    # Now: block if >=3 stale (most tasks update 2-3 libraries naturally).
    # Also block if NO growth-log update after any code change.
    # self-model is excluded from blocking: staleness triggers a flag for
    # next-session-startup regeneration, not an end-of-session rush job.
    blocking_stale = [s for s in stale if s != 'self-model']
    if is_complex:
        if len(blocking_stale) >= 3:
            log.warning('Blocked: complex task but >=3 learning libs stale.')
            log.warning(f'Stale: {", ".join(stale)}. Update before stopping.')
            sys.exit(2)
        if 'growth-log' in stale:
            log.warning('Blocked: code changes made but no growth-log update.')
            log.warning('Write growth-log before stopping (even if "no new learnings").')
            sys.exit(2)

    # 6. Session cost recording — append metrics for layered decision-making
    # Stored in ~/.claude/session-data/cost-log.jsonl (separate from memory)
    # L0(1-4):collect → L1(5-14):observe → L2(15-29):analyze → L3(30+):decide
    try:
        cost_log = os.path.expanduser('~/.claude/session-data/cost-log.jsonl')
        os.makedirs(os.path.dirname(cost_log), exist_ok=True)
        now = datetime.datetime.now()
        record = {
            'ts': now.isoformat(),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M'),
            'edits': edit_count,
            'min': 0,
            'complex': is_complex,
        }
        with open(cost_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except OSError:
        pass

    # AutoLoop v0.8: write review-needed + curation-needed flags
    # Carmack fix: split into individual try/except per flag write, never silent-catch-all
    mem_dir = get_project_memory_dir()
    if mem_dir:
        # ── Review-needed flag ──
        last_review = os.path.join(mem_dir, ".last-review")
        sessions_since_review = 999
        lr_ts = ""
        if os.path.exists(last_review):
            try:
                lr = json.loads(open(last_review, 'r', encoding='utf-8').read())
                lr_ts = lr.get("ts", "")
            except Exception:
                pass
        if os.path.exists(cost_log):
            count = 0
            for line in open(cost_log, 'r', encoding='utf-8'):
                try:
                    e = json.loads(line.strip())
                    if lr_ts and e.get("ts", "") <= lr_ts:
                        continue
                    count += 1
                except json.JSONDecodeError:
                    continue
            sessions_since_review = count

        review_reasons = []
        if sessions_since_review >= 5:
            review_reasons.append(f"sessions:{sessions_since_review}")
        # Carmack BUG 2: dir() in main() returns LOCAL scope — check_evidence_staleness is module-level.
        # Just call it directly. If it doesn't exist, Python will raise NameError (which is correct —
        # a missing function SHOULD be noisy, not silently skipped).
        ev_stale = check_evidence_staleness(mem_dir)
        if len(ev_stale) >= 3:
            review_reasons.append(f"evidence_stale:{len(ev_stale)}")

        if review_reasons:
            rn = os.path.join(mem_dir, ".review-needed")
            tier = "T3" if len(ev_stale) >= 5 or sessions_since_review >= 15 else ("T2" if sessions_since_review >= 10 else "T1")
            try:
                with open(rn, 'w', encoding='utf-8') as f:
                    json.dump({"reason": ";".join(review_reasons), "suggested_tier": tier,
                               "sessions_since_review": sessions_since_review,
                               "ts": datetime.datetime.now().isoformat()}, f, ensure_ascii=False)
            except OSError as e:
                log.warning('AutoLoop: cannot write .review-needed: %s', e)

        # ── Curation-needed flag ──
        last_curation = os.path.join(mem_dir, ".last-curation")
        sessions_since_curation = 999
        lc_ts = ""
        if os.path.exists(last_curation):
            try:
                lc = json.loads(open(last_curation, 'r', encoding='utf-8').read())
                lc_ts = lc.get("ts", "")
            except Exception:
                pass
        if os.path.exists(cost_log):
            count = 0
            for line in open(cost_log, 'r', encoding='utf-8'):
                try:
                    e = json.loads(line.strip())
                    if lc_ts and e.get("ts", "") <= lc_ts:
                        continue
                    count += 1
                except json.JSONDecodeError:
                    continue
            sessions_since_curation = count
        if sessions_since_curation >= 10:
            cn = os.path.join(mem_dir, ".curation-needed")
            try:
                with open(cn, 'w', encoding='utf-8') as f:
                    json.dump({"sessions_since": sessions_since_curation,
                               "ts": datetime.datetime.now().isoformat()}, f, ensure_ascii=False)
            except OSError as e:
                log.warning('AutoLoop: cannot write .curation-needed: %s', e)

    sys.exit(0)


if __name__ == '__main__':
    if '--check' in sys.argv:
        # Freshness diagnostic (was root quality-gate.py, now merged). Informational only.
        import logging as chk
        chk.basicConfig(level=chk.INFO, format='%(message)s')
        md = get_project_memory_dir()
        if not md:
            chk.error('memory dir not found')
            sys.exit(1)
        ss = check_self_model(md)
        chk.warning('self-model: STALE — %s', ss) if ss else chk.info('self-model: FRESH')
        ls = check_stale_libs(md)
        chk.warning('libs stale: %s', ', '.join(ls)) if ls else chk.info('learning libs: FRESH')
        sys.exit(0)
    else:
        main()
