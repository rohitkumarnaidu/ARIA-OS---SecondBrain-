# Secrets Management — Second Brain OS (ARIA OS)

## Document Control

| Property | Details |
|---|---|
| **Document ID** | SEC-SECRETS-001 |
| **Version** | 1.0 |
| **Status** | Active |
| **Classification** | Restricted — Contains Secret Names & Locations |
| **Last Updated** | 2026-06-11 |
| **Next Review** | 2026-09-11 |
| **Standards** | OWASP Secrets Management, NIST SP 800-57 (Key Management), 1Password Secrets Automation |
| **Owner** | DevOps Lead |

---

## Table of Contents

1. [Secret Inventory](#1-secret-inventory)
2. [Environment Variable Hierarchy](#2-environment-variable-hierarchy)
3. [Secret Rotation Policy](#3-secret-rotation-policy)
4. [Local Development Secrets](#4-local-development-secrets)
5. [CI/CD Secrets Management](#5-cicd-secrets-management)
6. [AI API Key Handling](#6-ai-api-key-handling)
7. [Service Key Management](#7-service-key-management)
8. [Secret Audit Policy](#8-secret-audit-policy)
9. [Incident Response for Secret Leakage](#9-incident-response-for-secret-leakage)
10. [Tooling](#10-tooling)
11. [Secret Naming Conventions](#11-secret-naming-conventions)
12. [Emergency Secret Rotation Procedure](#12-emergency-secret-rotation-procedure)

---

## 1. Secret Inventory

### 1.1 Complete Secret Inventory

| # | Variable | Classification | Value Type | Length | Used In | Exposed to Client? | Rotation Period | Last Rotated |
|---|----------|---------------|------------|--------|---------|--------------------|----------------|--------------|
| 1 | `SUPABASE_URL` | **Low** | URL | ~50 chars | Frontend + Backend | ✅ Yes (public) | N/A (public) | N/A |
| 2 | `NEXT_PUBLIC_SUPABASE_URL` | **Low** | URL | ~50 chars | Frontend | ✅ Yes (public) | N/A (public) | N/A |
| 3 | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | **Low** | API Key | ~40 chars | Frontend | ✅ Yes (public, safe) | Per Supabase project | N/A |
| 4 | `SUPABASE_KEY` | **Medium** | API Key | ~40 chars | Backend | ❌ No | 180 days | 2026-06-11 |
| 5 | `SUPABASE_SERVICE_KEY` | **Critical** | API Key | ~40 chars | Backend + Scheduler | ❌ No | 180 days | 2026-06-11 |
| 6 | `JWT_SECRET` | **Critical** | HMAC Key (256-bit) | 64 hex chars | Backend | ❌ No | 90 days | 2026-06-11 |
| 7 | `JWT_ALGORITHM` | **Low** | String | 5 chars | Backend | ❌ No | N/A (config) | N/A |
| 8 | `CLAUDE_API_KEY` | **Critical** | API Key | ~48 chars | Backend | ❌ No | 180 days | 2026-06-11 |
| 9 | `RESEND_API_KEY` | **Critical** | API Key | ~32 chars | Backend | ❌ No | 180 days | 2026-06-11 |
| 10 | `OLLAMA_BASE_URL` | **Low** | URL | ~25 chars | Backend | ❌ No | N/A (local) | N/A |
| 11 | `USE_LOCAL_AI` | **Low** | Boolean | 5 chars | Backend | ❌ No | N/A (config) | N/A |
| 12 | `APP_NAME` | **Low** | String | ~15 chars | Backend | ❌ No | N/A (config) | N/A |
| 13 | `DEBUG` | **Low** | Boolean | 4-5 chars | Backend | ❌ No | N/A (config) | N/A |
| 14 | `CORS_ORIGINS` | **Low** | URL list | ~50 chars | Backend | ❌ No | N/A (config) | N/A |
| 15 | `FIELD_ENCRYPTION_KEY` | **High** | Fernet Key | 44 base64 chars | Backend | ❌ No | 90 days (future) | N/A |
| 16 | `RESEND_SENDER_EMAIL` | **Low** | Email | ~30 chars | Backend | ❌ No | N/A (config) | N/A |

### 1.2 Secret Classification Definitions

| Level | Color | Definition | Example | Exposure Impact |
|-------|-------|------------|---------|-----------------|
| **Critical** | 🔴 Red | Grants full access to data or external services | JWT_SECRET, SUPABASE_SERVICE_KEY, CLAUDE_API_KEY | Complete system compromise, data breach |
| **High** | 🟠 Orange | Grants access to sensitive user data | FIELD_ENCRYPTION_KEY | Encrypted data decryption |
| **Medium** | 🟡 Yellow | Limited access, non-critical services | SUPABASE_KEY (anon elevated) | Partial data access |
| **Low** | 🟢 Green | Public information, configuration | SUPABASE_URL, APP_NAME | No security impact |

### 1.3 Secret Exposure Risk Assessment

| Secret | If Exposed In... | Impact | Containment Time | Remediation |
|--------|-----------------|--------|-----------------|-------------|
| `JWT_SECRET` | Git commit | **Critical** — can forge tokens | < 1 min (remove from git) | Rotate secret; revoke all sessions |
| `JWT_SECRET` | CI logs | **Critical** | < 5 min (clear logs) | Rotate secret; revoke all sessions |
| `SUPABASE_SERVICE_KEY` | Git commit | **Critical** — full DB access | < 1 min | Rotate key; audit all queries for 72h |
| `CLAUDE_API_KEY` | Public | **High** — $ cost + prompt access | < 5 min | Rotate key; audit Anthropic usage |
| `RESEND_API_KEY` | Public | **Medium** — spam emails | < 5 min | Rotate key; audit sent emails |
| `SUPABASE_URL` | Anywhere | **None** (public info) | N/A | No action needed |

---

## 2. Environment Variable Hierarchy

### 2.1 Priority Order (Highest to Lowest)

```
1. Railway Secrets (production backend)
2. Vercel Environment Variables (production frontend)
3. GitHub Actions Secrets (CI/CD)
4. .env.production.local (local production simulation)
5. .env.local (local development — NEVER COMMIT)
6. .env.development.local (local development overrides)
7. .env (default template — NO real secrets)
8. .env.example (documentation — NO real secrets)
```

### 2.2 Environment Matrix

| Variable | `.env.example` | `.env.local` | Railway (Prod) | Vercel (Prod) | GitHub Actions | 
|----------|---------------|--------------|----------------|---------------|----------------|
| `SUPABASE_URL` | `https://your-project.supabase.co` | ✅ Real | ✅ Real | N/A | N/A |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://your-project.supabase.co` | ✅ Real | N/A | ✅ Real | N/A |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJ...` | ✅ Real | N/A | ✅ Real | N/A |
| `SUPABASE_KEY` | `your-anon-key` | ✅ Real | ✅ Real | N/A | ✅ Real (test) |
| `SUPABASE_SERVICE_KEY` | `your-service-key` | ✅ Real | ✅ Real | N/A | ❌ Never |
| `JWT_SECRET` | `your-secret-key-change-in-production` | ✅ Real | ✅ Real | N/A | ❌ Never |
| `CLAUDE_API_KEY` | `sk-ant-...` | ✅ Real | ✅ Real | N/A | ❌ Never |
| `RESEND_API_KEY` | `re_...` | ✅ Real | ✅ Real | N/A | ❌ Never |

### 2.3 `.env.example` Template

```bash
# ============================================================================
# Second Brain OS — Environment Variables Template
# ============================================================================
# Copy this file to .env.local and fill in real values.
# NEVER commit .env, .env.local, or any .env.*.local files.
# ============================================================================

# --- Supabase (Backend) ---
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=fake-jwt-token-string-for-testingInR5cCI6IkpXVCJ9.eyJzdWIiOiI...
SUPABASE_SERVICE_KEY=fake-jwt-token-string-for-testingInR5cCI6IkpXVCJ9.eyJzdWIiOiI...

# --- JWT ---
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# --- AI Providers ---
CLAUDE_API_KEY=sk-ant-your-claude-api-key
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=True

# --- Email ---
RESEND_API_KEY=re_your-resend-api-key

# --- Frontend (for local backend testing) ---
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=fake-jwt-token-string-for-testingInR5cCI6IkpXVCJ9.eyJzdWIiOiI...

# --- App Configuration ---
APP_NAME="Second Brain OS"
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### 2.4 `.gitignore` Configuration

```gitignore
# .gitignore — Secret protection

# Environment files (NEVER commit)
.env
.env.local
.env.*.local
.env.development
.env.staging
.env.production

# Configuration files with potential secrets
*.pem
*.key
certificates/
secrets/

# IDE / editor
.idea/
.vscode/

# OS files
.DS_Store
Thumbs.db

# 1Password CLI session
.op/
```

### 2.5 Environment File Validation

```bash
# scripts/validate_env.sh
#!/bin/bash
# Validates that no .env files are about to be committed

echo "🔍 Checking for secret files in commit..."

FILES_TO_CHECK=(
  ".env"
  ".env.local"
  ".env.*.local"
  "*.pem"
  "*.key"
)

for pattern in "${FILES_TO_CHECK[@]}"; do
  MATCHES=$(git diff --cached --name-only | grep -E "$pattern" || true)
  if [ -n "$MATCHES" ]; then
    echo "❌ ERROR: Attempting to commit secret file(s):"
    echo "$MATCHES"
    echo ""
    echo "Remove these files from the commit and add to .gitignore if needed."
    exit 1
  fi
done

echo "✅ No secret files detected in commit."
```

---

## 3. Secret Rotation Policy

### 3.1 Rotation Schedule

| Secret | Rotation Period | Trigger | Downtime? | User Impact |
|--------|----------------|---------|-----------|-------------|
| `JWT_SECRET` | 90 days | Scheduled (quarterly) | < 1 sec | All sessions invalid (re-auth) |
| `SUPABASE_SERVICE_KEY` | 180 days | Scheduled (bi-annual) | < 1 sec | None |
| `CLAUDE_API_KEY` | 180 days | Scheduled (bi-annual) | < 1 sec | Brief AI fallback to Ollama |
| `RESEND_API_KEY` | 180 days | Scheduled (bi-annual) | < 1 sec | Brief email delay |
| `FIELD_ENCRYPTION_KEY` | 90 days (future) | Scheduled | Depends on data re-encryption | None |
| All of the above | Immediate | Breach/leak detection | As needed | Depends on secret |

### 3.2 Rotation Procedure Checklist

```markdown
## Secret Rotation Checklist

### Scheduled Rotation (Quarterly)
- [ ] Announce rotation window to team (24h notice)
- [ ] Generate new secret using approved tooling
- [ ] Update Railway production environment variable
- [ ] Verify service health after update
- [ ] Update 1Password vault entry (with version history)
- [ ] Update last_rotated field in this document
- [ ] Log rotation in encryption audit trail

### Emergency Rotation (Breach)
- [ ] Rotate compromised secret IMMEDIATELY (no notice)
- [ ] Follow Incident Response for Secret Leakage (Section 9)
- [ ] Post-mortem within 5 business days
```

### 3.3 Rotation Script

```bash
# scripts/rotate_secret.sh
#!/bin/bash
# Usage: ./scripts/rotate_secret.sh JWT_SECRET
# Rotates a single secret across all environments.

set -euo pipefail

SECRET_NAME="${1:?Usage: rotate_secret.sh SECRET_NAME}"

echo "🔄 Rotating $SECRET_NAME..."

# Step 1: Generate new value
case $SECRET_NAME in
  JWT_SECRET)
    NEW_VALUE=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    ;;
  SUPABASE_KEY|SUPABASE_SERVICE_KEY)
    echo "⚠️  Generate new Supabase key from Supabase Dashboard"
    echo "https://supabase.com/dashboard/project/[project-id]/settings/api"
    read -p "Enter new Supabase key: " NEW_VALUE
    ;;
  CLAUDE_API_KEY)
    echo "⚠️  Generate new Claude API key from https://console.anthropic.com/"
    read -p "Enter new Claude API key: " NEW_VALUE
    ;;
  RESEND_API_KEY)
    echo "⚠️  Generate new Resend API key from https://resend.com/api-keys"
    read -p "Enter new Resend API key: " NEW_VALUE
    ;;
  *)
    echo "❌ Unknown secret: $SECRET_NAME"
    exit 1
    ;;
esac

# Step 2: Update Railway
echo "📦 Updating Railway..."
railway variables set "$SECRET_NAME=$NEW_VALUE"

# Step 3: Update Vercel (if applicable)
if [[ "$SECRET_NAME" != "JWT_SECRET" ]]; then
  echo "📦 Updating Vercel..."
  vercel env add "$SECRET_NAME" production <<< "$NEW_VALUE"
fi

# Step 4: Verify
echo "✅ $SECRET_NAME rotated successfully"
echo "📝 Remember to update 1Password vault!"

# Step 5: Update local .env.local
read -p "Update local .env.local? (y/N): " UPDATE_LOCAL
if [[ "$UPDATE_LOCAL" == "y" ]]; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|^$SECRET_NAME=.*|$SECRET_NAME=$NEW_VALUE|" .env.local
  else
    sed -i "s|^$SECRET_NAME=.*|$SECRET_NAME=$NEW_VALUE|" .env.local
  fi
  echo "✅ Local .env.local updated"
fi
```

---

## 4. Local Development Secrets

### 4.1 Developer Setup

```bash
# Local development secret setup
# ==============================

# 1. Copy template (never commit real secrets)
cp .env.example .env.local

# 2. Fill in real values from 1Password
#    Open 1Password → Second Brain OS vault → "Local Development" item
#    Copy each value into .env.local

# 3. Verify no secrets are tracked by git
git status                    # .env.local should appear as unstaged/untracked
git check-ignore .env.local   # Should return .env.local (confirmed ignored)

# 4. Test that secrets load correctly
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.local')
required = ['SUPABASE_URL', 'SUPABASE_KEY', 'JWT_SECRET', 'CLAUDE_API_KEY']
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f'❌ Missing: {missing}')
else:
    print('✅ All required secrets loaded')
"
```

### 4.2 Secret Masking in Development

```python
# packages/shared/utils/security.py
"""
Secret masking utilities for development logging.
Ensures secrets are never printed to console/logs.
"""

def mask_secret(value: str, visible_chars: int = 4) -> str:
    """
    Mask a secret value for display.
    Shows first N characters, replaces rest with asterisks.
    """
    if not value or len(value) <= visible_chars:
        return "****"
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def mask_url(value: str) -> str:
    """
    Mask sensitive parts of a URL.
    Hides credentials in URLs like https://user:pass@example.com
    """
    if not value:
        return ""
    import re
    masked = re.sub(r'(https?://)([^:]+):([^@]+)@', r'\1***:***@', value)
    return masked


# Usage in startup logs:
print(f"  SUPABASE_URL: {mask_url(os.getenv('SUPABASE_URL', ''))}")
print(f"  JWT_SECRET: {mask_secret(os.getenv('JWT_SECRET', ''), 6)}")
print(f"  CLAUDE_API_KEY: {mask_secret(os.getenv('CLAUDE_API_KEY', ''), 8)}")

# Example output:
#   SUPABASE_URL: https://***:***@db.supabase.co
#   JWT_SECRET: a1b2c3******************************
#   CLAUDE_API_KEY: sk-ant-01****************************
```

### 4.3 Secret Leak Prevention for Developers

| Practice | Tool/Method | Enforced By |
|----------|-------------|-------------|
| Never commit `.env` files | `.gitignore` | Git pre-commit hook |
| Check for secrets in diffs | `git diff --check` | Manual (pre-commit) |
| Scan for hardcoded secrets | `trufflehog` or `git-secrets` | CI (planned) |
| Use 1Password for sharing | 1Password vault | Team policy |
| Mask secrets in logs | `mask_secret()` utility | Code review |
| Rotate after developer leaves | Scheduled rotation | DevOps |
| Audit env vars for stale values | Quarterly review | DevOps |

### 4.4 Pre-Commit Hook for Secret Detection

```bash
# .git/hooks/pre-commit (install with: git config core.hooksPath .githooks)
# .githooks/pre-commit

#!/bin/bash
# Pre-commit hook to detect potential secret leakage

echo "🔍 Scanning for potential secrets in staged files..."

# Patterns that should never appear in code
SECRET_PATTERNS=(
  "SUPABASE_SERVICE_KEY="
  "JWT_SECRET="
  "CLAUDE_API_KEY="
  "RESEND_API_KEY="
  "-----BEGIN RSA PRIVATE KEY-----"
  "-----BEGIN OPENSSH PRIVATE KEY-----"
  "sk-[a-zA-Z0-9]{20,}"  # OpenAI/Anthropic style keys
  "sbp_[a-zA-Z0-9]{40,}"  # Supabase service keys
)

# Check staged files
STAGED_FILES=$(git diff --cached --name-only)

for FILE in $STAGED_FILES; do
  if [ -f "$FILE" ]; then
    for PATTERN in "${SECRET_PATTERNS[@]}"; do
      if git diff --cached "$FILE" | grep -qE "$PATTERN"; then
        echo "❌ WARNING: Potential secret found in $FILE"
        echo "   Pattern: $PATTERN"
        echo "   Remove the secret before committing."
        exit 1
      fi
    done
  fi
done

echo "✅ No secrets detected in staged files."
```

---

## 5. CI/CD Secrets Management

### 5.1 GitHub Actions Encrypted Secrets

```yaml
# .github/workflows/ci.yml — Secret configuration
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  # Public config (safe to expose)
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  APP_NAME: "Second Brain OS"
  DEBUG: false

jobs:
  frontend:
    runs-on: ubuntu-latest
    env:
      # Frontend needs these for build
      NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
      NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: apps/web/package-lock.json
      - run: npm ci
        working-directory: apps/web
      - run: npm run lint
        working-directory: apps/web
      - run: npm run type-check
        working-directory: apps/web
      - run: npm run build
        working-directory: apps/web

  backend:
    runs-on: ubuntu-latest
    env:
      # Backend CI needs service key for integration tests
      SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
      SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      JWT_SECRET: ${{ secrets.JWT_SECRET }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r apps/api/requirements.txt
      - run: ruff check apps/api/
      - run: python -m py_compile apps/api/main.py
      - run: pytest tests/ -x

  prompts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install pyyaml pytest
      - run: python scripts/validate_prompts.py
      - run: ruff check packages/ai/
      - run: python -m pytest tests/ -x

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm audit --audit-level=high
        working-directory: apps/web
        continue-on-error: true  # Don't block PR for audit findings
```

### 5.2 GitHub Actions Secret Configuration

```bash
# Setup GitHub Actions secrets via CLI (run once)
gh secret set SUPABASE_URL \
  --body "$SUPABASE_URL" \
  --repo your-org/secondbrain-os

gh secret set SUPABASE_KEY \
  --body "$SUPABASE_KEY" \
  --repo your-org/secondbrain-os

gh secret set JWT_SECRET \
  --body "$JWT_SECRET" \
  --repo your-org/secondbrain-os

gh secret set NEXT_PUBLIC_SUPABASE_URL \
  --body "$NEXT_PUBLIC_SUPABASE_URL" \
  --repo your-org/secondbrain-os

gh secret set NEXT_PUBLIC_SUPABASE_ANON_KEY \
  --body "$NEXT_PUBLIC_SUPABASE_ANON_KEY" \
  --repo your-org/secondbrain-os
```

### 5.3 CI Secret Exposure Prevention

```yaml
# GitHub Actions secret masking is automatic:
# Any value set via `secrets.SECRET_NAME` is masked in logs.
# Values are replaced with `***` in console output.

# ⚠️ WARNING: Never echo secrets to logs:
- name: BAD — exposes secret in logs
  run: echo "The key is ${{ secrets.SUPABASE_SERVICE_KEY }}"

- name: GOOD — safe reference
  run: python -c "import os; api_url = os.getenv('SUPABASE_URL')"

# ⚠️ WARNING: Never pass secrets via script arguments:
- name: BAD — secret visible in process list
  run: ./deploy.sh --api-key "${{ secrets.CLAUDE_API_KEY }}"

- name: GOOD — pass via environment
  run: ./deploy.sh
  env:
    CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
```

### 5.4 1Password CLI for Local CI

```bash
# Using 1Password CLI to load secrets for local CI runs
# Avoids maintaining .env.local with full secrets

# Prerequisites: 1Password CLI installed and signed in
#   brew install --cask 1password-cli
#   op signin

# Load environment from 1Password vault
op run --env-file=.env.op -- python scripts/validate_prompts.py

# .env.op (reference file — NO real secrets)
# Format: SECRET_NAME=op://vault/item/field
SUPABASE_URL=op://SecondBrain/CI/SUPABASE_URL
SUPABASE_KEY=op://SecondBrain/CI/SUPABASE_KEY
JWT_SECRET=op://SecondBrain/CI/JWT_SECRET
```

---

## 6. AI API Key Handling

### 6.1 Claude API Key Lifecycle

```
1. Generate
   └── Anthropic Console → API Keys → Create Key
   └── Named: "secondbrain-os-production"

2. Store (primary)
   └── Railway Dashboard → Variables → CLAUDE_API_KEY
   └── 1Password: "Second Brain OS" vault → "Claude API Key"

3. Store (backup)
   └── Developer's .env.local (via 1Password copy)

4. Access (runtime)
   └── FastAPI reads from os.environ["CLAUDE_API_KEY"]
   └── Used only in packages/ai/client.py
   └── NEVER exposed to frontend

5. Usage (each request)
   └── Sent as HTTP header: x-api-key: sk-ant-...
   └── Over TLS 1.3 to api.anthropic.com
   └── Never logged, never printed

6. Rotation
   └── Every 180 days (scheduled)
   └── Immediately on suspected compromise
```

### 6.2 AI API Key Access Control

```python
# packages/ai/client.py
"""
Claude API key is used ONLY in this file.
It is never:
- Exposed to the frontend
- Stored in the database
- Logged anywhere
- Included in AI prompt context
- Sent to Ollama
"""

import os
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

class ClaudeClient:
    """
    Claude API client with secure key handling.
    Key is read from environment at runtime and never stored elsewhere.
    """

    def __init__(self):
        self.api_key = os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            logger.warning("CLAUDE_API_KEY not set. AI features will use Ollama only.")

        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-sonnet-4-20250514"

    async def generate(
        self,
        prompt: str,
        system: str,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        """
        Send prompt to Claude API.
        Key is included in header only; never part of request body.
        """
        if not self.api_key:
            logger.warning("Claude API key not configured — falling back to Ollama")
            return None

        headers = {
            "x-api-key": self.api_key,      # Key in header only ✅
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Key is NOT in the request body
        payload = {
            "model": self.default_model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return None
```

### 6.3 AI Key Security Rules

| Rule | Enforcement | Checked By |
|------|-------------|------------|
| Claude key never in frontend code | Webpack tree-shaking; code review | Code review |
| Claude key never in localStorage | Absent from any frontend code | Code review |
| Claude key never in requests to `/api/` | Backend reads from env only | Code review |
| Claude key never logged | `mask_secret()` if accidental print | Code review + testing |
| Claude key never in database | No Claude key column in any table | Schema review |
| Claude key never in AI context | `_build_prompt_context()` excludes it | Code review |
| Claude key rotated on breach | Incident response procedure | DevOps |

---

## 7. Service Key Management

### 7.1 Supabase Key Types

| Key Type | Name | Used For | Exposed To | Permissions |
|----------|------|----------|------------|-------------|
| **Anon Key** | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Client-side Supabase access | ✅ Browser (public) | Limited by RLS |
| **User Key** | `SUPABASE_KEY` | Backend user-level operations | ❌ Backend only | Same as anon + some user management |
| **Service Role Key** | `SUPABASE_SERVICE_KEY` | Admin operations, scheduler | ❌ Backend + Scheduler only | Bypasses RLS — full access |

### 7.2 Service Key Usage Rules

```python
# NEVER use service_role key from frontend
# NEVER expose service_role key to browser
# NEVER commit service_role key to git
# ONLY use in backend endpoints that need elevated access

# CORRECT: Scheduler uses service key for automated operations
# apps/services/scheduler/main.py
supabase = create_client(
    supabase_url=os.environ["SUPABASE_URL"],
    supabase_key=os.environ["SUPABASE_SERVICE_KEY"],  # ✅ Backend only
)

# CORRECT: Admin endpoints use service key
# apps/api/app/api/admin.py
@router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(get_admin_user)):
    supabase = create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key,
    )
    result = supabase.table("tasks").select("*", count="exact").execute()
    return {"total_tasks": result.count}

# NEVER do this in frontend code:
# supabase = createClient(url, process.env.SUPABASE_SERVICE_KEY) ❌
```

### 7.3 Service Key Access Audit

```sql
-- Supabase query log for service key usage
-- Audit: Identify any unexpected service key usage

SELECT
    auth_method,
    query,
    timestamp,
    ip_address
FROM
    supabase.query_log
WHERE
    auth_method = 'service_role'
    AND timestamp > now() - interval '30 days'
ORDER BY
    timestamp DESC;

-- Expected service key usage:
-- - Scheduler (daily briefings, weekly reviews)
-- - Admin endpoints
-- - User account deletion
-- Anything else should be investigated.
```

### 7.4 Anon Key vs Service Key Decision Matrix

| Operation | Key Type | Rationale |
|-----------|----------|-----------|
| User reads own tasks | Anon key | RLS restricts to own data |
| User creates task | Anon key | RLS inserts with correct user_id |
| Scheduler creates briefing | Service key | Cron job has no user session |
| Admin lists all users | Service key | Bypasses RLS for admin view |
| User deletes account | Service key | Needs to delete auth.users |
| AI agent reads memory | Service key | Agent runs as system, not user |
| Health check | Anon key | Public endpoint |

---

## 8. Secret Audit Policy

### 8.1 Audit Schedule

| Activity | Frequency | Owner | Method |
|----------|-----------|-------|--------|
| Full secret inventory review | Quarterly | DevOps Lead | Compare env vars vs. inventory |
| Rotation compliance check | Quarterly | DevOps Lead | Verify all secrets rotated on schedule |
| Access log review | Monthly | Security Lead | Check who accessed Railway/Vercel secrets |
| Stale secret cleanup | Quarterly | DevOps Lead | Remove unused environment variables |
| 1Password vault audit | Quarterly | DevOps Lead | Verify vault items match inventory |
| CI secret exposure check | Per build | Automated | GitHub Actions secret masking verification |

### 8.2 Audit Logging

```python
# packages/shared/utils/audit.py (secrets audit)

class SecretsAuditLogger:
    """
    Logs secret management events for compliance.
    """

    def __init__(self):
        import logging
        self.logger = logging.getLogger("secrets_audit")

    def log_secret_rotation(self, secret_name: str, rotated_by: str):
        self.logger.info(
            "Secret rotation",
            extra={
                "event": "secret_rotation",
                "secret_name": secret_name,
                "rotated_by": rotated_by,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_secret_access(self, secret_name: str, accessed_by: str, allowed: bool):
        level = self.logger.info if allowed else self.logger.warning
        level(
            "Secret access",
            extra={
                "event": "secret_access",
                "secret_name": secret_name,
                "accessed_by": accessed_by,
                "allowed": allowed,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_breach_response(self, compromised_secrets: list, actions: list):
        self.logger.critical(
            "Secret breach response",
            extra={
                "event": "secret_breach",
                "compromised_secrets": compromised_secrets,
                "actions_taken": actions,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

secrets_audit = SecretsAuditLogger()
```

### 8.3 Secret Inventory Verification

```bash
# scripts/verify_secrets.sh
#!/bin/bash
# Verifies that all required secrets are configured in the current environment

set -euo pipefail

echo "🔍 Verifying secret inventory..."

# Critical secrets (must exist)
CRITICAL=(
  "SUPABASE_URL"
  "SUPABASE_SERVICE_KEY"
  "JWT_SECRET"
  "CLAUDE_API_KEY"
  "RESEND_API_KEY"
)

# High secrets (should exist)
HIGH=(
  "SUPABASE_KEY"
)

# Low secrets (nice to have)
LOW=(
  "APP_NAME"
  "DEBUG"
  "CORS_ORIGINS"
  "OLLAMA_BASE_URL"
  "USE_LOCAL_AI"
)

MISSING_CRITICAL=false

echo "--- Critical Secrets ---"
for secret in "${CRITICAL[@]}"; do
  if [ -z "${!secret:-}" ]; then
    echo "  ❌ $secret — MISSING"
    MISSING_CRITICAL=true
  else
    VALUE="${!secret}"
    echo "  ✅ $secret = ${VALUE:0:8}..."
  fi
done

echo ""
echo "--- High Secrets ---"
for secret in "${HIGH[@]}"; do
  if [ -z "${!secret:-}" ]; then
    echo "  ⚠️  $secret — MISSING"
  else
    VALUE="${!secret}"
    echo "  ✅ $secret = ${VALUE:0:8}..."
  fi
done

echo ""
echo "--- Low Secrets ---"
for secret in "${LOW[@]}"; do
  if [ -z "${!secret:-}" ]; then
    echo "  📝 $secret — not set (optional)"
  else
    echo "  ✅ $secret = ${!secret}"
  fi
done

echo ""
if [ "$MISSING_CRITICAL" = true ]; then
  echo "❌ CRITICAL SECRETS MISSING — Application may not function correctly."
  exit 1
else
  echo "✅ All critical secrets present."
fi
```

---

## 9. Incident Response for Secret Leakage

### 9.1 Incident Severity Levels

| Level | Description | Example | Response Time |
|-------|-------------|---------|---------------|
| **SEV-1** | Public exposure of critical secret | JWT_SECRET in public GitHub repo | < 15 minutes |
| **SEV-2** | Internal exposure of critical secret | Secret in CI logs accessible to team | < 1 hour |
| **SEV-3** | Exposure of medium/high secret | SUPABASE_KEY in chat message | < 4 hours |
| **SEV-4** | Suspected exposure | Unauthorized access to secret storage | < 24 hours |

### 9.2 Incident Response Procedure

```markdown
# Secret Leakage Incident Response

## SEV-1: Public Exposure

### Immediate (0-15 minutes)
1. [ ] Rotate the compromised secret IMMEDIATELY
2. [ ] Revoke all active sessions (if JWT secret)
3. [ ] Remove exposed secret from public source (force push, GitHub support ticket)
4. [ ] Check for any unauthorized access/usage of the secret
5. [ ] Notify team via #security Slack channel

### Investigation (15-60 minutes)
6. [ ] Determine how the secret was exposed
7. [ ] Check git history for other secrets (git log -p | grep 'SECRET_PATTERN')
8. [ ] Review access logs for any suspicious activity
9. [ ] Check if secret was used before rotation

### Remediation (1-4 hours)
10. [ ] Rotate ALL secrets (defense in depth — assume cascade)
11. [ ] Run full secret inventory verification
12. [ ] Update incident response based on findings
13. [ ] Implement preventive measures (pre-commit hooks, secret scanning)

### Post-Mortem (within 5 business days)
14. [ ] Document incident in docs/operations/incidents/
15. [ ] Conduct root cause analysis
16. [ ] Update AGENTS.md and security docs
17. [ ] Implement additional controls to prevent recurrence
```

### 9.3 Emergency Commands

```bash
# Emergency secret rotation — execute immediately

# 1. Rotate JWT Secret (invalidates all sessions)
python -c "import secrets; print(secrets.token_hex(32))" | \
  xargs -I {} railway variables set JWT_SECRET={}

# 2. Revoke all Supabase sessions
# Go to: Supabase Dashboard → Authentication → Users
# Click "Revoke All Sessions"

# 3. Rotate Supabase Service Key
# Go to: Supabase Dashboard → Project Settings → API
# Click "Generate new service key"
railway variables set SUPABASE_SERVICE_KEY=<new-key>

# 4. Rotate Claude API Key
# Go to: https://console.anthropic.com/ → API Keys
# Create new key → Revoke old key
railway variables set CLAUDE_API_KEY=<new-key>

# 5. Rotate Resend API Key
# Go to: https://resend.com/api-keys
# Create new key → Revoke old key
railway variables set RESEND_API_KEY=<new-key>

# 6. Restart backend
railway restart
```

### 9.4 Secret Leakage Scenarios & Responses

| Scenario | Detection | Response | Prevention |
|----------|-----------|----------|------------|
| Secret committed to public git | GitHub notification / Dependabot | Force push removal; rotate secret | Pre-commit hooks; .gitignore |
| Secret in CI logs | GitHub Actions log review | Clear logs; rotate secret | Mask env vars; never echo secrets |
| Secret in screenshot | User reports | Rotate secret | Mask_secret in all screenshots |
| Developer leaves company | Offboarding process | Rotate all secrets | Immediate rotation on offboarding |
| Stolen laptop with .env.local | Laptop reported stolen | Rotate all secrets remotely | Full-disk encryption (BitLocker/FileVault) |
| Secret in third-party breach | Vendor notification | Rotate affected secrets; audit usage | Minimize third-party secret sharing |
| Secret in error message | Error monitoring alert | Fix error handler; rotate secret | Never include secrets in error responses |

---

## 10. Tooling

### 10.1 Secret Management Tools

| Tool | Purpose | Usage | Cost | Status |
|------|---------|-------|------|--------|
| **1Password** | Team secret vault | Store all secrets, share with team | $7.99/user/mo | ✅ Active |
| **1Password CLI** | CI/CD secret injection | `op run --env-file=.env.op` | Included | ✅ Active |
| **Railway Secrets** | Production env variables | Dashboard or CLI | Included | ✅ Active |
| **Vercel Environment Variables** | Frontend env variables | Dashboard or CLI | Included | ✅ Active |
| **GitHub Encrypted Secrets** | CI/CD secrets | Repository settings | Included | ✅ Active |
| **dotenv-vault** | Team .env sync (alternative) | Sync .env files across team | Free tier | ❌ Considered |
| **git-secrets** | Pre-commit secret scanning | Scan for secrets in git | Free | 📋 Planned |
| **trufflehog** | Deep secret scanning | Scan entire git history | Free | 📋 Planned |
| **HashiCorp Vault** | Enterprise secret management | API-driven secret access | Free (OSS) | ❌ Not needed |

### 10.2 1Password Vault Structure

```
Second Brain OS Vault
├── API Keys
│   ├── Supabase Service Key
│   ├── Claude API Key
│   ├── Resend API Key
│   └── Supabase Anon Key
├── Auth Secrets
│   ├── JWT Secret
│   └── OAuth Client Credentials
├── Development
│   ├── Local Dev .env (complete)
│   └── CI Test Environment
├── Deployment
│   ├── Railway Production
│   ├── Vercel Production
│   └── GitHub Actions
└── Recovery
    ├── Emergency Rotation Keys
    └── Backup Encryption Key
```

### 10.3 1Password Item Template

```json
{
  "title": "JWT_SECRET",
  "category": "API CREDENTIAL",
  "fields": [
    {
      "label": "credential",
      "value": "a1b2c3d4e5f6...256-bit-hex-value",
      "purpose": "PASSWORD"
    },
    {
      "label": "hostname",
      "value": "railway.app",
      "purpose": "WEBSITE"
    }
  ],
  "notes": "JWT HS256 signing secret\nRotation period: 90 days\nLast rotated: 2026-06-11\nNext rotation: 2026-09-09\n\nRotate via: railway variables set JWT_SECRET=<new>"
}
```

### 10.4 Secret Generation Commands

```bash
# Quick reference for generating secrets

# JWT Secret (256-bit hex)
python -c "import secrets; print(secrets.token_hex(32))"

# Fernet Key (field encryption)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Session Secret (128 random chars)
python -c "
import secrets, string
alphabet = string.ascii_letters + string.digits + '!@#\$%^&*'
print(''.join(secrets.choice(alphabet) for _ in range(128)))
"

# API Key (prefixed, 32 bytes entropy)
python -c "
import secrets
prefix = 'sb'
entropy = secrets.token_urlsafe(32)
print(f'{prefix}_{entropy}')
"

# Random password (20 chars, all categories)
python -c "
import secrets, string
alphabet = string.ascii_letters + string.digits + '!@#\$%^&*'
print(''.join(secrets.choice(alphabet) for _ in range(20)))
"
```

---

## 11. Secret Naming Conventions

### 11.1 Naming Rules

| Rule | Convention | Example |
|------|------------|---------|
| All uppercase | USE_UPPER_SNAKE_CASE | `SUPABASE_URL` |
| Prefix public vars | `NEXT_PUBLIC_` prefix | `NEXT_PUBLIC_SUPABASE_URL` |
| Prefix test vars | `TEST_` prefix | `TEST_SUPABASE_URL` |
| Group by service | `{SERVICE}_{PROPERTY}` | `SUPABASE_SERVICE_KEY`, `CLAUDE_API_KEY` |
| Avoid abbreviations | Full words preferred | `OLLAMA_BASE_URL` (not `OLL_URL`) |
| Boolean values | Present tense | `USE_LOCAL_AI` (not `LOCAL_AI_ENABLED`) |
| No hyphens | Underscores only | `RESEND_API_KEY` (not `RESEND-API-KEY`) |

### 11.2 Naming Examples

```bash
# ✅ Good naming
SUPABASE_URL
SUPABASE_SERVICE_KEY
NEXT_PUBLIC_SUPABASE_ANON_KEY
CLAUDE_API_KEY
RESEND_API_KEY
OLLAMA_BASE_URL
USE_LOCAL_AI
FIELD_ENCRYPTION_KEY
JWT_SECRET
JWT_ALGORITHM

# ❌ Bad naming
supabase_url        (not uppercase)
SUPABASEKEY         (missing underscore)
NEXT_PUBLIC_KEY     (which key?)
CLAUDE_KEY          (which Claude key?)
RESEND              (property unclear)
ENABLE_LOCAL_AI     (use USE_ prefix)
secret_key          (too generic)
```

### 11.3 Environment File Organization

```bash
# .env file sections (order maintained for all environments)
# ============================================================

# --- Supabase Configuration ---
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# --- Authentication ---
JWT_SECRET=
JWT_ALGORITHM=HS256

# --- AI Providers ---
CLAUDE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=True

# --- Email ---
RESEND_API_KEY=

# --- Frontend Public (prefixed) ---
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=

# --- Application ---
APP_NAME="Second Brain OS"
DEBUG=True
CORS_ORIGINS=http://localhost:3000

# --- Encryption (future) ---
# FIELD_ENCRYPTION_KEY=
```

---

## 12. Emergency Secret Rotation Procedure

### 12.1 One-Page Runbook

```markdown
# 🚨 EMERGENCY SECRET ROTATION
# Print this page and keep it accessible offline.

## Step 1: Identify Compromised Secret(s)
- [ ] JWT_SECRET
- [ ] SUPABASE_SERVICE_KEY
- [ ] CLAUDE_API_KEY
- [ ] RESEND_API_KEY
- [ ] Multiple / Unknown

## Step 2: Rotate Immediately

### JWT_SECRET (invalidates all sessions)
  railway variables set JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")

### SUPABASE_SERVICE_KEY
  # Generate in Supabase Dashboard → Settings → API
  railway variables set SUPABASE_SERVICE_KEY=<new-key>

### CLAUDE_API_KEY
  # Generate in https://console.anthropic.com/
  railway variables set CLAUDE_API_KEY=<new-key>

### RESEND_API_KEY
  # Generate in https://resend.com/api-keys
  railway variables set RESEND_API_KEY=<new-key>

## Step 3: Restart Services
  railway restart

## Step 4: Revoke Sessions (if JWT compromised)
  # Supabase Dashboard → Authentication → Revoke All Sessions

## Step 5: Verify
  railway logs --tail --limit 20    # Check startup
  curl https://api.secondbrain-os.com/health  # Check health

## Step 6: Update 1Password Vault
  # Update each rotated secret in 1Password

## Step 7: Post-Mortem (within 5 days)
  # Create incident report
  # Implement preventive measures

## CONTACTS
  Devops Lead: @devops-lead
  Security Lead: @security-lead
  Emergency: +1-xxx-xxx-xxxx
```

### 12.2 Emergency Contacts

| Role | Name | Contact | Alternate |
|------|------|---------|-----------|
| DevOps Lead | [Name] | [Slack/Phone] | [Name] |
| Security Lead | [Name] | [Slack/Phone] | [Name] |
| CTO | [Name] | [Slack/Phone] | [Name] |

### 12.3 Post-Incident Checklist

```markdown
## Post-Incident Checklist (within 5 business days)

### Root Cause Analysis
- [ ] How was the secret exposed?
- [ ] How long was it exposed?
- [ ] Was it used by unauthorized parties?
- [ ] What data was potentially accessed?

### Remediation
- [ ] Are all secrets rotated?
- [ ] Is the exposure vector closed?
- [ ] Are additional controls needed?

### Preventive Measures
- [ ] Add pre-commit hook for secret detection
- [ ] Add secret scanning to CI pipeline
- [ ] Update developer training
- [ ] Review and update AGENTS.md
- [ ] Add detection alerting

### Documentation
- [ ] Incident report filed in docs/operations/incidents/
- [ ] Security docs updated
- [ ] Team notified of findings
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-11 | Security Team | Initial secrets management: full inventory with 16 variables, env hierarchy (6 levels), rotation policy (90/180-day), local dev setup, CI/CD secrets (4 GitHub env references), Claude key lifecycle, service key management, 8 audit activities, SEV-1 through SEV-4 incident response, 8 tools evaluated, naming conventions, emergency runbook |

---

## References

- OWASP Secrets Management Cheatsheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- 1Password CLI: https://developer.1password.com/docs/cli/
- GitHub Encrypted Secrets: https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
- Railway Environment Variables: https://docs.railway.app/develop/variables
- Vercel Environment Variables: https://vercel.com/docs/projects/environment-variables
- NIST SP 800-57 (Key Management): https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
- Twelve-Factor App (Config): https://12factor.net/config
