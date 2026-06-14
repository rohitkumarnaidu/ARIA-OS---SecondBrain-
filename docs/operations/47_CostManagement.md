# Cost Management & FinOps Plan

**Document ID:** OPS-47  
**Version:** 1.0  
**Last Updated:** 2026-06-11  
**Owner:** Developer (Solo)  
**Status:** Active  

---

## 1. Executive Summary

### 1.1 Purpose
Track and optimize all costs across Second Brain OS services — ensuring the system remains sustainable on a near-zero budget while maintaining performance, reliability, and room to scale when needed.

### 1.2 FinOps Philosophy
**Spend smart, not zero.** Invest where it matters (AI quality, user experience), save where it doesn't (compute, bandwidth, idle resources). Every dollar saved on infrastructure is a dollar available for better AI or faster development.

### 1.3 Current Monthly Cost Target
**$0–$5/mo** — with AI (Claude API) as the only variable cost.

---

## 2. Cost Inventory

### 2.1 Current Service Costs

| Service | Plan | Monthly Cost | Inclusions (Quotas) | Usage Metrics | Notes |
|---|---|---|---|---|---|
| **Supabase** | Free | $0 | 500 MB DB, 50K auth users, 2 GB bandwidth, 50K edge func invocations | DB size: ~20 MB, Rows: ~2K, Bandwidth: ~200 MB | PostgreSQL + auth + storage |
| **Vercel** | Free (Hobby) | $0 | 100 GB bandwidth, 6000 build minutes/mo, 1 concurrent build | Bandwidth: ~5 GB, Builds: ~200 min | Next.js hosting + edge functions |
| **Railway** | Free | $0 | $5 one-time credit, 500 hrs/mo compute | Hours: ~100 hrs/mo | Backup/fastify API (light usage) |
| **Ollama (Local)** | N/A | $0 | Unlimited local inference | ~5000 reqs/mo (default AI) | Runs on dev machine, zero marginal cost |
| **Anthropic Claude API** | Pay-as-you-go | ~$1.50 | ~$0.015/request (100K input tokens) | ~100 reqs/mo (AI features) | Only when Ollama is insufficient |
| **Resend** | Free | $0 | 100 emails/day, 500 emails total | ~30 emails/day | Transactional + notification emails |
| **GitHub** | Free | $0 | Unlimited repos, 2000 CI min/mo | ~500 min/mo | CI/CD + code hosting |
| **Total** | | **~$1.50/mo** | | | |

### 2.2 Usage Tracking

| Service | How to Check Usage |
|---|---|
| **Supabase** | Dashboard → Settings → Usage → View all metrics |
| **Vercel** | Dashboard → Usage (bandwidth, builds, functions) |
| **Railway** | Dashboard → Usage (compute hours, credits remaining) |
| **Ollama** | Local: `ollama ps` (running models), log files |
| **Anthropic Claude** | Console → Usage (tokens, cost, requests) |
| **Resend** | Dashboard → Activity → Analytics (daily email count) |
| **GitHub** | Settings → Billing & plans → Actions (CI minutes) |

### 2.3 Historical Cost Tracking

| Month | Supabase | Vercel | Railway | Claude | Resend | GitHub | **Total** |
|---|---|---|---|---|---|---|---|
| 2026-01 | $0 | $0 | $0 | $1.20 | $0 | $0 | **$1.20** |
| 2026-02 | $0 | $0 | $0 | $1.50 | $0 | $0 | **$1.50** |
| 2026-03 | $0 | $0 | $0 | $1.10 | $0 | $0 | **$1.10** |
| 2026-04 | $0 | $0 | $0 | $1.80 | $0 | $0 | **$1.80** |
| 2026-05 | $0 | $0 | $0 | $1.40 | $0 | $0 | **$1.40** |
| 2026-06 | $0 | $0 | $0 | — | $0 | $0 | **—** |
| 2026-07 | | | | | | | |
| 2026-08 | | | | | | | |
| 2026-09 | | | | | | | |
| 2026-10 | | | | | | | |
| 2026-11 | | | | | | | |
| 2026-12 | | | | | | | |

