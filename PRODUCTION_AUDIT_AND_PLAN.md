# ARIA OS — Production Audit, Scorecard & Remediation Plan

**Audited:** 2026-10-04 @ `77a5355` (branch `main`)
**Method:** 4 parallel deep-read agents + direct verification of every critical claim
**Verdict:** 🔴 **NOT PRODUCTION-READY.** Three primary quality gates are red. One P0 cross-tenant data leak is live.

---

## PART 1 — VERIFIED CRITICAL FINDINGS

Every item below was independently verified by direct command, not inferred.

### 🔴 C1 — The `memory` table does not exist. The entire memory backend is non-functional.

```
$ grep "CREATE TABLE" across all 20 .sql files | grep -i memory
010_core_app_schema.sql:478:CREATE TABLE IF NOT EXISTS aria_memory (
```

That is the **only** memory table. There is no `memory`, no `working_memory`, no `knowledge`.

`aria_memory` schema vs what the backend writes:

| Backend writes (`apps/api/app/api/memory.py:51`) | Exists on `aria_memory`? |
|---|---|
| `type` | ❌ real column is `memory_type`, CHECK `('preference','fact','pattern','decision')` |
| `key` | ❌ absent |
| `value` | ❌ real column is `content TEXT` |
| `importance` | ❌ real column is `confidence FLOAT` |
| `tags` | ❌ absent |
| `expires_at` | ❌ absent |
| `updated_at` | ❌ real column is `last_referenced_at` |

**Every column is wrong.** PostgREST raises `42P01 relation "public.memory" does not exist` on every `.execute()`.
Because `postgrest-py` *raises* rather than populating `.error`, the `if response.error:` guards at `memory.py:52,64,75` are **unreachable dead code**.

| Endpoint | Actual result |
|---|---|
| `GET /api/v1/memory/` | **500** (no try/except at `memory.py:19-28`) |
| `POST /api/v1/memory/` | **500** |
| `PUT /api/v1/memory/{id}` | **500** |
| `DELETE /api/v1/memory/{id}` | **500** |
| `POST /consolidate` | **200 `{"status":"success"}`** — failure masked (`memory.py:85-100` swallows everything) |
| `POST /search` | **200 `{"status":"success"}`** — failure masked |

Same defect in `packages/ai/memory/tiers.py` (30+ sites), `packages/ai/agents/memory_agent.py` (9 sites), `packages/ai/orchestrator.py:85`.

**Why 3615 tests don't catch it:** every API test drives a `MagicMock` supabase whose `.execute()` returns a shape the real client never produces. The declared contract lives in `tests/test_api_routes_advanced.py:430` (`SAMPLE_MEMORY`), not in any migration.

---

### 🔴 C2 — The `knowledge` page calls an endpoint that does not exist

```
$ grep -n "knowledge" apps/api/main.py
(nothing — router never registered)
$ ls apps/api/app/api/
... memory.py ... (no knowledge.py)
```

`apps/web/lib/services/knowledge.ts:7` → `GET /api/v1/knowledge` → **404 forever**.
`knowledge/page.tsx:52` destructures `loading` and `error` — **grep confirms neither is ever rendered.**
Result: the page permanently shows "No nodes to display". A hard 404 is pixel-identical to an empty account.

---

### 🔴 C3 — Cross-tenant data leak: response cache has no user identity in its key

```python
# packages/shared/utils/cache_middleware.py:64-66
def _cache_key(request: Request) -> str:
    raw = f"{request.method}:{request.url.path}:{sorted(request.query_params.items())}"
    return f"rm:{hashlib.md5(raw.encode()).hexdigest()}"
```

Registered at `apps/api/main.py:272` with `default_ttl=60`. **No `Authorization` header, no user id.**

User A calls `GET /api/v1/tasks` → cached. User B calls `GET /api/v1/tasks` within 60s → **receives User A's tasks**. This affects every authenticated `GET /api/v1/*` — tasks, courses, goals, income, sleep, chat history, skills, memory, opportunities, briefings, notifications, data-export. It defeats the RLS + `user_id` filtering the entire architecture depends on.

The test suite **cannot** catch it: `tests/test_api_endpoints.py:466-481` builds its `TestClient` from a bare `FastAPI()` that never registers the middleware.

