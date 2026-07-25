#!/usr/bin/env python3
"""check_article_facts.py — Mechanical gate for DEV.to article fact verification.

Scans a DEV.to article draft and mechanically verifies every claim that can be
checked against the filesystem (file existence, data counts, checkpoint files,
numerical claims). No LLM calls. No subagent delegation. No inference.

Exit 0 if all verifiable claims pass. Exit 2 if any claim fails mechanical check.

Importers: Called standalone via `python scripts/check_article_facts.py <draft_path>`
Callers: Pre-publish hook in content pipeline, manual runs before DEV.to push
Not imported as a module. No API calls. No network requests.
Data schemas: None. Reads markdown files, JSONL training data, JSON trainer state,
adapter model files (filesystem existence + size + line count).
Reads: article draft (.md), DPO training data (.jsonl), experiment results (.json/.txt),
articles.md index, cross_model_validation.py source.
Writes: stdout only (pass/fail report).

Why this exists: A subagent once reported "DPO pipeline not yet run" because it
reasoned instead of checking the filesystem. The training data was there (150 pairs
in 82.4KB file, checkpoint-38, 141MB adapter). This script reads the filesystem directly —
it doesn't reason, it checks. Mechanical gates > subagent reasoning.

User verbatim: "如何保证不会再犯" — 要机械方案，不要承诺。发布前跑这个脚本，
exit 2 = 不能发。
"""

import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAPER_VALIDATOR = Path("C:/Users/86131/paper-validator")


# ---------------------------------------------------------------------------
# Individual fact checkers — each returns (passed: bool, detail: str)
# ---------------------------------------------------------------------------

def check_dpo_training_exists() -> tuple[bool, str]:
    """Verify DPO training actually ran (checkpoint + training data)."""
    dpo_dir = PAPER_VALIDATOR / "dpo_training"
    if not dpo_dir.exists():
        return False, f"DPO directory not found: {dpo_dir}"

    # Check training data
    train_file = dpo_dir / "data" / "causal_pairs_train.jsonl"
    test_file = dpo_dir / "data" / "causal_pairs_test.jsonl"
    if not train_file.exists():
        return False, f"Training data missing: {train_file}"

    # Count training pairs
    train_lines = 0
    try:
        with open(train_file, encoding="utf-8") as f:
            train_lines = sum(1 for line in f if line.strip())
    except Exception as e:
        return False, f"Cannot read training data: {e}"

    # Check model checkpoint
    checkpoint_dir = dpo_dir / "models" / "causal-dpo-qwen1.5b" / "checkpoint-38"
    adapter = checkpoint_dir / "adapter_model.safetensors"
    if not adapter.exists():
        return False, f"Checkpoint adapter missing: {adapter}"

    adapter_size_mb = adapter.stat().st_size / (1024 * 1024)

    # Check trainer state for actual training evidence
    trainer_state = checkpoint_dir / "trainer_state.json"
    trained = False
    global_step = None
    if trainer_state.exists():
        try:
            ts = json.loads(trainer_state.read_text(encoding="utf-8"))
            global_step = ts.get("global_step")
            trained = global_step is not None and global_step > 0
        except Exception:
            pass

    if trained:
        return True, (
            f"DPO TRAINED: {train_lines} training pairs, "
            f"checkpoint-38 ({adapter_size_mb:.0f}MB adapter), "
            f"global_step={global_step}"
        )
    else:
        return False, (
            f"DPO checkpoint exists ({adapter_size_mb:.0f}MB) but trainer_state "
            f"shows no completed training steps"
        )


def check_experiment_count_consistency() -> tuple[bool, str]:
    """Verify PAPER.md, README.md, dashboard.md all agree on experiment count."""
    paper_path = REPO / "PAPER.md"
    readme_path = REPO / "README.md"
    dashboard_path = REPO / ".claude" / "knowledge" / "strategy" / "dashboard.md"

    # Count PAPER.md overview rows
    paper_count = 0
    if paper_path.exists():
        text = paper_path.read_text(encoding="utf-8")
        in_table = False
        for line in text.split("\n"):
            if line.startswith("## Experiment Overview"):
                in_table = True
                continue
            if in_table:
                if line.startswith("##") or line.startswith("---"):
                    break
                if line.startswith("|") and not re.match(r"^\|\s*[-:]+\s*\|", line):
                    if "Experiment" in line and "Design" in line:
                        continue
                    paper_count += 1

    # Extract README claim
    readme_count = -1
    if readme_path.exists():
        m = re.search(r"(\d+)\s+experiments?\s+completed", readme_path.read_text(encoding="utf-8"))
        readme_count = int(m.group(1)) if m else -1

    # Extract dashboard claim
    dashboard_count = -1
    if dashboard_path.exists():
        m = re.search(r"completed:\s*(\d+)", dashboard_path.read_text(encoding="utf-8"))
        dashboard_count = int(m.group(1)) if m else -1

    counts = [c for c in [paper_count, readme_count, dashboard_count] if c > 0]
    if len(set(counts)) == 1:
        return True, f"Experiment count consistent: {counts[0]} (paper/README/dashboard)"
    else:
        return False, (
            f"Experiment count MISMATCH: PAPER={paper_count}, "
            f"README={readme_count}, dashboard={dashboard_count}"
        )


