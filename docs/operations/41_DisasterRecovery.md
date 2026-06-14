# Disaster Recovery & Business Continuity Plan

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-DR-001 |
| Version | 1.0.0 |
| Status | Draft |
| Classification | Internal — Confidential |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Recovery Objectives](#2-recovery-objectives)
3. [Risk Assessment & Scenarios](#3-risk-assessment--scenarios)
4. [Backup Architecture](#4-backup-architecture)
5. [Recovery Procedures](#5-recovery-procedures)
6. [Business Continuity Procedures](#6-business-continuity-procedures)
7. [Communication Plan](#7-communication-plan)
8. [Testing & Validation](#8-testing--validation)
9. [Roles & Responsibilities](#9-roles--responsibilities)
10. [Appendices](#10-appendices)

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

---

## 2. Recovery Objectives

### 2.1 Recovery Time Objective (RTO)

| Tier | Service | RTO | Description |
|---|---|---|---|
| P0 | User Authentication | 4 hours | Login, session management |
| P0 | Database (read/write) | 4 hours | All CRUD operations on user data |
| P0 | Core API (tasks, habits, etc.) | 8 hours | All 13 FastAPI routers |
| P1 | Frontend | 8 hours | Next.js application |
| P1 | AI Features | 24 hours | Chat, briefing, agents |
| P2 | Scheduler / Cron | 48 hours | APScheduler jobs |
| P2 | Email Notifications | 48 hours | Resend integration |
| P3 | 3D Background / Effects | Best effort | Three.js visual effects |

### 2.2 Recovery Point Objective (RPO)

| Data Class | RPO | Method |
|---|---|---|
| User data (tasks, habits, logs, entries) | 24 hours | Daily Supabase backup |
| Auth data (users, sessions) | 0 hours | Supabase managed (real-time) |
| Chat history | 7 days | Periodic export |
| AI memory / context | 24 hours | Supabase table backup |
| Source code | Real-time | GitHub commits |
| Environment variables | Manual | Encrypted `.env` backup |
| Configuration files | Per release | GitHub repository |

### 2.3 Criticality Classification

```
CRITICAL (P0)
├── Supabase Database
├── Supabase Auth
├── GitHub Repository
├── API Endpoints (all 13 routers)
└── Environment Secrets

HIGH (P1)
├── Frontend Deployment (Vercel)
├── AI Client Configuration
└── Email Service Configuration

MEDIUM (P2)
├── APScheduler Jobs
├── Analytics Data
├── Log Files
└── Design Assets

LOW (P3)
├── Three.js 3D Backgrounds
├── Documentation Files
├── Archived Data
└── Old DB Snapshots
```

---

## 3. Risk Assessment & Scenarios

### 3.1 Failure Scenarios

| Scenario | Probability | Impact | RTO | Recovery Strategy |
|---|---|---|---|---|
| Supabase DB corruption | Low | Critical | 4h | Restore from daily backup |
| Supabase DB deletion | Very Low | Critical | 4h | Restore from Supabase point-in-time |
| Vercel deployment failure | Medium | High | 2h | Rollback to previous deployment |
| Railway service down | Low | High | 4h | Redeploy on alternative platform |
| GitHub repository loss | Very Low | Critical | 8h | Restore from local clones |
| API key rotation/leak | Low | Critical | 1h | Rotate keys, redeploy |
| Local dev machine failure | Medium | Medium | 24h | Clone repo, set up new environment |
| AI model provider outage | Medium | Low | — | Fallback to local Ollama or algorithmic mode |
| Email provider outage | Low | Low | — | Queue emails, retry |
| DNS/Custom domain expiry | Low | Medium | 24h | Auto-renewal, manual intervention |

### 3.2 Probability Matrix

```
┌─────────────────────────────────────────────────────────┐
│                    LIKELIHOOD                             │
│         Very Low    Low    Medium    High    Very High    │
│   ┌─────────────────────────────────────────────────┐    │
│ C │  DB del.     DB corr.  API leak  Deploy fail   │    │
│ R │  Repo loss   M/C fail  ---       ---           │    │
│ I ├─────────────────────────────────────────────────┤    │
│ T │              AI out.   ---       ---           │    │
│ I │  ---         ---       ---       ---           │    │
│ C ├─────────────────────────────────────────────────┤    │
│ A │              Email out. ---      ---            │    │
│ L │  ---         DNS exp.  ---      ---            │    │
│   └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Single Point of Failure Analysis

| SPOF | Risk | Mitigation |
|---|---|---|
| Single developer | Knowledge loss, single point of failure | Document all procedures in runbooks |
| Supabase as sole database | No read replica, no failover | Leverage Supabase's built-in HA |
| Single Railway instance | No auto-scaling, no multi-region | Document migration plan to Render |
| Local Ollama AI | System unavailable if laptop is off | Claude API as fallback |
| Free-tier hosting limits | Rate limiting, storage caps | Monitor usage, plan upgrade triggers |
| No CI/CD pipeline | Manual deployments error-prone | GitHub Actions plan in backlog |
| Single environment (prod) | No staging for testing | Vercel preview deployments for frontend |

---

## 4. Backup Architecture

### 4.1 Backup Schedule

```
┌──────────────────┬─────────────┬────────────┬──────────────┐
│     DATA         │ FREQUENCY   │ METHOD     │ RETENTION    │
├──────────────────┼─────────────┼────────────┼──────────────┤
│ PostgreSQL DB    │ Daily       │ pg_dump    │ 30 days      │
│ Auth & Users     │ Real-time   │ Supabase   │ Unlimited    │
│ Source Code      │ Per commit  │ GitHub     │ Unlimited    │
│ Env Variables    │ Per change  │ Encrypted  │ Per version  │
│ Chat History     │ Weekly      │ JSON export│ 90 days      │
│ Config Files     │ Per release │ GitHub     │ Unlimited    │
│ Design Assets    │ Weekly      │ Manual     │ 90 days      │
│ Logs             │ No backup   │ —          │ 7 days       │
└──────────────────┴─────────────┴────────────┴──────────────┘
```

### 4.2 Database Backup Procedure

```sql
-- Daily backup script (to be run via cron or Supabase dashboard)
-- Method 1: pg_dump via Supabase CLI (recommended)
supabase db dump --file backups/sb_daily_$(date +%Y%m%d).sql

-- Method 2: Supabase dashboard manual export
-- Settings → Database → Database backup → Create backup

-- Method 3: Python script for automated backups
-- scripts/backup_db.py
/*
import subprocess, datetime
date = datetime.datetime.now().strftime("%Y%m%d")
cmd = f"pg_dump $SUPABASE_DB_URL > backups/sb_{date}.sql"
subprocess.run(cmd, shell=True, check=True)
*/

-- Recovery:
-- psql $SUPABASE_DB_URL < backups/sb_20260611.sql
```

### 4.3 Backup Storage

| Backup Type | Primary Storage | Secondary Storage |
|---|---|---|
| Database dumps | Local `backups/` directory | GitHub repo (backup branch) |
| `.env` files | `~/.config/secondbrain/.env.encrypted` | — |
| Source code | GitHub (main branch) | Local `.git` clone |
| Design assets | `docs/design/` in repo | Figma (if applicable) |

### 4.4 Backup Verification

```bash
# Verify backup integrity — run after each backup
scripts/verify_backup.sh
# Steps:
# 1. Check file size > 1KB
# 2. pg_restore --list (validates SQL syntax)
# 3. Check row counts for critical tables
# 4. Log result to backups/audit.log
```

---

## 5. Recovery Procedures

### 5.1 Database Recovery

```
Scenario: Supabase database is corrupted or deleted

Step 1: Identify the incident
  ├── Check Supabase dashboard → Database → Health
  ├── Check error logs in Railway
  └── Confirm with supabase-py client error

Step 2: Initiate recovery
  ├── Option A: Supabase Point-in-Time Recovery (preferred)
  │   └── Dashboard → Database → Backups → PITR
  │   └── RPO: Last 5 minutes (pro plan) or 24h (free plan)
  │
  ├── Option B: Manual pg_dump restore
  │   ├── Locate latest backup: backups/sb_YYYYMMDD.sql
  │   ├── psql $SUPABASE_DB_URL < backups/sb_20260611.sql
  │   └── Verify row counts match expected

Step 3: Verify recovery
  ├── Run health check: curl /api/health
  ├── Check 5 random rows from critical tables
  └── Confirm auth users still exist

Step 4: Document incident
  └── Update docs/operations/40_IncidentResponse.md
```

### 5.2 Application Recovery (Backend)

```
Scenario: FastAPI backend is down or corrupt

Step 1: Diagnose
  ├── Check Railway dashboard → Deployments → Logs
  ├── Verify environment variables are set
  └── Check Python startup errors

Step 2: Redeploy
  ├── Option A: Rollback to previous deployment
  │   └── Railway → Deployments → Select previous → Redeploy
  │
  ├── Option B: Deploy from latest code
  │   └── git pull origin main
  │   └── Railway → Connect repo → Deploy

Step 3: Local fallback (if Railway is down)
  ├── cd apps/api
  ├── pip install -r requirements.txt  
  ├── uvicorn main:app --host 0.0.0.0 --port 8000
  └── Point frontend to localhost:8000

Step 4: Verify
  ├── curl http://localhost:8000/api/health
  ├── Test one CRUD endpoint per module
  └── Confirm AI client initializes
```

### 5.3 Application Recovery (Frontend)

```
Scenario: Next.js frontend fails or corrupt

Step 1: Diagnose
  ├── Check Vercel dashboard → Deployments → Build logs
  ├── Verify NEXT_PUBLIC_* env vars are set in Vercel
  └── Check for TypeScript/Next.js build errors

Step 2: Recover
  ├── Option A: Rollback Vercel deployment
  │   └── Vercel Dashboard → Deployments → ... → Rollback
  │
  ├── Option B: Force redeploy
  │   └── Vercel Dashboard → Deploy → Redeploy
  │   └── Or: git push (triggers auto-deploy)
  │
  ├── Option C: Local build test
  │   └── npm run build → Fix errors → git push

Step 3: Verify
  └── Visit production URL → Test 3 core pages
```

### 5.4 API Key / Secret Leak Recovery

```
Scenario: API key or secret is compromised

Step 1: Immediate containment
  ├── Revoke compromised key at source
  │   ├── Supabase: Dashboard → Settings → API → Regenerate
  │   ├── Claude: Anthropic console → API Keys → Delete
  │   └── Resend: Dashboard → API Keys → Rotate

Step 2: Redeploy with new keys
  ├── Update .env files locally
  ├── Update Railway environment variables
  ├── Update Vercel environment variables
  └── Trigger redeploy of both services

Step 3: Audit
  ├── Check GitHub for committed secrets
  ├── Run git secrets --scan (if configured)
  └── Check access logs for unusual activity

Step 4: Post-mortem
  ├── Add pre-commit hook for secret scanning
  └── Update AGENTS.md with warning
```

### 5.5 AI Service Failure Recovery

```
Scenario: Ollama or Claude API is unavailable

Step 1: Detect
  ├── API returns 503 / timeout in /api/chat
  ├── Briefing generation fails
  └── Agent tasks return errors

Step 2: Fallback chain
  ├── Default: Ollama (local)
  │   └── If down → Claude API (cloud)
  │   └── If down → Algorithmic fallback (no AI)
  │
  ├── Algorithmic fallback features:
  │   ├── Task prioritization (Eisenhower matrix)
  │   ├── Habit streaks (simple calc)
  │   ├── Daily briefing (template-based)
  │   └── Chat response ("AI is offline. Please try again later.")

Step 3: Restore
  ├── Ollama: 
  │   ├── ollama serve (start service)
  │   ├── ollama pull mistral (download model)
  │   └── Verify: curl http://localhost:11434/api/tags
  │
  ├── Claude:
  │   └── Check billing, rate limits at console.anthropic.com

Step 4: Monitor
  └── Set up cron to check AI health every hour
```

---

## 6. Business Continuity Procedures

### 6.1 Degraded Mode Operations

The system is designed to operate in three modes:

```
┌──────────────────┬──────────────────┬──────────────────┐
│    FULL MODE     │  DEGRADED MODE   │  EMERGENCY MODE  │
│   (All systems)  │ (AI unavailable) │  (Core only)     │
├──────────────────┼──────────────────┼──────────────────┤
│ ✓ All API routes │ ✓ All API routes │ ✓ Auth           │
│ ✓ AI agents      │ ✗ AI chat        │ ✓ Tasks CRUD     │
│ ✓ Chat           │ ✗ Briefings      │ ✓ Habits CRUD    │
│ ✓ Briefings      │ ✗ Opportunity    │ ✓ Courses CRUD   │
│ ✓ Scheduler      │   radar          │ ✗ Everything     │
│ ✓ 3D backgrounds │ ✓ Scheduler      │   else           │
│ ✓ All features   │ ✓ 3D (frontend)  │                  │
│                  │ ✓ All other      │                  │
│                  │   features       │                  │
└──────────────────┴──────────────────┴──────────────────┘

Transition conditions:
  Full → Degraded:  AI provider unreachable > 30s
  Degraded → Emergency: Backend unavailable > 5min
  Emergency → Degraded: Backend restored
  Degraded → Full: AI provider restored
```

### 6.2 Communication During Outage

| Phase | Channel | Message | Timing |
|---|---|---|---|
| Detection | Internal log | "ALERT: {service} failure detected" | Immediate |
| Diagnosis | Internal | "Investigating {issue}" | Within 5 min |
| Resolution | — | Working on fix | Within 15 min |
| Recovery | — | "{Service} restored" | Within RTO |
| Post-mortem | doc | Incident report in 40_IncidentResponse.md | Within 24h |

### 6.3 Data Integrity Checks

After any recovery operation, run these checks:

```bash
# scripts/verify_data_integrity.sh

# 1. Check row counts
echo "Row counts:"
echo "Tasks: $(curl -s /api/tasks | jq length)"
echo "Habits: $(curl -s /api/habits | jq length)"
echo "Users: $(curl -s /api/users | jq length)"

# 2. Check recent data
echo "Recent tasks (last 24h):"
curl -s "/api/tasks?since=$(date -d '24 hours ago' +%Y-%m-%d)" | jq length

# 3. Check foreign key integrity
echo "Orphan records check..."
# SQL: SELECT count(*) FROM tasks WHERE user_id NOT IN (SELECT id FROM auth.users)

# 4. Check auth still works
curl -s -X POST /api/auth/verify | jq .valid
```

---

## 7. Communication Plan

### 7.1 Internal Communication

| Scenario | Notify | Method | Template |
|---|---|---|---|
| Database failure | Developer (self) | Email + SMS | See 7.3 |
| API failure | Developer | Email | See 7.3 |
| Frontend failure | Developer | Email | See 7.3 |
| Security incident | Developer (immediate) | SMS | See 7.3 |
| Scheduled maintenance | Developer (24h prior) | Calendar | See 7.3 |

### 7.2 Escalation Chain

```
Priority 0 (Critical): Developer → Self-resolution
Priority 1 (High):    Developer → Cloud provider support
Priority 2 (Medium):  Developer → Next business day resolution
Priority 3 (Low):     Developer → Logged as tech debt
```

### 7.3 Communication Templates

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

## 8. Testing & Validation

### 8.1 DR Test Schedule

| Test | Frequency | Type | Success Criteria |
|---|---|---|---|
| Database restore | Monthly | Manual | Full restore verified in < 2h |
| API key rotation | Quarterly | Manual | New keys work, old keys fail |
| AI fallback test | Monthly | Automated | Degraded mode activates correctly |
| Backup integrity | Weekly | Automated | All backups > 1KB, valid SQL |
| Full recovery drill | Quarterly | Manual | Complete system restored in < 8h |
| Local dev rebuild | Per release | Manual | Fresh clone + setup works in < 30min |

### 8.2 DR Test Procedure (Quarterly)

```bash
# Quarterly Recovery Drill — Step by Step

# Phase 1: Simulate failure (manual)
echo "Phase 1: Simulating database failure..."
# Rename SUPABASE_URL to break connection

# Phase 2: Detect and diagnose
echo "Phase 2: Detecting outage..."
curl http://localhost:8000/api/health

# Phase 3: Initiate recovery
echo "Phase 3: Restoring from backup..."
pg_restore -d $SUPABASE_URL backups/sb_latest.sql

# Phase 4: Verify
echo "Phase 4: Verifying data integrity..."
scripts/verify_data_integrity.sh

# Phase 5: Document
echo "Phase 5: Documenting drill results..."
echo "Drill date: $(date)" >> docs/operations/drill_log.md
echo "Result: SUCCESS/FAILURE" >> docs/operations/drill_log.md
```

### 8.3 Test Success Metrics

| Metric | Target | Current | Status |
|---|---|---|---|
| Database restore time | < 2 hours | — | ❌ Not tested |
| Full recovery time | < 8 hours | — | ❌ Not tested |
| Backup integrity rate | 100% | — | ❌ Not tested |
| AI fallback activation | < 30s | — | ❌ Not tested |
| Data loss per incident | < 24h RPO | — | ❌ Not tested |

---

## 9. Roles & Responsibilities

### 9.1 Team Structure

| Role | Person | Responsibilities |
|---|---|---|
| Incident Commander | Developer (self) | Lead recovery, make decisions |
| Technical Lead | Developer (self) | Execute recovery procedures |
| Communications | Developer (self) | Document and notify |
| Post-Mortem Lead | Developer (self) | Write incident report |

> **Note:** As a single-developer project, all roles are filled by the same person. The role separation exists to ensure systematic thinking during incidents.

### 9.2 DR Maintenance

| Task | Frequency | Owner |
|---|---|---|
| Review DR plan | Quarterly | Developer |
| Update backup scripts | Monthly | Developer |
| Rotate API keys | Quarterly | Developer |
| Test recovery procedures | Quarterly | Developer |
| Update contacts in communication plan | Semi-annually | Developer |
| Review RTO/RPO targets | Annually | Developer |

---

## 10. Appendices

### Appendix A: Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    DR QUICK REFERENCE                        │
│                                                              │
│  DB DOWN:    pg_restore → verify → redeploy                 │
│  API DOWN:   Railway rollback → verify                      │
│  FRONTEND:   Vercel rollback → verify                       │
│  KEY LEAK:   Revoke → rotate → redeploy → audit            │
│  AI DOWN:    Check Ollama → replace Claude→ algorithmic    │
│  LOCAL FAIL: git clone → pip install → npm install → run    │
│                                                              │
│  Supabase Dashboard: https://supabase.com/dashboard         │
│  Vercel Dashboard:   https://vercel.com/dashboard           │
│  Railway Dashboard:  https://railway.app/dashboard          │
│  GitHub:             https://github.com/{owner}/{repo}      │
└────────────────────────────────────────────────────────────┘
```

### Appendix B: Critical Contacts

| Service | Contact Method | Account ID |
|---|---|---|
| Supabase Support | supabase.com/support | Project ref from dashboard |
| Vercel Support | vercel.com/support | Email on account |
| Railway Support | railway.app/support | Email on account |
| Anthropic (Claude) | support@anthropic.com | API key owner email |
| Resend (Email) | resend.com/support | Account email |

### Appendix C: Recovery Scripts Overview

| Script | Location | Purpose |
|---|---|---|
| `scripts/backup_db.py` | `scripts/` | Automated pg_dump backup |
| `scripts/verify_backup.sh` | `scripts/` | Verify backup file integrity |
| `scripts/verify_data_integrity.sh` | `scripts/` | Check DB health after restore |
| `scripts/deploy_rollback.sh` | `scripts/` | Rollback to previous deployment |
| `scripts/rotate_keys.py` | `scripts/` | Rotate all API keys |

### Appendix D: Environment Snapshot Template

```env
# Fill this out and store encrypted at ~/.config/secondbrain/
# Last updated: 2026-06-11

# --- Supabase ---
SUPABASE_URL=
SUPABASE_KEY=
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

# --- SMS (future) ---
# TWILIO_ACCOUNT_SID=
# TWILIO_AUTH_TOKEN=

# --- App ---
APP_NAME="Second Brain OS"
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### Appendix E: Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial disaster recovery plan |