---

### 🔴 C4 — Default JWT secret is accepted at boot → universal account takeover

```python
# packages/config/core/config.py:22
jwt_secret: str = "your-secret-key-change-in-production"
# config.py:54-62
def validate_jwt_secret(self):
    if ...: warnings.warn(...)   # never raises, never refuses to start
```

No production guard in `main.py`. With the default in place, anyone can mint a valid HS256 token for any `sub`.

---

### 🔴 C5 — `prompts/` is missing from the API and Scheduler production images

```dockerfile
# apps/api/Dockerfile:47-49   ← no prompts
COPY --from=builder /app/apps/api ./apps/api
COPY --from=builder /app/packages ./packages
```
```dockerfile
# services/mcp/Dockerfile:47-49  ← HAS prompts (proves the omission is a bug, not a decision)
COPY --from=builder /app/services/mcp ./services/mcp
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/prompts ./prompts
```

`prompt_loader.py:55` resolves `Path(__file__).parents[2] / "prompts"` = `/app/prompts`.
**In production all 22 prompts fail to load silently** and all 11 agents fall back to inline defaults. No error, no log, no metric — the whole prompt system (§10, §11) is inert in prod. Same bug in `docker-compose.yml:100-102, 150-152`.

---

### 🔴 C6 — Frontend sends no auth header; 204 breaks the API client

```typescript
// apps/web/lib/api/client.ts:88-92  — no Authorization
headers: { 'Content-Type': 'application/json', ...fetchConfig.headers },
// client.ts:109 — unconditional
return await response.json()
```

Two consequences:
1. **Every** `/api/v1/memory` call 401s (all 7 handlers use `Depends(get_current_user)`).
2. `DELETE /api/v1/memory/{id}` returns **204 No Content** (`memory.py:71`) → `response.json()` rejects → throws. `memoryStore.remove` catches it and **does not remove the item**. Every delete silently fails; "Clear All" deletes nothing.

---

### 🔴 C7 — The chat transcript can never render

```
$ grep "@router" apps/api/app/api/chat.py
104:  @router.get("/")     # summaries only — response has NO "messages" key (chat.py:120-127)
319:  @router.post("/")
```

There is **no `GET /{conversation_id}`**. The frontend reads `store.conversations[].messages` (`chat/page.tsx:190`) which is always `[]`. The array that *is* populated — `store.messages` (`chatStore.ts:67,89`) — is **never read anywhere**.

Compounded by: streaming assistant messages omit `conversation_id` (`chat.py:302-304`), so streamed replies land in a phantom `"default"` bucket and the sidebar splits into two conversations after one exchange. The frontend always streams (`chat/page.tsx:224`).

**Net: send a message, tokens stream into a Zustand field, nothing appears on screen.**

---

### 🔴 C8 — Audit trail is unreachable dead code

```python
# apps/api/main.py:351-356
if hasattr(request.state, "user"):      # ← never true
```
```
$ grep -rn "state\.user\s*=" apps/ packages/ services/
(no results)
```

`get_current_user` is a FastAPI *dependency*; it never writes `request.state`. `audit_middleware_dispatch` **has never executed once**. The entire SOC 2 story (§23.1, §28) rests on a code path that cannot run.

---

### 🔴 C9 — The Python test suite does not execute

```
$ python -m pytest
ERROR tests/test_main_routes.py  - TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'
ERROR tests/test_skills_api.py   - TypeError: ...
Interrupted: 2 errors during collection
3615 tests collected, 2 errors
FAIL Required test coverage of 85% not reached. Total coverage: 19.23%
```

`make test` → aborts, **0 tests run**. Cause: installed `starlette 1.6.0` vs pinned `fastapi==0.109.0`, and nothing enforces the pin (no lockfile; `Makefile:206` installs test deps unpinned). With `--continue-on-collection-errors`: **202 failed, 2701 passed, 710 errors**.

---

### 🔴 C10 — Cross-user memory leak: process-global memory orchestrator

