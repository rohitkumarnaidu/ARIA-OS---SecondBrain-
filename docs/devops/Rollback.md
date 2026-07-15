# Rollback Procedures

## Document Control

| Field | Value |
|---|---|
| Document ID | DVO-ROLL-015 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Rollback Philosophy](#2-rollback-philosophy)
3. [Decision Matrix](#3-decision-matrix)
4. [Frontend Rollback (Vercel)](#4-frontend-rollback-vercel)
5. [Backend Rollback (Railway)](#5-backend-rollback-railway)
6. [Database Rollback (Supabase)](#6-database-rollback-supabase)
7. [Full Stack Rollback](#7-full-stack-rollback)
8. [Rollback Scripts](#8-rollback-scripts)
9. [Verification Checklist](#9-verification-checklist)
10. [Performance Targets](#10-performance-targets)
11. [Failure Scenarios](#11-failure-scenarios)
12. [Testing Strategy](#12-testing-strategy)
13. [Edge Cases](#13-edge-cases)
14. [References](#14-references)

---

## 1. Executive Summary

This document provides quick-reference rollback procedures for all Second Brain OS components. Rollback is the primary mitigation strategy for deployment failures, serving as the fastest path to restoration.

---

## 2. Rollback Philosophy

- **Speed first**: Rollback is faster than fixing forward. Deploy the fix later.
- **Immutable**: Never modify a broken deployment. Always promote a known-good one.
- **Verified**: Every rollback must be verified via health checks.
- **Documented**: Every rollback logged in deployment audit trail.

---

## 3. Decision Matrix

| Symptom | Frontend | Backend | Database | RTO | RPO |
|---|---|---|---|---|---|
| Visual/UI bug | ✅ Rollback | ❌ | ❌ | < 2 min | 0 |
| API 500 on new path | ❌ | ✅ Rollback | ❌ | < 3 min | 0 |
| API 500 on all routes | ❌ | ✅ Rollback | ❌ | < 3 min | 0 |
| Auth broken | ❌ | ✅ Rollback | ❌ | < 3 min | 0 |
| Data corruption | ❌ | ❌ | ✅ PITR | < 30 min | < 5 min |
| Security vulnerability | ✅ | ✅ | ✅ | < 15 min | < 5 min |
| Dependency vuln (no API change) | ✅ | ✅ | ❌ | < 1 hour | 0 |
| Feature flag misconfig | ✅ | ✅ | ❌ | < 5 min | 0 |
| DB migration broke schema | ❌ | ✅ Revert migration | ✅ Revert | < 10 min | < 1 min |

---

## 4. Frontend Rollback (Vercel)

### Dashboard (Fastest — < 1 min)

```
1. Go to https://vercel.com/dashboard
2. Select "secondbrain-frontend"
3. Click "Deployments" tab
4. Find last known-good deployment (status: READY)
5. Click "..." → "Promote to Production"
6. Confirm dialog
7. Verify at https://app.secondbrainos.com
```

### CLI (< 2 min)

```bash
# List deployments
vercel list --token $VERCEL_TOKEN

# Promote a specific deployment
vercel promote dpl_abc123 --token $VERCEL_TOKEN
```

### Git Revert (~5 min)

```bash
# Revert last commit and push (triggers auto-deploy)
git revert HEAD --no-edit
git push origin main
```

### Automated Script (< 2 min)

```bash
./scripts/rollback.sh frontend 1
```

---

## 5. Backend Rollback (Railway)

### Dashboard (< 2 min)

```
1. Go to https://railway.app/dashboard
2. Select "secondbrain-backend"
3. Click "Deployments" tab
4. Find last known-good deployment
5. Click "Rollback to this deploy"
6. Wait for health check to pass
```

### CLI (< 2 min)

```bash
railway login
railway rollback --service backend 1
```

### Automated Script (< 3 min)

```bash
./scripts/rollback.sh backend 1

# Verify
curl https://api.secondbrainos.com/api/health
# → {"status": "healthy", "version": "X.Y.Z"}
```

---

## 6. Database Rollback (Supabase)

### Application-Level Fix (Preferred)

```sql
-- Identify bad records
SELECT * FROM tasks WHERE created_at > '2026-07-10T12:00:00Z' AND title LIKE '%error%';

-- Fix or delete
DELETE FROM tasks WHERE id IN ('bad-uuid-1', 'bad-uuid-2');
UPDATE tasks SET status = 'pending' WHERE id = 'affected-uuid';
```

### Migration Revert

```bash
# Revert the last migration
python scripts/run_migrations.py revert 005

# Verify schema
python scripts/run_migrations.py status
```

### Point-in-Time Recovery (Pro Tier)

```
1. Supabase Dashboard → Database → Backups
2. Click "Restore"
3. Select timestamp BEFORE the incident
4. Enter database password
5. Wait 5-15 min for restoration
6. Verify data integrity
```

**WARNING**: PITR creates a new project. Update connection strings in all services.

---

## 7. Full Stack Rollback

When multiple components need rollback simultaneously:

```bash
# Method 1: Automated script
./scripts/rollback.sh all

# Method 2: Sequential manual
./scripts/rollback.sh frontend 1
./scripts/rollback.sh backend 1
python scripts/run_migrations.py revert 005

# Method 3: Git revert (if single-commit deploy)
git revert HEAD --no-edit
git push origin main
```

---

## 8. Rollback Scripts

### `scripts/rollback.sh`

```bash
#!/bin/bash
# Rollback to previous deployment
# Usage: ./scripts/rollback.sh [frontend|backend|all] [steps]

TARGET="${1:-all}"
STEPS="${2:-1}"

rollback_frontend() {
    vercel list --token $VERCEL_TOKEN | grep "READY" | \
        head -$STEPS | tail -1 | awk '{print $2}' | \
        xargs vercel promote --token $VERCEL_TOKEN
}

rollback_backend() {
    railway rollback --service backend $STEPS
}

case $TARGET in
    frontend) rollback_frontend ;;
    backend)  rollback_backend ;;
    all)
        rollback_frontend
        rollback_backend
        ;;
esac
```

---

## 9. Verification Checklist

```
□ Frontend: https://app.secondbrainos.com loads without errors
□ Frontend: Console shows no 4xx/5xx API errors
□ Frontend: Web Vitals normal (LCP < 2.5s, CLS < 0.1)
□ Backend: GET /api/health returns {"status": "healthy"}
□ Backend: Test key endpoints return expected data
□ Backend: Error rate < 0.1%
□ Database: Query execution times at baseline
□ Database: No locked tables or long-running queries
□ Auth: Login flow works end-to-end
□ Scheduler: All 15 cron jobs executing on schedule
□ Monitoring: Alert dashboard shows green
□ Logs: No ERROR level logs from new (rolled-back) deployment
□ Audit: Rollback documented in deployment_audit.log
```

---

## 10. Performance Targets

| Metric | Target |
|---|---|
| Frontend rollback | < 2 min |
| Backend rollback | < 3 min |
| Database PITR | < 30 min |
| Migration revert | < 5 min |
| Full stack rollback | < 15 min |
| Rollback verification | < 5 min |

---

## 11. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| Vercel deploy list fails | Can't identify good deployment | Use git revert method |
| Railway rollback fails | Stuck on broken version | Redeploy previous version manually |
| PITR takes too long | Extended downtime | Switch to read-only mode temporarily |
| No known-good deployment exists | Can't roll back | Fix forward with emergency hotfix |
| Database and code out of sync | Schema mismatch | Fix forward, apply schema fixes first |

---

## 12. Testing Strategy

| Test | Frequency | Scope |
|---|---|---|
| Rollback drill | Monthly | Frontend + Backend |
| PITR test | Quarterly | Database restore to staging |
| Script test | Per release | `scripts/rollback.sh` dry run |
| Verification test | Per deployment | Health check suite |

---

## 13. Edge Cases

- **Rollback of rollback**: If the rolled-back version also has issues, repeat process with earlier deployment
- **Database + code mismatch**: If schema changed, revert migration before rolling back code
- **Partial rollback**: Only roll back the broken component; leave others running
- **Canary rollback**: If canary deployment fails, traffic is automatically shifted back to stable
- **Multiple deploys in quick succession**: Skip intermediate versions, roll back to last verified good

---

## 14. References

| Resource | Location |
|---|---|
| Deployment Strategy | `docs/devops/26_Deployment.md` (Section 14) |
| DevOps Practices | `docs/devops/27_DevOps.md` |
| CD Pipeline | `docs/devops/CD.md` |
| Disaster Recovery | `docs/operations/41_DisasterRecovery.md` |
| Incident Response | `docs/operations/40_IncidentResponse.md` |
