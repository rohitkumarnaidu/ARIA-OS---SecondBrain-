# Disaster Recovery & Business Continuity Plan

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-DR-001 |
| Version | 2.0.0 |
| Status | Approved |
| Classification | Internal — Confidential |
| Owner | Developer |
| Last Updated | 2026-07-11 |
| Next Review | 2026-10-11 |
| Review Cycle | Quarterly |
| Approving Authority | Developer |
| Location | `docs/operations/41_DisasterRecovery.md` |
| Supporting Documents | `docs/devops/backup-verification-procedure.md`, `docs/operations/40_IncidentResponse.md`, `docs/operations/39_Runbooks.md` |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [DR Team & Roles](#2-dr-team--roles)
3. [Recovery Prioritization Matrix](#3-recovery-prioritization-matrix)
4. [Recovery Objectives](#4-recovery-objectives)
5. [Risk Assessment & Scenarios](#5-risk-assessment--scenarios)
6. [Backup Architecture](#6-backup-architecture)
7. [Step-by-Step Recovery Procedures](#7-step-by-step-recovery-procedures)
8. [Business Continuity Procedures](#8-business-continuity-procedures)
9. [Communication Plan](#9-communication-plan)
10. [Post-Recovery Verification](#10-post-recovery-verification)
11. [DR Test Schedule](#11-dr-test-schedule)
12. [DR Test Template](#12-dr-test-template)
13. [Commands Cheat Sheet](#13-commands-cheat-sheet)
14. [Appendices](#14-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

This Disaster Recovery (DR) and Business Continuity Plan (BCP) documents the procedures, responsibilities, and infrastructure required to recover the Second Brain OS platform in the event of a service disruption, data loss, or infrastructure failure. The plan ensures that critical user data is never permanently lost and that service is restored within defined Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO).

### 1.2 Scope

| In Scope | Out of Scope |
|---|---|
| Supabase database (PostgreSQL) | Third-party AI API availability |
| FastAPI backend service | User's local network connectivity |
| Next.js frontend deployment | External service provider outages (Vercel, Railway) |
| APScheduler cron jobs | Hardware-level failures at hosting providers |
| Source code repository (GitHub) | Force majeure events beyond cloud provider SLA |
| Environment variables & secrets | |
| AI model configuration files | |
| User authentication (Supabase Auth) | |

### 1.3 Assumptions

- All infrastructure runs on cloud providers (Supabase, Vercel, Railway) with built-in redundancy
- Source code is maintained in GitHub with full commit history
- The project is maintained by a single developer (no on-call rotation)
- Cost is a constraint — recovery solutions must fit within free/low-cost tiers
- No dedicated staging environment exists (prod-only recovery)
- Developer workstation has local clones, Python and Node runtimes, and necessary CLI tools installed

---

## 2. DR Team & Roles

### 2.1 Team Roster

| Role | Person | Responsibilities | Backup |
|---|---|---|---|
| Incident Commander | Developer (self) | Lead recovery, make decisions, declare severity | Self |
| Technical Lead | Developer (self) | Execute recovery procedures, run commands | Self |
| Communications | Developer (self) | Document timeline, update logs | Self |
| Post-Mortem Lead | Developer (self) | Write incident report, track action items | Self |

> **Single-developer note:** All roles are filled by the same person. Role separation exists to ensure systematic thinking during incidents. Use the checklist in Section 12 to maintain procedural discipline.

### 2.2 Escalation Chain

| Level | Contact | Method | Response Time |
|---|---|---|---|
| Level 0 — Self-resolution | Developer | Immediate action | — |
| Level 1 — Cloud provider support | Supabase / Vercel / Railway | Dashboard ticket or email | < 1 hour for billing issues |
| Level 2 — External consultant | Freelance backup (if contracted) | Email / phone | < 24 hours |
| Level 3 — Service deprecation | Migrate to alternative provider | Per migration plan | Weeks |

### 2.3 DR Plan Maintenance

| Task | Frequency | Owner |
|---|---|---|
| Review DR plan | Quarterly | Developer |
| Update backup scripts | Monthly | Developer |
| Rotate API keys | Quarterly | Developer |
| Test recovery procedures | Quarterly | Developer |
| Update contacts in communication plan | Semi-annually | Developer |
| Review RTO/RPO targets | Annually | Developer |

---

## 3. Recovery Prioritization Matrix

| Module | RTO | RPO | Priority | Recovery Procedure |
|---|---|---|---|---|
| Database (Supabase) | 4 hours | 1 hour | P0 | Point-in-time recovery via Supabase dashboard or pg_dump restore |
| Auth Service | 2 hours | N/A | P0 | Supabase reconnection, verify Google OAuth config, re-deploy if needed |
| AI Service | 1 hour | N/A | P1 | Ollama restart, Claude API failover, algorithmic fallback |
| API Backend (Railway) | 2 hours | N/A | P0 | Redeploy from last known good deployment or rollback |
| Frontend (Vercel) | 1 hour | N/A | P0 | Rollback to previous deployment via Vercel dashboard or CLI |
| Scheduler | 4 hours | 1 day | P2 | Restart APScheduler service, backfill missed cron jobs |
| Email (Resend) | 8 hours | N/A | P2 | Verify API key, check dashboard, queue and retry |
| Analytics | 24 hours | 1 week | P3 | Rebuild from logs if needed |

### 3.1 Recovery Priority Definitions

- **P0 — Critical:** Complete service outage, data loss, or security breach. Immediate action required.
- **P1 — High:** Major feature unavailable. Action within 1 hour.
- **P2 — Medium:** Partial degradation. Action within 4 hours.
- **P3 — Low:** Non-critical. Action within 24 hours.

---

## 4. Recovery Objectives

### 4.1 Recovery Time Objectives (RTO)

| Tier | Service | RTO | Description |
|---|---|---|---|
| P0 | User Authentication | 2 hours | Login, session management |
| P0 | Database (read/write) | 4 hours | All CRUD operations on user data |
| P0 | Core API (tasks, habits, etc.) | 2 hours | All FastAPI routers |
| P1 | Frontend | 1 hour | Next.js application |
| P1 | AI Features | 1 hour | Chat, briefing, agents |
| P2 | Scheduler / Cron | 4 hours | APScheduler jobs |
| P2 | Email Notifications | 8 hours | Resend integration |
| P3 | 3D Background / Effects | Best effort | Three.js visual effects |

### 4.2 Recovery Point Objectives (RPO)

| Data Class | RPO | Method |
|---|---|---|
| User data (tasks, habits, logs, entries) | 1 hour | Automated Supabase backups + pg_dump |
| Auth data (users, sessions) | 0 hours | Supabase managed (real-time replication) |
| Chat history | 7 days | Periodic JSON export |
| AI memory / context | 24 hours | Supabase table backup |
| Source code | Real-time | GitHub commits |
| Environment variables | Manual | Encrypted `.env` backup (GPG) |
| Configuration files | Per release | GitHub repository |

---

## 5. Risk Assessment & Scenarios

### 5.1 Failure Scenarios

| Scenario | Probability | Impact | RTO | Recovery Strategy |
|---|---|---|---|---|
| Supabase DB corruption | Low | Critical | 4h | Point-in-time recovery or pg_dump restore |
| Supabase DB deletion | Very Low | Critical | 4h | Restore from Supabase PITR (if available) or latest pg_dump |
| Vercel deployment failure | Medium | High | 1h | Rollback to previous deployment |
| Railway service down | Low | High | 2h | Redeploy on Railway or local fallback |
| GitHub repository loss | Very Low | Critical | 8h | Restore from local clones + push to new remote |
| API key rotation/leak | Low | Critical | 1h | Revoke, rotate, redeploy |
| Local dev machine failure | Medium | Medium | 24h | Clone repo, install deps, configure .env |
| AI model provider outage | Medium | Low | 1h | Ollama → Claude → algorithmic fallback chain |
| Email provider outage | Low | Low | — | Queue emails, retry on restore |
| DNS/Custom domain expiry | Low | Medium | 24h | Auto-renewal or manual intervention at registrar |

### 5.2 Single Point of Failure Analysis

| SPOF | Risk | Mitigation |
|---|---|---|
| Single developer | Knowledge loss, single point of failure | Document all procedures in runbooks and this DR plan |
| Supabase as sole database | No read replica, no failover | Leverage Supabase's built-in HA and automated backups |
| Single Railway instance | No auto-scaling, no multi-region | Document migration plan to alternative platform |
| Local Ollama AI | System unavailable if laptop is off | Claude API as cloud fallback |
| Free-tier hosting limits | Rate limiting, storage caps | Monitor usage monthly; plan upgrade triggers |
| Single environment (prod) | No staging for testing | Vercel preview deployments for frontend testing |

---

## 6. Backup Architecture

### 6.1 Backup Schedule

| Data | Frequency | Method | Retention |
|---|---|---|---|
| PostgreSQL DB | Daily (automated) | Supabase daily backup + pg_dump | 30 days (local) + Supabase retention |
| Auth & Users | Real-time | Supabase managed | Unlimited (Supabase) |
| Source Code | Per commit | GitHub | Unlimited |
| Environment Variables | Per change | GPG-encrypted file | Per version |
| Chat History | Weekly | JSON export | 90 days |
| Config Files | Per release | GitHub | Unlimited |
| Design Assets | Weekly | Manual backup | 90 days |
| Logs | Not backed up | — | 7 days (streaming) |

### 6.2 Backup Storage Locations

| Backup Type | Primary Storage | Secondary Storage |
|---|---|---|
| Database dumps | Local `backups/` directory | GitHub backup branch (encrypted) |
| `.env` files | `~/.config/secondbrain/.env.encrypted` | USB/external drive (quarterly) |
| Source code | GitHub (main branch) | Local `.git` clone(s) |
| Design assets | `docs/design/` in repo | Figma (if applicable) |

### 6.3 Database Backup Commands

```bash
# pg_dump — full database export
pg_dump "$SUPABASE_DB_URL" > "backups/sb_$(date +%Y%m%d_%H%M%S).sql"

# Supabase CLI dump
supabase db dump --file "backups/sb_supabase_$(date +%Y%m%d).sql"

# Verify backup integrity
wc -l "backups/sb_latest.sql"
head -5 "backups/sb_latest.sql"    # Should show CREATE/COPY statements
```

---

## 7. Step-by-Step Recovery Procedures

### 7.1 Database Corruption (P0)

**Scenario:** Supabase PostgreSQL database is corrupted, has missing tables, or returns query errors.

```
Step 1: Diagnose
  ├── Check Supabase dashboard → Database → Health
  ├── Run: curl -s http://localhost:8000/api/health
  ├── Check Railway logs for database errors
  └── Verify with: psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM tasks;"

Step 2: Initiate Point-in-Time Recovery (PITR)
  ├── Option A: Supabase Dashboard PITR
  │   ├── Navigate to: Database → Backups → Point-in-Time Recovery
  │   ├── Select target time (before corruption occurred)
  │   ├── Confirm and wait for restoration
  │   └── Note: Available on Pro plan; free plan uses daily backups
  │
  └── Option B: Manual pg_dump Restore
      ├── Locate latest uncorrupted backup:
      │   ls -lt backups/sb_*.sql | head -5
      ├── Verify backup timestamp matches pre-corruption window
      ├── Restore:
      │   psql "$SUPABASE_DB_URL" < backups/sb_20260710_120000.sql
      └── If restore fails, try second-most-recent backup

Step 3: Verify Recovery
  ├── Run: curl -s http://localhost:8000/api/health
  ├── Check row counts for critical tables:
  │   psql "$SUPABASE_DB_URL" -c "
  │     SELECT 'tasks' as tbl, count(*) FROM tasks
  │     UNION ALL SELECT 'habits', count(*) FROM habits
  │     UNION ALL SELECT 'goals', count(*) FROM goals;"
  ├── Verify auth users exist:
  │   psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM auth.users;"
  └── Test one CRUD operation per module via API

Step 4: Document
  └── Log in: docs/operations/40_IncidentResponse.md
  └── Update backup verification: docs/devops/backup-verification-procedure.md
```

### 7.2 Full System Outage (P0)

**Scenario:** Frontend, backend, and/or database are all unreachable.

```
Step 1: Frontend Recovery (Vercel)
  ├── Check: Vercel Dashboard → Deployments → Status
  ├── Rollback:
  │   vercel rollback --safe=10
  │   # Or via Dashboard: Deployments → ... → Rollback to Previous
  └── Verify: Visit production URL, confirm page loads

Step 2: Backend Recovery (Railway)
  ├── Check: Railway Dashboard → Deployments → Logs
  ├── Rollback:
  │   railway redeploy --deployment <last-known-good>
  │   # Or via Dashboard: Deployments → Select previous → Redeploy
  └── Verify: curl -s http://localhost:8000/api/health | jq .

Step 3: Database Recovery
  ├── Check: Supabase Dashboard → Database → Health
  ├── If corrupted → follow Section 7.1 (Database Corruption recovery)
  └── Verify: API returns correct data for CRUD endpoints

Step 4: AI Service Recovery
  ├── Check AI health:
  │   curl -s http://localhost:11434/api/tags  # Ollama
  ├── If Ollama down → start it:
  │   ollama serve &
  │   ollama pull mistral  # if model missing
  └── Verify: POST /api/v1/chat with a test message

Step 5: Scheduler Recovery
  ├── Restart scheduler service:
  │   cd services/scheduler && python main.py &
  └── Verify: Check logs for job execution
```

### 7.3 AI Provider Failure (P1)

**Scenario:** Ollama local, Claude API, or both are unavailable.

**Fallback Chain:**
1. Default: **Ollama** (local, free)
2. Fallback: **Claude API** (cloud, ~$0.015/request)
3. Last resort: **Algorithmic fallback** (no AI, deterministic logic)

```
Step 1: Detect
  ├── Chat returns 503 or timeout
  ├── Briefing generation fails
  └── Agent tasks return errors in logs

Step 2: Diagnose
  ├── Check Ollama:
  │   curl -s http://localhost:11434/api/tags
  │   # If connection refused → Ollama is down
  ├── Check Claude:
  │   curl -s https://api.anthropic.com/v1/messages -H "x-api-key: $CLAUDE_API_KEY"
  │   # Check billing at console.anthropic.com
  └── Check environment:
      echo $USE_LOCAL_AI  # "True" means Ollama primary

Step 3: Restore
  ├── If Ollama down:
  │   ollama serve                    # Start service
  │   ollama pull mistral             # Download model if missing
  │   Verify: curl http://localhost:11434/api/tags
  │
  ├── If Claude API exhausted:
  │   Top up billing at console.anthropic.com
  │   Or set USE_LOCAL_AI=True temporarily
  │
  └── If both down:
      System enters degraded mode (algorithmic fallback)
      All AI features use template-based responses

Step 4: Verify
  ├── curl -s http://localhost:8000/api/v1/chat -X POST -d '{"message":"hello"}'
  └── Check response contains valid data (not an error message)
```

### 7.4 Auth Provider Failure (P0)

**Scenario:** Supabase Auth is down, users cannot log in, or OAuth is broken.

```
Step 1: Diagnose
  ├── Check: Supabase Dashboard → Authentication → Settings
  ├── Verify: Google OAuth redirect URIs are correct
  ├── Check: JWT_SECRET matches between Supabase and .env
  └── Test: Try login with email/password (if configured)

Step 2: Recover
  ├── If Supabase Auth service issue:
  │   Wait for Supabase to resolve (check status.supabase.com)
  │   No self-service fix available
  │
  ├── If configuration issue (wrong redirect URI, expired secret):
  │   Update OAuth provider settings in Supabase Dashboard
  │   Update JWT_SECRET if rotated
  │   Redeploy backend: railway redeploy
  │   Redeploy frontend: Vercel auto-deploy (or manual)
  │
  └── If Google OAuth quota exceeded:
      Log into Google Cloud Console → APIs & Services
      Check OAuth consent screen quota
      Request increase if needed

Step 3: Verify
  ├── Navigate to login page, complete OAuth flow
  ├── Verify JWT token is returned
  └── Confirm API calls succeed with new token
```

### 7.5 Scheduler Not Running (P2)

**Scenario:** APScheduler service is stopped, cron jobs are not triggering.

```
Step 1: Diagnose
  ├── Check if scheduler process is running:
  │   ps aux | grep scheduler
  │   # Windows: Get-Process -Name python | Where-Object {$_.CommandLine -match "scheduler"}
  ├── Check scheduler logs:
  │   tail -100 services/scheduler/logs/scheduler.log
  └── Check Railway dashboard if deployed there

Step 2: Restart
  ├── Local deployment:
  │   cd services/scheduler
  │   source venv/bin/activate    (or .\venv\Scripts\Activate on Windows)
  │   python main.py &
  │
  └── Railway deployment:
      Railway Dashboard → Services → Scheduler → Restart

Step 3: Backfill Missed Jobs
  ├── Briefing (missed 7 AM):
  │   curl -X POST http://localhost:8000/api/v1/automation/trigger/briefing
  │
  ├── Opportunity radar (missed 6 AM):
  │   curl -X POST http://localhost:8000/api/v1/automation/trigger/radar
  │
  ├── Weekly review (missed Sunday 8 PM):
  │   curl -X POST http://localhost:8000/api/v1/automation/trigger/weekly-review
  │
  ├── Sleep analysis (missed 9:30 PM):
  │   curl -X POST http://localhost:8000/api/v1/automation/trigger/sleep-analysis
  │
  └── Nudges (missed 6 PM):
      curl -X POST http://localhost:8000/api/v1/automation/trigger/nudges

Step 4: Verify
  ├── Check scheduler logs for job execution
  ├── Verify briefings were generated:
  │   curl -s http://localhost:8000/api/v1/briefings/today
  └── Set cron health check:
      Monitor that jobs run on next scheduled interval
```

### 7.6 API Key / Secret Leak (P0)

```
Step 1: Immediate containment
  ├── Revoke compromised key at source
  │   Supabase: Dashboard → Settings → API → Regenerate anon key
  │   Claude: console.anthropic.com → API Keys → Delete
  │   Resend: Dashboard → API Keys → Rotate
  │
  ├── Check GitHub for committed secrets (even in history):
  │   git log --all -p | grep -E "(SUPABASE|CLAUDE|JWT_SECRET|RESEND)"
  │   # If found, use git filter-branch or BFG Repo-Cleaner

Step 2: Rotate and redeploy
  ├── Generate new keys at respective provider dashboards
  ├── Update .env files locally
  ├── Update Railway environment variables
  ├── Update Vercel environment variables
  └── Trigger redeploy of both services

Step 3: Audit
  ├── Check access logs for unusual activity
  ├── Review recent deployments for unauthorized changes
  └── Run git secrets --scan if available

Step 4: Post-mortem
  ├── Add or update pre-commit hooks for secret scanning
  └── Document in Incident Response log
```

---

## 8. Business Continuity Procedures

### 8.1 Degraded Mode Operations

The system is designed to operate in three modes:

```
Full Mode → All systems operational
  ↓ (AI provider unreachable > 30s)
Degraded Mode → AI disabled, template-based responses
  ↓ (Backend unavailable > 5min)
Emergency Mode → Static frontend with outage message
  ↓ (Backend restored)
Degraded Mode → Full functionality except AI
  ↓ (AI provider restored)
Full Mode → All systems operational
```

### 8.2 Degraded Mode Capabilities

| Feature | Full Mode | Degraded Mode (No AI) | Emergency Mode (No Backend) |
|---|---|---|---|
| Task CRUD | Full | Full | Read-only (cached) |
| Habit tracking | Full | Full | Read-only (cached) |
| Dashboard | Live data | Live data | Cached snapshot |
| AI Chat | LLM responses | "AI offline" message | Unavailable |
| Daily Briefing | AI-generated | Template-based | Unavailable |
| Agent Operations | Full AI | Algorithmic fallback | Unavailable |
| Authentication | Full | Full | Unavailable |

### 8.3 Communication During Outage

| Phase | Channel | Message | Timing |
|---|---|---|---|
| Detection | Internal log | "ALERT: {service} failure detected" | Immediate |
| Diagnosis | Internal | "Investigating {issue}" | Within 5 min |
| Resolution | — | Working on fix | Within 15 min |
| Recovery | — | "{Service} restored" | Within RTO |
| Post-mortem | Incident doc | Report in `40_IncidentResponse.md` | Within 24h |

---

## 9. Communication Plan

### 9.1 Notification Procedures

| Scenario | Notify | Method | Template |
|---|---|---|---|
| Database failure | Developer (self) | Terminal alert + email | Section 9.3 |
| API failure | Developer | Terminal alert + email | Section 9.3 |
| Frontend failure | Developer | Terminal alert + email | Section 9.3 |
| Security incident | Developer (immediate) | Push notification + SMS | Section 9.3 |
| Scheduled maintenance | Developer (24h prior) | Calendar event | — |

### 9.2 Escalation Chain

```
P0 (Critical): Developer → Self-resolution (immediate)
P1 (High):     Developer → Self-resolution (< 4 hours)
P2 (Medium):   Developer → Next business day resolution
P3 (Low):      Developer → Logged as tech debt
```

### 9.3 Communication Templates

**Incident Detection:**
```
[ALERT] SecondBrain OS - {SERVICE} Failure
Time: {timestamp}
Impact: {description of impact}
Severity: {P0/P1/P2/P3}
Action: {immediate action taken}
```

**Resolution:**
```
[RESOLVED] SecondBrain OS - {SERVICE} Restored
Time: {timestamp}
Downtime: {duration}
Root Cause: {brief explanation}
Action Taken: {what was done}
```

**Post-Mortem:**
```
Incident: {incident_id}
Date: {date}
Duration: {duration}
Root Cause: {detailed explanation}
Impact: {users/data affected}
Resolution: {steps taken}
Prevention: {preventive measures added}
Action Items: [list]
```

---

## 10. Post-Recovery Verification

After any recovery operation, run the following checks in order:

### 10.1 Verification Checklist

```
Phase 1: Health Checks
  [ ] curl -s http://localhost:8000/api/health | jq .status == "healthy"
  [ ] curl -s http://localhost:8000/api/health/live | jq .status == "ok"
  [ ] curl -s http://localhost:8000/api/health/ready | jq .dependencies.supabase.status == "ok"
  [ ] Production URL loads in browser (200 OK)
  [ ] No 5xx errors in logs

Phase 2: Data Integrity
  [ ] Task count matches expected range:
      psql "$DB_URL" -c "SELECT count(*) FROM tasks;"
  [ ] Habit logs for today exist:
      psql "$DB_URL" -c "SELECT count(*) FROM habit_logs WHERE date = CURRENT_DATE;"
  [ ] No orphan records:
      psql "$DB_URL" -c "
        SELECT count(*) FROM tasks t
        LEFT JOIN auth.users u ON t.user_id = u.id
        WHERE u.id IS NULL;"
  [ ] Foreign keys are intact

Phase 3: Functional Verification
  [ ] Login works (OAuth flow completes)
  [ ] Task CRUD (create → read → update → delete)
  [ ] Habit log creation
  [ ] AI chat responds (may be template in degraded mode)
  [ ] Dashboard loads with correct data

Phase 4: System Verification
  [ ] All environment variables are set (compare against .env.encrypted)
  [ ] Cron jobs are running (check scheduler logs)
  [ ] AI model is responsive (ollama ps)
  [ ] Latest backup ran successfully
```

### 10.2 Data Integrity SQL Queries

```sql
-- Run after every recovery
SELECT 'tasks' AS table_name, COUNT(*) AS row_count FROM tasks
UNION ALL SELECT 'habits', COUNT(*) FROM habits
UNION ALL SELECT 'habit_logs', COUNT(*) FROM habit_logs
UNION ALL SELECT 'goals', COUNT(*) FROM goals
UNION ALL SELECT 'courses', COUNT(*) FROM courses
UNION ALL SELECT 'sleep_logs', COUNT(*) FROM sleep_logs
UNION ALL SELECT 'income_entries', COUNT(*) FROM income_entries
UNION ALL SELECT 'ideas', COUNT(*) FROM ideas
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'resources', COUNT(*) FROM resources
UNION ALL SELECT 'opportunities', COUNT(*) FROM opportunities
UNION ALL SELECT 'time_entries', COUNT(*) FROM time_entries
ORDER BY table_name;

-- Check for orphaned records
SELECT 'orphan_tasks' AS check_name, COUNT(*) FROM tasks t
  LEFT JOIN auth.users u ON t.user_id = u.id WHERE u.id IS NULL
UNION ALL
SELECT 'orphan_habits', COUNT(*) FROM habits h
  LEFT JOIN auth.users u ON h.user_id = u.id WHERE u.id IS NULL;
```

---

## 11. DR Test Schedule

### 11.1 Test Cadence

| Test | Frequency | Type | Success Criteria | Last Run | Next Run |
|---|---|---|---|---|---|
| Database restore | Monthly | Manual | Full restore in < 2 hours | Not run | 2026-08-01 |
| API key rotation | Quarterly | Manual | New keys work, old keys fail | Not run | 2026-10-01 |
| AI fallback test | Monthly | Semi-automated | Degraded mode activates in < 30s | Not run | 2026-08-01 |
| Backup integrity | Weekly | Automated | All backups > 1KB, valid SQL | Not run | 2026-07-18 |
| Full recovery drill | Quarterly | Manual | Complete system restored in < 4 hours | Not run | 2026-10-01 |
| Local dev rebuild | Per release | Manual | Fresh clone + setup in < 30 min | Not run | Next release |
| Auth failover | Quarterly | Manual | Login works after simulated auth failure | Not run | 2026-10-01 |
| Scheduler restart | Monthly | Manual | Jobs resume and backfill correctly | Not run | 2026-08-01 |

### 11.2 DR Test Procedure (Quarterly Full Drill)

```bash
# Phase 1: Simulate failure
echo "[DR DRILL] Phase 1: Simulating database failure..."
echo "  Action: Revoke SUPABASE_URL in Railway temporarily"
echo "  Expected: API health returns 503"

# Phase 2: Detect and diagnose
echo "[DR DRILL] Phase 2: Detecting outage..."
curl -s http://localhost:8000/api/health | jq .
echo "  Verify: Response indicates database connection failure"

# Phase 3: Initiate recovery
echo "[DR DRILL] Phase 3: Restoring from backup..."
echo "  Action: Restore SUPABASE_URL, trigger pg_dump restore"
echo "  Timer started: $(date)"

# Phase 4: Verify
echo "[DR DRILL] Phase 4: Verifying data integrity..."
echo "  Action: Run verification SQL queries"
echo "  Timer stopped: $(date)"

# Phase 5: Document
echo "[DR DRILL] Phase 5: Documenting results..."
echo "Date: $(date)" >> docs/operations/drill_log.md
echo "Result: SUCCESS/FAILURE" >> docs/operations/drill_log.md
echo "Duration: XX minutes" >> docs/operations/drill_log.md
echo "Issues: [none/describe]" >> docs/operations/drill_log.md
```

### 11.3 Test Success Metrics

| Metric | Target | Current | Status |
|---|---|---|---|
| Database restore time | < 2 hours | — | Untested |
| Full recovery time | < 4 hours | — | Untested |
| Backup integrity rate | 100% | — | Untested |
| AI fallback activation | < 30s | — | Untested |
| Data loss per incident | < 1 hour RPO | — | Untested |

---

## 12. DR Test Template

Use this template for every DR drill:

```markdown
# DR Drill Report

**Drill ID:** DR-{YYYY}-{NNN}
**Date:** YYYY-MM-DD
**Type:** [Database Restore / Full Recovery / AI Fallback / Key Rotation / Scheduler Restart]
**Duration:** XX minutes
**Conducted by:** Developer

## Scenario
{description of simulated failure}

## Procedure Followed
1. {step}
2. {step}
3. {step}

## Results

| Metric | Target | Actual | Pass/Fail |
|---|---|---|---|
| Time to detect | < 5 min | XX min | ✅ / ❌ |
| Time to recover | < RTO | XX min | ✅ / ❌ |
| Data loss | < RPO | XX min | ✅ / ❌ |
| Verification passed | All checks | X/Y passed | ✅ / ❌ |

## Issues Encountered
- {issue 1}
- {issue 2}

## Improvements Identified
- {improvement 1}
- {improvement 2}

## Action Items
- [ ] {action} — Owner, Due date

## Log Location
`docs/operations/drill_log.md`
```

---

## 13. Commands Cheat Sheet

### 13.1 Database

```bash
# Health check
curl -s http://localhost:8000/api/health | jq .

# pg_dump backup
pg_dump "$SUPABASE_DB_URL" > backups/sb_$(date +%Y%m%d_%H%M%S).sql

# pg_restore
psql "$SUPABASE_DB_URL" < backups/sb_latest.sql

# Row counts
psql "$SUPABASE_DB_URL" -c "SELECT schemaname, tablename, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"

# Orphan check
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM tasks t LEFT JOIN auth.users u ON t.user_id = u.id WHERE u.id IS NULL;"
```

### 13.2 Backend (Railway)

```bash
# Health check
curl -s http://localhost:8000/api/health

# Rollback Railway
railway redeploy --deployment <id>

# Local fallback
cd apps/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 13.3 Frontend (Vercel)

```bash
# Health check (browser or curl)
curl -s -o /dev/null -w "%{http_code}" https://secondbrain-os.vercel.app

# Rollback
vercel rollback
# Or: Vercel Dashboard → Deployments → ... → Rollback

# Force redeploy (no code change needed)
vercel --prod
```

### 13.4 AI Service

```bash
# Check Ollama
curl -s http://localhost:11434/api/tags | jq .
curl -s http://localhost:11434/api/generate -d '{"model":"mistral","prompt":"hello"}'

# Start Ollama
ollama serve

# Pull model
ollama pull mistral

# Check Claude
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### 13.5 Scheduler

```bash
# Start scheduler
cd services/scheduler && python main.py

# Manual job triggers
curl -X POST http://localhost:8000/api/v1/automation/trigger/briefing
curl -X POST http://localhost:8000/api/v1/automation/trigger/radar
curl -X POST http://localhost:8000/api/v1/automation/trigger/weekly-review
curl -X POST http://localhost:8000/api/v1/automation/trigger/sleep-bodtime
curl -X POST http://localhost:8000/api/v1/automation/trigger/nudges

# Check scheduler logs
tail -f services/scheduler/logs/scheduler.log
```

### 13.6 Environment & Secrets

```bash
# Encrypt .env
gpg -c .env.production

# Decrypt .env
gpg -d .env.production.gpg > .env.production

# Check for secrets in git history
git log --all -p | grep -E "(SUPABASE|CLAUDE|JWT_SECRET|RESEND)"
```

### 13.7 Git & Rollback

```bash
# Full code rollback
git revert HEAD --no-edit
git push origin main

# List recent tags
git tag -l 'v*' --sort=-version:refname

# Create hotfix branch
git checkout -b hotfix/XX-description
```

---

## 14. Appendices

### Appendix A: Quick Reference Card

```
┌────────────────────────────────────────────────────────────────────┐
│          DISASTER RECOVERY — QUICK REFERENCE                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  DATABASE DOWN:                                                    │
│  1. psql "$DB_URL" < backups/sb_latest.sql                         │
│  2. Verify row counts                                              │
│  3. Test CRUD via API                                              │
│                                                                    │
│  API DOWN:                                                         │
│  1. Railway Dashboard → Rollback                                   │
│  2. Verify: curl /api/health                                       │
│                                                                    │
│  FRONTEND DOWN:                                                    │
│  1. Vercel Dashboard → Rollback                                    │
│  2. Verify: production URL loads                                   │
│                                                                    │
│  AUTH DOWN:                                                        │
│  1. Check Supabase Auth status                                     │
│  2. Verify OAuth redirect URIs                                     │
│  3. Redeploy if config changed                                     │
│                                                                    │
│  AI DOWN:                                                          │
│  1. ollama serve (if local)                                        │
│  2. Check Claude billing                                           │
│  3. System falls back automatically                                │
│                                                                    │
│  KEY LEAK:                                                         │
│  1. Revoke at source                                               │
│  2. Rotate key                                                     │
│  3. Update .env + redeploy                                         │
│  4. Audit git history                                              │
│                                                                    │
│  FULL OUTAGE:                                                      │
│  1. Frontend rollback (1h RTO)                                     │
│  2. Backend rollback (2h RTO)                                      │
│  3. Database restore (4h RTO)                                      │
│  4. AI restart (1h RTO)                                            │
│  5. Scheduler restart (4h RTO)                                     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Appendix B: Critical Contacts

| Service | Contact Method | Account ID |
|---|---|---|
| Supabase Support | supabase.com/support | Project ref from dashboard |
| Vercel Support | vercel.com/support | Email on account |
| Railway Support | railway.app/support | Email on account |
| Anthropic (Claude) | support@anthropic.com | API key owner email |
| Resend (Email) | resend.com/support | Account email |
| GitHub Support | support.github.com | Account email |
| Google Cloud (OAuth) | cloud.google.com/support | Project ID from console |
| Domain Registrar | Per registrar | Account email |

### Appendix C: Recovery Scripts Reference

| Script | Location | Purpose |
|---|---|---|
| `scripts/backup_db.py` | `scripts/` | Automated pg_dump backup with timestamp |
| `scripts/verify_backup.sh` | `scripts/` | Verify backup file integrity (size, checksum, SQL syntax) |
| `scripts/verify_data_integrity.sh` | `scripts/` | Check DB health after restore (row counts, orphans) |
| `scripts/deploy_rollback.sh` | `scripts/` | Rollback to previous deployment (Vercel + Railway) |
| `scripts/rotate_keys.py` | `scripts/` | Rotate all API keys with confirmation prompts |

### Appendix D: DR Plan Distribution

| Copy | Location | Encrypted |
|---|---|---|
| Primary | `docs/operations/41_DisasterRecovery.md` | No |
| Backup verification | `docs/devops/backup-verification-procedure.md` | No |
| Offline | `~/Documents/ops/secondbrain-dr-plan.md` | Recommended (GPG) |

### Appendix E: Environment Snapshot Template

```env
# Second Brain OS — Production Environment Snapshot
# Store encrypted: gpg -c .env.production
# Last updated: YYYY-MM-DD

# --- Supabase ---
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=

# --- Auth ---
JWT_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# --- AI ---
CLAUDE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=True

# --- Email ---
RESEND_API_KEY=

# --- App ---
APP_NAME="Second Brain OS"
NEXT_PUBLIC_APP_URL=https://secondbrain-os.vercel.app
CORS_ORIGINS=http://localhost:3000
```

### Appendix F: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial disaster recovery plan |
| 2.0.0 | 2026-07-11 | Developer | Complete rewrite: added DR team roster with solo-dev notation, Recovery Prioritization Matrix with RTO/RPO/Priority/Procedure, step-by-step recovery for 6 failure scenarios (DB corruption, full outage, AI failure, auth failure, scheduler not running, key leak), commands cheat sheet for all services, post-recovery verification checklist with SQL queries, quarterly DR test schedule with template, degraded mode capabilities table, communication templates, and quick reference card. Updated RTOs based on production deployment reality. |
