"""L1 Mechanical Gate: KB integrity + data-freshness validator.
Run: python _check_kb.py
Exit 0 = PASS, Exit 1 = FAIL (errors), Exit 2 = WARNING-ONLY (warnings but no errors)

── 平台核验 SOP（2026-09-10 起）─────────────────────────────────────
背景：检查 2d 比的是 dashboard 与索引两份**内部**文档。两者可以完全自洽而同时全错——
2026-09-10 实测：dashboard 说 20，索引说 20，平台已发布 22。漏掉的两篇
（2026-07-26、2026-08-14）无人发现，因为**没有任何检查碰过平台真值**。
对策：2f 锚定平台真值（一个计数），而不是继续互证。

刷新流程（14 天一次，一遍到底，别分次）：
  1. 浏览器登录，一次把下列页面全过：
     · DEV.to dashboard      → profile "N posts published" + 汇总卡各数
     · 掘金 创作者中心 → 内容管理 → 文章管理  ← 计数真值（逐条列状态）
     · 掘金 创作者中心 → 数据中心 → 内容数据  ← 聚合数
     · 掘金 创作者中心 → 数据中心 → 单篇分析  ← 单篇数
  2. 写回：
     · strategy/dashboard.md      → 对应平台段
     · devto/articles.md          → platform_published + last_verified
     · juejin/articles.md         → platform_published + last_verified + 补未入索引的新篇
  3. 跑本脚本 → 应 PASS

口径警告（掘金同一平台自相矛盾）：
  · 「文章管理」的 已发布 N  = **权威**（逐条可核）
  · 「内容数据」的 总文章数  = 不同口径（2026-09-10 实测 31 vs 23），**不采用**

设计约束（勿回退）：
  · 单篇阅读/点赞/收藏/评论**不进索引文件**——它们是派生数据，权威在平台。
    手工拷贝 = O(N) 维护，且陈旧值恒 <= 真值，任何"求和比对"式检查都抓不到它烂掉
    （旧 2e 检查因此删除）。索引只存路由：标题/URL/日期/平台对应/核心。
  · 聚合数字只留在 dashboard.md；单篇数字只留在平台 + dashboard.most_popular 一处。
  · 新增"平台真值"类字段时，用 `key: value` 明文（见 2f 正则），勿藏进 yaml 嵌套。
────────────────────────────────────────────────────────────────
"""
import sys, re
from datetime import datetime, timedelta
from pathlib import Path

# Windows GBK stdout 无法输出中文告警 → 强制 UTF-8（2026-10-09）。
# 病因：本脚本在 Stop hook 里跑，stdout 被捕获；默认 GBK 下中文 WARN 渲染成
# `���� ���� data_gaps_since ê�㣬` —— **门报了什么没人读得懂**，等于没报。
# 实证：Stop hook 实际输出即为此乱码。同源样板：write-guard.py:38-43 /
# bloat-watcher.py:18-22 / harness-pruner.py:45-50 / hook_out.py（已修）。
if sys.platform == "win32":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