---

## 3. Budget Allocation

### 3.1 Monthly Budget

| Category | Budget | Owner | Escalation At | Notes |
|---|---|---|---|---|
| **Infrastructure (hosting)** | $0 (free tier) | Developer | >80% of any free tier limit | Supabase + Vercel + Railway |
| **AI (Claude API)** | $2.50/mo | Developer | Weekly check when > $2.00 | Default to local Ollama first |
| **Email (Resend)** | $0 (free tier) | Developer | >80 emails/day or >400/mo | Batch notifications to reduce |
| **CI/CD (GitHub Actions)** | $0 (free tier) | Developer | >1500 min/mo | Optimize workflows |
| **Domain (future)** | $15/yr | Developer | Annual renewal | Not yet purchased |
| **Total** | **$2.50/mo** | | | **$30/yr + $15 domain = $45/yr max** |

### 3.2 Annual Budget Forecast

| Year | Infrastructure | AI (Claude) | Domain | CI/CD | **Total** |
|---|---|---|---|---|---|
| **2026** | $0 | $30 | $0 | $0 | **$30** |
| **2027** | $0–$60 | $30–$120 | $15 | $0 | **$45–$195** |
| **2028** | $60–$300 | $60–$300 | $15 | $0–$50 | **$135–$665** |

*Escalation assumes user growth or monetization by 2028.*

---

## 4. Cost Optimization Strategies

### 4.1 Infrastructure Optimization

#### Supabase
| Strategy | Impact | Effort |
|---|---|---|
| Stay on free tier as long as physically possible | $25+/mo saved per month delayed | Low |
| Archive old data (>90 days completed tasks, resolved ideas) | Reduces row count 10–30% | Medium |
| Use efficient queries (select specific columns, not `*`) | Reduces compute 5–15% | Low |
| Clean up unused tables/indexes monthly | Reduces storage 5–10% | Low |
| Use views instead of materialized where possible | Reduces storage | Medium |
| **Upgrade trigger:** >80% of any free limit for 2 consecutive checks | Upgrade to Pro ($25/mo) | N/A |

#### Vercel
| Strategy | Impact | Effort |
|---|---|---|
| Optimize build times — use `turbo` for cache | Reduces build minutes 30–50% | Medium |
| Use ISR for static pages (reduce function invocations) | Reduces serverless calls 40–60% | Medium |
| Compress images/assets with `next/image` | Reduces bandwidth 20–40% | Low |
| Prefer Edge functions (cheaper than serverless) | 50% cheaper per invocation | Medium |
| Use incremental static regeneration over SSR | Cost per request ~$0 vs $0.0001 | Low |
| **Upgrade trigger:** >80% bandwidth or builds for 2 months | Upgrade to Pro ($20/mo) | N/A |