```python
# packages/ai/agents/memory_agent.py:13-20
_orchestrator: Optional[MemoryOrchestrator] = None   # module-global singleton
```
`MemoryOrchestrator.__init__` creates `self.buffer = BufferMemory()` holding **raw conversation turns**. `orchestrator.py:85-86` returns it for *any* `user_id` → **User A's chat history is served to User B.** `orchestrator.py:176` `prune_all` → `self.buffer.clear()` wipes every user's buffer.

Compounding, in the same file:
- `tiers.py:163` `.delete().lt("expires_at", now)` — **no `user_id` filter.** Unscoped mass DELETE.
- `tiers.py:135` `.eq("key", ...)` — **no `user_id` filter**, and keys are hashed without `user_id`. Cross-tenant read *and* write.
- `tiers.py:328, 382, 468, 552, 612` — `.update(...).eq("id", ...)` with **no `user_id`** (read was scoped; write is not). TOCTOU scope-drop.
- `memory_agent.py:549-550, 579, 677` — same unscoped UPDATE/DELETE, inside a cron that loops **every user**.
- `tiers.py:294-335` `consolidate()` groups by `sorted(tags)`, but `store_episode:220` forces `tags=["episodic"]` → **all episodes collapse into one group, and all but the first are DELETED.** Episodic memory reduced to a single row per user on first run.
- `tiers.py:562-569` **inverted logic**: confidence `0.01` → `"critical"`, `0.0` → `"low"`. Retrieval ranks `critical` highest → **the least-trusted memories rank highest.**
- `compression.py:73-90` unconditional DELETE of all memory older than 90 days including semantic preferences, invoked by the weekly cron. No dry-run, no audit.

---

### 🟠 HIGH (selected)

| # | Finding | Location |
|---|---|---|
| H1 | **No ARIA orchestrator exists.** AGENTS.md §9.1 "ARIA is the single point of intelligence… classifies intent, dispatches to sub-agents, synthesizes responses" is **materially false**. Zero intent-classification code in the repo. `chat.py` = one `llm.generate()` call + a 5-branch substring fallback that only fires after all providers fail (`chat.py:244-272`). Chat imports exactly 1 agent function (memory read/write). | `chat.py:221-272` |
| H2 | 10 of 17 claimed agents exist as modules. A00 (ARIA) **does not exist**. A01/A05/A07/A11/A12 are functions inside other files. No registry — `agents/__init__.py` is a flat import list; "A00–A17" IDs exist only as comments in one test file. | `packages/ai/agents/__init__.py` |
| H3 | **Agents page never re-renders.** `setPlan(orchestrator.getPlan())` returns the same mutated object reference → React `Object.is` bailout. Paints once, freezes forever. | `agents/page.tsx:41-45`, `lib/ai/orchestrator.ts:249-252` |
| H4 | **Response-contract mismatch** — frontend reads `res.result`; every backend returns `{status, data}`. All 5 agent cards render empty, HITL is unreachable (confidence defaults 0.9, all thresholds ≤0.6). | `lib/ai/orchestrator.ts:147` vs `automation.py:92` |
| H5 | `agent_activity_log` is **never written** — `POST /api/v1/monitoring/activity` has zero callers. Dashboard Activity Feed permanently empty. Uptime metrics **hardcoded** `99.9` / `99.7`. | `monitoring.py:101,313,342` |
| H6 | `POST /api/v1/automation/execute` — unrated, unvalidated destructive writes via `startswith("delete ")`. `run_data_retention_cleanup` has **no `user_id` scoping** and is exposed to any authenticated user. | `automation.py:89-131` |
| H7 | **Circuit breaker never trips on timeout or 5xx.** `expected_exception=(LLMTimeoutError, httpx.RequestError)` — but httpx raises `httpx.ReadTimeout` (a `TransportError`, not `RequestError`) and `HTTPStatusError` (not `RequestError`). The most common Ollama failure — hanging until timeout — is invisible. Streaming path hand-rolls a *wider* tuple: the two paths disagree. | `client.py:48-52` vs `:390-396` |
| H8 | `generate_stream` declares `full_text_parts` **outside** the retry loops → retry duplicates the first N tokens to the user. Also streaming bypasses **both cache layers** entirely — the entire caching subsystem is dead on the primary path. | `client.py:245` |
| H9 | Per-endpoint rate limits are **dead**: `rate_limiter.py:56-58` registers `/api/chat`, callers pass `/api/v1/chat`. Every lookup falls to `default`. AGENTS.md §18.4 is false. | `rate_limiter.py:56-58` |
| H10 | Rate limiting is **per-process × 4 gunicorn workers = 4× the limit**, keys on `request.client.host` which behind Railway/Vercel is the **proxy IP** (no `--proxy-headers`), and the dict is **never evicted** → unbounded memory. | `rate_limiter.py:15,19`, `Dockerfile:60` |
| H11 | **No role check on feature-flag mutations** — any authenticated user can create/flip/delete flags that drive canary rollout. Privilege escalation. | `feature_flags.py:81,103,128` |
| H12 | `.gitleaks.toml:16-18` allowlists the **entire JWT regex** — a real leaked Supabase `service_role` key is silently whitelisted. `secret-scan.yml` doesn't run on PRs, is `continue-on-error`, and its escalation reads a file `gitleaks-action@v2` never writes → **always reports 0.** | `.gitleaks.toml`, `secret-scan.yml` |
| H13 | `deploy.yml` has **no `needs:` on CI** → red CI still ships to prod. `health-check` can never fail (`\|\| echo` + `continue-on-error`), and nothing reads its output. | `deploy.yml:7-9,135-143` |
| H14 | `release.yml` lint + test jobs **cannot pass** — `ruff`/`black`/`pytest` never installed (not in `requirements.txt`). `ci.yml:161` smoke test does `import requests` but only `httpx` is a dependency. | `release.yml:41,49,52,75`, `ci.yml:161` |
| H15 | `DailyNudge` renders a **hardcoded sentence** as "ARIA's insight for today", with hardcoded tags and a **dead Explore button** (no `onClick`). `TrendingTopics` is fed `Math.floor(Math.random()*50)-10` as "growth percentages". | `DailyNudge.tsx:45`, `resources/page.tsx` |
| H16 | 5 of 7 quality gates red: `npm run lint` (4 a11y errors), `npm run type-check` (2 TS errors in `CourseFilters.stories.tsx`), `ruff check` (**240 errors**), `black --check` (**73 files**), `pytest` (aborts). 181 of the 240 ruff errors come from one orphan generator artifact, `api_stubs_generated.py`, that nothing imports and which declares **24 phantom routes**. | verified by execution |