def check_article_experiment_count(draft_path: Path) -> tuple[bool, str]:
    """Verify article's experiment count claim matches actual count."""
    text = draft_path.read_text(encoding="utf-8")
    m = re.search(r"(\d+)\s+experiments?", text)
    if not m:
        return True, "No experiment count claim found in article (skip)"

    claimed = int(m.group(1))

    # Get actual count from README
    readme_path = REPO / "README.md"
    actual = -1
    if readme_path.exists():
        rm = re.search(r"(\d+)\s+experiments?\s+completed", readme_path.read_text(encoding="utf-8"))
        actual = int(rm.group(1)) if rm else -1

    if actual == -1:
        return True, f"Article claims {claimed} experiments, cannot verify (skip)"
    elif claimed == actual:
        return True, f"Article experiment count correct: {claimed}"
    else:
        return False, f"Article claims {claimed} experiments, actual count is {actual}"


def check_kappa_values(draft_path: Path) -> tuple[bool, str]:
    """Verify kappa and agreement claims against kappa script output."""
    text = draft_path.read_text(encoding="utf-8")

    # Check if article mentions kappa
    if "κ" not in text and "kappa" not in text.lower():
        return True, "No kappa claim in article (skip)"

    # Check the kappa script output
    kappa_result = REPO / "paper" / "experiment" / "kappa-blind-check-results.txt"
    if not kappa_result.exists():
        return True, "Kappa results file not found, cannot verify mechanically (skip)"

    result_text = kappa_result.read_text(encoding="utf-8")

    # Extract kappa value from result file (handles both "kappa" and Greek "κ")
    kappa_match = re.search(r"(?:Cohen.*?(?:kappa|[κκ]))\s*[:：]\s*([-\d.]+)", result_text)
    if not kappa_match:
        # Fallback: find κ or kappa anywhere in the file
        kappa_match = re.search(r"(?:[κκ]|kappa)\s*[:=＝]\s*([-\d.]+)", result_text)
    agreement_match = re.search(r"raw\s+agreement.*?([\d.]+)", result_text, re.IGNORECASE)
    if not agreement_match:
        agreement_match = re.search(r"(\d+)\s*/\s*(\d+)\s*\(?([\d.]+)", result_text)

    kappa_val = float(kappa_match.group(1)) if kappa_match else None
    agreement_val = float(agreement_match.group(1)) if agreement_match else None

    # Check article claims match computed values
    errors = []
    if kappa_val is not None:
        k_in_article = re.search(r"[κk]appa\s*[=＝]\s*([-\d.]+)", text)
        if k_in_article and float(k_in_article.group(1)) != kappa_val:
            errors.append(f"kappa claimed={k_in_article.group(1)}, computed={kappa_val}")

    if agreement_val is not None:
        # Look for agreement% near words like "agreed", "agreement", or "consistency"
        # within the kappa paragraph, not the first % in the article
        kappa_pos = text.find("κ = 0.00")
        if kappa_pos == -1:
            kappa_pos = text.lower().find("kappa")
        if kappa_pos >= 0:
            context = text[max(0, kappa_pos - 200):kappa_pos + 500]
        else:
            context = text
        # Find a percentage near agreement-related words
        pct_match = re.search(
            r'(?:agreed?|agreement|consistency|accord)[^.]*?(\d+\.?\d*)\s*%',
            context, re.IGNORECASE
        )
        if pct_match:
            claimed_pct = float(pct_match.group(1))
            actual_pct = agreement_val * 100
            if abs(claimed_pct - actual_pct) > 1.0:
                errors.append(f"agreement claimed={claimed_pct}%, computed={actual_pct:.1f}%")

    if errors:
        return False, "; ".join(errors)
    return True, f"Kappa claims verified: kappa={kappa_val}, agreement={agreement_val:.1%}"


