# Paper Experiment: Task Specifications (30 tasks)

> Protocol: Each task run in BASELINE (empty CLAUDE.md) and TREATMENT (full framework).
> Assignment: Odd=baseline, Even=treatment. Alternating.
> Scoring: 5-category + 3-gate. See paper-methods-draft.md.

---

## Task 1 [BASELINE] — CSV Stats
**Domain**: Implementation | **Time**: 10 min

Write Python function `summarize_csv(filepath)` that:
1. Reads CSV with columns: date, product, quantity, price
2. Computes: total revenue, top 3 by quantity, avg price per product
3. Returns dict. Handles NaN by skipping row. Type hints + docstring.

---

## Task 2 [TREATMENT] — Async Race Condition
**Domain**: Implementation | **Time**: 15 min

```js
let counter = 0;
async function increment() {
  const current = counter;
  await new Promise(r => setTimeout(r, Math.random() * 10));
  counter = current + 1;
}
```
Fix race condition so counter always = 5. Explain + test.

---

## Task 3 [BASELINE] — React Refactor
**Domain**: Refactoring | **Time**: 20 min

Refactor 200-line Dashboard.jsx into: useDashboardData() hook + DashboardView component. Keep all functionality. Proper patterns.

---

## Task 4 [TREATMENT] — SQL Migration
**Domain**: Architecture | **Time**: 15 min

PostgreSQL migration for subscriptions table: id, user_id (FK), plan_type, started_at, expires_at, auto_renew. Up+Down. Index on user_id+expires_at. CHECK constraint.

---

## Task 5 [BASELINE] — Rate Limiter
**Domain**: Implementation | **Time**: 15 min

Python sliding-window RateLimiter(max_requests, window_seconds). allow_request(client_id) → bool. Thread-safe. Unit tests.

---

## Task 6 [TREATMENT] — API Tests
**Domain**: Implementation | **Time**: 15 min

Unit tests for FastAPI POST /users/{id}/orders endpoint. Cover: happy path, invalid total, user not found, inactive user, DB error.

---

## Task 7 [BASELINE] — REST API Design
**Domain**: Architecture | **Time**: 15 min

OpenAPI 3.0 spec for task management app. CRUD tasks, projects. Filtering, pagination. 3 endpoint examples.

---

## Task 8 [TREATMENT] — Memory Leak
**Domain**: Implementation | **Time**: 15 min

Fix Node.js memory leak: unbounded cache. Implement LRU (max 1000) + TTL (1hr). Test eviction.

---

## Task 9 [BASELINE] — Dockerfile
**Domain**: DevOps | **Time**: 10 min

Multi-stage Dockerfile for Python FastAPI: build→runtime, python:3.12-slim, non-root, health check, layer caching.

---

## Task 10 [TREATMENT] — Pagination
**Domain**: Implementation | **Time**: 10 min

Cursor-based pagination: base64 cursor, next_cursor, has_more. Handle deleted items. PostgreSQL SQL.

---

## Task 11 [BASELINE] — Product Launch
**Domain**: Content | **Time**: 10 min

300-word launch announcement for "MergeFlow" (Git AI merge tool). Target: engineering leads. Excited but professional.

---

## Task 12 [TREATMENT] — Bug Fix Blog
**Domain**: Content | **Time**: 15 min

500-word tech blog: race condition → duplicate orders. Root cause: non-atomic check-then-insert. Fix: ON CONFLICT + idempotency keys.

---

## Task 13 [BASELINE] — Error Messages
**Domain**: Content | **Time**: 10 min

5 user-facing form error messages. Each: what went wrong, how to fix, be kind.

---

## Task 14 [TREATMENT] — Customer Review Reply
**Domain**: Content | **Time**: 10 min

Reply to critical review: API docs incomplete, rate limits unclear, useless errors, slow support. Empathetic, specific commitments.

---

## Task 15 [BASELINE] — CLI Documentation
**Domain**: Content | **Time**: 10 min

