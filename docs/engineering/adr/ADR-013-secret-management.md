## Document Control

| Field | Value |
|---|---|
| Document ID | ENG-ADR13-001 |
| Version | 1.0.0 |
| Status | Accepted |
| Last Updated | 2026-07-11 |

# ADR-013: Secret Management Strategy

## Document Control

| Field | Value |
|---|---|
| ADR Number | 013 |
| Status | Accepted |
| Date | 2026-07-10 |
| Deciders | Developer |
| Replaces | None |
| Superseded By | None |
| Category | Security Infrastructure |

---

## 1. Title

Secret Management Strategy â€” Environment Variables with Git-Never Pattern

---

## 2. Context

Second Brain OS requires several secrets to operate:
- Supabase URL and API keys
- JWT signing secret
- Claude API key
- Groq API key
- Sentry DSN
- Encryption keys

These secrets must be:
1. Accessible to the application at runtime
2. Never committed to version control
3. Rotatable without code changes
4. Documented for onboarding

---

## 3. Decision

Use **environment variables** as the primary secret management mechanism, following the **git-never pattern**:

1. Secrets are stored in `.env` files (never committed)
2. `.env.example` documents all required variables (committed)
3. Environment variables injected by deployment platforms
4. Local development uses `.env.local` (gitignored)

---

## 4. Detailed Design

### 4.1 File Hierarchy

| File | Committed? | Purpose |
|---|---|---|
| `.env.example` | âœ… Yes | Template with default values and documentation |
| `.env.local` | âŒ No (gitignored) | Local development overrides |
| `.env.production` | âŒ No | Production secrets (deployment platform) |
| `.env` | âŒ No (gitignored) | Automatic fallback |

### 4.2 .env.example Structure

```bash
# =============================================================================
# Second Brain OS â€” Environment Configuration
# =============================================================================
# Copy this file to .env.local and fill in your values:
#   cp .env.example .env.local
# =============================================================================

# --- Supabase (Required) ---
# Project URL from Supabase Dashboard â†’ Settings â†’ API
SUPABASE_URL=https://your-project.supabase.co
# anon/public key (safe for client-side)
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
# service role key (server-side only, NEVER expose to client)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...

# --- Authentication ---
# Generate with: openssl rand -hex 32
JWT_SECRET=your-jwt-secret-at-least-32-chars
JWT_ALGORITHM=HS256

# --- AI Providers ---
# Ollama (local)
USE_LOCAL_AI=True
OLLAMA_BASE_URL=http://localhost:11434

# Claude API (optional, for cloud fallback)
CLAUDE_API_KEY=sk-ant-...

# Groq API (optional)
GROQ_API_KEY=gsk-...

# --- Error Tracking ---
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# --- CORS ---
CORS_ORIGINS=http://localhost:3000,https://secondbrain-os.vercel.app
```

### 4.3 Loading Strategy

```python
# packages/config/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    
    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    
    # AI Providers
    use_local_ai: bool = True
    ollama_base_url: str = "http://localhost:11434"
    claude_api_key: str | None = None
    groq_api_key: str | None = None
    
    # Error Tracking
    sentry_dsn: str | None = None
    next_public_sentry_dsn: str | None = None
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

settings = Settings()
```

### 4.4 Deployment Platform Secrets

```yaml
# Railway (backend)
# Set via Dashboard â†’ Variables
SUPABASE_URL=<value>
SUPABASE_KEY=<value>
SUPABASE_SERVICE_KEY=<value>
JWT_SECRET=<value>
CLAUDE_API_KEY=<value>

# Vercel (frontend)
# Set via Dashboard â†’ Environment Variables
NEXT_PUBLIC_SUPABASE_URL=<value>
NEXT_PUBLIC_SUPABASE_KEY=<value>
NEXT_PUBLIC_SENTRY_DSN=<value>
```

---

## 5. Alternatives Considered

### Alternative 1: HashiCorp Vault

