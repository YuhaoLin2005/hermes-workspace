"""Pipeline Signal Hub — auto-sync dashboard from 5 pipelines.

Reads all pipeline data sources, generates updated dashboard.md with
per-field synced_at timestamps. Run at SessionStart before AI reads dashboard.

Usage: python _signals.py --check
  --check  Dry-run: print what would change, exit 0 if fresh, 1 if stale.
  (no flag) ⛔ 已拒绝执行 —— 生成路径 2026-09-10 判死（会用 tier 求和覆盖
           人工核实字段）。确要覆盖须显式 --write-override。

Design (Brooks): signal layer = data flow only. Verification is _verify.py.
Design (Carmack): every auto-derived field carries synced_at. Manual fields
  carry source: manual so the AI knows to distrust them.
"""

import re, sys, os, json
from datetime import datetime, timezone
from pathlib import Path

# Windows GBK stdout 无法输出中文 → 强制 UTF-8。
# 2026-10-09：本脚本的 [REFUSED] 拒绝报文含中文，在 UTF-8 捕获（hook / AI 读回）下变乱码，
# 读到的人无法知道它为什么拒绝。写法照抄本机既有样板 write-guard.py:38-43 / bloat-watcher.py:18-22（同一根因）。
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    """生成 dashboard 的 YAML 块。

    ⛔ 2026-10-09 整改：**有现 yaml 块就原样继承，一个字都不改。**
    此前本函数对现文件做破坏性重建，实测一次生成改掉 70 行（42 行是人工浏览器核验的
    原值 + 行尾核对注释）：
      juejin.total_reads 5615→0、total_likes 41→0、prs_merged 4→0、issues_filed 11→0、
      comments_written 49→4、completed 13→19、self.last_regeneration → '?'，
      paper.status 被换成 chapters_drafted，data_gaps_since / career_lock /
      p1_merges_recon / evalscope_next_move 四个顶层块整个丢弃，
      早先当作 vanity 删掉的 session_streak 又被写回 '?'，synced_at 被推进成「现在」。
    根因：collect_* 全是**文本启发式桩**（juejin 从 hot/warm/cold tier 文件求和、
    github 数 markdown 表行数），拿不到真值就返回 0 —— 而生成器把 0 当事实写。
    这是 `empty-result-read-as-zero` 的**生成侧异体**：拿不到 ≠ 是 0。
    现在只有**没有现 yaml 块**时（bootstrap）才用启发式桩造骨架。
    ⚠️ `main() --check` 的比较值**不走本函数**，走 collect_*；否则一继承就新旧恒等，
       检查退化成永远绿的橡皮图章。
    """
    text = read_file(DASHBOARD) or ""
    m = re.search(r'```yaml\s*\n(.*?)\n```', text, re.DOTALL)
    if m:
        return '```yaml\n' + m.group(1) + '\n```'

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


def _leading_int(v):
    """取 YAML 值里行内注释之前的首个整数。

    ⛔ 用 `int(v) if v.isdigit() else 0` 是错的：`_simple_yaml_parse` 不剥行内注释，
      值实际长这样 —— '32  # 2026-08-18 browser-verified (dashboard nav Posts 32)'。
      `.isdigit()` 对整串恒为假 → 旧值被置 0 → `stale` 恒 True →
      **每次 SessionStart 都打印假的 `STALE: devto 0→32`**。
      该假红 2026-09-17 被记为「发现但未修，需用户裁决」，挂到 2026-09-25 才修。
    """
    if isinstance(v, int):
        return v
    m = re.match(r'\s*(-?\d+)', str(v or ''))
    return int(m.group(1)) if m else 0


