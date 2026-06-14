# Environment Architecture

> **Document ID**: SB-ENV-001  
> **Version**: 1.0.0  
> **Status**: Active  
> **Last Updated**: 2026-06-11  
> **Classification**: Internal — Engineering Reference  
> **Target Audience**: Developers, DevOps Engineers, QA Engineers

---

## Table of Contents

1. [Environment Architecture Overview](#1-environment-architecture-overview)
2. [Local Development Setup](#2-local-development-setup)
3. [Staging Environment](#3-staging-environment)
4. [Production Environment](#4-production-environment)
5. [Preview Deployments](#5-preview-deployments)
6. [Environment Variable Management](#6-environment-variable-management)
7. [Database Migration Strategy](#7-database-migration-strategy)
8. [Feature Flags Per Environment](#8-feature-flags-per-environment)
9. [AI Model Differences Per Environment](#9-ai-model-differences-per-environment)
10. [Testing in Each Environment](#10-testing-in-each-environment)
11. [Promotion Workflow: Dev → Staging → Prod](#11-promotion-workflow-dev--staging--prod)
12. [Rollback Procedures Per Environment](#12-rollback-procedures-per-environment)
13. [Environment Parity Checklist](#13-environment-parity-checklist)

---

## 1. Environment Architecture Overview

### 1.1 Environment Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT ARCHITECTURE                             │
│                                                                             │
│   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│   │   LOCAL DEV       │    │    PREVIEW        │    │    PRODUCTION    │      │
│   │   (Developer)     │    │    (PR Deploy)    │    │    (Live)        │      │
│   │                   │    │                   │    │                  │      │
│   │  ┌─────────────┐  │    │  ┌─────────────┐  │    │  ┌────────────┐  │      │
│   │  │ Next.js :3000│  │    │  │ Vercel      │  │    │  │ Vercel     │  │      │
│   │  │ FastAPI:8000 │  │    │  │ Preview URL │  │    │  │ Production │  │      │
│   │  │ Ollama:11434 │  │    │  │ Railway Dev │  │    │  │ Railway    │  │      │
│   │  │ Supabase     │  │    │  │ Branch       │  │    │  │ Production │  │      │
│   │  │ (local CLI)  │  │    │  └──────┬──────┘  │    │  └────────────┘  │      │
│   │  └─────────────┘  │    │         │          │    │                  │      │
│   └──────────────────┘    └──────────┼──────────┘    └──────────────────┘      │
│                                      │                                         │
│                           ┌──────────┴──────────┐                              │
│                           │     STAGING          │                              │
│                           │     (Pre-Prod)       │                              │
│                           │                      │                              │
│                           │  ┌────────────────┐  │                              │
│                           │  │ Vercel Staging  │  │                              │
│                           │  │ Railway Staging │  │                              │
│                           │  │ Supabase        │  │                              │
│                           │  │ Staging Project │  │                              │
│                           │  └────────────────┘  │                              │
│                           └──────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘

                    Feature Branch  ──▶  PR Preview
                           │
                    Main Branch  ──▶  Staging Deploy
                           │
                    Release Tag  ──▶  Production Deploy
```

### 1.2 Environment Summary

| Environment | Purpose | Hosting | DB | AI | Access |
|---|---|---|---|---|---|
| **Local Dev** | Development, debugging | Local machine | Supabase local or remote | Ollama (local) | Developer only |
| **Preview (PR)** | Feature review, testing | Vercel + Railway ephemeral | Supabase staging project | Ollama (local) or Staging | Team + Reviewers |
| **Staging** | Integration testing, UAT | Vercel + Railway staging | Supabase staging project | Staging model (smaller) | Internal team |
| **Production** | Live user traffic | Vercel + Railway prod | Supabase production | Full model (claude) | All users |

### 1.3 Environment Isolation

| Isolation Domain | Local | Preview | Staging | Production |
|---|---|---|---|---|
| **Frontend** | Completely isolated | Dedicated preview URL | Dedicated subdomain | Production domain |
| **Backend** | Local process | Railway branch service | Railway staging project | Railway production |
| **Database** | Local or dev-only | Shared staging DB | Dedicated staging DB | Production DB (no access) |
| **AI** | Local Ollama | Local Ollama or staging | Smaller model | Full model |
| **Auth** | Test accounts | Test accounts | Test + internal accounts | Real user auth |
| **Cache** | In-memory (volatile) | Per-instance | Shared staging cache | Production cache |

---

## 2. Local Development Setup

### 2.1 Required Tooling

| Tool | Version | Purpose | Installation |
|---|---|---|---|
| Node.js | 18.x | Frontend runtime | `nvm install 18` or `winget install OpenJS.NodeJS.LTS` |
| Python | 3.10+ | Backend runtime | `winget install Python.Python.3.10` or pyenv |
| Git | Latest | Version control | `winget install Git.Git` |
| Ollama | Latest | Local AI | `winget install Ollama.Ollama` or `curl -fsSL https://ollama.ai/install.sh | sh` |
| Docker Desktop | Latest | Container orchestration | `winget install Docker.DockerDesktop` |
| Supabase CLI | Latest | Local Supabase | `npm install -g supabase` |

### 2.2 Local Startup Sequence

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
cd apps/api
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 3: Start Frontend
cd apps/web
npm install
npm run dev

# Terminal 4: Start Scheduler (optional)
cd services/scheduler
pip install -r requirements.txt
python main.py

# Terminal 5: Prompt Validation
python scripts/validate_prompts.py
```

### 2.3 Local Hosts Configuration

```
# C:\Windows\System32\drivers\etc\hosts (Windows)
# /etc/hosts (macOS/Linux)

127.0.0.1  localhost
127.0.0.1  api.localhost     # Backend alias (optional)
```

### 2.4 Local Environment Variables

```env
# apps/web/.env.local
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:8000

# apps/api/.env
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=super-secret-jwt-for-dev-only
JWT_ALGORITHM=HS256
CLAUDE_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=True
RESEND_API_KEY=re_...
APP_NAME="Second Brain OS (Local Dev)"
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 2.5 Local Supabase Setup

```bash
# Start local Supabase (requires Docker)
supabase init
supabase start

# Output:
# Started supabase local development setup.
#         API URL: http://localhost:54321
#          DB URL: postgresql://postgres:postgres@localhost:54322/postgres
#      Studio URL: http://localhost:54323
#    Inbucket URL: http://localhost:54324
#       anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Apply local migrations
supabase db push

# Reset local DB
supabase db reset
```

### 2.6 Local vs Remote Data Strategy

```yaml
Data Strategy for Local Development:

  Option 1: Local Supabase (Docker)  [RECOMMENDED]
    - Full isolation
    - No network dependency
    - Fast iteration
    - Seed data from scripts/
    - Reset on demand

  Option 2: Remote Supabase (Dev Project)
    - Shared data across team
    - Network required
    - Risk of polluting shared DB
    - Use dedicated dev project (not staging/prod)

  Option 3: Supabase Branching
    - Each branch gets a Supabase preview DB
    - Supabase Pro feature ($25/mo)
    - Best for complex migration testing
```

---

## 3. Staging Environment

### 3.1 Staging Architecture

```
                      ┌──────────────────────────────┐
                      │       STAGING                 │
                      │                              │
                      │  https://staging.example.com  │
                      │                              │
                      │  ┌────────────────────────┐  │
                      │  │  Vercel Staging Branch │  │
                      │  │  (Git: main branch)     │  │
                      │  └───────────┬────────────┘  │
                      │              │                │
                      │              ▼                │
                      │  ┌────────────────────────┐  │
                      │  │  Railway Staging        │  │
                      │  │  (staging branch)       │  │
                      │  │  FastAPI + Scheduler    │  │
                      │  └───────────┬────────────┘  │
                      │              │                │
                      │              ▼                │
                      │  ┌────────────────────────┐  │
                      │  │  Supabase Staging       │  │
                      │  │  (separate project)     │  │
                      │  │  + Anonymized Data      │  │
                      │  └────────────────────────┘  │
                      └──────────────────────────────┘
```

### 3.2 Staging Configuration

**Vercel Staging:**

| Setting | Value |
|---|---|
| Git Branch | `main` |
| Production Branch | (none — staging is not production) |
| Auto Deploy | On push to `main` |
| Domain | `staging-secondbrain-os.vercel.app` |
| Custom Domain | `staging.secondbrain-os.com` |
| Environment | `staging` |
| Framework Preset | Next.js |
| Build Command | `npm run build` |
| Output Directory | `.next` |

**Railway Staging:**

| Setting | Value |
|---|---|
| Project | `sbos-api-staging` |
| Branch | `staging` |
| Service | `fastapi-backend` |
| Domain | `staging.api.secondbrain-os.com` |
| Container Size | 1 vCPU, 512MB RAM |
| Auto Deploy | On push to `staging` branch |
| Health Check | `/health` |

**Supabase Staging:**

| Setting | Value |
|---|---|
| Project Name | `sbos-staging` |
| Region | us-east-1 |
| DB Password | (separate from production) |
| PITR | Enabled (7-day retention) |
| Branching | Connected to GitHub branches |

### 3.3 Staging Environment Variables

```env
# Vercel Staging Env Vars
NEXT_PUBLIC_SUPABASE_URL=https://staging-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=https://staging.api.secondbrain-os.com

# Railway Staging Env Vars
SUPABASE_URL=https://staging-project.supabase.co
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
JWT_SECRET=staging-jwt-secret-do-not-use-for-prod
JWT_ALGORITHM=HS256
CLAUDE_API_KEY=...
OLLAMA_BASE_URL=http://ollama-staging:11434
USE_LOCAL_AI=True
RESEND_API_KEY=...
APP_NAME="Second Brain OS (Staging)"
DEBUG=True
CORS_ORIGINS=https://staging-secondbrain-os.vercel.app,https://staging.secondbrain-os.com
```

### 3.4 Staging Access Control

| User Type | Access | Restrictions |
|---|---|---|
| Developers | Full access | Auth via Google OAuth (dev emails) |
| QA Testers | Limited access | Test accounts only |
| External | No access | Blocked at CDN level (IP whitelist or basic auth) |

**Basic Auth for Staging (Vercel):**
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "x-vercel-protection-bypass",
          "value": "staging-bypass-secret"
        }
      ]
    }
  ]
}
```

### 3.5 Staging Data Strategy

| Data Type | Source | Refresh Frequency | Volume |
|---|---|---|---|
| Schema | Migrations from `main` | Every deploy | ~20 tables |
| Seed Data | `scripts/seed_staging.py` | Weekly | ~100 users, ~1000 records |
| Anonymized Prod Data | `scripts/anonymize.py` | Monthly | ~500MB |

---

## 4. Production Environment

### 4.1 Production Architecture

```
                      ┌──────────────────────────────┐
                      │      PRODUCTION               │
                      │                              │
                      │  https://secondbrain-os.com   │
                      │                              │
                      │  ┌────────────────────────┐  │
                      │  │  Vercel Production     │  │
                      │  │  (main branch,         │  │
                      │  │   custom domain)       │  │
                      │  └───────────┬────────────┘  │
                      │              │                │
                      │              ▼                │
                      │  ┌────────────────────────┐  │
                      │  │  Railway Production     │  │
                      │  │  (production branch)    │  │
                      │  │  FastAPI + Scheduler    │  │
                      │  └───────────┬────────────┘  │
                      │              │                │
                      │              ▼                │
                      │  ┌────────────────────────┐  │
                      │  │  Supabase Production    │  │
                      │  │  (production project)   │  │
                      │  │  + Full data + PITR    │  │
                      │  └────────────────────────┘  │
                      └──────────────────────────────┘
```

### 4.2 Production Configuration

**Vercel Production:**

| Setting | Value |
|---|---|
| Git Branch | `main` |
| Production Branch | `main` |
| Auto Deploy | On push to `main` (after CI passes) |
| Domain | `secondbrain-os.com` |
| Environment | `production` |
| Framework Preset | Next.js |
| Build Command | `npm run build` |
| Output Directory | `.next` |
| Function Max Duration | 30s (API), 10s (SSR) |
| Function Memory | 1024MB (API), 512MB (SSR) |

**Railway Production:**

| Setting | Value |
|---|---|
| Project | `sbos-api-production` |
| Branch | `production` |
| Service | `fastapi-backend` |
| Domain | `api.secondbrain-os.com` |
| Container Size | 1 vCPU, 512MB RAM |
| Auto Deploy | Manual (click-to-deploy after approval) |
| Health Check | `/health` |
| Sleep Mode | Never |

**Supabase Production:**

| Setting | Value |
|---|---|
| Project Name | `sbos-production` |
| Region | us-east-1 |
| DB Password | (stored in 1Password) |
| PITR | Enabled (7-day retention) |
| SSL Enforcement | Required |
| Network Restrictions | IP allowlist (Railway, office IPs) |

### 4.3 Production Environment Variables

```env
# Vercel Production Env Vars
NEXT_PUBLIC_SUPABASE_URL=https://production-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=https://api.secondbrain-os.com

# Railway Production Env Vars
SUPABASE_URL=https://production-project.supabase.co
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
JWT_SECRET=production-jwt-secret-in-1password
JWT_ALGORITHM=HS256
CLAUDE_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=False
RESEND_API_KEY=...
APP_NAME="Second Brain OS"
DEBUG=False
CORS_ORIGINS=https://secondbrain-os.com,https://www.secondbrain-os.com
```

### 4.4 Production Readiness Gates

Before promoting to production, the following must pass:

```
☐ All CI checks pass (frontend, backend, prompts, security)
☐ Staging deployment fully validated
☐ Database migrations tested and approved
☐ Performance benchmarks meet targets
☐ Security scan completed (no high-severity vulns)
☐ Changelog updated
☐ Release manager approval obtained
☐ Rollback plan documented
☐ Backup verified (database + environment vars)
```

### 4.5 Production Runbook Summary

| Action | Command / Procedure | Responsible |
|---|---|---|
| Deploy | GitHub merge to `main` → Vercel auto-deploy | CI/CD |
| Verify | Check Vercel deployment status, Railway logs | Developer |
| Monitor | Watch Sentry errors, Vercel Analytics, Supabase | Developer |
| Rollback | Vercel: Deployment → ... → Rollback | Developer |
| Emergency | Railway: Previous deploy → Redeploy | On-call |

---

## 5. Preview Deployments

### 5.1 Vercel Preview Deployments

**How it works:**
- Every push to a PR branch triggers a Vercel preview deployment
- Vercel assigns a unique URL: `project-name-git-branch-hash.vercel.app`
- The preview is a full Next.js deployment with its own environment variables

**Configuration:**
```json
// vercel.json
{
  "github": {
    "silent": false,
    "autoJobCancelation": true
  },
  "preview": {
    "enabled": true,
    "minimumInterval": 300
  }
}
```

**Preview URLs:**
```
Feature Branches:
  https://sbos-git-feature-tasks-ui-abc123.vercel.app    (unique hash)

PR Comments:
  Vercel bot posts the URL automatically in PR comments
```

### 5.2 Railway Ephemeral Environments

Railway does not natively support ephemeral environments, but the staging project can serve as the shared preview backend:

```yaml
Preview Backend Strategy:
  - All preview deployments share the Railway staging backend
  - Feature branches do NOT deploy separate backend instances
  - Railway staging branch is used for backend integration
  - When PR is merged, staging backend auto-deploys
```

**Limitations:**
| Limitation | Workaround |
|---|---|
| One shared staging backend | Isolate via API key prefix or header |
| No per-branch DB | Use Supabase branching (Pro feature) |
| Concurrent PRs share same backend | Acceptable for low-traffic team |

### 5.3 Supabase Branching (Future)

Supabase Pro ($25/mo) provides database branching:

```
Each PR branch → Supabase Branch → Preview Deploy

  main  ─── staging (stable)
  feat/login ─── feat/login-preview (isolated)
  feat/ui ─── feat/ui-preview (isolated)
```

### 5.4 Preview Deployment Workflow

```
Developer pushes to branch `feat/new-feature`
    │
    ▼
GitHub detects push to feature branch
    │
    ▼
CI Pipeline starts (lint, type-check, test, validate prompts)
    │
    ├── Success → Vercel Preview Deploy + Railway staging deploy
    │
    └── Failure → PR checks show ❌, developer notified
    │
    ▼
Vercel bot posts preview URL in PR
    │
    ▼
Reviewer tests the preview
    │
    ▼
PR merged → Preview auto-canceled → Main deploys to staging
```

---

## 6. Environment Variable Management

### 6.1 Environment Variable Sources

| Source | Frontend | Backend | Purpose |
|---|---|---|---|
| `.env.local` | `apps/web/` | `apps/api/` | Local development |
| Vercel Dashboard | ✅ Project settings | — | Frontend env vars per env |
| Railway Dashboard | — | ✅ Service variables | Backend env vars per env |
| GitHub Actions Secrets | — | — | CI/CD pipeline secrets |
| 1Password Vault | — | — | Backup / disaster recovery |

### 6.2 Environment Variable Matrix

| Variable | Local | Staging | Production | Notes |
|---|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Local Supabase | Staging | Production | Public (exposed to browser) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Local | Staging | Production | Public (safe for client) |
| `NEXT_PUBLIC_API_URL` | `localhost:8000` | Staging | Production | Public |
| `SUPABASE_URL` | Local | Staging | Production | Secret |
| `SUPABASE_SERVICE_KEY` | Local | Staging | Production | **Critical secret** |
| `JWT_SECRET` | Dev default | Staging secret | Production secret | **Critical secret** |
| `CLAUDE_API_KEY` | Personal key | Staging key | Production key | **Critical secret** |
| `USE_LOCAL_AI` | `True` | `True` | `False` | Local vs remote |
| `DEBUG` | `True` | `True` | `False` | Error verbosity |
| `CORS_ORIGINS` | Localhost | Staging URL | Prod URL | Frontend origin |

### 6.3 Environment Variable Security

| Practice | Frontend | Backend |
|---|---|---|
| **Exposure** | `NEXT_PUBLIC_*` vars exposed in browser | All vars hidden from clients |
| **Storage** | Vercel encrypted env vars | Railway encrypted env vars |
| **Rotation** | Quarterly or on team change | Quarterly or on security incident |
| **Audit** | Vercel audit log (Pro) | Manual check quarterly |
| **Backup** | 1Password vault | 1Password vault |

### 6.4 Validation Script

```python
# scripts/validate_env.py
import os
import sys

REQUIRED_VARS = {
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SUPABASE_SERVICE_KEY",
    "JWT_SECRET",
    "JWT_ALGORITHM",
    "CLAUDE_API_KEY",
    "APP_NAME",
    "CORS_ORIGINS",
}

def validate_env():
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    print("All required environment variables are set.")
    sys.exit(0)

if __name__ == "__main__":
    validate_env()
```

---

## 7. Database Migration Strategy

### 7.1 Migration Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Develop   │────▶│    Test     │────▶│   Deploy    │
│  (Local)    │     │  (Staging)  │     │  (Prod)     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Create SQL  │     │ Run migrate │     │ Run migrate │
│ in supabase │     │ on staging  │     │ on prod     │
│ /migrations │     │ + verify    │     │ + verify    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 7.2 Migration File Structure

```
supabase/
└── migrations/
    ├── 20260101000000_initial_schema.sql
    ├── 20260201000000_add_habit_logs.sql
    ├── 20260301000000_add_sleep_tracking.sql
    ├── 20260401000000_add_income_entries.sql
    ├── 20260501000000_add_ai_memory.sql
    └── README.md
```

### 7.3 Migration Best Practices

| Practice | Description | Enforced By |
|---|---|---|
| **Forward-only** | Never modify committed migrations; create new ones | Code review |
| **Idempotent** | Use `CREATE IF NOT EXISTS`, `ALTER ... IF EXISTS` | Migration template |
| **Tested on staging** | All migrations run on staging before prod | CI/CD pipeline |
| **Backward compatible** | Don't remove columns/indices still in use | Code review |
| **Rollback plan** | Include rollback SQL for each migration | Migration template |
| **One concern per file** | Single table/feature per migration file | Convention |

### 7.4 Staging Migration Testing

```bash
# Before deploying to production:
# 1. Push to main branch → auto-deploys to staging
# 2. Run migrations on staging:
supabase db push --linked  # Uses staging project link

# 3. Verify migration results:
supabase db diff --linked

# 4. Run integration tests:
pytest tests/ -x --env=staging

# 5. Only then promote to production
```

### 7.5 Production Migration Procedure

```bash
# 1. Create backup
pg_dump --format=custom -f pre_migration_backup.dump \
  --dbname="$(supabase link --project-ref production)"

# 2. Run migration
supabase db push --linked  # Links to production project

# 3. Verify
supabase db diff --linked

# 4. If migration fails (10 min timeout):
#    - Auto-rollback not supported, restore from backup manually
#    - Or run rollback SQL if provided
```

---

## 8. Feature Flags Per Environment

### 8.1 Feature Flag Architecture

```typescript
// packages/shared/utils/feature-flags.ts
export type FeatureFlag = {
  name: string
  enabled: {
    local: boolean
    preview: boolean
    staging: boolean
    production: boolean
  }
  description: string
  owner: string
}

export const FEATURE_FLAGS: Record<string, FeatureFlag> = {
  NEW_DASHBOARD: {
    name: 'new-dashboard',
    enabled: {
      local: true,
      preview: true,
      staging: true,
      production: false,  // Rolled out after UAT
    },
    description: 'New dashboard with bento grid layout',
    owner: '@developer',
  },
  AI_SLEEP_AGENT: {
    name: 'ai-sleep-agent',
    enabled: {
      local: true,
      preview: true,
      staging: true,
      production: false,
    },
    description: 'AI-powered bedtime wind-down messages',
    owner: '@developer',
  },
  V2_API: {
    name: 'v2-api',
    enabled: {
      local: true,
      preview: false,
      staging: true,
      production: false,
    },
    description: 'API v2 with improved response format',
    owner: '@developer',
  },
}
```

### 8.2 Feature Flag Evaluation

```typescript
// Usage in components
import { FEATURE_FLAGS } from '@/utils/feature-flags'

function DashboardPage() {
  const env = process.env.NEXT_PUBLIC_APP_ENV || 'local'
  const isNewDashboardEnabled = FEATURE_FLAGS.NEW_DASHBOARD.enabled[env]

  if (isNewDashboardEnabled) {
    return <NewDashboard />
  }
  return <LegacyDashboard />
}
```

### 8.3 Environment-Level Feature Comparison

| Feature | Local | Preview | Staging | Production |
|---|---|---|---|---|
| New Dashboard | ✅ | ✅ | ✅ | ❌ (Pilot) |
| AI Sleep Agent | ✅ | ✅ | ✅ | ❌ |
| V2 API | ✅ | ❌ | ✅ | ❌ |
| Analytics Dashboard | ✅ | ✅ | ❌ | ❌ |
| Export Features | ✅ | ✅ | ✅ | ✅ |
| Admin Panel | ✅ | ✅ | ✅ | ❌ |
| Debug Logging | ✅ | ❌ | ✅ | ❌ |

---

## 9. AI Model Differences Per Environment

### 9.1 AI Configuration by Environment

| Environment | Primary AI | Fallback | Model | Temperature | Max Tokens | Cost |
|---|---|---|---|---|---|---|
| **Local** | Ollama | N/A | Mistral 7B | 0.5 | 4096 | $0 |
| **Preview** | Ollama (dev machine) | Claude | Mistral 7B / Claude | 0.5 | 4096 | ~$0.02/req |
| **Staging** | Ollama (staging) | Claude | Mistral 7B (staging container) | 0.5 | 4096 | ~$0.02/req |
| **Production** | Ollama (if available) | **Claude** | Claude Sonnet 4 | 0.5 | 8192 | ~$0.015/req |

### 9.2 Model Selection Logic

```python
# packages/ai/client.py
import os

def get_model_config():
    env = os.getenv("APP_ENV", "local")
    use_local = os.getenv("USE_LOCAL_AI", "True").lower() == "true"

    configs = {
        "local": {
            "primary": "ollama/mistral:7b",
            "fallback": None,  # No fallback needed
            "temperature": 0.5,
            "max_tokens": 4096,
        },
        "staging": {
            "primary": "ollama/mistral:7b",
            "fallback": "claude-sonnet-4",
            "temperature": 0.5,
            "max_tokens": 4096,
        },
        "production": {
            "primary": "claude-sonnet-4" if not use_local else "ollama/mistral:7b",
            "fallback": "claude-sonnet-4",
            "temperature": 0.5,
            "max_tokens": 8192,
        }
    }

    return configs.get(env, configs["local"])
```

### 9.3 Key Differences

```
Local:            ollama (localhost:11434) → immediate, free
Preview:          ollama (dev machine) → may be offline, falls back to Claude
Staging:          ollama (staging container) → consistent, tracked costs
Production:       Claude (API) → reliable, monitored, sanctioned cost
```

---

## 10. Testing in Each Environment

### 10.1 Test Types by Environment

| Test Type | Local | Preview | Staging | Production |
|---|---|---|---|---|
| **Unit Tests** | ✅ Run locally | ✅ Run in CI | ❌ | ❌ |
| **Integration Tests** | ✅ Run locally | ✅ Run in CI | ✅ Run on deploy | ❌ |
| **E2E Tests** | ✅ Run locally | ❌ | ✅ Run on deploy | ❌ |
| **Performance Tests** | ❌ | ❌ | ✅ Run on deploy | ✅ Monitored |
| **Security Scan** | ✅ Run locally | ✅ Run in CI | ❌ | ✅ Scheduled |
| **Smoke Tests** | ❌ | ❌ | ✅ Run on deploy | ✅ Run on deploy |

### 10.2 Testing Commands by Environment

```bash
# Local
pytest tests/ -x                               # All tests
npm run lint && npm run type-check              # Frontend checks
ruff check . && python -m py_compile main.py    # Backend checks

# CI (all environments)
python -m pytest tests/ -x --junitxml=report.xml  # Test report
python scripts/validate_prompts.py                 # Prompt validation

# Staging (post-deploy)
pytest tests/ -x --env=staging                     # Integration against staging
playwright test --config=e2e/playwright.config.ts  # E2E tests (future)

# Production (post-deploy)
curl -f https://api.secondbrain-os.com/health     # Health check
curl -f https://secondbrain-os.com                # Frontend check
```

### 10.3 Environment Smoke Test

```python
# scripts/smoke_test.py
"""Run smoke tests against deployed environments."""
import requests
import sys

ENDPOINTS = {
    "local": {
        "frontend": "http://localhost:3000",
        "backend": "http://localhost:8000",
        "health": "http://localhost:8000/health",
    },
    "staging": {
        "frontend": "https://staging-secondbrain-os.vercel.app",
        "backend": "https://staging.api.secondbrain-os.com",
        "health": "https://staging.api.secondbrain-os.com/health",
    },
    "production": {
        "frontend": "https://secondbrain-os.com",
        "backend": "https://api.secondbrain-os.com",
        "health": "https://api.secondbrain-os.com/health",
    }
}

def smoke_test(env: str):
    urls = ENDPOINTS.get(env)
    if not urls:
        print(f"Unknown environment: {env}")
        sys.exit(1)

    for name, url in urls.items():
        try:
            resp = requests.get(url, timeout=10)
            assert resp.status_code < 500, f"{url} returned {resp.status_code}"
            print(f"✅ {name}: {url} - {resp.status_code}")
        except Exception as e:
            print(f"❌ {name}: {url} - {e}")
            sys.exit(1)

if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else "local"
    smoke_test(env)
```

---

## 11. Promotion Workflow: Dev → Staging → Prod

### 11.1 Promotion Pipeline

```
                              PROMOTION PIPELINE
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │  DEVELOP                 STAGING                    PRODUCTION   │
  │  ┌────────┐             ┌────────┐                ┌────────┐    │
  │  │ Branch │─── PR ────▶│  main  │─── Release ───▶│  main  │    │
  │  └────────┘             └────────┘                └────────┘    │
  │      │                      │                         │          │
  │      ▼                      ▼                         ▼          │
  │  Local Dev              Auto Deploy               Manual        │
  │  + Tests                + CI Checks               + Approval    │
  │  + Preview URL          + Smoke Tests             + Release Tag │
  │                         + Staging Validation      + Production  │
  │                                                    Deploy       │
  └──────────────────────────────────────────────────────────────────┘
```

### 11.2 Step-by-Step Promotion

```yaml
Step 1: Local Development
  - Create feature branch from main
  - Develop, test locally
  - Commit and push

Step 2: Preview (PR)
  - Open PR against main
  - CI runs: lint, test, type-check, validate prompts
  - Vercel preview URL generated
  - Reviewers test preview

Step 3: Merge to Main (Staging)
  - PR approved, squash-merged to main
  - CI runs full pipeline
  - Vercel staging deployment triggered
  - Railway staging deployment triggered
  - Smoke tests run against staging

Step 4: Staging Validation
  - Integration tests pass
  - Manual QA on staging URL
  - Performance benchmarks verified
  - Database migrations confirmed

Step 5: Release to Production
  - Create release tag: vX.Y.Z
  - Update CHANGELOG.md
  - Approve production deploy
  - Monitor for 30 minutes post-deploy

Step 6: Post-Release
  - Verify Sentry errors
  - Check Vercel Analytics
  - Confirm Supabase performance
  - Announce to team
```

### 11.3 Release Tagging Convention

```bash
# Semantic versioning
git tag -a v2.1.0 -m "Release v2.1.0: New dashboard, AI sleep agent"
git push origin v2.1.0

# Tag format:
# vMAJOR.MINOR.PATCH
# MAJOR: Breaking changes
# MINOR: New features
# PATCH: Bug fixes
```

### 11.4 Promotion Approval Matrix

| Environment | Approval Required | Approver | Method |
|---|---|---|---|
| Preview | None | Auto-generated | PR comment |
| Staging | None | Auto-deployed | CI pipeline |
| Production | Yes | Lead Developer | GitHub Release + Manual Railway deploy |

---

## 12. Rollback Procedures Per Environment

### 12.1 Rollback by Environment

| Environment | Rollback Method | Time to Rollback | Data Impact |
|---|---|---|---|
| **Preview** | Re-push or close PR | <2 min | None (ephemeral) |
| **Staging** | Vercel: Previous deploy | <5 min | None (shared DB, backward-compat schema) |
| **Production** | Vercel: Rollback + Railway: Previous deploy | <10 min | Minimal (API version compatibility) |
| **Database** | PITR restore | 15–60 min | Data loss from time of restore |

### 12.2 Frontend Rollback (Vercel)

**Method 1: Dashboard Rollback**
1. Go to Vercel Dashboard → Deployments
2. Find the last known-good deployment
3. Click "..." → "Promote to Production"

**Method 2: CLI Rollback**
```bash
# List recent deployments
vercel list

# Rollback to specific deployment
vercel rollback <deployment-id>

# Rollback to previous (immediate)
vercel rollback
```

### 12.3 Backend Rollback (Railway)

**Method 1: Dashboard Deploy**
1. Go to Railway Dashboard → Deployment
2. Click "Deploy" → Select previous image version
3. Confirm deploy

**Method 2: CLI Rollback**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Link to project
railway link

# Rollback to previous deployment
railway up --deploy <previous-deployment-id>
```

### 12.4 Database Rollback (Supabase)

```bash
# WARNING: Database rollback is LAST RESORT
# It WILL result in data loss

# Step 1: Stop application to prevent writes
# (Scale Railway to 0 instances)

# Step 2: Download latest backup
supabase db dump --linked -f prod_backup.sql

# Step 3: Restore from PITR
# Use Supabase dashboard:
#   Database → Backups → Point-in-Time Recovery
#   Select timestamp before bad migration

# Step 4: Verify data integrity
# Step 5: Restart application
```

### 12.5 Rollback Checklist

```
☐ Identify the rollback trigger (error rate, bug, performance)
☐ Notify team via Slack #devops channel
☐ Stop new deploys (lock Vercel, Railway)
☐ Rollback frontend (Vercel dashboard)
☐ Rollback backend (Railway previous deploy)
☐ Verify rollback health checks pass
☐ If database migration rollback needed: restore from PITR
☐ Post-mortem: create issue for root cause analysis
☐ Unlock deploys after resolution
```

---

## 13. Environment Parity Checklist

### 13.1 Parity Items

Use this checklist to verify environment consistency before production releases:

```
SOURCE CODE PARITY
☐ Same Git commit deployed to all environments
☐ No environment-specific code branches
☐ Feature flags match intended configuration

ENVIRONMENT VARIABLES PARITY
☐ All required variables present in each environment
☐ Values differ only when intentionally different (e.g., URLs)
☐ No hardcoded values in code (all config via env vars)
☐ Secrets rotated on schedule
☐ Secret values verified via 1Password match

DATABASE PARITY
☐ Same migration version applied everywhere
☐ Schema diff between staging and prod is empty
☐ Indexes match between environments
☐ RLS policies match between environments
☐ Seed data representative of production patterns

AI CONFIGURATION PARITY
☐ Model versions match (or intentional upgrade in prod)
☐ Prompt files match across environments
☐ Temperature/parameter settings match
☐ Fallback behavior tested in staging

BUILD PARITY
☐ Same Node.js version (18.x) everywhere
☐ Same Python version (3.10+) everywhere
☐ Same dependency versions (package-lock.json, requirements.txt)
☐ Same Docker base images
☐ Same build arguments

NETWORK PARITY
☐ CORS origins correct for each environment
☐ SSL/TLS certificates valid
☐ DNS records resolve correctly
☐ API URLs match environment
☐ WebSocket URLs match environment

MONITORING PARITY
☐ Health check endpoints responding
☐ Sentry DSN configured per environment
☐ Logging level appropriate (debug in staging, info in prod)
☐ Alert thresholds configured

PERFORMANCE PARITY
☐ Build time under 3 minutes
☐ Lighthouse score > 80 in staging
☐ API p95 response time < 2s in staging
☐ No memory leaks detected in 15-min soak test
```

### 13.2 Parity Validation Script

```bash
#!/bin/bash
# scripts/check_parity.sh
# Run after staging deploy, before production deploy

echo "=== Environment Parity Check ==="

# 1. Check git commit parity
STAGING_COMMIT=$(curl -s https://staging.api.secondbrain-os.com/health | jq -r '.commit')
PROD_COMMIT=$(curl -s https://api.secondbrain-os.com/health | jq -r '.commit')
echo "Staging commit: $STAGING_COMMIT"
echo "Prod commit:    $PROD_COMMIT"
if [ "$STAGING_COMMIT" != "$PROD_COMMIT" ]; then
  echo "WARNING: Commits differ! Staging is ahead of production."
fi

# 2. Check health endpoints
echo "Staging health: $(curl -s -o /dev/null -w '%{http_code}' https://staging.api.secondbrain-os.com/health)"
echo "Prod health:    $(curl -s -o /dev/null -w '%{http_code}' https://api.secondbrain-os.com/health)"

# 3. Check SSL
echo "Staging SSL: $(curl -sI https://staging-secondbrain-os.vercel.app | grep -c 'HTTP/2 200')"
echo "Prod SSL:    $(curl -sI https://secondbrain-os.com | grep -c 'HTTP/2 200')"

echo "=== Parity Check Complete ==="
```

### 13.3 Environment Sizing Comparison

```
┌────────────────────┬──────────┬──────────┬──────────────┐
│ Resource            │ Local    │ Staging  │ Production   │
├────────────────────┼──────────┼──────────┼──────────────┤
│ Frontend Instances  │ 1        │ 1        │ Auto-scaled  │
│ Backend Instances   │ 1        │ 1        │ 2+           │
│ Worker Instances    │ 1        │ 1        │ 1            │
│ DB Storage          │ Local FS │ 500MB    │ 500MB–10GB   │
│ DB Connections      │ Unlimited│ 60       │ 60–200       │
│ Cache (in-memory)   │ Volatile │ 50MB     │ 200MB        │
│ AI (primary)        │ Ollama   │ Ollama   │ Claude       │
│ AI (fallback)       │ None     │ Claude   │ Claude       │
│ Log Retention       │ No limit │ 7 days   │ 30 days      │
│ Backup Frequency    │ Manual   │ Daily    │ Daily + PITR │
└────────────────────┴──────────┴──────────┴──────────────┘
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-11 | Developer | Initial environment architecture documentation |
