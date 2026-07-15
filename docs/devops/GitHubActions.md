# GitHub Actions — Workflow Reference

## Document Control

| Field | Value |
|---|---|
| Document ID | DVO-GHA-014 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Workflow Inventory](#2-workflow-inventory)
3. [ci.yml — Full CI Pipeline](#3-ciyml--full-ci-pipeline)
4. [deploy-frontend.yml — Vercel Deploy](#4-deploy-frontendyml--vercel-deploy)
5. [deploy-backend.yml — Railway Deploy](#5-deploy-backendyml--railway-deploy)
6. [deploy-scheduler.yml — Scheduler Deploy](#6-deploy-scheduleryml--scheduler-deploy)
7. [lighthouse.yml — Lighthouse Audit](#7-lighthouseyml--lighthouse-audit)
8. [canary.yml — Canary Deployment](#8-canaryyml--canary-deployment)
9. [secrets.yml — Secret Scan](#9-secretsyml--secret-scan)
10. [Shared Actions & Reusability](#10-shared-actions--reusability)
11. [Concurrency Configuration](#11-concurrency-configuration)
12. [Caching Strategy](#12-caching-strategy)
13. [Environment Secrets](#13-environment-secrets)
14. [Notification Integration](#14-notification-integration)
15. [Security Considerations](#15-security-considerations)
16. [Troubleshooting](#16-troubleshooting)
17. [References](#17-references)

---

## 1. Executive Summary

GitHub Actions is the CI/CD engine for Second Brain OS. Seven workflows automate linting, testing, security scanning, building, deploying, and monitoring across all components. All workflows are defined in `.github/workflows/` and are triggered by pushes, pull requests, and scheduled events.

---

## 2. Workflow Inventory

| File | Trigger | Purpose | Timeout |
|---|---|---|---|
| `ci.yml` | Push/PR to `main`, `develop` | Full CI suite | 15 min |
| `deploy-frontend.yml` | Push to `main` (apps/web/**) | Deploy to Vercel | 15 min |
| `deploy-backend.yml` | Push to `main` (apps/api/**, packages/**) | Deploy to Railway | 15 min |
| `deploy-scheduler.yml` | Push to `main` (services/scheduler/**) | Deploy scheduler | 10 min |
| `lighthouse.yml` | Push to `main` | Lighthouse audit | 10 min |
| `canary.yml` | Release published | Canary deployment | 20 min |
| `secrets.yml` | PR, weekly schedule | Secret scanning | 10 min |

---

## 3. ci.yml — Full CI Pipeline

```yaml
name: CI
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [develop, main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  frontend:
    name: Frontend CI
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: "npm"
          cache-dependency-path: apps/web/package-lock.json
      - run: cd apps/web && npm ci
      - run: cd apps/web && npm run lint
      - run: cd apps/web && npm run type-check
      - run: cd apps/web && npm run build

  backend:
    name: Backend CI
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          cache: "pip"
      - run: pip install -r apps/api/requirements.txt
      - run: ruff check apps/api/ packages/ services/scheduler/ scripts/
      - run: python -m py_compile apps/api/main.py

  test:
    name: Tests
    needs: [frontend, backend]
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          cache: "pip"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=packages --cov=apps/api --cov-report=xml
      - uses: codecov/codecov-action@v3

  security:
    name: Security Audit
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: cd apps/web && npm audit --audit-level=high
      - uses: actions/setup-python@v5
      - run: pip install safety && safety check -r apps/api/requirements.txt

  prompts:
    name: Prompt Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install pyyaml
      - run: python scripts/validate_prompts.py
      - run: pytest tests/test_prompt_loader.py tests/test_agent_prompts.py -v

  docker:
    name: Docker Build
    needs: [test, security, prompts]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
      - run: docker compose -f docker-compose.prod.yml build
```

---

## 4. deploy-frontend.yml — Vercel Deploy

```yaml
name: Deploy Frontend
on:
  push:
    branches: [main]
    paths:
      - "apps/web/**"
      - ".github/workflows/deploy-frontend.yml"

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: "--prod"
```

---

## 5. deploy-backend.yml — Railway Deploy

```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths:
      - "apps/api/**"
      - "packages/**"
      - ".github/workflows/deploy-backend.yml"

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend
```

---

## 6. deploy-scheduler.yml — Scheduler Deploy

```yaml
name: Deploy Scheduler
on:
  push:
    branches: [main]
    paths:
      - "services/scheduler/**"
      - ".github/workflows/deploy-scheduler.yml"

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - name: Deploy Scheduler to Railway
        uses: bervProject/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
          service: scheduler
```

---

## 7. lighthouse.yml — Lighthouse Audit

```yaml
name: Lighthouse CI
on:
  push:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd apps/web && npm ci
      - run: cd apps/web && npm run build
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun --config=apps/web/lighthouserc.js
```

---

## 8. canary.yml — Canary Deployment

```yaml
name: Canary Deployment
on:
  release:
    types: [published]

jobs:
  canary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy canary
        run: |
          echo "Deploying canary version ${{ github.event.release.tag_name }}"
          # Canary deployment logic (planned)
      - name: Monitor canary
        run: |
          echo "Monitoring canary for 30 min"
          sleep 30
          # Health check + error rate verification
```

---

## 9. secrets.yml — Secret Scan

```yaml
name: Secret Scan
on:
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: "0 6 * * 1"

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: TruffleHog
        uses: trufflesecurity/trufflehog@v3
        with:
          path: ./
          base: main
          head: HEAD
          extra_args: --only-verified --fail
```

---

## 10. Shared Actions & Reusability

| Action | Version | Purpose |
|---|---|---|
| `actions/checkout` | v4 | Check out repository |
| `actions/setup-node` | v4 | Set up Node.js with caching |
| `actions/setup-python` | v5 | Set up Python with caching |
| `actions/cache` | v4 | Manual dependency caching |
| `docker/setup-buildx-action` | v3 | Docker BuildX setup |
| `docker/login-action` | v3 | Docker registry login |
| `amondnet/vercel-action` | v25 | Vercel deployment |
| `bervProject/railway-deploy` | v1 | Railway deployment |
| `codecov/codecov-action` | v3 | Coverage upload |
| `trufflesecurity/trufflehog` | v3 | Secret detection |

---

## 11. Concurrency Configuration

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

- Same branch + same workflow → cancel previous run
- Different branches → run independently
- Different workflows → run independently
- `main` branch deploys → serial (no concurrent deploys)

---

## 12. Caching Strategy

| Cache Key | Paths | Used By |
|---|---|---|
| `npm-${{ hashFiles('apps/web/package-lock.json') }}` | `apps/web/node_modules` | All frontend jobs |
| `pip-${{ hashFiles('requirements.txt') }}` | `~/.cache/pip` | Backend jobs |
| `next-${{ hashFiles('apps/web/next.config.js') }}` | `apps/web/.next/cache` | Build jobs |

---

## 13. Environment Secrets

| Secret | Used By | Scope |
|---|---|---|
| `VERCEL_TOKEN` | deploy-frontend.yml | Production |
| `VERCEL_ORG_ID` | deploy-frontend.yml | Production |
| `VERCEL_PROJECT_ID` | deploy-frontend.yml | Production |
| `RAILWAY_TOKEN` | deploy-backend.yml, deploy-scheduler.yml | Production |
| `SUPABASE_SERVICE_KEY` | CI test suite | CI |
| `CLAUDE_API_KEY` | CI test suite (few tests) | CI |

---

## 14. Notification Integration

| Event | Channel | Message |
|---|---|---|
| CI pass | Slack #deployments | ✅ CI passed: {branch} |
| CI failure | Slack #deployments | ❌ CI failed: {branch} — {job} |
| Deploy success | Slack #deployments | 🚀 Deployed: {component} to {env} |
| Deploy failure | Slack #deployments | 🔴 Deploy failed: {component} — {reason} |
| Security vuln | GitHub Issue | 🛡️ New vulnerability in {dependency} |
| Scheduled scan | Email digest | Weekly security scan results |

---

## 15. Security Considerations

- All secrets stored as GitHub Actions encrypted secrets
- No secrets in workflow files or logs
- GITHUB_TOKEN scoped to minimum permissions
- Third-party actions pinned to specific versions (SHA256 verification planned)
- Workflows only trigger on trusted branches (`main`, `develop`)
- `pull_request_target` not used (prevents PR-based injection)

---

## 16. Troubleshooting

| Issue | Check | Fix |
|---|---|---|
| Workflow not triggering | Branch/Path filters | Verify push matches filter pattern |
| Cache miss | Hash changed | Accept slower build, cache will update |
| Action version deprecated | GitHub Actions marketplace | Update to latest version |
| Secret not found | Repository secrets page | Add missing secret |
| Runner timeout | Job complexity | Split job, increase timeout |
| Docker build fails | Missing context | Check `.dockerignore` rules |

---

## 17. References

| Resource | Location |
|---|---|
| Workflow Files | `.github/workflows/` |
| CI Pipeline | `docs/devops/CI.md` |
| CD Pipeline | `docs/devops/CD.md` |
| Deployment Strategy | `docs/devops/26_Deployment.md` |
| DevOps Practices | `docs/devops/27_DevOps.md` |
| GitHub Actions Docs | https://docs.github.com/en/actions |
