# Production Deployment Runbook

| Field | Value |
|---|---|
| Document ID | DVO-PROD-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-07-11 |
| Classification | Internal â€” Operations |
| Owner | Developer |
| Review Cycle | Monthly |
| Drill Frequency | Bi-weekly |

---

## Table of Contents

1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Environment Variables Reference](#2-environment-variables-reference)
3. [Backend Deployment â€” Railway CLI](#3-backend-deployment--railway-cli)
4. [Frontend Deployment â€” Vercel CLI](#4-frontend-deployment--vercel-cli)
5. [Scheduler Deployment](#5-scheduler-deployment)
6. [Full Deployment](#6-full-deployment)
7. [Post-Deployment Verification](#7-post-deployment-verification)
8. [Rollback Procedures](#8-rollback-procedures)
9. [Secrets Management](#9-secrets-management)
10. [Post-Deployment Monitoring (First 30 Minutes)](#10-post-deployment-monitoring-first-30-minutes)
11. [Incident Response for Common Deployment Failures](#11-incident-response-for-common-deployment-failures)
12. [Environment Sync Matrix](#12-environment-sync-matrix)

---

## 1. Pre-Deployment Checklist

Run every item below **before** any production deployment:

### 1.1 Code Quality Gates

```bash
# 1. Run full pre-commit suite (must pass clean)
make pre-commit

# 2. Validate prompt frontmatter
make validate-prompts

# 3. Run full test suite with coverage (threshold: 80%)
make test-coverage
# â†’ Verify last line: "TOTAL xx%  (threshold: 80%)" â€” must be â‰¥ 80%

# 4. TypeScript type-check
make type-check

# 5. Confirm the app builds
cd apps/web && npm run build
cd apps/api && python -m compileall .

# 6. Run E2E tests (production-like environment recommended)
make test-e2e
```

### 1.2 Docker Build Verification

```bash
# Build all production images locally â€” must succeed
docker compose build --pull
```

### 1.3 Environment Variables

- [ ] All required env vars (Section 2) are set in the target platform
- [ ] No production secrets differ from `.env.example` without documentation
- [ ] `USE_LOCAL_AI` is `False` in production (Claude fallback)
- [ ] `CORS_ORIGINS` includes the production frontend URL
- [ ] `JWT_SECRET` is a long, unique, randomly generated string
- [ ] Supabase project is the **production** project (not staging/dev)
- [ ] Database migrations have been applied (via Supabase Dashboard â†’ SQL Editor)

### 1.4 Pre-Deploy Sanity

- [ ] GitHub CI is green on the target branch (main)
- [ ] All PRs targeting main are merged
- [ ] CHANGELOG.md is updated for this deployment
- [ ] No active incidents (check Sentry, Railway Dashboard, Vercel Dashboard)
- [ ] Supabase production project has automated backups enabled
- [ ] Smoke test the app locally against production Supabase:
  ```bash
  # Point .env to production Supabase, then:
  make dev-api
  curl http://localhost:8000/health/ready
  # â†’ {"status":"healthy","dependencies":{...}}
  ```

---

## 2. Environment Variables Reference

### 2.1 Required (All Services)

| Variable | Description | Source | Example |
|---|---|---|---|
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard â†’ Settings â†’ API | `https://xxxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon public key | Supabase Dashboard â†’ Settings â†’ API | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_KEY` | Supabase service_role key (secret) | Supabase Dashboard â†’ Settings â†’ API | `eyJhbGciOiJIUzI1NiIs...` |
| `JWT_SECRET` | JWT signing secret (â‰¥ 32 chars) | Generate via `openssl rand -hex 32` | `a1b2c3d4e5f6...` |
| `JWT_ALGORITHM` | JWT algorithm | Fixed | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | Configurable | `10080` (7 days) |

### 2.2 Backend + Scheduler

| Variable | Description | Source | Default |
|---|---|---|---|
| `USE_LOCAL_AI` | Use Ollama vs Claude fallback | Configurable | `True` (set `False` in prod) |
| `OLLAMA_BASE_URL` | Ollama endpoint | Ollama host | `http://localhost:11434` |
| `CLAUDE_API_KEY` | Anthropic Claude API key | Anthropic Console | â€” |
| `RESEND_API_KEY` | Email delivery API key | Resend Dashboard | â€” |
| `CORS_ORIGINS` | Allowed CORS origins | Comma-separated URLs | `http://localhost:3000` |
| `RATE_LIMIT_MAX` | Max requests per window | Configurable | `100` |
| `RATE_LIMIT_WINDOW` | Rate limit window seconds | Configurable | `60` |
| `SENTRY_DSN` | Sentry error tracking DSN | Sentry Dashboard | â€” |
| `LOGTAIL_TOKEN` | Logtail ingestion token | Logtail Dashboard | â€” |

### 2.3 Frontend (Next.js)

| Variable | Description | Source | Default |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Public Supabase URL | Supabase Dashboard | â€” |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public Supabase anon key | Supabase Dashboard | â€” |
| `NEXT_PUBLIC_PWA_ENABLED` | Enable PWA features | Configurable | `true` |
| `NEXT_PUBLIC_SENTRY_DSN` | Public Sentry DSN | Sentry Dashboard | â€” |

### 2.4 Production-Specific Values

```env
# docker-compose production override
NODE_ENV=production
DEBUG=False
USE_LOCAL_AI=False
CORS_ORIGINS=https://secondbrain-os.vercel.app
```

---

## 3. Backend Deployment â€” Railway CLI

### 3.1 Prerequisites

```bash
# Install Railway CLI (one-time)
npm install -g @railway/cli

# Login (one-time)
railway login
```

### 3.2 Deploy to Railway

```bash
# Link to the project (one-time per clone)
railway link

# Deploy the latest code
railway up --service secondbrain-api

# Or use the Makefile target:
make deploy-api
```

### 3.3 Railway Dashboard Deploy (Alternative)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select the `secondbrain-api` project
3. Click "Deploy" â†’ "Trigger Deploy" â†’ branch `main`
4. Click "Deploy" to confirm

### 3.4 Verify Railway Deployment

```bash
# Check deployment status
railway status

# View live logs
railway logs -f

# Check health endpoint
curl https://api.secondbrain-os.com/health/ready
# â†’ {"status":"healthy","dependencies":{"supabase":"ok","ollama":"configured","claude_api":"configured"}}
```

---

## 4. Frontend Deployment â€” Vercel CLI

### 4.1 Prerequisites

```bash
# Install Vercel CLI (one-time)
npm install -g vercel

# Login (one-time)
vercel login
```

### 4.2 Deploy to Vercel

```bash
# Deploy to production
vercel --prod

# Or use the Makefile target:
make deploy-web
```

### 4.3 Automatic Deploy (Git Push)

Vercel auto-deploys on every push to `main`. To trigger without a code change:

```bash
git commit --allow-empty -m "deploy: trigger production deployment"
git push origin main
```

### 4.4 Verify Vercel Deployment

```bash
# Check deployment status
vercel list

# Open the deployed URL
open https://secondbrain-os.vercel.app

# Check the health endpoint (frontend has no /health, verify page loads)
curl -s -o /dev/null -w "%{http_code}" https://secondbrain-os.vercel.app
# â†’ 200
```

---

## 5. Scheduler Deployment

The scheduler is deployed alongside the backend on Railway as a separate service.

### 5.1 Deploy Scheduler

```bash
# Option A: Via Railway CLI with service flag
railway up --service secondbrain-scheduler

# Option B: Via Makefile
make deploy-scheduler
```

### 5.2 Verify Scheduler

```bash
# Check scheduler logs
railway logs -f --service secondbrain-scheduler

# Look for startup message:
# "Scheduler started" with job_count=14 (or expected count)

# Check health
curl https://scheduler.secondbrain-os.com/health
# â†’ {"status":"healthy","service":"scheduler","jobs":14}
```

### 5.3 Scheduler Health Status File

The scheduler writes its health status to a file at startup and every 5 minutes via the health_check cron. If jobs are failing, the `/health/ready` endpoint returns 503 (unhealthy).

---

## 6. Full Deployment

### 6.1 Sequential Deployment (Recommended)

```bash
# 1. Deploy API first (backward-compatible schema changes only)
make deploy-api

# 2. Verify API is healthy (wait for green health check)
sleep 30
curl https://api.secondbrain-os.com/health/ready

# 3. Deploy scheduler
make deploy-scheduler

# 4. Verify scheduler is running
sleep 15

# 5. Deploy frontend last (zero-downtime on Vercel)
make deploy-web
```

### 6.2 Batch Deployment

```bash
make deploy-all
```

---

## 7. Post-Deployment Verification

Run these checks **immediately after every deployment**:

### 7.1 API Health

```bash
# Health check
curl https://api.secondbrain-os.com/health
curl https://api.secondbrain-os.com/health/live
curl https://api.secondbrain-os.com/health/ready

# Expected response structure:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "timestamp": "2026-07-11T12:00:00Z",
#   "dependencies": {
#     "supabase": "ok",
#     "ollama": "configured",
#     "claude_api": "configured"
#   }
# }
```

### 7.2 API Functional Tests

```bash
# Auth endpoint
curl -X POST https://api.secondbrain-os.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}' \
  -w "\nHTTP %{http_code}\n"

# Tasks endpoint (expects 401 for unauthenticated â€” proves auth is working)
curl https://api.secondbrain-os.com/api/v1/tasks \
  -w "\nHTTP %{http_code}\n"
# â†’ 401 (expected without auth)

# Feature flags endpoint
curl https://api.secondbrain-os.com/api/v1/feature-flags \
  -w "\nHTTP %{http_code}\n"
```

### 7.3 Frontend Verification

```bash
# Page loads
curl -s -o /dev/null -w "Status: %{http_code}\nSize: %{size_download} bytes\nTTFB: %{time_starttransfer}s\n" \
  https://secondbrain-os.vercel.app
# â†’ Status: 200, Size: > 1000, TTFB: < 2s

# Lighthouse score (via CLI)
npx lighthouse https://secondbrain-os.vercel.app --quiet --output=json \
  | node -e "process.stdin.resume(); let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>{const r=JSON.parse(d);console.log('Performance:',r.categories.performance.score*100);console.log('Accessibility:',r.categories.accessibility.score*100);})"
# â†’ Performance â‰¥ 90, Accessibility â‰¥ 90
```

### 7.4 E2E Smoke Tests

```bash
# Run Playwright E2E tests against production
cd apps/web
PROD_URL=https://secondbrain-os.vercel.app npx playwright test --grep "@smoke"
```

### 7.5 Data Integrity Checks

```bash
# Verify Supabase connection via API
curl https://api.secondbrain-os.com/api/v1/tasks?limit=1 \
  -H "Authorization: Bearer $(your_test_token)" \
  | python -c "import sys,json; d=json.load(sys.stdin); assert 'data' in d, 'Missing data field'; print(f'API connected: {len(d[\"data\"])} tasks returned')"

# Check that the database has recent data (not empty production)
```

---

## 8. Rollback Procedures

### 8.1 Rollback Criteria

Initiate rollback if any of the following are detected within 30 minutes of deployment:
- Health endpoint returns non-200 status
- Error rate > 5% (check Sentry / Railway Vercel logs)
- Key API endpoint returns 500 errors
- Frontend fails to load (> 5s TTFB or blank page)
- Auth flow is broken
- Data integrity issue detected (missing/corrupted records)

### 8.2 Frontend Rollback â€” Vercel

```bash
# Option A: CLI rollback (fastest â€” ~30 seconds)
vercel rollback secondbrain-os --safe=10

# Option B: Dashboard rollback
# 1. Go to https://vercel.com/dashboard â†’ secondbrain-os
# 2. Click "Deployments" tab
# 3. Find the last known-good deployment
# 4. Click "..." â†’ "Promote to Production"

# Option C: Git revert + push (triggers auto-deploy)
git revert HEAD --no-edit
git push origin main
```

**Rollback ETA:** < 2 minutes

### 8.3 Backend Rollback â€” Railway

```bash
# Option A: CLI rollback
railway rollback --service secondbrain-api

# Option B: Dashboard rollback
# 1. Go to https://railway.app/dashboard â†’ secondbrain-api
# 2. Click "Deployments"
# 3. Select the previous successful deployment
# 4. Click "Redeploy"

# Option C: Redeploy a specific deployment
railway redeploy <deployment-id>
```

**Rollback ETA:** < 5 minutes

### 8.4 Scheduler Rollback

Repeat the Railway rollback procedure for the `secondbrain-scheduler` service.

### 8.5 Full Rollback

```bash
# Rollback all services (frontend + backend + scheduler)
make deploy-rollback
```

### 8.6 Database Rollback (Supabase)

```bash
# Supabase does not auto-rollback migrations. To undo a database change:
#
# 1. Open Supabase Dashboard â†’ Database â†’ SQL Editor
# 2. Run the DOWN migration SQL (reverse of the deployed migration)
# 3. Verify data integrity after rollback
#
# âš  Database rollbacks are destructive. Prefer deploying a forward fix.
```

### 8.7 Post-Rollback Verification

After rollback, repeat the [Post-Deployment Verification](#7-post-deployment-verification) steps to confirm the system is healthy.

---

## 9. Secrets Management

### 9.1 Principles

- **Never commit secrets** to the repository. `.env` and `.env.*` are in `.gitignore` and `.dockerignore`.
- **Use platform secret managers** â€” Vercel Environment Variables, Railway Secrets, not files.
- **Rotate secrets quarterly** â€” especially `JWT_SECRET`, `CLAUDE_API_KEY`, `SUPABASE_SERVICE_KEY`.
- **Audit access** â€” only the Developer has access to production secrets.

### 9.2 Railway Secrets

Set via CLI:
```bash
railway variables set JWT_SECRET="$(openssl rand -hex 32)"
railway variables set SUPABASE_URL="https://xxxx.supabase.co"
railway variables set SUPABASE_KEY="eyJ..."
railway variables set SUPABASE_SERVICE_KEY="eyJ..."
railway variables set CLAUDE_API_KEY="sk-ant-..."
railway variables set RESEND_API_KEY="re_..."
railway variables set CORS_ORIGINS="https://secondbrain-os.vercel.app"
railway variables set USE_LOCAL_AI="False"
```

Set via Dashboard:
1. Go to Railway Dashboard â†’ Project â†’ Variables
2. Add each variable with its production value
3. Click "Save"

### 9.3 Vercel Secrets

Set via CLI:
```bash
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
vercel env add NEXT_PUBLIC_PWA_ENABLED production
```

Set via Dashboard:
1. Go to Vercel Dashboard â†’ Project â†’ Settings â†’ Environment Variables
2. Add each variable for the `Production` environment
3. Click "Save"

---

## 10. Post-Deployment Monitoring (First 30 Minutes)

### 10.1 Immediate Checks (Minutes 0-5)

| Check | Tool | What to Look For | Action |
|---|---|---|---|
| API health | `curl /health/ready` | `status: "healthy"` | If 503/error â†’ rollback |
| Scheduler health | `curl scheduler:8001/health` | `status: "healthy"` | If unhealthy â†’ check logs |
| Frontend loads | Browser | Page renders without JS errors | If blank â†’ check Vercel build logs |
| Auth flow | Manual login | Login redirects correctly | If broken â†’ check Supabase auth config |

### 10.2 Monitoring Dashboards (Minutes 5-15)

| Dashboard | URL | Metrics to Watch |
|---|---|---|
| Railway Logs | Railway Dashboard â†’ Logs | Error rate, 5xx responses, startup errors |
| Vercel Analytics | Vercel Dashboard â†’ Analytics | TTFB, Error rate, 404s |
| Vercel Logs | Vercel Dashboard â†’ Logs | Build errors, runtime errors |
| Supabase Dashboard | Supabase Dashboard â†’ Database | Connection count, query performance |
| Sentry (if configured) | Sentry Dashboard | Error count, new issues, crash-free rate |

### 10.3 Watch Metrics (Minutes 15-30)

- **API p95 latency** â€” should stay < 500ms
- **Error rate** â€” should stay < 1%
- **Scheduler jobs** â€” all 14 jobs should trigger on their schedule
- **Frontend TTFB** â€” should stay < 2s
- **CPU/Memory** â€” no sustained spikes above 80%

### 10.4 Communication

- If any metric is above threshold â†’ assess severity (P0-P4)
- For P0/P1 â†’ initiate rollback immediately, then investigate
- For P2/P3 â†’ file an issue, fix in next deployment
- Post a message in the team channel: "âœ… Production deploy vX.X.X complete. Monitoring..."

---

## 11. Incident Response for Common Deployment Failures

### 11.1 Build Failure

**Symptom:** Railway or Vercel build fails.
**Root Causes:** Missing dependency, broken import, TypeScript error, lint error.

**Response:**
```bash
# 1. Check build logs
railway logs --service secondbrain-api --build   # Railway
vercel log                                      # Vercel

# 2. Fix the issue locally, verify with:
make pre-commit

# 3. Commit fix and push
git add -A && git commit -m "fix: build failure"
git push origin main
```

### 11.2 Health Check Failure After Deploy

**Symptom:** `/health/ready` returns 503.
**Root Causes:** Database connection issue, missing env var, service not fully started.

**Response:**
```bash
# 1. Check live logs
railway logs -f --service secondbrain-api

# 2. Verify environment variables
railway variables list

# 3. Check Supabase connectivity
# (Add debug logging to health check if needed)

# 4. If startup takes longer than healthcheckTimeout, increase the timeout in railway.json
```

### 11.3 Database Connection Issues

**Symptom:** API returns 500 on any database query.
**Root Causes:** Wrong `SUPABASE_URL`/`SUPABASE_KEY`, network policy, connection pool exhausted.

**Response:**
```bash
# 1. Verify Supabase project is accessible
curl https://<your-project>.supabase.co/rest/v1/ \
  -H "apikey: $SUPABASE_KEY"

# 2. Check Supabase Dashboard â†’ Database â†’ Connections
# 3. Verify IP access policies allow Railway outbound IPs
# 4. If connection pool is exhausted â†’ scale up or reduce pool size
```

### 11.4 AI Service Failure

**Symptom:** Chat or agent endpoints return errors.
**Root Causes:** Ollama not running, Claude API key expired, circuit breaker open.

**Response:**
```bash
# 1. Check USE_LOCAL_AI setting
railway variables get USE_LOCAL_AI
# â†’ Should be "False" in production

# 2. Verify Claude API key
railway variables get CLAUDE_API_KEY
# â†’ Should be set and non-empty

# 3. Check circuit breaker state
# (Add to health check if needed)

# 4. If using Ollama in production: verify Ollama service is running
```

### 11.5 Scheduler Not Starting

**Symptom:** Cron jobs don't trigger.
**Root Causes:** Import error, port conflict, database unavailable.

**Response:**
```bash
# 1. Check scheduler logs
railway logs -f --service secondbrain-scheduler

# 2. Look for startup message:
# "Scheduler started" with job count

# 3. If "Failed to write initial health status" â†’ check filesystem permissions
# 4. If import errors â†’ verify PYTHONPATH includes packages/
```

### 11.6 CORS Errors in Browser

**Symptom:** Frontend can connect, API calls fail with CORS errors.
**Root Causes:** `CORS_ORIGINS` doesn't include the Vercel deployment URL.

**Response:**
```bash
# 1. Check current CORS setting
railway variables get CORS_ORIGINS

# 2. Update to include the production URL:
railway variables set CORS_ORIGINS="https://secondbrain-os.vercel.app,https://secondbrain-os.railway.app"

# 3. Redeploy the API
make deploy-api
```

### 11.7 Version Mismatch

**Symptom:** Frontend expects API field that doesn't exist, or vice versa.
**Root Causes:** Deploying frontend and backend out of sync.

**Response:**
```bash
# Deploy both in quick succession (frontend first to avoid breaking existing users)
make deploy-web
# Verify
make deploy-api
# Verify
```

---

## 12. Environment Sync Matrix

| Config Item | Local Dev | Railway (Staging) | Railway (Production) | Vercel (Production) |
|---|---|---|---|---|
| `NODE_ENV` | `development` | `production` | `production` | `production` |
| `DEBUG` | `True` | `False` | `False` | â€” |
| `USE_LOCAL_AI` | `True` | `False` | `False` | â€” |
| `CORS_ORIGINS` | `http://localhost:3000` | Vercel preview URL | `https://secondbrain-os.vercel.app` | â€” |
| `SUPABASE_URL` | Dev project | Staging project | Production project | â€” |
| Database | Local / Dev Supabase | Staging Supabase | Production Supabase | â€” |
| Auth | Google OAuth (local) | Google OAuth | Google OAuth (prod URIs) | â€” |
| SSL | No | Yes (Railway) | Yes (Railway) | Yes (Vercel) |
| Secrets | `.env` file | Railway Secrets | Railway Secrets | Vercel Env Vars |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial production deployment runbook |
