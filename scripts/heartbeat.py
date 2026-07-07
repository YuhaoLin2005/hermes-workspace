"""Stop hook: mechanical session heartbeat.
Records objective session metrics — tool-call counts, output length,
complexity indicators — without LLM introspection.
Principle 2 (Mechanical Enforcement) + Principle 5 (Causal Verification).

Reads stdin (transcript), echoes to stdout, appends metrics to heartbeat.jsonl.
"""

import sys
import re
import json
import os
from datetime import datetime, timezone


def count_tool_calls(text: str) -> dict[str, int]:
    """Count tool invocations by type from transcript."""
    counts: dict[str, int] = {}
    for tool in ["Read", "Write", "Edit", "Bash", "Grep", "Glob",
                  "Agent", "WebSearch", "WebFetch", "TaskCreate", "TaskUpdate"]:
        n = len(re.findall(rf'"name":\s*"{tool}"', text))
        if n:
            counts[tool] = n
    return counts


def estimate_output_length(text: str) -> int:
    """Estimate AI output length by finding assistant turn blocks."""
    total = 0
    for m in re.finditer(r'"role":\s*"assistant"', text):
        start = m.end()
        chunk = text[start:start + 5000]
        content_m = re.search(r'"content":\s*"', chunk)
        if content_m:
            total += len(chunk)
    return total


def detect_edit_write_count(text: str) -> int:
    """Count Edit + Write tool calls in recent transcript."""
    tail = text[-20000:] if len(text) > 20000 else text
    edits = len(re.findall(r'"name":\s*"Edit"', tail))
    writes = len(re.findall(r'"name":\s*"Write"', tail))
    return edits + writes


def detect_workflow_agent_count(text: str) -> int:
    """Count Workflow + Agent calls in recent transcript."""
    tail = text[-20000:] if len(text) > 20000 else text
    workflows = len(re.findall(r'"name":\s*"Workflow"', tail))
    agents = len(re.findall(r'"name":\s*"Agent"', tail))
    return workflows + agents


def detect_diverge_triggers(text: str) -> int:
    """Count DIVERGE output markers."""
    return len(re.findall(r"✓DIVERGE", text))


def detect_context_markers(text: str) -> int:
    """Count CONTEXT/THINK/DELIVERY output markers."""
    markers = 0
    for tag in ["✓CONTEXT", "✓THINK", "✓DELIVERY"]:
        markers += len(re.findall(re.escape(tag), text))
    return markers


def estimate_tokens(text: str) -> int:
    """Rough token estimate: chars / 2 for CJK-heavy text."""
    cjk = len(re.findall(r"[一-鿿]", text))
    ascii_chars = len(text) - cjk
    return (cjk // 1) + (ascii_chars // 3)


def main() -> None:
    raw = sys.stdin.read()

    # Stop-hook contract: echo stdin to stdout
    sys.stdout.write(raw)

    tool_counts = count_tool_calls(raw)
    output_len = estimate_output_length(raw)
    edit_count = detect_edit_write_count(raw)
    agent_count = detect_workflow_agent_count(raw)
    diverge_count = detect_diverge_triggers(raw)
    marker_count = detect_context_markers(raw)
    token_est = estimate_tokens(raw)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tools": tool_counts,
        "total_tool_calls": sum(tool_counts.values()),
        "tool_diversity": len(tool_counts),
        "edit_write_count": edit_count,
        "agent_workflow_count": agent_count,
        "output_chars_est": output_len,
        "token_est": token_est,
        "diverge_triggers": diverge_count,
        "context_markers": marker_count,
    }

    log_dir = os.path.expanduser("~/.claude/session-data")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "heartbeat.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