**Approach:** Self-hosted or cloud Vault for secret management.

**Pros:** Enterprise-grade, audit logging, dynamic secrets
**Cons:** Overkill for single-user, complex setup, infrastructure cost
**Decision:** Rejected â€” too heavy for the project's scale

### Alternative 2: Encrypted .env Files

**Approach:** Encrypt `.env` with GPG and commit encrypted version.

**Pros:** Secrets in repo, one-step decrypt
**Cons:** Key distribution problem, merge conflicts, easy to leak decrypt key
**Decision:** Rejected â€” git-never is simpler and safer

### Alternative 3: AWS Secrets Manager / Parameter Store

**Approach:** Cloud secret store with SDK integration.

**Pros:** Rotation, audit, cross-service sharing
**Cons:** AWS dependency, latency on each access, cost for small usage
**Decision:** Rejected â€” adds cloud dependency with minimal benefit

---

## 6. Secret Rotation Policy

| Secret | Rotation Frequency | Rotation Method |
|---|---|---|
| SUPABASE_KEY | Never (static) | Regenerate from Supabase Dashboard |
| SUPABASE_SERVICE_KEY | Quarterly | Regenerate from Supabase Dashboard |
| JWT_SECRET | Quarterly | `openssl rand -hex 32` â†’ update in all environments |
| CLAUDE_API_KEY | Per credential expiry | Regenerate from Anthropic Console |
| GROQ_API_KEY | Per credential expiry | Regenerate from Groq Console |
| SENTRY_DSN | If compromised | Regenerate from Sentry Settings |

---

## 7. Security Controls

| Control | Implementation |
|---|---|
| **No secrets in code** | `.gitignore` blocks `.env*` except `.env.example` |
| **No secrets in logs** | Structured logger redacts `password`, `token`, `key`, `secret` |
| **No secrets in error messages** | Exception handler strips sensitive fields |
| **Least privilege** | `SUPABASE_KEY` (anon) used client-side, `SERVICE_KEY` server-only |
| **Encryption at rest** | Environment variables encrypted by Railway/Vercel |

### 7.1 Gitignore Rules

```gitignore
# .gitignore
.env
.env.local
.env.production
.env.development
!.env.example
```

### 7.2 Secret Scanner (Pre-commit)

```bash
# Scans for secrets before commit
# .pre-commit-config.yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
    - id: gitleaks
```

---

## 8. Consequences

### Positive

| Benefit | Description |
|---|---|
| **Simple to implement** | No infrastructure, no SDKs |
| **Platform-native** | Railway/Vercel handle secret injection |
| **Git-safe** | No risk of committing secrets |
| **Documented** | `.env.example` serves as documentation |
| **Easy local dev** | Copy `.env.example` â†’ `.env.local`, fill in values |

### Negative

| Cost | Mitigation |
|---|---|
| **Manual rotation** | Calendar reminders for quarterly rotation |
| **No access audit** | Acceptable for single-user system |
| **Platform-dependent** | Works with Railway/Vercel/Heroku pattern |

---

## 9. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Secret committed accidentally | Low | Critical | `.gitignore`, pre-commit hooks |
| Secret leaked via CI logs | Low | High | Redact in CI output, use secret masking |
| `.env.example` out of sync | Medium | Low | Review when adding new secrets |
| Platform security breach | Low | Critical | Rotation capability, limited blast radius |

---

## 10. Related Decisions

| ADR | Relation |
|---|---|
| ADR-006: Error Handling | Error responses never expose secrets |
| ADR-010: AI Provider Failover | API keys for multiple providers |

---

## 11. References

| Reference | Link |
|---|---|
| `.env.example` | `/.env.example` |
| Settings Config | `packages/config/core/config.py` |
| Gitignore | `/.gitignore` |
| Railway Variables | https://docs.railway.app/develop/variables |
| Vercel Environment | https://vercel.com/docs/environment-variables |