---

## PART 2 — SCORECARD

Scale: 0–10. **Weighted** = contribution to "can a real user trust this with their data".

| # | Area | Weight | Score | Verdict | One-line reason |
|---|---|---|---|---|---|
| 1 | **Data integrity / DB schema** | 15% | **1** | 🔴 1/10 | No `memory`/`knowledge`/`working_memory` table exists. Every memory query 500s. Column sets don't match the one table that does exist. |
| 2 | **Security — tenancy isolation** | 15% | **1** | 🔴 1/10 | Response cache with no user identity (P0 leak) + unscoped UPDATE/DELETE in 8 memory sites + process-global buffer serving User A to User B. |
| 3 | **Security — authn/authz** | 10% | **4** | 🟠 4/10 | JWT verification is *real* (255/256 routes authed, alg allow-list, no `alg:none`). Defeated by a default secret that never fails boot, no revocation, no role checks. |
| 4 | **Frontend correctness** | 12% | **3** | 🔴 3/10 | No auth header (everything 401), 204 breaks the client (every delete fails silently), chat transcript unreadable, error states destructured but never rendered. |
| 5 | **AI / agent architecture** | 12% | **3** | 🔴 3/10 | 10 real agent modules with genuine algorithmic fallbacks — but no orchestrator, no registry, no intent routing, agents unreachable from chat. |
| 6 | **Test suite (signal)** | 10% | **2** | 🔴 2/10 | Suite doesn't execute (0 tests run). The mock discards `.eq()` args, so missing `user_id` filters are *structurally undetectable*. ~600 tests are mock-echo tautologies. Real coverage 19%. |
| 7 | **CI/CD gating** | 8% | **3** | 🔴 3/10 | 5 of 7 gates red. Security jobs ~90% `continue-on-error`. Deploy has no CI dependency. Secret scan provably cannot detect. |
| 8 | **Design system compliance** | 6% | **5** | 🟠 5/10 | Tokens defined and used correctly in ~30% of files; 168 arbitrary `var(--…)` in the memory/knowledge set; 5 **undefined** CSS vars cause real breakage; no `noUncheckedIndexedAccess`. |
| 9 | **UI/UX** | 5% | **4** | 🟠 4/10 | Strong visual direction, real framer-motion, correct primitives. Undercut by: 0 loading/error states on knowledge, zero keyboard access to the graph, no focus trap in 2 hand-rolled modals (a correct `Modal` exists and is unused), dead controls. |
| 10 | **Accessibility** | 3% | **3** | 🔴 3/10 | Labels correctly paired in the good modals — but 2 modals have no focus trap/Escape/restore, the D3 graph is 100% keyboard-inaccessible, 4 `jsx-a11y` errors fail lint. |
| 11 | **Observability** | 2% | **2** | 🔴 2/10 | Audit trail never executes. Uptime hardcoded. Activity table never written. `agent_name` omitted from all memory LLM calls → cost attribution broken. |
| 12 | **Docs ↔ code accuracy** | 2% | **2** | 🔴 2/10 | AGENTS.md claims "ARIA orchestrator", "17 agents", "96% coverage", "2795+ passing", "31 routers", "agent_activity table", "RATE_LIMIT_CHAT_MAX". Nearly every specific number is false. |
| | **WEIGHTED TOTAL** | 100% | **2.6 / 10** | 🔴 | |