Document deployctl --config flag: path, defaults, formats, env override, 3 examples, common errors.

---

## Task 16 [TREATMENT] — Revenue Analysis
**Domain**: Data | **Time**: 10 min

200-row sales CSV. Revenue by product, top 3, monthly trend, declining products (>20% drop). Structured summary.

---

## Task 17 [BASELINE] — Correlation Matrix
**Domain**: Data | **Time**: 15 min

6-variable correlation matrix. Strongest +/- pairs, confounders, control variables for regression. Explain to non-technical stakeholder.

---

## Task 18 [TREATMENT] — Date Cleaning
**Domain**: Data | **Time**: 15 min

Clean inconsistent date formats (ISO, US, EU, human, compact, empty, N/A). Detect format, parse, flag ambiguous, output ISO, report unparseable.

---

## Task 19 [BASELINE] — Survey Analysis
**Domain**: Data | **Time**: 10 min

500-respondent Likert survey. Summary stats, visualization plan, ceiling/floor effects, recommend 3 questions to drop.

---

## Task 20 [TREATMENT] — Anomaly Detection
**Domain**: Data | **Time**: 15 min

Server metrics spike: CPU 95%, mem 95%, req 5/s for 15 min. Classify anomaly type, root cause hypotheses, alert rule with hysteresis, additional metrics needed.

---

## Task 21 [BASELINE] — Monolith vs Microservices
**Domain**: Strategy | **Time**: 15 min

8-engineer startup, 50K LOC Django, 1K→10K users. Evaluate trade-offs. Recommend with rationale + revisit trigger.

---

## Task 22 [TREATMENT] — Feature Prioritization
**Domain**: Strategy | **Time**: 10 min

6-feature backlog, 2 sprints, 4 engineers. Dark mode(3SP), CSV export(2SP), Payment v2(8SP), Onboarding(5SP), Audit log(5SP), Social login(3SP). Rank + state what gets cut.

---

## Task 23 [BASELINE] — Third-Party Risk
**Domain**: Strategy | **Time**: 10 min

Series A startup API as core dependency. 99.5% SLA. No alternative. Technical + business risk assessment. Mitigation plan.

---

## Task 24 [TREATMENT] — A/B Test Design
**Domain**: Strategy | **Time**: 15 min

Landing page A/B: 3.2%→3.7% target, 50K visitors/month, $50K/month value. Sample size, duration, test choice, peeking, early stop criteria.

---

## Task 25 [BASELINE] — Technical Roadmap
**Domain**: Strategy | **Time**: 15 min

3-month roadmap: "real-time game analytics without SDK." 50 customers, 4 engineers. Q1/Q2/Q3 milestones, key decisions, risks, metrics.

---

## Task 26 [TREATMENT] — Design Doc + Estimate
**Domain**: Mixed | **Time**: 20 min

Real-time collaboration feature design: architecture, OT vs CRDT, schema, APIs, story points, risks.

---

## Task 27 [BASELINE] — Feedback + Bug Report
**Domain**: Mixed | **Time**: 15 min

Classify 5 user complaints (bug/UX/feature). Prioritize. Structured bug report for top 2. Quick wins this week.

---

## Task 28 [TREATMENT] — Schema + Queries
**Domain**: Mixed | **Time**: 15 min

Event booking system: users create events, attendees register, waitlist, cancellations. DDL + 3 key queries + indexes.

---

## Task 29 [BASELINE] — Monitoring Dashboard
**Domain**: Mixed | **Time**: 15 min

Web app monitoring dashboard: latency(p50/p95/p99), error rate, request rate, CPU, memory. Alert thresholds. Layout. 3 on-call runbooks.

---

## Task 30 [TREATMENT] — Incident Postmortem
**Domain**: Mixed | **Time**: 15 min

Deploy→latency spike (200ms→8s for 18 min, 2000 requests affected). New index caused bad query plan. Rollback fixed. Timeline, root cause, what went well/wrong, action items.
