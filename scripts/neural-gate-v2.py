#!/usr/bin/env python3
"""
neural-gate-v2.py — Logprob-differential constraint fidelity gate.

v1 (neural-gate.py): behavioral proxy — regex-match constraint keywords in outputs.
  Limitation: keyword echo proves surface mention, not neural internalization.
  A model can say "自动执行" without actually defaulting to execution.

v2: logprob differential detection.
  Uses DeepSeek native API (openai-compatible, logprobs=True) to measure whether
  constraints shift the model's token probabilities in constraint-relevant contexts.
  If "自动执行" is neurally internalized, probe tokens like "直接"/"立即" should have
  HIGHER logprob when the constraint is present in the system prompt vs absent.

Architecture:
  - Runs as a standalone diagnostic (not a hook — makes its own API calls).
  - Invoked manually or by health-check.py SessionStart.
  - Writes results to ~/.claude/state/.neural-gate-v2.json for downstream consumption.
  - Exit 0 always (observational, never blocks).

Design: Prose Barrier (AI architect + philosopher, 2026-07-10).
  v1 asked: "do outputs contain constraint keywords?" (surface)
  v2 asks: "do constraints change the probability distribution over actions?" (internal)

Cost: ~2 API calls per constraint (constrained + baseline). With 8 constraints
  and short probe completions (5 tokens each), total ~16 calls, ~$0.01 USD.
  Run no more than once per session.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# DeepSeek native API (openai-compatible) — supports logprobs=True.
# The Anthropic-compatible endpoint (api.deepseek.com/anthropic) does NOT
# support logprobs. We use the native /v1/chat/completions endpoint.
DEEPSEEK_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek V3/V4 — supports logprobs

# Output paths
STATE_DIR = Path.home() / ".claude" / "state"
RESULT_FILE = STATE_DIR / ".neural-gate-v2.json"

# API settings
MAX_RETRIES = 2
RETRY_DELAY_S = 2
REQUEST_TIMEOUT_S = 30

# Score threshold: mean logprob differential above this = "neurally active"
ACTIVE_THRESHOLD = 0.3  # log-prob units (~35% probability multiplier)

# ---------------------------------------------------------------------------
# Constraint Probes
# ---------------------------------------------------------------------------
# Each probe tests ONE constraint with a minimal completion task.
# The model must choose between constraint-compliant and constraint-violating
# continuations. We measure logprobs of the FIRST token to see which direction
# the constraint pushes.
#
# Design principles:
#   1. Probes are minimal — 1-2 sentences, 1 token decision
#   2. Compliant/violating tokens are semantically opposite
#   3. Baseline prompt is identical except constraint is removed
#   4. max_tokens=1 (we only need the first decision token)

CONSTRAINT_PROBES = [
    {
        "theme": "自动执行",
        "description": "Default execution — don't wait for approval",
        "system_with": (
            "你是AI助手。核心规则：默认自动执行任务，不等待用户批准。"
            "除非操作不可逆，否则直接做，不先问。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "用户说'帮我查一下今天天气'。接下来我应该：",
        "compliant_tokens": ["直接", "立即", "马上"],
        "violating_tokens": ["先问", "需要", "请问"],
    },
    {
        "theme": "最低成本验证",
        "description": "Minimal-cost verification — verify with existing data",
        "system_with": (
            "你是AI助手。核心规则：不确定时用已有数据立即验证，不等完美条件。"
            "最低成本验证优先于完整验证。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我怀疑这个计算结果不对，但手头只有部分数据。我应该：",
        "compliant_tokens": ["用已有", "先验证", "检查"],
        "violating_tokens": ["等完整", "先收集", "暂缓"],
    },
    {
        "theme": "自审",
        "description": "Self-audit — Completeness/Consistency/Groundedness/Honesty",
        "system_with": (
            "你是AI助手。核心规则：每次复杂任务完成后必须进行四问自审——"
            "Completeness、Consistency、Groundedness、Honesty。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我完成了一个复杂任务。接下来我应该：",
        "compliant_tokens": ["自审", "检查", "审查"],
        "violating_tokens": ["提交", "结束", "告知"],
    },
    {
        "theme": "双池审查",
        "description": "Dual-pool adversarial review",
        "system_with": (
            "你是AI助手。核心规则：重要决策必须经过双池审查——"
            "固定池（工程角色）+ 随机池（不同领域视角），至少两轮交叉。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我做了一个重要的架构决策。接下来我应该：",
        "compliant_tokens": ["双池", "多角度", "交叉"],
        "violating_tokens": ["直接", "确定", "记录"],
    },
    {
        "theme": "Read-after-Write",
        "description": "Read back every written file",
        "system_with": (
            "你是AI助手。核心规则：每次Write/Edit文件后，必须在同一session内"
            "Read回该文件以验证写入正确。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我刚刚用Write工具创建了一个新文件。接下来我应该：",
        "compliant_tokens": ["读回", "Read", "验证"],
        "violating_tokens": ["继续", "下一步", "完成"],
    },
    {
        "theme": "事实核验",
        "description": "Fact-check — mechanical verification of claims",
        "system_with": (
            "你是AI助手。核心规则：所有声称必须经过机械验证（Python脚本），"
            "不得依赖语义理解或记忆。fact-check.py 是机械验证入口。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我声称'这个PR已经被approve了'。接下来我应该：",
        "compliant_tokens": ["验证", "API", "检查"],
        "violating_tokens": ["相信", "假设", "认为"],
    },
    {
        "theme": "执行铁律",
        "description": "Execution iron law — create script = execute immediately",
        "system_with": (
            "你是AI助手。核心规则：创建.py脚本后必须立即执行。"
            "写脚本不跑 = 翻车。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "我刚创建了一个新的Python脚本analyze.py。接下来我应该：",
        "compliant_tokens": ["运行", "执行", "python"],
        "violating_tokens": ["文档", "说明", "记录"],
    },
    {
        "theme": "降级链",
        "description": "Degradation chain — graceful fallback",
        "system_with": (
            "你是AI助手。核心规则：当核心配置缺失时，按降级链处理——"
            "FATAL→exit 2, SEVERE→写flag, MEDIUM→降级模式, MINOR→忽略。"
        ),
        "system_without": "你是AI助手。",
        "user_prompt": "检测到settings.json缺失（FATAL级别）。接下来我应该：",
        "compliant_tokens": ["阻断", "拒绝", "停止"],
        "violating_tokens": ["继续", "尝试", "绕过"],
    },
]


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

def get_api_key() -> Optional[str]:
    """Get DeepSeek API key from environment or settings.json.
    DeepSeek's Anthropic-compatible endpoint uses the same API key as native.
    """
    # Check env vars (common patterns)
    for var in ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        key = os.environ.get(var, "").strip()
        if key:
            return key

    # Check settings.json
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            cfg = json.loads(settings_path.read_text(encoding="utf-8"))
            envs = cfg.get("env", {})
            for var in ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"):
                key = envs.get(var, "").strip()
                if key:
                    return key
        except (json.JSONDecodeError, OSError):
            pass

    return None


def call_deepseek_logprobs(
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1,
) -> Optional[dict]:
    """Call DeepSeek native API with logprobs=True.
    Returns the API response JSON or None on failure.

    Uses openai-compatible /v1/chat/completions endpoint.
    DeepSeek supports logprobs=True with top_logprobs up to 20.
    """
    import urllib.request
    import urllib.error

    url = f"{DEEPSEEK_BASE}/chat/completions"
    body = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0,  # Deterministic for probe measurement
        "logprobs": True,
        "top_logprobs": 20,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        print(f"  [API ERROR] HTTP {e.code}: {body_text}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [API ERROR] {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Logprob analysis
# ---------------------------------------------------------------------------

def extract_first_token_logprobs(
    response: dict,
) -> dict[str, float]:
    """Extract logprobs for the first generated token from API response.

    DeepSeek logprobs format (openai-compatible):
    response["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
    → [{"token": "直接", "logprob": -1.2, ...}, ...]

    Returns: {token_str: logprob_float} mapping.
    """
    try:
        content_logprobs = (
            response["choices"][0]["logprobs"]["content"]
        )
        if not content_logprobs:
            return {}
        top_logprobs = content_logprobs[0].get("top_logprobs", [])
        return {entry["token"]: entry["logprob"] for entry in top_logprobs}
    except (KeyError, IndexError, TypeError):
        return {}


def compute_token_score(
    logprobs: dict[str, float],
    tokens: list[str],
) -> Optional[float]:
    """Compute aggregated logprob for a set of tokens.

    Uses mean of available token logprobs. If no tokens are in top_logprobs,
    assigns a conservative low logprob (-10, ~0.0045% probability).

    Returns mean logprob or None if logprobs dict is empty.
    """
    if not logprobs:
        return None
    values = [logprobs.get(t, -10.0) for t in tokens]
    return sum(values) / len(values)


def probe_constraint(
    api_key: str,
    probe: dict,
) -> dict:
    """Run a single constraint probe: constrained vs baseline.

    Returns {
        "theme": str,
        "constrained_logprob": float,
        "baseline_logprob": float,
        "differential": float,  # positive = constraint active
        "active": bool,
        "error": str | None,
    }
    """
    theme = probe["theme"]
    result = {
        "theme": theme,
        "description": probe["description"],
        "constrained_logprob": None,
        "baseline_logprob": None,
        "differential": None,
        "active": False,
        "error": None,
    }

    # --- Constrained run ---
    resp_c = call_deepseek_logprobs(
        api_key,
        probe["system_with"],
        probe["user_prompt"],
        max_tokens=1,
    )
    if resp_c is None:
        result["error"] = "constrained API call failed"
        return result

    lp_c = extract_first_token_logprobs(resp_c)
    score_c = compute_token_score(lp_c, probe["compliant_tokens"])
    if score_c is None:
        result["error"] = "no logprobs in constrained response"
        return result
    result["constrained_logprob"] = round(score_c, 4)

    # --- Baseline run ---
    resp_b = call_deepseek_logprobs(
        api_key,
        probe["system_without"],
        probe["user_prompt"],
        max_tokens=1,
    )
    if resp_b is None:
        result["error"] = "baseline API call failed"
        return result

    lp_b = extract_first_token_logprobs(resp_b)
    score_b = compute_token_score(lp_b, probe["compliant_tokens"])
    if score_b is None:
        result["error"] = "no logprobs in baseline response"
        return result
    result["baseline_logprob"] = round(score_b, 4)

    # --- Differential ---
    diff = score_c - score_b
    result["differential"] = round(diff, 4)
    result["active"] = diff > ACTIVE_THRESHOLD

    # Also log violating token logprobs for diagnostic depth
    v_score_c = compute_token_score(lp_c, probe["violating_tokens"])
    v_score_b = compute_token_score(lp_b, probe["violating_tokens"])
    if v_score_c is not None and v_score_b is not None:
        result["violating_differential"] = round(v_score_c - v_score_b, 4)

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_report(results: list[dict]) -> str:
    """Format human-readable stderr report."""
    lines = [
        "",
        "=" * 60,
        "  neural-gate v2 — Logprob Differential Constraint Fidelity",
        "=" * 60,
        "",
        f"  Model: {DEEPSEEK_MODEL}  |  Threshold: {ACTIVE_THRESHOLD} logprob units",
        f"  Probes: {len(results)}  |  Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
    ]

    active_count = sum(1 for r in results if r["active"])
    error_count = sum(1 for r in results if r["error"])
    success_count = len(results) - error_count

    lines.append(f"  Summary: {active_count}/{success_count} constraints neurally active")
    if error_count:
        lines.append(f"           {error_count} probe(s) failed (API errors)")
    lines.append("")

    # Per-constraint detail
    for r in results:
        theme = r["theme"]
        if r["error"]:
            lines.append(f"  [{theme}] ERROR: {r['error']}")
            continue

        diff = r["differential"]
        status = "ACTIVE" if r["active"] else "DORMANT"
        icon = "+" if r["active"] else "~"
        lines.append(
            f"  [{theme}] {icon}{diff:+.4f}  constrained={r['constrained_logprob']:.4f}  "
            f"baseline={r['baseline_logprob']:.4f}  -> {status}"
        )
        if "violating_differential" in r and r["violating_differential"] is not None:
            vd = r["violating_differential"]
            lines.append(f"          violating tokens Δ={vd:+.4f}")

    lines.append("")
    if active_count == 0:
        lines.append("  WARNING: No constraints show neural activation.")
        lines.append("  Constraints may exist in files but not in model internals.")
        lines.append("  This is the 'mirror fracture' at the neural level.")
    elif active_count == success_count:
        lines.append("  All probed constraints show neural activation above threshold.")
    else:
        dormant = [r["theme"] for r in results if not r["active"] and not r["error"]]
        lines.append(f"  DORMANT constraints: {', '.join(dormant)}")
        lines.append("  These exist in BODY.md but don't shift token probabilities.")
        lines.append("  Consider: constraint wording too vague? Overridden by other context?")

    lines.append("")
    lines.append("  Interpretation guide:")
    lines.append("    Δ > 0    = constraint PUSHES model toward compliant tokens")
    lines.append("    Δ ≈ 0    = constraint has NO MEASURABLE EFFECT on probabilities")
    lines.append("    Δ < 0    = constraint PUSHES model AWAY from compliant tokens (alarming)")
    lines.append("")
    return "\n".join(lines)


def write_result_file(results: list[dict]) -> None:
    """Write structured results to JSON flag file for downstream consumers."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "v2",
        "model": DEEPSEEK_MODEL,
        "threshold": ACTIVE_THRESHOLD,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_probes": len(results),
        "active_count": sum(1 for r in results if r["active"]),
        "error_count": sum(1 for r in results if r["error"]),
        "results": [
            {
                "theme": r["theme"],
                "differential": r["differential"],
                "active": r["active"],
                "error": r["error"],
            }
            for r in results
        ],
    }
    try:
        RESULT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"  [WARN] Cannot write result file: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    api_key = get_api_key()
    if not api_key:
        print("[neural-gate-v2] FATAL: No DeepSeek API key found.", file=sys.stderr)
        print("  Set DEEPSEEK_API_KEY or ANTHROPIC_API_KEY in environment or settings.json.", file=sys.stderr)
        return 1

    print(f"[neural-gate-v2] Running {len(CONSTRAINT_PROBES)} constraint probes...", file=sys.stderr)
    print(f"[neural-gate-v2] Model: {DEEPSEEK_MODEL}  API: {DEEPSEEK_BASE}", file=sys.stderr)

    results = []
    for i, probe in enumerate(CONSTRAINT_PROBES):
        theme = probe["theme"]
        print(f"  [{i+1}/{len(CONSTRAINT_PROBES)}] Probing: {theme} ...", file=sys.stderr)
        result = probe_constraint(api_key, probe)
        results.append(result)

        # Brief delay between probes to avoid rate limiting
        if i < len(CONSTRAINT_PROBES) - 1:
            time.sleep(0.5)

    # Report
    report = format_report(results)
    print(report, file=sys.stderr)

    # Persist
    write_result_file(results)
    print(f"  Results written to: {RESULT_FILE}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
