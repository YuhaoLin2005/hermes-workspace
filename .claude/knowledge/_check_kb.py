"""L1 Mechanical Gate: KB integrity + data-freshness validator.
Run: python _check_kb.py
Exit 0 = PASS, Exit 1 = FAIL (errors), Exit 2 = WARNING-ONLY (warnings but no errors)
"""
import sys, re
from datetime import datetime, timedelta
from pathlib import Path

KB_ROOT = Path(__file__).parent
VALID_DOMAINS = {'experiment', 'platform', 'config', 'architecture', 'narrative', 'tutorial', 'personal'}
VALID_STATUSES = {'active', 'superseded', 'historical'}
HOT_MAX_AGE = 30       # days — hot articles must be <30d old
DASHBOARD_MAX_AGE = 3  # days — dashboard must be <3d fresh (was 7d, tightened 2026-07-25)
DATA_GAP_MAX_AGE = 7   # days — "?" fields must not persist >7d without becoming warnings
DASHBOARD_DATA_MIN_AGE = 3  # days — if synced_at >3d old, DATA_STALE warning (even if last_updated is fresh)


def check_all():
    errors, warnings = [], []

    # ── Phase 1: Structural integrity (unchanged from original) ──
    hot_files = list(KB_ROOT.glob('**/hot.md'))
    if not hot_files:
        errors.append("No hot.md files found")
        return errors, warnings

    for f in hot_files:
        content = f.read_text(encoding='utf-8')
        rel = f.relative_to(KB_ROOT)

        if '```yaml' not in content:
            errors.append(f"{rel}: missing yaml block")
            continue

        for field in ['slug:', 'title:', 'url:', 'date:', 'domain:', 'finding:', 'status:']:
            if field not in content:
                errors.append(f"{rel}: missing field '{field[:-1]}'")

        for m in re.finditer(r'domain:\s*(\w+)', content):
            if m.group(1) not in VALID_DOMAINS:
                errors.append(f"{rel}: invalid domain '{m.group(1)}'")

        for m in re.finditer(r'status:\s*(\w+)', content):
            if m.group(1) not in VALID_STATUSES:
                errors.append(f"{rel}: invalid status '{m.group(1)}'")

        for m in re.finditer(r'date:\s*(\d{4}-\d{2}-\d{2})', content):
            try:
                d = datetime.strptime(m.group(1), '%Y-%m-%d')
                age = (datetime.now() - d).days
                if age > HOT_MAX_AGE:
                    slug_m = re.search(r'slug:\s*(\S+)', content[max(0,m.start()-250):m.start()])
                    warnings.append(f"{rel}: '{slug_m.group(1) if slug_m else '?'}' {age}d old (hot≤{HOT_MAX_AGE}d)")
            except ValueError:
                errors.append(f"{rel}: invalid date '{m.group(1)}'")

    # Cross-reference: claims in hot/warm exist in paper/claims.md
    claims_file = KB_ROOT / 'paper' / 'claims.md'
    known_claims = set()
    if claims_file.exists():
        known_claims.update(re.findall(r'claim-\d+', claims_file.read_text(encoding='utf-8')))

    for f in hot_files + list(KB_ROOT.glob('**/warm.md')):
        content = f.read_text(encoding='utf-8')
        refs = re.findall(r'claims:\s*\[(.*?)\]', content)
        for ref in refs:
            for c in re.findall(r'claim-\d+', ref):
                if c not in known_claims:
                    warnings.append(f"{f.relative_to(KB_ROOT)}: claim '{c}' not in paper/claims.md")

    # Strategy files existence
    strategy_dir = KB_ROOT / 'strategy'
    required_strategy = ['dashboard.md', 'research-pipeline.md', 'content-pipeline.md', 'github-strategy.md']
    for sf in required_strategy:
        sp = strategy_dir / sf
        if not sp.exists():
            errors.append(f"strategy/{sf}: file missing")
            continue
        content = sp.read_text(encoding='utf-8')
        if '```yaml' not in content:
            warnings.append(f"strategy/{sf}: missing yaml block (may be empty)")

    pipeline = strategy_dir / 'research-pipeline.md'
    if pipeline.exists():
        content = pipeline.read_text(encoding='utf-8')
        if 'critical_path:' not in content:
            warnings.append("strategy/research-pipeline.md: missing critical_path")

    # ── Phase 2: Data freshness (NEW — 2026-07-25) ──
    dashboard = strategy_dir / 'dashboard.md'
    if not dashboard.exists():
        return errors, warnings

    content = dashboard.read_text(encoding='utf-8')

    # 2a. synced_at freshness — was the data actually browser-verified recently?
    synced_m = re.search(r'synced_at:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', content)
    if synced_m:
        try:
            synced_dt = datetime.strptime(synced_m.group(1), '%Y-%m-%dT%H:%M:%SZ')
            synced_age = (datetime.now() - synced_dt).days
            if synced_age > DASHBOARD_DATA_MIN_AGE:
                # Check if it was browser-verified or just manually touched
                synced_line_start = max(0, synced_m.start() - 200)
                synced_line_end = min(len(content), synced_m.end() + 200)
                synced_context = content[synced_line_start:synced_line_end]
                if 'browser-verified' not in synced_context:
                    warnings.append(
                        f"strategy/dashboard.md: synced_at={synced_m.group(1)} ({synced_age}d ago) "
                        f"not browser-verified — data may be stale"
                    )
                elif synced_age >= DASHBOARD_DATA_MIN_AGE:
                    warnings.append(
                        f"strategy/dashboard.md: last browser-verified {synced_age}d ago "
                        f"(max {DASHBOARD_DATA_MIN_AGE}d — re-verify with browser)"
                    )
        except ValueError:
            warnings.append("strategy/dashboard.md: invalid synced_at format")

    # 2b. last_updated freshness (tightened from 7d → 3d)
    lu_m = re.search(r'last_updated:\s*(\d{4}-\d{2}-\d{2})', content)
    if lu_m:
        try:
            lu_dt = datetime.strptime(lu_m.group(1), '%Y-%m-%d')
            lu_age = (datetime.now() - lu_dt).days
            if lu_age > DASHBOARD_MAX_AGE:
                warnings.append(
                    f"strategy/dashboard.md: last_updated {lu_age}d ago "
                    f"(max {DASHBOARD_MAX_AGE}d allowed)"
                )
        except ValueError:
            warnings.append("strategy/dashboard.md: invalid last_updated date")
    else:
        warnings.append("strategy/dashboard.md: missing last_updated field")

    # 2c. "?" gap detection — fields that have been unknown for too long
    unknown_fields = re.findall(r'(\w+):\s*\?\s*(?:#.*)?$', content, re.MULTILINE)
    if unknown_fields:
        # Check if there's a gap-since date for unknowns
        gap_m = re.search(r'data_gaps_since:\s*(\d{4}-\d{2}-\d{2})', content)
        gap_start = None
        if gap_m:
            try:
                gap_start = datetime.strptime(gap_m.group(1), '%Y-%m-%d')
            except ValueError:
                pass

        persistent_unknowns = []
        for field in unknown_fields:
            # Skip fields that are inherently manual (followers, stars)
            if field in ('followers', 'total_reactions', 'unread_comments'):
                continue
            persistent_unknowns.append(field)

        if persistent_unknowns:
            gap_age = (datetime.now() - gap_start).days if gap_start else DATA_GAP_MAX_AGE + 1
            if gap_age > DATA_GAP_MAX_AGE:
                warnings.append(
                    f"strategy/dashboard.md: {len(persistent_unknowns)} unknown fields "
                    f"({', '.join(persistent_unknowns[:5])}{'...' if len(persistent_unknowns) > 5 else ''}) "
                    f"unresolved for {gap_age}d (max {DATA_GAP_MAX_AGE}d)"
                )

    # 2d. Article count consistency: dashboard vs article indices
    devto_idx = KB_ROOT / 'devto' / 'articles.md'
    juejin_idx = KB_ROOT / 'juejin' / 'articles.md'

    for idx_path, dash_key, platform in [
        (devto_idx, 'devto', 'DEV.to'),
        (juejin_idx, 'juejin', '掘金'),
    ]:
        if not idx_path.exists():
            warnings.append(f"{platform} article index missing: {idx_path}")
            continue

        idx_content = idx_path.read_text(encoding='utf-8')
        # Count articles by finding ### [slug] headers in the index
        idx_count = len(re.findall(r'^###\s+\[', idx_content, re.MULTILINE))

        # Extract dashboard claim
        dash_count_m = re.search(
            rf'{dash_key}:\s*\n\s+articles:\s*(\d+)', content
        )
        if dash_count_m:
            dash_count = int(dash_count_m.group(1))
            if dash_count != idx_count:
                errors.append(
                    f"strategy/dashboard.md: {platform} article count mismatch — "
                    f"dashboard says {dash_count}, index has {idx_count}"
                )

    # 2e. Total reads sanity: dashboard total_reads should be >= sum of individual reads
    # (reads grow over time; dashboard total is from platform, individual from last check)
    for idx_path, dash_key, platform in [
        (juejin_idx, 'juejin', '掘金'),
    ]:
        if not idx_path.exists():
            continue
        idx_content = idx_path.read_text(encoding='utf-8')
        # Sum individual reads from articles index
        individual_reads = sum(
            int(m) for m in re.findall(r'\*\*阅读\*\*:\s*(\d+)', idx_content)
        )
        dash_reads_m = re.search(
            rf'{dash_key}:\s*\n\s+total_reads:\s*(\d+)', content
        )
        if dash_reads_m and individual_reads > 0:
            dash_reads = int(dash_reads_m.group(1))
            if dash_reads < individual_reads:
                warnings.append(
                    f"strategy/dashboard.md: {platform} total_reads ({dash_reads}) < "
                    f"sum of individual article reads ({individual_reads}) — "
                    f"dashboard may be stale"
                )

    return errors, warnings


if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    errors, warnings = check_all()
    print(f"KB Check: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print(f"  [ERR] {e}")
    for w in warnings:
        print(f"  [WARN] {w}")
    if errors:
        print("RESULT: FAIL")
        sys.exit(1)
    if warnings:
        print("RESULT: WARNINGS (exit 2)")
        sys.exit(2)
    print("RESULT: PASS")
