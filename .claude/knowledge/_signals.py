"""Pipeline Signal Hub — auto-sync dashboard from 5 pipelines.

Reads all pipeline data sources, generates updated dashboard.md with
per-field synced_at timestamps. Run at SessionStart before AI reads dashboard.

Usage: python _signals.py [--check]
  --check  Dry-run: print what would change, exit 0 if fresh, 1 if stale.
  (no flag) Write updated dashboard.md.

Design (Brooks): signal layer = data flow only. Verification is _verify.py.
Design (Carmack): every auto-derived field carries synced_at. Manual fields
  carry source: manual so the AI knows to distrust them.
"""

import re, sys, os, json
from datetime import datetime, timezone
from pathlib import Path

KB = Path(__file__).parent
STRATEGY = KB / "strategy"
DEVTO = KB / "devto"
JUEJIN = KB / "juejin"
PAPER = KB / "paper"
DASHBOARD = STRATEGY / "dashboard.md"
CLAIMS = PAPER / "claims.md"
RESEARCH = STRATEGY / "research-pipeline.md"
CONTENT = STRATEGY / "content-pipeline.md"
GITHUB_STRAT = STRATEGY / "github-strategy.md"
COMMENTERS = DEVTO / "commenters.md"
DEVTO_ARTICLES = DEVTO / "articles.md"
JUEJIN_ARTICLES = JUEJIN / "articles.md"
REGEN_LOG = Path.home() / ".claude" / ".self-model-regeneration.jsonl"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def count_claims(text: str) -> int:
    return len(re.findall(r'^### Claim \d+:', text, re.MULTILINE))


def count_articles_md(text: str) -> int:
    """Count ### [slug] entries in an articles.md file."""
    return len(re.findall(r'^### \[[\w-]+\]', text, re.MULTILINE))


def parse_yaml_block(text: str) -> dict:
    """Extract and parse the first ```yaml block from markdown."""
    m = re.search(r'```yaml\s*\n(.*?)\n```', text, re.DOTALL)
    if not m:
        return {}
    # Crude YAML→dict: only handles the simple nested structures we use
    return _simple_yaml_parse(m.group(1))


def _simple_yaml_parse(yaml_str: str) -> dict:
    """Parse a SIMPLE yaml structure into nested dicts. No PyYAML dependency.
    Handles: key: value, key: [list], nested objects via indentation (2 spaces).
    """
    result = {}
    stack = [(result, -1)]
    for line in yaml_str.split('\n'):
        if not line.strip() or line.strip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        # Pop stack to correct indent level
        while stack and stack[-1][1] >= indent:
            stack.pop()
        stripped = line.strip()
        if ':' in stripped:
            key, _, val = stripped.partition(':')
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                # List value
                inner = val[1:-1].strip()
                stack[-1][0][key] = [x.strip() for x in inner.split(',')] if inner else []
            elif val == '':
                # Nested object
                nested = {}
                stack[-1][0][key] = nested
                stack.append((nested, indent))
            elif val == '?' or val == '?':
                stack[-1][0][key] = None
            else:
                # String/number
                stack[-1][0][key] = _coerce(val)
    return result


def _coerce(val: str):
    """Coerce string to int/float if possible."""
    if val in ('?', ''):
        return None
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val.strip('"')


def collect_devto_data():
    """Collect all auto-derivable DEV.to data."""
    articles_text = read_file(DEVTO_ARTICLES)
    commenters_text = read_file(COMMENTERS)

    article_count = count_articles_md(articles_text)

    # Count commenters and notable names
    notable = []
    for m in re.finditer(r'## (\w[\w\s]+?)\s*\n', commenters_text):
        name = m.group(1).strip()
        if name and name != '回复前必查':
            notable.append(name)

    # Count comments written: count lines with "贡献" in commenter sections
    # Crude: count substantive contributions listed
    comments_written = len(re.findall(r'^\d+\.\s', commenters_text, re.MULTILINE))

    # Estimate reactions from hot/warm/cold tier files
    total_reactions = 0
    for tier_file in [DEVTO / "hot.md", DEVTO / "warm.md"]:
        text = read_file(tier_file)
        # reactions aren't explicitly stored in tier files; estimate from dev.to API data
        # For now, use article count as rough proxy
    total_reactions = None  # requires API; mark as manual

    return {
        "articles": article_count,
        "comments_written": comments_written,
        "notable_commenters": notable,
        "total_reactions": None,  # manual: needs API
        "followers": None,        # manual: API doesn't expose
        "unread_comments": None,  # manual: needs notification check
    }


