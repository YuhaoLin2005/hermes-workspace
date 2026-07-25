"""Stop hook: mechanical post-hoc honesty checks via regex.
Detects known failure signatures — unsubstantiated praise, omission of failure,
hedging after errors. Complements 四问自审 by operating on text patterns,
not LLM self-assessment. Principle 2 (Mechanical Enforcement).

Reads stdin (transcript), echoes to stdout, writes flags to honesty-flags.jsonl.
"""

import sys
import re
import json
import os
from datetime import datetime, timezone


def check_praise_without_evidence(text: str) -> list[str]:
    """Praise words without causation/evidence language within 200 chars."""
    praise_words = [
        "excellent", "great work", "well done", "perfect",
        "amazing", "outstanding", "fantastic", "brilliant",
    ]
    evidence_markers = [
        "because", "since", "as .{0,20} shown", "证据", "验证",
        "confirmed", "tested", "measured", "demonstrated", "proved",
    ]
    flags = []
    for pw in praise_words:
        pattern = re.compile(rf"\b{re.escape(pw)}\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            after = text[m.end():m.end() + 200]
            has_evidence = any(
                re.search(em, after, re.IGNORECASE) for em in evidence_markers
            )
            if not has_evidence:
                flags.append(
                    f"UNSUBSTANTIATED: '{m.group()}' without evidence linkage"
                )
                break  # One flag per praise word type
    return flags


def check_omission(text: str) -> list[str]:
    """Detect errors present but not addressed in completion summary."""
    flags = []
    has_error = bool(
        re.search(r"\b(error|fail|exception|traceback|denied|blocked)\b",
                  text, re.IGNORECASE)
    )
    has_completion = bool(
        re.search(r"\b(completed?|done|finished|success|完成|✅)\b",
                  text, re.IGNORECASE)
    )
    if has_error and has_completion:
        addressed = re.search(
            r"\b(error|fail).{0,150}(fix|resolv|handl|recover|mitigat|workaround)",
            text, re.IGNORECASE,
        )
        if not addressed:
            flags.append("OMISSION: errors present but unaddressed in completion")
    return flags


def check_hedging_after_error(text: str) -> list[str]:
    """Hedging language within 300 chars after a tool/operation error."""
    flags = []
    error_positions = [
        m.end()
        for m in re.finditer(
            r"\b(error|fail|exception|traceback|denied|blocked)\b",
            text, re.IGNORECASE,
        )
    ]
    hedging = [
        "might have been", "possibly", "could be", "maybe",
        "似乎", "可能", "也许", "应该是",
    ]
    for pos in error_positions[-3:]:  # Last 3 errors only
        after = text[pos:pos + 300]
        for hw in hedging:
            if re.search(re.escape(hw), after, re.IGNORECASE):
                flags.append(f"HEDGING_AFTER_ERROR: '{hw}' within 300 chars of error")
                break
    return flags


def check_claim_evidence_ratio(text: str) -> list[str]:
    """Count claim-like statements vs evidence citations. Flag imbalance."""
    claims = len(re.findall(
        r"\b(capable|verified|proven|confirmed|works?|pass(?:ed)?|done|fixed)\b",
        text, re.IGNORECASE,
    ))
    evidence = len(re.findall(
        r"\b(file|code|line \d+|output|result|log|test|grep|read)\b",
        text, re.IGNORECASE,
    ))
    if claims > 10 and evidence < claims * 0.3:
        return [f"CLAIM_EVIDENCE_RATIO: {claims} claims, {evidence} evidence refs"]
    return []


def main() -> None:
    raw = sys.stdin.read()

    # Stop-hook contract: echo stdin to stdout
    sys.stdout.write(raw)

    # Only scan the last 30000 chars (recent turns)
    tail = raw[-30000:] if len(raw) > 30000 else raw

    flags: list[str] = []
    flags.extend(check_praise_without_evidence(tail))
    flags.extend(check_omission(tail))
    flags.extend(check_hedging_after_error(tail))
    flags.extend(check_claim_evidence_ratio(tail))

    if flags:
        flag_dir = os.path.expanduser("~/.claude/session-data")
        os.makedirs(flag_dir, exist_ok=True)
        log_path = os.path.join(flag_dir, "honesty-flags.jsonl")
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "flag_count": len(flags),
            "flags": flags,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
