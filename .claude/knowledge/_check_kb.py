"""L1 Mechanical Gate: KB integrity validator.
Run: python _check_kb.py
Exit 0 = PASS, Exit 1 = FAIL (errors found)
"""
import sys, re
from datetime import datetime
from pathlib import Path

KB_ROOT = Path(__file__).parent
VALID_DOMAINS = {'experiment', 'platform', 'config', 'architecture', 'narrative', 'tutorial', 'personal'}
VALID_STATUSES = {'active', 'superseded', 'historical'}
HOT_MAX_AGE = 30  # days

def check_all():
    errors, warnings = [], []

    # Check hot files exist and parse
    hot_files = list(KB_ROOT.glob('**/hot.md'))
    if not hot_files:
        errors.append("No hot.md files found")
        return errors, warnings

    for f in hot_files:
        content = f.read_text(encoding='utf-8')
        rel = f.relative_to(KB_ROOT)

        # YAML block exists
        if '```yaml' not in content:
            errors.append(f"{rel}: missing yaml block")
            continue

        # Required fields (mechanical check: field names present)
        for field in ['slug:', 'title:', 'url:', 'date:', 'domain:', 'finding:', 'status:']:
            if field not in content:
                errors.append(f"{rel}: missing field '{field[:-1]}'")

        # Domain validity
        for m in re.finditer(r'domain:\s*(\w+)', content):
            if m.group(1) not in VALID_DOMAINS:
                errors.append(f"{rel}: invalid domain '{m.group(1)}'")

        # Status validity
        for m in re.finditer(r'status:\s*(\w+)', content):
            if m.group(1) not in VALID_STATUSES:
                errors.append(f"{rel}: invalid status '{m.group(1)}'")

        # Hot freshness
        for m in re.finditer(r'date:\s*(\d{4}-\d{2}-\d{2})', content):
            try:
                d = datetime.strptime(m.group(1), '%Y-%m-%d')
                age = (datetime.now() - d).days
                if age > HOT_MAX_AGE:
                    # Find slug near this date
                    slug_m = re.search(r'slug:\s*(\S+)', content[max(0,m.start()-250):m.start()])
                    warnings.append(f"{rel}: '{slug_m.group(1) if slug_m else '?'}' {age}d old (hot≤{HOT_MAX_AGE}d)")
            except ValueError:
                errors.append(f"{rel}: invalid date '{m.group(1)}'")

    # Cross-reference check: claims in hot/warm exist in paper/claims.md
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

    # Strategy files existence + freshness
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

    # Dashboard freshness (≤7 days)
    dashboard = strategy_dir / 'dashboard.md'
    if dashboard.exists():
        content = dashboard.read_text(encoding='utf-8')
        m = re.search(r'last_updated:\s*(\d{4}-\d{2}-\d{2})', content)
        if m:
            try:
                d = datetime.strptime(m.group(1), '%Y-%m-%d')
                age = (datetime.now() - d).days
                if age > 7:
                    warnings.append(f"strategy/dashboard.md: {age}d stale (max 7d allowed)")
            except ValueError:
                warnings.append("strategy/dashboard.md: invalid last_updated date")
        else:
            warnings.append("strategy/dashboard.md: missing last_updated field")

    # Research pipeline: check critical_path exists
    pipeline = strategy_dir / 'research-pipeline.md'
    if pipeline.exists():
        content = pipeline.read_text(encoding='utf-8')
        if 'critical_path:' not in content:
            warnings.append("strategy/research-pipeline.md: missing critical_path")

    return errors, warnings

if __name__ == '__main__':
    errors, warnings = check_all()
    print(f"KB Check: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print(f"  ❌ {e}")
    for w in warnings:
        print(f"  ⚠ {w}")
    if errors:
        print("RESULT: FAIL")
        sys.exit(1)
    print("RESULT: PASS")