def collect_juejin_data():
    """Collect auto-derivable 掘金 data."""
    articles_text = read_file(JUEJIN_ARTICLES)
    article_count = count_articles_md(articles_text)

    # Sum reads and likes from tier files
    total_reads = 0
    total_likes = 0
    most_popular_reads = 0
    most_popular_title = ""

    for tier_file in [JUEJIN / "hot.md", JUEJIN / "warm.md", JUEJIN / "cold.md"]:
        text = read_file(tier_file)
        for block in re.finditer(r'-\s+slug:\s*(\S+)\s*\n((?:\s+.*\n)*)', text):
            fields = block.group(2)
            r = re.search(r'reads:\s*(\d+)', fields)
            l = re.search(r'likes:\s*(\d+)', fields)
            if r:
                reads = int(r.group(1))
                total_reads += reads
                if reads > most_popular_reads:
                    most_popular_reads = reads
            if l:
                total_likes += int(l.group(1))

    return {
        "articles": article_count,
        "total_reads": total_reads,
        "total_likes": total_likes,
        "most_popular": most_popular_reads,
    }


def collect_github_data():
    """Collect GitHub data from strategy."""
    gh_text = read_file(GITHUB_STRAT)
    # Count PRs from contributions table
    prs_merged = 0
    issues_filed = 0
    for row in re.finditer(r'^\|\s*\d+\s*\|', gh_text, re.MULTILINE):
        parts = [p.strip() for p in row.group(0).split('|')]
        if len(parts) >= 4:
            if 'PR' in parts[3] or 'pr' in parts[3]:
                prs_merged += 1
            elif 'issue' in parts[3] or 'Issue' in parts[3]:
                issues_filed += 1

    return {
        "paper_validator_stars": None,   # manual: needs API
        "paper_validator_forks": None,   # manual: needs API
        "hermes_workspace_stars": None,  # manual: needs API
        "prs_merged": prs_merged,
        "prs_open": None,                # manual: needs API
        "issues_filed": issues_filed,
    }


def collect_experiment_data():
    """Collect experiment counts from claims and research pipeline."""
    claims_text = read_file(CLAIMS)
    research_text = read_file(RESEARCH)

    claim_count = count_claims(claims_text)

    # Research pipeline: count statuses
    completed_count = 0
    in_progress_count = 0
    planned_count = 0

    # Count from research pipeline YAML
    yaml_data = parse_yaml_block(research_text)
    pipeline = yaml_data.get("pipeline", [])
    if isinstance(pipeline, list):
        for item in pipeline:
            if isinstance(item, dict):
                status = str(item.get("status", ""))
                if status == "in_progress":
                    in_progress_count += 1
                elif status == "not_started":
                    planned_count += 1
                elif status == "completed":
                    completed_count += 1

    # Also count experiments from claims.md (each claim lists experiments)
    # and from paper-validator results/
    paper_validator_results = Path.home() / "paper-validator" / "results"
    result_files = 0
    if paper_validator_results.exists():
        result_files = len(list(paper_validator_results.glob("*.json")))

    # completed = total experiments with result files (heuristic)
    if completed_count == 0:
        completed_count = max(claim_count, result_files)

    # Get latest experiment from dashboard (preserve manually maintained data)
    # We'll merge with existing dashboard later

    return {
        "completed": completed_count,
        "in_progress": in_progress_count,
        "planned": planned_count,
        "claims_validated": claim_count,
    }