#### Railway
| Strategy | Impact | Effort |
|---|---|---|
| Sleep service when inactive for >1 hour | Reduces hours 40–60% | Low (config) |
| Single instance (no HA needed for single user) | $0 saved vs multi-instance | Low |
| Use free credits wisely (don't deploy idle services) | Preserves $5 credit buffer | Low |
| Monitor credit burn rate weekly | Prevents surprise charges | Low |
| **Upgrade trigger:** Need >500 hrs/mo or >1 GB RAM | Upgrade to Developer ($5/mo) | N/A |

### 4.2 AI Cost Optimization

| Strategy | Estimated Savings | Complexity | Implementation |
|---|---|---|---|
| **Default to local Ollama** (free) | ~$30/yr (100% of Claude cost) | Easy | Default AI config; Claude only for complex tasks |
| **Token budget enforcement** | ~20% | Easy | Set max_tokens=4096, cap per-request tokens |
| **Cache common query responses** | ~10% | Medium | In-memory cache layer for frequently asked questions |
| **Context window optimization** | ~15% | Medium | Strip irrelevant context; use sliding window |
| **Batch similar requests** | ~5% | Hard | Queue similar AI tasks and send in one API call |
| **Use shorter system prompts** | ~5% | Easy | Keep system prompts under 500 tokens |
| **Implement request throttling** | ~10% | Medium | Rate-limit AI calls per minute |
| **Total potential savings** | **~50–80%** | | |

**Default AI Routing Logic:**
1. Simple/repetitive tasks → Ollama (local, free)
2. Complex reasoning, code generation, summarization → Claude API
3. If Claude budget > 80% → Degrade gracefully: offer Ollama-only mode

### 4.3 Email Cost Optimization

| Strategy | Impact | Effort |
|---|---|---|
| Stay within 100 emails/day on Resend free tier | $0/mo | Low |
| Batch notifications (single digest email vs individual) | Reduces count 40–60% | Medium |
| Only send P0/P1 notifications (critical only) | Reduces count 30–50% | Low |
| Remove non-critical email triggers (daily summaries) | Reduces count 20–30% | Low |
| Use in-app notifications instead of email when possible | Reduces count 50%+ | Medium |

---

## 5. Cost Monitoring & Alerts

### 5.1 Monitoring Tools

| Service | Monitoring Method | Alert Channel | Frequency |
|---|---|---|---|
| **Supabase usage** | Dashboard + manual cron check | Monthly review notes | Monthly |
| **Vercel usage** | Dashboard + email notifications | Email (automatic at 80%) | Real-time (email) |
| **Railway usage** | Dashboard | Monthly review | Monthly |
| **Claude cost** | Console + custom budget script | Email when > 50% of budget | Weekly |
| **Resend usage** | Dashboard + daily summary | Weekly review | Weekly |
| **GitHub Actions** | Dashboard | Monthly review | Monthly |
| **Ollama** | Local health check | Manual check on issues | As needed |

### 5.2 Alert Thresholds

| Metric | Warning (Yellow) | Critical (Red) | Action on Critical |
|---|---|---|---|
| Supabase storage | > 350 MB (70%) | > 450 MB (90%) | Archive old data or upgrade |
| Supabase row count | > 35K rows (70%) | > 45K rows (90%) | Purge stale data or upgrade |
| Supabase bandwidth | > 1.4 GB (70%) | > 1.8 GB (90%) | Optimize queries/caching |
| Vercel bandwidth | > 70 GB (70%) | > 90 GB (90%) | Compress assets, use CDN |
| Vercel build minutes | > 4200 min (70%) | > 5400 min (90%) | Optimize builds, use caching |
| Railway compute hours | > 350 hrs (70%) | > 450 hrs (90%) | Enable sleep, reduce uptime |
| Railway credits | < $1.50 remaining | < $0.50 remaining | Top up or reduce usage |
| Claude monthly cost | > $2.00 (80%) | > $2.50 (100%) | Switch to Ollama-only mode |
| Resend daily emails | > 80/day (80%) | > 95/day (95%) | Batch or downgrade frequency |
| GitHub Actions minutes | > 1400 min (70%) | > 1800 min (90%) | Optimize CI pipelines |

### 5.3 Cost Review Cadence

| Review Type | Frequency | Participants | Output |
|---|---|---|---|
| **Quick cost check** | Weekly (Mon AM) | Developer | 5-min usage snapshot → AGENTS.md note |
| **Detailed cost review** | Monthly (1st of month) | Developer | Cost report + optimization actions list |
| **Budget planning** | Quarterly (Jan/Apr/Jul/Oct) | Developer | Budget adjustments for next quarter |
| **Infrastructure review** | Annually (Jan) | Developer | Plan upgrades + capacity needs for the year |
| **Upgrade evaluation** | Trigger-based | Developer | Decision doc when any threshold hit |

---

## 6. Upgrade Planning

### 6.1 Upgrade Triggers

| Service | Upgrade Trigger | Target Plan | New Cost | Cost Increase |
|---|---|---|---|---|
| **Supabase** | >80% storage OR >80% row count for 2 months | Pro | $25/mo | +$25/mo |
| **Supabase** | Need PITR (point-in-time recovery) for prod data | Pro | $25/mo | +$25/mo |
| **Supabase** | Need >2 GB bandwidth consistently | Pro | $25/mo | +$25/mo |
| **Vercel** | >80% bandwidth OR >80% build minutes for 2 months | Pro | $20/mo | +$20/mo |
| **Vercel** | Need team features / preview deployments | Pro | $20/mo | +$20/mo |
| **Vercel** | Need >1 concurrent build | Pro | $20/mo | +$20/mo |
| **Railway** | Need >500 compute hours/mo | Developer | $5/mo | +$5/mo |
| **Railway** | Need >1 GB RAM | Developer | $5/mo | +$5/mo |
| **Claude** | Need higher rate limits / lower latency | API Tier | Usage-based | Variable |
| **Resend** | >100 emails/day consistently | Growth | $15/mo | +$15/mo |
| **GitHub** | >2000 CI min/mo | Team | $4/mo | +$4/mo |
| **All combined** | System is monetized / has paying users | Self-funding | Revenue-based | Revenue-covered |

### 6.2 Upgrade Decision Matrix

| Condition | Decision |
|---|---|
| Monthly costs < $5 AND free tiers sufficient | **Stay free** — no action needed |
| Monthly costs $5–$25 AND system actively used | **Upgrade to paid tiers** — necessary growth |
| Monthly costs > $25 | **Evaluate monetization** before upgrading — does value justify cost? |
| System not used for 60+ days | **Pause services, downgrade to free** — idle infrastructure is waste |
| AI costs > 50% of total budget | **Shift to Ollama-first** — Claude only for critical tasks |
| Free tier limit exceeded for 2+ consecutive months | **Trigger upgrade** — base cost justified by active use |

---

## 7. Budget Governance

### 7.1 Cost Allocation

Since Second Brain OS is a solo-dev project:

| Category | Allocation | Payment Method |
|---|---|---|
| **Development cost** | $0 (personal time) | Sweat equity |
| **Infrastructure cost** | $0–$5/mo | Out of pocket (personal card) |
| **AI (Claude) cost** | $0–$2.50/mo | Out of pocket (personal card) |
| **Domain (future)** | $15/yr | Out of pocket (annual) |
| **Total annual out-of-pocket** | **$30–$75/yr** | |

### 7.2 Cost Recovery Options (if monetized)

| Option | Model | Est. Monthly Revenue | Feasibility |
|---|---|---|---|
| **SaaS subscription** | $5–$10/mo per user | $5–$500 (1–50 users) | Medium — requires hosting scale |
| **GitHub Sponsors** | Donation-based | $0–$50/mo | Low — small project visibility |
| **Buy Me a Coffee / Ko-fi** | One-time tips | $0–$20/mo | Low — passive |
| **Freemium** | Free core + paid AI features | $3–$8/mo per premium user | Medium — feature-gating needed |
| **Affiliate referrals** | Cloud service referrals | $0–$10/mo | Low — passive |

### 7.3 Budget Approval

| Cost Tier | Approval | Requirement |
|---|---|---|
| **Under $25/mo** | Self-approved (developer) | None |
| **$25–$100/mo** | Self-approved with justification | Brief doc explaining value vs cost |
| **Over $100/mo** | Requires monetization or sponsorship | Must have revenue stream covering >= 50% |

---

## 8. Cloud Waste Reduction

### 8.1 Common Waste Sources

| Waste Source | Impact | How to Fix |
|---|---|---|
| **Stale data** (old tasks, resolved ideas, completed goals) | Supabase row count grows 5–10% monthly | Archive/purge data >90 days old |
| **Unused indexes** | DB storage + write overhead 2–5% | Run `pg_stat_user_indexes`, drop unused |
| **Oversized AI prompts** (too much context) | Claude token cost doubles | Strip irrelevant context; max 4K tokens |
| **Unnecessary API calls** (redundant fetches) | Bandwidth + compute 10–20% overhead | Add client-side caching, debounce |
| **Inefficient queries** (`SELECT *` vs specific columns) | Bandwidth + DB compute 5–15% | Always select only needed columns |
| **Development resources** (Railway deployed but idle) | Credit burn even when unused | Shut down dev deployments on Railway |
| **Over-fetching in frontend** (large payloads) | Bandwidth + render time 10–25% | Paginate, use GraphQL or partial responses |
| **Ollama running unnecessarily** | Local CPU/RAM (free but battery) | Stop Ollama when not using AI features |

### 8.2 Weekly Waste Reduction Checklist

```markdown
### Weekly Waste Check (Mon AM — 5 min)

- [ ] Review Supabase Row Counts (Dashboard → Settings → Usage)
- [ ] Check Vercel Bandwidth (Dashboard → Usage)
- [ ] Review Claude API costs (Console → Usage → Cost)
- [ ] Purge stale data (tasks >90 days completed, resolved ideas)
- [ ] Check for unused API calls (look at network tab or logs)
- [ ] Review recent build minutes on Vercel
- [ ] Clean up old DB backups (keep last 7 days)
- [ ] Verify Ollama is default AI (check AI config)
- [ ] Check Railway compute hours and remaining credits
- [ ] Confirm Resend email count is under 80/day
```

### 8.3 Monthly Waste Reduction Actions

```markdown
### Monthly Waste Cleanup (1st of month — 15 min)

### Database
- [ ] Run: `SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0` → drop unused indexes
- [ ] Archive: move tasks completed >90 days to `tasks_archive` table
- [ ] Vacuum: `VACUUM ANALYZE` on frequently updated tables
- [ ] Query audit: review slow queries in Supabase Query Performance

### Storage
- [ ] Check Supabase storage bucket for orphaned files
- [ ] Check for duplicate uploads or stale temp files

### AI
- [ ] Review Claude token usage by feature (which features use most?)
- [ ] Check Ollama is handling default AI routing (verify config)
- [ ] Audit prompt lengths — are system prompts growing?

### Infrastructure
- [ ] Review Railway deployments — any idle services?
- [ ] Check Vercel — any stale preview deployments?
- [ ] Review GitHub Actions — any failing/costly workflows?
```

---

## 9. FinOps Maturity Model

| Phase | Characteristics | Criteria | Current Status |
|---|---|---|---|
| **Phase 1: Cost Aware** | Know what services cost, basic tracking in place | ✅ Cost inventory completed, monthly tracking started | ✅ **Achieved** |
| **Phase 2: Cost Optimized** | Active optimization, waste reduction routines | ⚠️ AI optimization pending, waste checklist in use | ⚠️ **Partial** |
| **Phase 3: Cost Predictive** | Forecast usage, model cost growth | ❌ No forecasting model yet | ❌ **Not started** |
| **Phase 4: Business Aligned** | Cost tied to value/user growth, unit economics | ❌ N/A (single user, no revenue) | ❌ **Not applicable** |

### FinOps Roadmap

| Quarter | Goal | Deliverable |
|---|---|---|
| **2026 Q3** | Achieve Phase 2 fully | Implement all optimization strategies; AI cost reduced 50% |
| **2026 Q4** | Begin Phase 3 prep | 3 months of cost data collected for trend analysis |
| **2027 Q1** | Phase 3: Basic forecasting | Simple spreadsheet model predicting 6-month costs |
| **2027 Q2+** | Phase 4 (if monetized) | Cost-per-user metric, unit economics tracker |

---

## 10. Appendices

### Appendix A: Service Pricing Comparison

| Service | Free Tier | Paid Tier | Paid Price | Key Paid Benefits |
|---|---|---|---|---|
| **Supabase** | 500 MB DB, 50K rows, 2 GB BW | Pro | $25/mo | 8 GB DB, 250K rows, 50 GB BW, PITR |
| **Vercel** | 100 GB BW, 6000 build min | Pro | $20/mo | 1 TB BW, 6000 build min, team features |
| **Railway** | $5 credit, 500 hrs | Developer | $5/mo | Unlimited hrs, 1 GB RAM |
| **Claude API** | Pay-as-you-go | API Tier | Usage | Higher rate limits with spend commitment |
| **Resend** | 100 emails/day | Growth | $15/mo | 50K emails/mo, custom domain |
| **GitHub** | 2000 CI min/mo | Team | $4/mo | 3000 CI min, private repos |

### Appendix B: Monthly Cost Tracking Template

Copy this into a file or spreadsheet each month:

```markdown
# Monthly Cost Report — [Month] [Year]

## Service Usage
| Service | Metric Used | Limit | % Used | Cost |
|---|---|---|---|---|
| Supabase DB | [size] MB | 500 MB | [%] | $0 |
| Supabase Rows | [count] rows | 50K | [%] | $0 |
| Supabase BW | [size] GB | 2 GB | [%] | $0 |
| Vercel BW | [size] GB | 100 GB | [%] | $0 |
| Vercel Builds | [minutes] min | 6000 min | [%] | $0 |
| Railway Hours | [hours] hrs | 500 hrs | [%] | $0 |
| Railway Credits | $[amount] | $5 | [%] | $0 |
| Claude API | $[amount] | $2.50 | [%] | $[amount] |
| Resend Emails | [count]/day | 100/day | [%] | $0 |
| GitHub CI | [minutes] | 2000 min | [%] | $0 |

**Total Cost:** $[amount]

## Changes from Last Month
- [list any notable changes in cost or usage]

## Optimization Actions Taken
- [list actions taken this month]

## Optimization Actions Planned
- [list planned actions for next month]

## Upgrade Risk Assessment
- [ ] Any service >70% of limit? (Warning)
- [ ] Any service >90% of limit? (Critical)
- [ ] Recommended upgrades: [none / list]
```

### Appendix C: Waste Reduction Weekly Checklist

(See Section 8.2 — formatted as markdown checklist; copy into weekly task.)

### Appendix D: Upgrade Impact Analysis Matrix

| Upgrade | Monthly Δ | Annual Δ | Benefit | Risk if Not Upgrading |
|---|---|---|---|---|
| Supabase Free → Pro | +$25 | +$300 | 16x DB, 5x rows, 25x BW, PITR | Data loss risk, performance degrades |
| Vercel Hobby → Pro | +$20 | +$240 | 10x BW, team features | Bandwidth limits, no team |
| Railway Free → Developer | +$5 | +$60 | Unlimited hours, 1 GB RAM | Service downtime, OOM errors |
| Resend Free → Growth | +$15 | +$180 | 500x email capacity, custom domain | Email limits hit |
| GitHub Free → Team | +$4 | +$48 | 50% more CI minutes | CI pipeline failures |

### Appendix E: API Cost Calculator (Claude Token Cost Estimation)

| Feature | Avg Input Tokens | Avg Output Tokens | Cost / Request* | Est. Monthly Calls | Est. Monthly Cost |
|---|---|---|---|---|---|
| Simple Q&A | 2,000 | 500 | ~$0.004 | 50 | ~$0.20 |
| Task Generation | 4,000 | 1,000 | ~$0.008 | 40 | ~$0.32 |
| Code Review | 6,000 | 2,000 | ~$0.015 | 20 | ~$0.30 |
| Content Summarization | 8,000 | 1,500 | ~$0.018 | 30 | ~$0.54 |
| Complex Reasoning | 10,000 | 3,000 | ~$0.028 | 10 | ~$0.28 |
| **Total** | | | | **150** | **~$1.64** |

*Claude 3.5 Sonnet pricing: $3/M input tokens, $15/M output tokens.  
*Haiku pricing: $0.25/M input, $1.25/M output — use for simple tasks to save ~85%.*

### Appendix F: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-06-11 | Developer | Initial release — full cost inventory, optimization strategies, monitoring, upgrade planning |
| | | | |

---

*End of Document — Next Review: 2026-07-01*