KB_ROOT = Path(__file__).parent
VALID_DOMAINS = {'experiment', 'platform', 'config', 'architecture', 'narrative', 'tutorial', 'personal'}
VALID_STATUSES = {'active', 'superseded', 'historical'}
HOT_MAX_AGE = 30       # days — hot articles must be <30d old
DASHBOARD_MAX_AGE = 14  # days — dashboard must be <14d fresh. History: 7d → 3d (2026-07-25 tightening) → 14d (2026-09-10). Platform metrics require manual browser login; real cadence ~10d, so 3d and 7d both misfired on every check.
DATA_GAP_MAX_AGE = 7   # days — "?" fields must not persist >7d without becoming warnings
DASHBOARD_DATA_MIN_AGE = 14  # days — if synced_at >14d old, DATA_STALE warning (even if last_updated is fresh)
INDEX_MAX_AGE = 14     # days — article-index platform cross-check must be <14d old (same cadence as dashboard, so ONE browser pass clears both)


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

        # Empty-hot state: `articles: []` is a valid "no current hot articles" state
        # (publishing lull). Skip the article-field presence check in that case.
        empty_hot = bool(re.search(r'articles:\s*\[\s*\]', content))
        for field in ['slug:', 'title:', 'url:', 'date:', 'domain:', 'finding:', 'status:']:
            if not empty_hot and field not in content:
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
                # 2026-10-12 修：本仓 dashboard 的 synced_at 注释长期写中文「真浏览器核验」，
                # 只认英文 'browser-verified' 会把「核过但超过 14 天」误报成「从未核验」，说假话。
                # 否定环视排除「非/未浏览器核验」这类真正的"未核验"措辞（页脚日志里大量出现）。
                # 2026-10-12 用户裁决「API 为主」：公开 API 覆盖得到的聚合数（dev.to
                # comments/reactions/views、掘金 reads/likes/bookmarks/comments）由
                # `knowledge/_platform_verify.py --write-dashboard` 机械刷新。
                # ⇒ 一次 **API 核验** 同样是核验，也应重置本闸门的年龄。
                # ⛔ 这不是把门放松：API 确实把那几个字段重新量了一遍。**但**必须同时
                #    写明"哪些字段 API 覆盖不到"（followers / 掘金展现数）—— 否则
                #    「只推日期、不写缺口」正是本文件 9/25 警惕的那种假合规。
                #    所以额外要求注释里出现「无对应」或「未覆盖」。
                _verified = ('browser-verified' in synced_context) or bool(
                    re.search(r'(?<![非未])浏览器核验', synced_context)
                )
                _api = bool(re.search(r'(?<![非未])API\s*核验', synced_context))
                if not (_verified or _api):
                    warnings.append(
                        f"strategy/dashboard.md: synced_at={synced_m.group(1)} ({synced_age}d ago) "
                        f"not browser/API-verified — data may be stale"
                    )
                elif _api and not re.search(r'无对应|未覆盖', synced_context):
                    warnings.append(
                        "strategy/dashboard.md: synced_at 标了 API 核验，却**没写明哪些字段 "
                        "API 覆盖不到**（followers / 掘金展现数）—— 「只推日期不写缺口」"
                    )
                elif synced_age >= DASHBOARD_DATA_MIN_AGE:
                    warnings.append(
                        f"strategy/dashboard.md: last verified {synced_age}d ago "
                        f"(max {DASHBOARD_DATA_MIN_AGE}d — re-verify via API or browser)"
                    )
        except ValueError:
            warnings.append("strategy/dashboard.md: invalid synced_at format")

    # 2b. last_updated freshness (7d → 3d on 2026-07-25 → 14d on 2026-09-10)
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
            # Skip fields that are inherently manual (no API/automation)
            if field in ('followers', 'total_reactions', 'unread_comments',
                         'target_deadline', 'total_api_calls_used', 'session_streak'):
                continue
            persistent_unknowns.append(field)

        if persistent_unknowns:
            # ⛔ 2026-10-09 修：原实现是
            #      gap_age = (datetime.now() - gap_start).days if gap_start else DATA_GAP_MAX_AGE + 1
            #    **锚点缺失时凭空造出 8 这个数字**，再当"已 8 天未解"报出来。
            #    实测：dashboard 里根本没有 `data_gaps_since` 字段 ⇒ gap_start 恒 None
            #    ⇒ 报出的 "8d" 是常量：今天 8d，一年后还是 8d。
            #    这属于「用期望值当测量值」——取证动作做全了，唯独没发生那个测量，
            #    而报告里的数字看着像量出来的。**没有锚点就说没有锚点，不许填一个。**
            fields_desc = (f"{len(persistent_unknowns)} unknown fields "
                           f"({', '.join(persistent_unknowns[:5])}"
                           f"{'...' if len(persistent_unknowns) > 5 else ''})")
            if gap_start is None:
                warnings.append(
                    f"strategy/dashboard.md: {fields_desc} —— 且无 `data_gaps_since` 锚点，"
                    f"**年龄未知**（不是 0，也不是 {DATA_GAP_MAX_AGE + 1}；"
                    f"旧版本在此处凭空填了后者并把它当测量值）"
                )
            else:
                gap_age = (datetime.now() - gap_start).days
                if gap_age > DATA_GAP_MAX_AGE:
                    warnings.append(
                        f"strategy/dashboard.md: {fields_desc} unresolved for {gap_age}d "
                        f"(max {DATA_GAP_MAX_AGE}d)"
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

    # 2e. (RETIRED 2026-09-10) Total-reads sanity: dash total_reads >= sum of individual reads.
    # Retired because it could not fail: per-article numbers are always <= live truth, so a
    # stale index passed by construction. The per-article numbers were removed from the index;
    # 2f below anchors to platform ground truth (a COUNT) instead of a sum of rotting copies.

    # 2f. Platform ground-truth anchor: index entry count vs platform_published, + last_verified age.
    # This is the check that would have caught juejin silently missing 2 published articles
    # (2026-07-26, 2026-08-14): dashboard said 20 and the index said 20 — internally consistent,
    # both wrong. Nothing compared either of them to the platform.
    for idx_path, platform in [
        (devto_idx, 'DEV.to'),
        (juejin_idx, '掘金'),
    ]:
        if not idx_path.exists():
            continue
        idx_content = idx_path.read_text(encoding='utf-8')
        idx_count = len(re.findall(r'^###\s+\[', idx_content, re.MULTILINE))
        rel = idx_path.relative_to(KB_ROOT)

        pub_m = re.search(r'platform_published:\s*(\d+)', idx_content)
        if not pub_m:
            warnings.append(
                f"{rel}: no 'platform_published:' anchor — unindexed articles cannot be detected"
            )
        else:
            pub = int(pub_m.group(1))
            if pub != idx_count:
                errors.append(
                    f"{rel}: {platform} index lists {idx_count} articles but platform "
                    f"reports {pub} published — {abs(pub - idx_count)} article(s) unindexed or extra"
                )

        ver_m = re.search(r'last_verified:\s*(\d{4}-\d{2}-\d{2})', idx_content)
        if not ver_m:
            warnings.append(
                f"{rel}: no 'last_verified:' date — platform cross-check has no freshness signal"
            )
        else:
            try:
                ver_age = (datetime.now() - datetime.strptime(ver_m.group(1), '%Y-%m-%d')).days
                if ver_age > INDEX_MAX_AGE:
                    warnings.append(
                        f"{rel}: {platform} platform cross-check {ver_age}d ago "
                        f"(max {INDEX_MAX_AGE}d — re-verify in browser)"
                    )
            except ValueError:
                errors.append(f"{rel}: invalid last_verified date")

    return errors, warnings


# ── 同 session 去重（2026-09-25）──────────────────────────────────────────
# 实证：同一次用户轮次内 `Stop hook feedback` 连拦 4 次（9/24 session 4377e283）；
# 语料全量 **37 次阻塞 : 7 次 informational** —— `stop_hook_active` 不足以保证去重。
# 而 dashboard 新鲜度是**状态**（文件里的日期），不是**本轮行为**：同一 session 内
# 它不会因为 AI 多答一轮而变。故「同一 session 同一条 WARN 只报一次」不损失信息，
# 只砍重复。**阈值 14d 一字不动** —— 调阈值是 7d→3d→14d 三次都没解决症状的老办法。
#
# ⛔ errors 永不去重（错误是本轮可修的，去重会把可修项变静默）。
# ⛔ 拿不到 session_id 时**原样返回** —— 去重失败必须偏保守，宁可吵不可静默。
WARN_STATE = Path.home() / '.claude' / '.kb-warn-reported.json'
PROBE = Path.home() / '.claude' / '.kb-hook-probe.json'

# ── 2026-10-12 · 单槽 → 按 session 分槽（本文件第二次修「假重复」）────────────
# 症状：同一个 session 里 `suppressed` **交替 0/2**，WARN 隔一次就重报 ⇒ 用户看到的
# 就是「一直警告」。探针 5 连发实证：0,2,0,2,0（且 session_id 稳定）。
#
# ⛔ 根因一 = **单槽状态**：旧格式只存一个 `session_id`。只要有**第二个发射方**打同一个
#    Stop hook，它就会反复把槽重置成自己 ⇒ 交替。探针里有**铁证**：两条 payload 含
#    `turn_id`/`model` —— 而真实 Stop payload 的键集是
#    ['background_tasks','cwd','effort','hook_event_name','last_assistant_message',
#     'permission_mode','prompt_id','session_crons','session_id','stop_hook_active',
#     'transcript_path']，**没有** turn_id/model ⇒ 那是**另一个 harness** 在写同一个文件。
#    （09-25「payload 断供」复盘只盯了一个发射方，所以当时看不见这一层。）
# ⛔ 根因二同族 BEH-03：旧码 `except Exception: state = {}` 把**读失败**和**无状态**压成
#    同一个值 ⇒ 一次瞬时读错（Windows 共享冲突/权限抖动）就走成「本 session 还没报过」。
#
# 判据（与 BEH-03 同一把）：**只认 FileNotFoundError 为「确实没有」**；其它 OSError =
# 「读不到」⇒ 偏保守放行 + **不回写**（绝不拿空状态盖掉别人的槽）。
KB_STATE_MAX_SESSIONS = 12


def _load_warn_state():
    """返回 `(state, readable)`。readable=False ⇒ 读失败，调用方**不得**回写。"""
    import json
    try:
        return json.loads(WARN_STATE.read_text(encoding='utf-8')), True
    except FileNotFoundError:
        return {}, True
    except Exception:
        return {}, False


def _migrate_state(raw):
    """旧格式 `{session_id, hashes}` → 新格式 `{sessions:{key:[hash,…]}}`。幂等。"""
    if isinstance(raw, dict) and isinstance(raw.get('sessions'), dict):
        return raw
    raw = raw if isinstance(raw, dict) else {}
    key, hashes = raw.get('session_id'), raw.get('hashes')
    sessions = {key: sorted(set(hashes))} if key and hashes else {}
    return {'sessions': sessions}


def _session_key(p):
    """从 hook payload 取去重键。三级回退，**任何一级拿到值就不用下一级**。

    实测 Stop payload 形状（transcript 语料 860×）：
      ['background_tasks','cwd','effort','hook_event_name','last_assistant_message',
       'permission_mode','prompt_id','session_crons','session_id','stop_hook_active','transcript_path']

    ⛔ 2026-09-25 首版只取 session_id、取不到就静默 early-return ⇒ 生产里状态文件
       从未生成 ⇒ 整个去重是**惰性的**。这正是本系统反复栽的「静默失败」形态。
    ⛔ 2026-09-25 第二版改用 prompt_id 优先，**改错了方向**。运行证据（同 session_id
       `SESS-AAA`、三个不同 prompt_id，模拟连续三轮用户消息）：**rc=2 / rc=2 / rc=2**，
       三轮全拦。原因是 prompt_id 每轮都变 ⇒ 状态里存的是上一轮的键 ⇒ 键不等 ⇒ 状态
       重置 ⇒ 去重归零。它只挡住了「同一轮内连拦 4 次」，而本文件头部设计说明要的是
       「同一 session 同一条 WARN 只报一次」—— 两段注释当时自相矛盾，代码跟了错的那段。
    ⛔ 故 **session_id 优先**（与头部设计说明一致）。session 级不会漏报新问题：
       每条 WARN 单独哈希、累进集合，新出现的 WARN 哈希不在集合里，照样报。
       头部那条「退到 session_id 对可修项太松」的顾虑只对 errors 成立，而第 285 行
       已写死 **errors 永不去重** —— 顾虑与实现不冲突。
    """
    for k in ('session_id', 'prompt_id', 'transcript_path'):
        v = p.get(k)
        if v:
            return f"{k}:{v}"
    return ""


# ⛔ **2026-09-25 现状警告**：以上去重逻辑经回归证明**正确**（`_prove_dedup.py`
#    → rc 2/0/0；`_prove_new_warn.py` → 2/0/1/1，新 WARN 照样报），但**在生产里不可达**：
#    harness 自 14:29:09 起不再向 Stop hook 送 payload ⇒ `_session_key` 恒返回 "" ⇒
#    `_dedup_session` 每轮 early-return ⇒ 状态文件从未生成。
#    证据与排除表见 `memory/growth-log/2026-09-25-stop-payload-hunt.md`。
#    ⛔ 别再改键顺序了 —— 键源本身是空的，改顺序是空转。先看探针 `stdin_bytes`。


def _dedup_session(warnings, session_id, out, payload=None):
    """摘掉本 session 已报过的 WARN。返回剩余 WARN。

    状态按 **session 分槽**（`{'sessions': {key: [hash,…]}}`，最多 `KB_STATE_MAX_SESSIONS`
    个槽，超出丢最旧）。多个发射方各写各的槽、互不重置 —— 单槽格式下它们会互相清空，
    正是「隔一次重报一遍」的成因。
    """
    import json, hashlib
    if not warnings or not session_id:
        _probe(payload, session_id, 0, len(warnings))
        return warnings
    raw, readable = _load_warn_state()
    if not readable:
        # 读不到 ≠ 没报过。偏保守：原样放行，且**不回写**（空状态会盖掉已有槽）。
        _probe(payload, session_id, 0, len(warnings), None, note='state_unreadable')
        return warnings
    state = _migrate_state(raw)
    sessions = state['sessions']
    seen = set(sessions.get(session_id) or [])
    kept, suppressed = [], 0
    for w in warnings:
        h = hashlib.sha1(w.encode('utf-8')).hexdigest()[:12]
        if h in seen:
            suppressed += 1
            continue
        seen.add(h)
        kept.append(w)
    # 本 session 提到队尾（dict 保序 ⇒ 队尾最新），超上限从队首淘汰最旧的槽
    sessions.pop(session_id, None)
    sessions[session_id] = sorted(seen)
    dropped = 0
    while len(sessions) > KB_STATE_MAX_SESSIONS:
        sessions.pop(next(iter(sessions)))
        dropped += 1
    wrote = True
    try:
        WARN_STATE.write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
    except Exception:
        wrote = False
    _probe(payload, session_id, suppressed, len(kept), wrote,
           note=('evicted:%d' % dropped) if dropped else '')
    if suppressed:
        out.write(f"  ({suppressed} WARN 本 session 已报过 — 已抑制)\n")
    return kept


def _probe(payload, key, suppressed, kept, wrote=None, note=''):
    """把「这次 hook 实际收到了什么」落盘。
    ⛔ 用途只有一个：下一次 Stop 点火后 `cat ~/.claude/.kb-hook-probe.json` 就能看到
       harness 真传了哪些键、去重键选成了什么、状态文件写没写成。
       没有它，我们只能靠猜 —— 而今天已经猜错过一次（首版惰性）。"""
    import json, time
    # ⛔ **有界历史，不是单槽**（2026-09-25 第二次踩坑后定稿）。
    #    单槽版有两个失败模式，一天内我都踩了：
    #      ① 命令行手跑（payload 为空）会把 harness 的真实记录冲掉；
    #      ② 我为此加的「空 payload 不写」护栏更糟 —— 它把「harness 传了空 payload」
    #         这个**真相**也一并藏了，导致我对着一个陈旧探针得出错误结论。
    #    仪表的第一职责是不丢证据。history 保留最近 5 条，谁也别想覆盖谁。
    entry = {
        'at': time.strftime('%H:%M:%S'),
        # ⛔ 2026-09-25 新增：`payload_keys: []` 有两种成因，**必须能区分**——
        #    ① stdin 根本没东西（harness 没传）  ② 传了但解析失败（编码错）。
        #    没有字节数就只能看见同一个「空」，把编码 bug 误判成 harness 行为。
        #    字节数 > 0 且 payload_keys == [] ⇒ 是解析失败，不是没传。
        'stdin_bytes': globals().get('_STDIN_BYTES', -1),
        'parse_err': globals().get('_STDIN_ERR', ''),
        'payload_keys': sorted((payload or {}).keys()),
        'chosen_key_prefix': (key or '').split(':', 1)[0],
        'chosen_key_empty': not key,
        # ⛔ 2026-10-12：记**键尾 8 位**。交替重报的根因是「多个发射方共用一个槽」，
        #    而旧探针只记前缀（恒为 'session_id'）⇒ 两个发射方在探针里长得**一模一样**，
        #    所以当时查不出来。仪表必须先能区分两个被试，才谈得上比较。
        'chosen_key_tail': (key or '')[-8:],
        'suppressed': suppressed,
        'reported': kept,
        'state_written': wrote,
        'note': note,
    }
    try:
        try:
            hist = json.loads(PROBE.read_text(encoding='utf-8'))
            if not isinstance(hist, list):
                hist = []
        except Exception:
            hist = []
        hist.append(entry)
        PROBE.write_text(json.dumps(hist[-5:], ensure_ascii=False, indent=1),
                         encoding='utf-8')
    except Exception:
        pass


if __name__ == '__main__':
    import io, json
    # Write ALL output to stderr so Stop hook mechanism surfaces it visibly
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    out = sys.stderr  # redirect to stderr for hook visibility
    # stop_hook_active: harness contract — repeated activation must return 0
    # (prevents warnings-only from locking the turn in an infinite loop)
    stop_hook_active = False
    _p = {}
    # ⚠️ 显式 UTF-8 解码（2026-09-25）。**这不是去重失效的根因** —— 我一开始这么
    #    以为（旧写法 `json.load(sys.stdin)` 走 locale 编码，本机 cp936，而 Stop
    #    payload 带中文 `last_assistant_message`，看着像 UnicodeDecodeError），
    #    但用**真实长度 payload**（2292B，含 ⛔/✅/—/《》/中文路径）实测**被证伪**：
    #    旧写法照样解析成功（keys=7）。GBK 解 UTF-8 中文多数情况不抛异常，只解成乱码。
    #    ⛔ 保留此改动仅因它**本身更正确**（locale 相关解码是潜在坑，乱码会污染
    #    last_assistant_message）；**不要把它当根因写进任何复盘**。
    #    真根因**仍未定**：探针 14:39:39（真实 Stop 链，drift_predictor 同秒写盘可证）
    #    记录 `payload_keys: []` / `state_written: null` ⇒ 那一次 harness 传进来的
    #    stdin **确实是空的**。为什么空，尚未查明。
    # ⛔ 2026-10-12 试探过给这里加"有界读"，**已回滚，不要重做**：
    #    `python _check_kb.py < <(sleep 30)` 确实会挂满 30s，但那个挂是我**自己的测试台**
    #    造出来的（我喂了一个永不关闭的管道），**不是生产里观测到的**。拿它当证据去改，
    #    改法（daemon 线程 + join timeout）反而引入**更坏的**缺陷：
    #    `Fatal Python error: _enter_buffered_busy ... possibly due to daemon threads`
    #    + **段错误 rc=139** —— daemon 线程在解释器退出时仍持有 BufferedReader 锁。
    #    ⇒ **用一个假设的挂死换了一个真实的崩溃。** 判据：自造的单点观测 ≠ 结构性结论；
    #    要修它先要有"生产里真发生过 stdin 缺失"的证据，且改法不得碰 buffered reader 的锁。
    _STDIN_BYTES = 0
    _STDIN_ERR = ''
    try:
        _raw = sys.stdin.buffer.read()
        _STDIN_BYTES = len(_raw)
        if _raw.strip():
            _p = json.loads(_raw.decode('utf-8', errors='replace'))
        stop_hook_active = bool(_p.get("stop_hook_active", False))
    except Exception as exc:
        _STDIN_ERR = '%s: %s' % (type(exc).__name__, exc)
        _p = {}
    session_id = _session_key(_p)
    errors, warnings = check_all()
    warnings = _dedup_session(warnings, session_id, out, _p)
    out.write(f"KB Check: {len(errors)} errors, {len(warnings)} warnings\n")
    for e in errors:
        out.write(f"  [ERR] {e}\n")
    for w in warnings:
        out.write(f"  [WARN] {w}\n")
    if errors:
        out.write("RESULT: FAIL\n")
        sys.exit(1)
    if warnings:
        if stop_hook_active:
            out.write("RESULT: WARNINGS (informational, not re-blocking)\n")
        else:
            out.write("RESULT: WARNINGS (exit 2)\n")
            sys.exit(2)
    out.write("RESULT: PASS\n")