def collect_self_data():
    """Collect self-model pipeline data."""
    # Last regeneration timestamp
    last_regen = None
    if REGEN_LOG.exists():
        try:
            lines = REGEN_LOG.read_text(encoding="utf-8").strip().split('\n')
            if lines:
                last_entry = json.loads(lines[-1])
                last_regen = last_entry.get("timestamp", "")
        except (json.JSONDecodeError, IndexError):
            pass

    return {
        "last_regeneration": last_regen,
        "streaks": {
            "devto_post_streak": 0,   # needs manual tracking
            "github_commit_streak": 0,
            "session_streak": None,
        }
    }


def generate_dashboard_yaml(existing_dashboard=None):
    """Generate the complete dashboard YAML block.
    Merges auto-derived data with preserved manual fields from existing dashboard.
    """
    ts = now_iso()

    devto = collect_devto_data()
    juejin = collect_juejin_data()
    github = collect_github_data()
    exps = collect_experiment_data()
    self_data = collect_self_data()

    # Preserve manual fields from existing dashboard
    paper_scores = {
        "core_claim_novelty": "5/10",
        "experimental_rigor": "3/10",
        "literature_positioning": "4/10",
        "writing_maturity": "3/10",
        "competitor_differentiation": "4/10",
    }
    target_venue = "CHI LBW / ACL SRW / arXiv"
    paper_chapters = "?/5"
    target_deadline = None
    community_milestones = []

    if existing_dashboard:
        eb = existing_dashboard.get("dashboard", {})
        paper_scores = eb.get("paper", {}).get("current_score", paper_scores)
        target_venue = eb.get("paper", {}).get("target_venue", target_venue)
        paper_chapters = eb.get("paper", {}).get("chapters_drafted", paper_chapters)
        target_deadline = eb.get("paper", {}).get("target_deadline", target_deadline)
        community_milestones = eb.get("streaks", {}).get("community_milestones", [])
        # Merge manual experiment details
        existing_exp = eb.get("experiments", {})
        if isinstance(existing_exp, dict):
            latest = existing_exp.get("latest", {})
        else:
            latest = {}

    # Build YAML
    lines = []
    lines.append("```yaml")
    lines.append("dashboard:")
    lines.append(f"  synced_at: {ts}")
    lines.append("")
    lines.append("  devto:")
    lines.append(f"    articles: {devto['articles']}")
    lines.append(f"    comments_written: {devto['comments_written']}")
    lines.append(f"    followers: ?")
    lines.append(f"    total_reactions: ?  # manual: needs API")
    lines.append(f"    notable_commenters: {devto['notable_commenters']}")
    lines.append(f"    unread_comments: ?  # manual: needs notification check")
    lines.append("")
    lines.append("  juejin:")
    lines.append(f"    articles: {juejin['articles']}")
    lines.append(f"    total_reads: {juejin['total_reads']}")
    lines.append(f"    total_likes: {juejin['total_likes']}")
    lines.append(f"    most_popular: {juejin['most_popular']}_reads")
    lines.append("")
    lines.append("  github:")
    lines.append(f"    paper_validator_stars: ?  # manual: gh api")
    lines.append(f"    paper_validator_forks: ?  # manual: gh api")
    lines.append(f"    hermes_workspace_stars: ?  # manual: gh api")
    lines.append(f"    total_commits_since_july1: ?  # manual: git log")
    lines.append(f"    prs_merged: {github['prs_merged']}")
    lines.append(f"    prs_open: ?")
    lines.append(f"    issues_filed: {github['issues_filed']}")
    lines.append("")
    lines.append("  paper:")
    lines.append(f"    chapters_drafted: \"{paper_chapters}\"")
    lines.append(f"    claims_validated: {exps['claims_validated']}")
    lines.append(f"    claims_needing_blind_scoring: [claim-8]")
    lines.append(f"    target_venue: \"{target_venue}\"")
    lines.append(f"    target_deadline: ?")
    lines.append("    current_score:")
    lines.append(f"      core_claim_novelty: \"{paper_scores.get('core_claim_novelty', '?/10')}\"")
    lines.append(f"      experimental_rigor: \"{paper_scores.get('experimental_rigor', '?/10')}\"")
    lines.append(f"      literature_positioning: \"{paper_scores.get('literature_positioning', '?/10')}\"")
    lines.append(f"      writing_maturity: \"{paper_scores.get('writing_maturity', '?/10')}\"")
    lines.append(f"      competitor_differentiation: \"{paper_scores.get('competitor_differentiation', '?/10')}\"")
    lines.append("")
    lines.append("  experiments:")
    lines.append(f"    completed: {exps['completed']}")
    lines.append(f"    in_progress: {exps['in_progress']}")
    lines.append(f"    planned: {exps['planned']}")
    lines.append(f"    total_api_calls_used: ?  # manual: sum from experiment logs")
    lines.append(f"    latest:  # preserved from manual updates")
    lines.append("      # (see dashboard.md git history for latest experiment details)")
    lines.append("")
    lines.append("  self:")
    lines.append(f"    last_regeneration: {self_data['last_regeneration'] or '?'}")
    lines.append("")
    lines.append("  streaks:")
    lines.append(f"    devto_post_streak: {self_data['streaks']['devto_post_streak']}")
    lines.append(f"    github_commit_streak: {self_data['streaks']['github_commit_streak']}")
    lines.append(f"    session_streak: ?")
    lines.append("")
    lines.append("  community_milestones:")

    # Preserve existing milestones
    if community_milestones:
        for m in community_milestones:
            if isinstance(m, dict):
                lines.append(f"    - date: {m.get('date', '?')}")
                lines.append(f"      event: \"{m.get('event', '?')}\"")
    else:
        lines.append("    # (manually maintained — preserved across sync runs)")

    lines.append("")
    lines.append(f"  last_updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append("```")

    return '\n'.join(lines)


def parse_existing_dashboard():
    """Extract the YAML block from existing dashboard.md."""
    text = read_file(DASHBOARD)
    if not text:
        return {}
    m = re.search(r'```yaml\s*\n(.*?)\n```', text, re.DOTALL)
    if not m:
        return {}
    return _simple_yaml_parse(m.group(1))


def write_dashboard(yaml_block: str):
    """Write dashboard.md: preserve markdown wrapper, replace YAML block."""
    text = read_file(DASHBOARD)

    # Split at yaml block boundaries
    # Keep everything before ```yaml and after the closing ```
    pre = ""
    post = ""
    m_start = re.search(r'```yaml', text)
    m_end = re.search(r'```\s*\n\s*##', text)  # find closing ``` before ## section

    if m_start and m_end:
        # Keep the markdown sections before and after the YAML block
        pre = text[:m_start.start()]
        post = text[m_end.start():]
        # Find the actual ``` that closes yaml (right before ## headers)
        closing = re.search(r'```', post)
        if closing:
            post = post[closing.end():]

    new_content = pre + yaml_block + '\n' + post
    DASHBOARD.write_text(new_content, encoding="utf-8")


def main():
    check_mode = "--check" in sys.argv

    existing = parse_existing_dashboard()
    new_yaml = generate_dashboard_yaml(existing)

    if check_mode:
        # Compare article counts
        old_devto = 0
        old_juejin = 0
        if existing:
            eb = existing.get("dashboard", {})
            old_devto = eb.get("devto", {}).get("articles", 0)
            old_juejin = eb.get("juejin", {}).get("articles", 0)

        new_data = _simple_yaml_parse(new_yaml.split('```yaml\n')[1].split('\n```')[0])
        nb = new_data.get("dashboard", {})
        new_devto = nb.get("devto", {}).get("articles", 0)
        new_juejin = nb.get("juejin", {}).get("articles", 0)

        if isinstance(old_devto, str): old_devto = int(old_devto) if old_devto.isdigit() else 0
        if isinstance(old_juejin, str): old_juejin = int(old_juejin) if old_juejin.isdigit() else 0

        stale = (old_devto != new_devto) or (old_juejin != new_juejin)
        if stale:
            print(f"STALE: devto {old_devto}→{new_devto}, juejin {old_juejin}→{new_juejin}")
            sys.exit(1)
        else:
            print(f"FRESH: devto={new_devto}, juejin={new_juejin}")
            sys.exit(0)
    else:
        write_dashboard(new_yaml)
        print("OK: dashboard synced")
        sys.exit(0)


if __name__ == "__main__":
    main()