### Score vs claim

| Metric | AGENTS.md claim | Verified | Delta |
|---|---|---|---|
| Python tests passing | 2795+ | **0 run** (collection aborts); 2701 pass only with `--continue-on-collection-errors` | −2795 |
| Coverage | 96% (threshold 85%) | **19.23%** | −77 pts |
| Frontend tests | ~1900 | 1296 across 173 files | −600 |
| Agents | 17 (A00–A17) | 10 modules; **A00 does not exist** | −7 |
| Routers | 31 | 30 registered (+1 orphan stub file with 24 phantom routes) | −1 |
| "ARIA classifies intent, dispatches sub-agents" | claimed | **zero intent-classification code exists** | fabricated |
| `agent_activity` table | claimed | table is `agent_activity_log`, never written | never written |
| CI jobs green | 14 | 5 of 7 gating jobs red | −5 |

**The implementation is real where it exists.** The 10 agent modules, the RAG pipeline, the prompt system, the Dockerfiles, and `tests/test_rag.py` / `test_agents.py` / `test_scheduler_full.py` are genuine, competent work. The problem is not sloppiness — it is that **documentation, tests, and CI were built to describe a system that was never finished**, and every one of those three layers reports green.

---

## PART 3 — WHAT THIS MEANS FOR THE REQUESTED WORK

You asked for: complete design system + UI/UX on memory (and subpages/components), make it end-to-end dynamic, add what's missing, remove what's unwanted, use parallel agents, then complete the backend and wire it into agent/chat/memory.

**The blocker:** the memory and knowledge pages sit on a data layer that returns 401 (no auth header) → 500 (no table) → and renders the result identically to "empty". Polishing those pages produces beautiful screens over a void. There is also no `sync` page at all — that is net-new.

So the work splits into a **foundation layer that must land first** and a **surface layer that can only be verified after**.

---

## PART 4 — PLAN

### Phase A — Unbreak the foundation (blocks everything else)