def main():
    check_mode = "--check" in sys.argv

    # ⛔ 生成路径（无 flag）闸 —— 2026-10-09 加，同日按整改**重写理由**（原病因已修）。
    # 原病因：generate_dashboard_yaml() 对 followers / total_reactions / prs_open /
    #       paper_validator_* / total_commits_since_july1 等**人工核实**字段无条件写死 `?`，
    #       并会用 tier 求和覆盖本文件 ⇒ 结构性恒红环：人填对 → 下轮生成冲掉 →
    #       _check_kb.py 报 unknown field 并计龄（「做对了反而触发告警」的形状）。
    # 现理由（闸**继续保留**，已不再因上述病因）：① `collect_*` 仍是文本启发式桩，
    #       平台聚合数**没有可信来源**，跑一次「同步」只给出「已同步」的假象；
    #       ② 写入端 `write_dashboard()` 靠 `re.search(r'```\s*\n\s*##')` 猜 YAML 块边界，
    #       文件结构一变就可能吃掉正文尾部 —— 这条风险与 YAML 内容无关，改生成器消不掉。
    # 现状：settings.json 只接线 `--check`（走不到本闸），无人调用生成路径。
    if not check_mode and "--write-override" not in sys.argv:
        print("[REFUSED] _signals.py 生成路径已判死：collect_* 是文本启发式桩，"
              "平台聚合数无可信来源，跑它只会产生「已同步」的假象。", file=sys.stderr)
        print("          仅支持 --check。（生成器已改为对现文件逐字节继承，"
              "--write-override 现在是恒等写回；保留该逃生口只为 bootstrap。）",
              file=sys.stderr)
        sys.exit(2)

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

        # ⛔ 比较值必须来自 collect_*，**不能来自 generate_dashboard_yaml() 的产物**。
        #    2026-10-09 起该函数对现文件原样继承（防破坏性重建），拿它的产物比则新旧恒等
        #    → 本检查退化成永远绿的橡皮图章。取「独立算出来的值」才有牙。
        new_devto = collect_devto_data()["articles"]
        new_juejin = collect_juejin_data()["articles"]

        # 两侧都要归一 —— 旧值可能带行内注释，不归一比较就永远不等（恒 stale）。
        old_devto, old_juejin = _leading_int(old_devto), _leading_int(old_juejin)
        new_devto, new_juejin = _leading_int(new_devto), _leading_int(new_juejin)

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


def _selftest():
    """两向验 + 对照组。

    ⛔ 为什么必须带对照组：修 `_leading_int` 之后，线上这条检查从「恒红」变成「绿」。
       如果不证明「计数真的不等时它仍会红」，那这次修复就可能只是把一条检查
       改成了橡皮图章 —— 永远绿的检查比没有更糟。
       对照组 = 把**旧写法**一起跑，证明它确实算错；它若算对，说明这条自测
       测不到原 bug，自测本身就是失效的。
    """
    cases = [
        ("32  # 2026-08-18 browser-verified (dashboard nav Posts 32)", 32, "真值·英文行内注释"),
        ("22  # 2026-09-10 平台权威口径（文章管理页…）", 22, "真值·中文行内注释"),
        (32, 32, "int 直通"),
        ("0", 0, "零"),
        ("", 0, "空串"),
        (None, 0, "None"),
        ("  -3  # x", -3, "负号+空白"),
        ("abc", 0, "非数字"),
    ]
    bad = []
    for raw, want, why in cases:
        got = _leading_int(raw)
        if got != want:
            bad.append(f"_leading_int({raw!r}) = {got}, 期望 {want}  [{why}]")

    # 对照组 1：旧写法对真值取到的不是 32 —— 证明这条自测能测到原 bug
    legacy = int(cases[0][0]) if cases[0][0].isdigit() else 0
    if legacy == 32:
        bad.append("对照组失效：旧写法居然算对了 → 这条自测测不到原 bug")
    if legacy != 0:
        bad.append(f"对照组异常：旧写法应得 0，实得 {legacy}")

    # 对照组 2：stale 判据两向 —— 不等要红、相等要绿
    o, n = _leading_int("32  # x"), _leading_int("33  # y")
    if (o != n) is False:
        bad.append("对照：计数不等（32 vs 33）时未判 STALE")
    o2, n2 = _leading_int("32  # x"), _leading_int("32  # y")
    if (o2 != n2) is True:
        bad.append("对照：计数相等（32 vs 32）时误判 STALE")

    for b in bad:
        print(f"  FAIL {b}")
    print(f"SELFTEST: {'PASS' if not bad else 'FAIL'} ({len(cases)} 用例 + 2 对照组)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    main()
