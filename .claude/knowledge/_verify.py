"""Pipeline Reference Integrity Verifier.

Validates cross-pipeline slug/claim/experiment references are not dangling.
Run at SessionStart after _signals.py. Exit 0 = all refs valid, 1 = warnings found.

Design (Carmack): depends_on targets must be mechanically verifiable, not free text.
Design (Brooks): verification layer = separate from signal layer.

Usage: python _verify.py
"""

import re, sys
from datetime import datetime
from pathlib import Path

KB = Path(__file__).parent
STRATEGY = KB / "strategy"
DEVTO = KB / "devto"
JUEJIN = KB / "juejin"
PAPER = KB / "paper"

CONTENT_PIPELINE = STRATEGY / "content-pipeline.md"
CLAIMS = PAPER / "claims.md"
RESEARCH = STRATEGY / "research-pipeline.md"
DEVTO_ARTICLES = DEVTO / "articles.md"
JUEJIN_ARTICLES = JUEJIN / "articles.md"
COMMENTERS = DEVTO / "commenters.md"


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_slugs(text: str, pattern: str) -> set:
    """Extract all unique slugs matching a regex pattern with one capture group."""
    return set(re.findall(pattern, text, re.MULTILINE))


def extract_yaml_field(text: str, field: str) -> list:
    """Extract list values from a YAML field like 'depends_on: [a, b]'."""
    results = []
    for m in re.finditer(rf'{field}:\s*\[(.*?)\]', text):
        inner = m.group(1)
        if inner.strip():
            results.extend([x.strip() for x in inner.split(',')])
    return results


def check_content_pipeline_deps():
    """Check content-pipeline.md depends_on references."""
    errors = []
    text = read_file(CONTENT_PIPELINE)
    if not text:
        return errors

    claims_text = read_file(CLAIMS)
    research_text = read_file(RESEARCH)

    # Known claim slugs
    claim_slugs = extract_slugs(claims_text, r'slug:\s*([\w-]+)')
    # Known experiment IDs from research pipeline
    exp_ids = extract_slugs(research_text, r'-\s+id:\s*([\w-]+)')

    # Check structured depends_on: claim, experiment, milestone
    for m in re.finditer(r'depends_on:\s*\n\s+claim:\s*(\S+)', text):
        slug = m.group(1)
        if slug and slug not in claim_slugs:
            errors.append(f"content-pipeline: depends_on.claim '{slug}' not found in claims.md")

    for m in re.finditer(r'depends_on:\s*\n\s+experiment:\s*(\S+)', text):
        eid = m.group(1)
        if eid and eid not in exp_ids:
            errors.append(f"content-pipeline: depends_on.experiment '{eid}' not found in research-pipeline.md")

    # milestone-type depends_on = future event, no validation needed
    # Legacy free-text depends_on (list format — deprecated)
    for dep in extract_yaml_field(text, 'depends_on'):
        if dep not in exp_ids and dep not in claim_slugs:
            errors.append(f"content-pipeline: legacy depends_on '[{dep}]' matches no experiment id or claim slug (migrate to structured format)")

    return errors


def check_article_tier_coverage():
    """Check all articles.md slugs appear in exactly one tier file."""
    errors = []

    # DEV.to
    devto_text = read_file(DEVTO_ARTICLES)
    devto_slugs = extract_slugs(devto_text, r'### \[([\w-]+)\]')

    tier_slugs = set()
    for tier_file in [DEVTO / "hot.md", DEVTO / "warm.md", DEVTO / "cold.md"]:
        text = read_file(tier_file)
        tier_slugs.update(extract_slugs(text, r'slug:\s*([\w-]+)'))

    missing = devto_slugs - tier_slugs
    for slug in sorted(missing):
        errors.append(f"devto/articles.md: '{slug}' not in any tier file (hot/warm/cold)")

    # 掘金
    juejin_text = read_file(JUEJIN_ARTICLES)
    juejin_slugs = extract_slugs(juejin_text, r'### \[([\w-]+)\]')

    jj_tier_slugs = set()
    for tier_file in [JUEJIN / "hot.md", JUEJIN / "warm.md", JUEJIN / "cold.md"]:
        text = read_file(tier_file)
        jj_tier_slugs.update(extract_slugs(text, r'slug:\s*([\w-]+)'))

    missing_jj = juejin_slugs - jj_tier_slugs
    for slug in sorted(missing_jj):
        errors.append(f"juejin/articles.md: '{slug}' not in any tier file (hot/warm/cold)")

    return errors


def check_commenter_article_refs():
    """Check commenters.md article references exist in devto/articles.md."""
    errors = []
    commenters_text = read_file(COMMENTERS)
    devto_text = read_file(DEVTO_ARTICLES)
    devto_slugs = extract_slugs(devto_text, r'### \[([\w-]+)\]')

    # Find "出现文章: [slug1] [slug2]" patterns
    for m in re.finditer(r'\*\*出现文章\*?\*?:\s*(.*?)$', commenters_text, re.MULTILINE):
        refs = re.findall(r'\[([\w-]+)\]', m.group(1))
        for ref in refs:
            if ref != 'the-line' and ref not in devto_slugs:
                errors.append(f"commenters.md: article ref '[{ref}]' not found in devto/articles.md")

    return errors


def check_cross_platform_mapping():
    """Check DEV.to↔掘金 mapping references exist on both sides."""
    errors = []
    juejin_text = read_file(JUEJIN_ARTICLES)
    devto_text = read_file(DEVTO_ARTICLES)

    devto_slugs = extract_slugs(devto_text, r'### \[([\w-]+)\]')
    juejin_slugs = extract_slugs(juejin_text, r'### \[([\w-]+)\]')

    # Parse mapping table: | [devto-slug] | [juejin-slug] |
    for m in re.finditer(r'\|\s*\[([\w-]+)\]\s*\|\s*\[([\w-]+)\]', juejin_text):
        devto_ref = m.group(1)
        juejin_ref = m.group(2)
        if devto_ref not in devto_slugs:
            errors.append(f"juejin/articles.md mapping: dev.to slug '[{devto_ref}]' not found in devto/articles.md")
        if juejin_ref not in juejin_slugs:
            errors.append(f"juejin/articles.md mapping: juejin slug '[{juejin_ref}]' not found in juejin/articles.md")

    return errors


def main():
    all_errors = []
    all_errors.extend(check_content_pipeline_deps())
    all_errors.extend(check_article_tier_coverage())
    all_errors.extend(check_commenter_article_refs())
    all_errors.extend(check_cross_platform_mapping())

    if all_errors:
        print(f"VERIFY: {len(all_errors)} reference integrity issue(s):")
        for e in all_errors:
            print(f"  [BROKEN] {e}")
        sys.exit(1)
    else:
        print("VERIFY: PASS — all cross-pipeline references intact")
        sys.exit(0)


if __name__ == "__main__":
    main()