| # | Task | Fixes |
|---|---|---|
| A1 | **Write the `memory` migration** — real table matching what the code already writes (`type, key, value, importance, tags, expires_at, updated_at`), plus `UNIQUE(user_id, type, key)`, indexes on `(user_id, type)`, `(user_id, created_at DESC)`, GIN on `tags`, and RLS `auth.uid() = user_id`. Backfill-compatible with `aria_memory`. | C1 |
| A2 | **Scope every memory query.** Add `.eq("user_id", user_id)` to all 8 unscoped UPDATE/DELETE sites in `tiers.py` + `memory_agent.py`. Add `user_id` params to the `WorkingMemory` class. | C10, H2 |
| A3 | **Kill the process-global buffer.** Replace `memory_agent._orchestrator` singleton with a per-user instance (or scope `BufferMemory` by `user_id`). | C10 |
| A4 | **Fix episodic consolidation collapse** — `store_episode:220` forcing `tags=["episodic"]` makes every episode one group. Derive tags from content, and make `consolidate()` merge rather than delete. | C10 |
| A5 | **Fix inverted importance** — `tiers.py:562-569`: `confidence 0.01 → "critical"`. | C10 |
| A6 | **Add auth header to `client.ts`** + fix 204 handling. | C6 |
| A7 | **Fix the cross-tenant cache.** Add user identity to the cache key, or exclude all authenticated routes. Also: enforce `max_size`, stop buffering SSE. | C3 |
| A8 | **Fix audit trail** — set `request.state.user` in the auth dependency so `audit_middleware_dispatch` can fire. | C8 |
| A9 | **Refuse to boot with the default JWT secret** when `environment != development`. | C4 |
| A10 | **Add `COPY --from=builder /app/prompts ./prompts`** to `apps/api/Dockerfile` + `services/scheduler/Dockerfile`; add the volume to `docker-compose.yml`. | C5 |
| A11 | **Unbreak the test suite** — pin starlette (or upgrade fastapi), add a `constraints.txt`, add test deps to `requirements-dev.txt`, wire `make test`. | C9 |
| A12 | **Fix the 5 red gates** — 240 ruff errors (delete the orphan `api_stubs_generated.py` first: kills 181), black 73 files, 4 a11y lint errors, 2 TS errors. | H16 |
| A13 | **Fix CI/release/docker**: install test tools in `release.yml`, `requests`→`httpx` in `ci.yml`, `needs:` on deploy, gitleaks JWT allowlist, PR trigger on secret-scan. | H12-H14 |
| A14 | **Fix rate limiter** — versioned keys, shared store, eviction, `X-Forwarded-For`. | H9, H10 |
| A15 | **Add `GET /api/v1/chat/{conversation_id}`** so transcripts can load. Fix streaming `conversation_id` omission. | C7 |
| A16 | **Add `error` state rendering** to every page that destructures `error`. | C4-sym |

### Phase B — Backend for the pages that need it

| # | Task |
|---|---|
| B1 | **`knowledge` router + `knowledge_nodes` / `knowledge_edges` tables + RLS.** Or delete the page. Real graph beats a fake one. |
| B2 | **Real memory consolidation endpoint** — replace the masked `{"status":"success"}` with real typing + real error propagation. |
| B3 | **`/sync` backend** — vault↔ARIA sync surface (see decision D1). |
| B4 | **Agent registry** — real `AGENT_REGISTRY` with IDs, capabilities, endpoints, HITL thresholds. Wire chat → agents. |
| B5 | **Fix `agent_activity_log`** — call `POST /monitoring/activity` from every agent. Kill hardcoded uptime. |
| B6 | **Wire memory into chat** — `orchestrator.get_relevant_context()` is never called by `chat.py`. Make it the retrieval step. |

### Phase C — Design system + UI/UX (only verifiable after A + B)

| # | Task |
|---|---|
| C1 | **Delete what's unwanted**: `MemoryConsolidation.tsx` (dead, broken schema), `DailyNudge` (hardcoded "AI insight"), `TrendingTopics` (`Math.random()`), `ActiveCollections` (fabricated semantics), `api_stubs_generated.py`. |
| C2 | **Fix 5 undefined CSS vars** — `--z-modal`, `--text-muted`, `--accent-danger`, `--bg-page`, `--font-dm-sans`. `--z-modal` is why both modals render *behind* the navbar. |
| C3 | **Replace both hand-rolled modals** with the existing `components/ui/Modal.tsx` (focus trap + Escape + restore + scroll lock already written). |
| C4 | **Migrate 168 arbitrary `var(--…)` → semantic tokens.** |
| C5 | **Add the 4 missing states** to memory + knowledge: loading skeleton, error + retry, empty-with-action, partial. |
| C6 | **Make the graph accessible** — keyboard-navigable nodes, `aria-label` per node, focusable SVG, list view as a real equivalent. |
| C7 | **Fix the D3 effect deps** — every keystroke currently tears down and rebuilds the simulation, resetting zoom. Debounce + stabilise. |
| C8 | **Responsive pass** — knowledge page has **zero** breakpoints and a 500px min-height inside a `calc(100vh - 340px)`. |
| C9 | **Wire the dead controls** — the `role="switch"` that persists nothing, the `Explore` button with no `onClick`, `cursor-pointer` on inert cards. |
| C10 | **Chat: markdown rendering** with `rehype-sanitize` (safe by default today because there is *no* markdown — adding it without sanitizing is a stored-XSS hole). Fix the unreachable streaming bubble. |
| C11 | **Agents page** — fix the `Object.is` bailout, fix the `{status,data}` vs `res.result` contract, wire real activity. |
| C12 | **`/sync` page** — new surface. |