def check_article_links_exist(draft_path: Path) -> tuple[bool, str]:
    """Verify all dev.to links in article are registered in articles.md."""
    text = draft_path.read_text(encoding="utf-8")
    devto_urls = re.findall(r'https?://dev\.to/yuhaolin2005/([^\s\)]+)', text)

    articles_md = REPO / ".claude" / "knowledge" / "devto" / "articles.md"
    if not articles_md.exists():
        return True, "articles.md not found, cannot verify links (skip)"

    articles_text = articles_md.read_text(encoding="utf-8")

    missing = []
    for slug in devto_urls:
        slug = slug.rstrip(".)")
        key_slug = slug.split("-")[0] if "-" in slug else slug[:20]
        if key_slug not in articles_text and slug[:30] not in articles_text:
            missing.append(slug)

    if missing:
        return False, f"Links not in articles.md: {missing}"
    return True, f"All {len(devto_urls)} DEV.to links verified in articles.md"


def check_referenced_repos(draft_path: Path) -> tuple[bool, str]:
    """Verify GitHub repos referenced in article actually exist locally."""
    text = draft_path.read_text(encoding="utf-8")
    repo_urls = re.findall(r'github\.com/YuhaoLin2005/([^\s/\)]+)', text)
    unique_repos = set(repo_urls)

    missing = []
    for repo in unique_repos:
        repo = repo.rstrip(".)")
        expected_paths = [
            Path(f"C:/Users/86131/{repo}"),
            Path(f"C:/Users/86131/repos/{repo}"),
        ]
        if not any(p.exists() for p in expected_paths):
            missing.append(repo)

    if missing:
        return False, f"Referenced repos not found locally: {missing}"
    return True, f"All {len(unique_repos)} referenced repos exist locally"


def check_cross_model_script() -> tuple[bool, str]:
    """Verify cross_model_validation.py has --model and --api-key flags."""
    script = REPO / "paper" / "experiment" / "logprob-v3" / "cross_model_validation.py"
    if not script.exists():
        return True, "cross_model_validation.py not found (skip)"

    text = script.read_text(encoding="utf-8")
    has_model = "--model" in text
    has_api_key = "--api-key" in text or "--api_key" in text

    if has_model and has_api_key:
        return True, "cross_model_validation.py: --model and --api-key flags present"
    else:
        missing_flags = []
        if not has_model:
            missing_flags.append("--model")
        if not has_api_key:
            missing_flags.append("--api-key")
        return False, f"cross_model_validation.py missing flags: {missing_flags}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_article_facts.py <article_draft.md>")
        print("Example: python scripts/check_article_facts.py paper/devto-audit-and-blind-scoring.md")
        return 2

    draft_path = Path(sys.argv[1])
    if not draft_path.exists():
        print(f"ERROR: Article draft not found: {draft_path}")
        return 2

    print("=" * 60)
    print(f"Article Fact Check: {draft_path.name}")
    print("=" * 60)
    print()

    # Run all checkers
    checks = [
        ("DPO training status", check_dpo_training_exists),
        ("Experiment count consistency", check_experiment_count_consistency),
        ("Article experiment count", lambda: check_article_experiment_count(draft_path)),
        ("Kappa values", lambda: check_kappa_values(draft_path)),
        ("DEV.to links in articles.md", lambda: check_article_links_exist(draft_path)),
        ("Referenced repos exist", lambda: check_referenced_repos(draft_path)),
        ("cross_model_validation.py flags", check_cross_model_script),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for name, checker in checks:
        try:
            ok, detail = checker()
        except Exception as e:
            ok, detail = False, f"CHECKER CRASHED: {e}"

        if ok and "skip" in detail.lower():
            print(f"  [SKIP] {name}: {detail}")
            skipped += 1
        elif ok:
            print(f"  [PASS] {name}: {detail}")
            passed += 1
        else:
            print(f"  [FAIL] {name}: {detail}")
            failed += 1

    print()
    print("=" * 60)
    if failed == 0:
        print(f"[PASS] All {passed} checks passed ({skipped} skipped). Article facts mechanically verified.")
        return 0
    else:
        print(f"[FAIL] {failed} check(s) failed, {passed} passed, {skipped} skipped.")
        print()
        print("DO NOT PUBLISH until all [FAIL] items are fixed.")
        print("These are mechanical checks against the filesystem — not opinions.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