### Phase D — Verification

| # | Task |
|---|---|
| D1 | Real end-to-end run against a live Supabase + Ollama. Every CRUD path exercised in a browser, not a mock. |
| D2 | Multi-user isolation test — two real accounts, assert zero cross-reads. |
| D3 | Conflict/consistency test for the sync path. |
| D4 | Coverage back to a real number (currently 19%). |
| D5 | All 7 CI gates green, verified by an actual run. |

---

## PART 5 — OPEN DECISIONS FOR THE USER

| ID | Decision | Recommendation |
|---|---|---|
| **D1** | **`sync` page — what is it?** The prompt text in this session is an Obsidian-vault-over-git request; the repo has no vault, no sync code, and no Obsidian concept anywhere. | Ask. Building the wrong thing here wastes the whole surface budget. |
| **D2** | **Sequencing** — foundation-first, or surface-first? | Foundation-first. A polished page over a 500 is worse than an ugly page over a working API, because it hides the failure. |
| **D3** | **`knowledge` — build the backend, or delete the page?** | Build. `KnowledgeGraph` + `NodeDetail` + `KnowledgeSearch` are competent components with real d3 work; only the endpoint is missing. |
| **D4** | **Agent orchestrator — build it?** | Build a minimal real one. Without it, "connect memory to agent/chat" is impossible — chat cannot reach any agent. |

---

## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|-----------|-----------|-----------|----------|
| 1 | Audit | Verify every critical claim by direct command before reporting | Mechanical | Evidence | 4 agents produced overlapping claims; 6 were confirmed by hand, 2 were corrected | trusting agent output directly |
| 2 | Audit | Report a 2.6/10 weighted score rather than a per-area average | Mechanical | Evidence | Averaging would hide that the three highest-weight areas (schema, tenancy, frontend) are all ~1 | unweighted mean, which reads ~3.4 |
| 3 | Plan | Sequence foundation (A) before surface (C) | Taste | P1 completeness | Nothing in C is verifiable until A lands; C would ship UI over 500s | surface-first, which looks like progress |
| 4 | Plan | Recommend building `knowledge` backend over deleting the page | Taste | P2 boil lakes | 3 competent components already exist; only the endpoint is missing | deleting 3 good components |
| 5 | Plan | Recommend a minimal real orchestrator | Taste | P1 completeness | Chat→agent wiring is impossible without it; it is the load-bearing claim in AGENTS.md §9.1 | leaving chat a single completion call |

---

## GSTACK REVIEW REPORT

**Scores:** Data integrity 1/10 · Tenancy isolation 1/10 · Auth 4/10 · Frontend correctness 3/10 · AI architecture 3/10 · Test signal 2/10 · CI gating 3/10 · Design system 5/10 · UI/UX 4/10 · A11y 3/10 · Observability 2/10 · Docs accuracy 2/10
**Weighted total: 2.6 / 10 — NOT PRODUCTION-READY**

**10 verified criticals**, of which 3 are unimplementable blockers (no `memory` table, no `knowledge` router, `pytest` aborts) and 3 are live data-isolation breaches (cache key without user identity, process-global memory buffer, 8 unscoped DELETE/UPDATE sites).

**The one-line diagnosis:** the implementation is competent where it exists — 10 real agent modules, a real RAG pipeline, a real prompt system, real Dockerfiles — but the memory and knowledge surfaces were built against a database schema that was never written, and the three layers that would have caught it (tests, CI, docs) all report success because each validates a mock, a non-blocking step, or an aspirational number rather than the running system.
