# Secrets Management

## Document Control

| Field | Value |
|---|---|
| Document ID | SEC-SMG-001 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-12 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Principles

- **No hardcoded secrets** in source code
- All secrets stored as environment variables
- `.env` files are gitignored (see `.gitignore`)
- Template documented in `.env.example` with placeholder values

## 7. Environment Variables (Legacy Reference)

| Source | Location | Purpose |
|---|---|---|
| `.env.local` | Root | Local development overrides |
| `.env.example` | Root | Template with documentation |
| Railway Dashboard | Cloud | Production backend secrets |
| Vercel Environment Variables | Cloud | Production frontend secrets |

## 8. Secret Categories (Legacy Reference)

| Category | Examples | Storage |
|---|---|---|
| API Keys | `SUPABASE_KEY`, `CLAUDE_API_KEY` | Railway / Vercel |
| Database | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | Railway |
| Auth | `JWT_SECRET` | Railway |
| Integrations | `RESEND_API_KEY`, `OPENAI_API_KEY` | Railway |

## 9. Rotation Policy (Legacy Reference)

- Secrets rotated quarterly
- Immediate rotation on suspected compromise
- Rotation verified by health check endpoints

## 10. Prevention (Legacy Reference)

- Pre-commit hooks scan for hardcoded secrets
- CI pipeline runs secret detection
- Code review checklist includes secret exposure check
- `print()` and logging of secrets strictly forbidden

## 2. Secret Inventory

The following table documents every secret used in the project, its environment variable name, data classification tier, and rotation cadence:

| Secret Name | Environment Variable | Classification | Rotation Cadence |
|---|---|---|---|
| Supabase URL | `SUPABASE_URL` | T2 Confidential | Per incident |
| Supabase Anon Key | `SUPABASE_KEY` | T2 Confidential | Per incident |
| Supabase Service Key | `SUPABASE_SERVICE_KEY` | T1 Restricted | 90 days |
| JWT Secret | `JWT_SECRET` | T1 Restricted | 90 days |
| JWT Algorithm | `JWT_ALGORITHM` | T3 Internal | Never (fixed value) |
| Anthropic API Key | `ANTHROPIC_API_KEY` | T1 Restricted | Per incident |
| Resend API Key | `RESEND_API_KEY` | T1 Restricted | Per incident |
| OpenAI API Key (optional) | `OPENAI_API_KEY` | T1 Restricted | Per incident |
| Ollama Base URL | `OLLAMA_BASE_URL` | T3 Internal | Per infrastructure change |
| CORS Origins | `CORS_ORIGINS` | T3 Internal | Per deployment change |
| Rate Limit Max | `RATE_LIMIT_MAX` | T3 Internal | Per tuning change |
| Rate Limit Window | `RATE_LIMIT_WINDOW` | T3 Internal | Per tuning change |

### 2.1 Classification Definitions

| Tier | Label | Definition | Examples |
|---|---|---|---|
| T1 | Restricted | Highly sensitive; exposure causes severe impact | API keys, JWT secret, database service key |
| T2 | Confidential | User-identifiable or system-identifiable info | Database URL, public API keys |
| T3 | Internal | Business operations data | Configuration values, algorithm names |
| T4 | Public | Non-sensitive, intended for public consumption | App version strings, feature flags (public) |

## 3. Secret Storage Strategy

### 3.1 Sources of Truth

| Environment | Storage Location | Scope | Access Control |
|---|---|---|---|
| Local development | `.env.local` (gitignored) | Per-developer | File system permissions |
| Local template | `.env.example` (committed) | All developers | Public (placeholder values only) |
| CI/CD | GitHub Actions secrets | CI pipeline | Repository admin only |
| Production (API) | Railway dashboard | Production backend | Railway project admin |
| Production (Web) | Vercel environment variables | Production frontend | Vercel project admin |

### 3.2 Principles

- **Never commit secrets to version control.** All `.env*` files (except `.env.example`) are listed in `.gitignore`
- **Never log secrets.** Structured logging via `packages/shared/utils/logger.py` redacts known secret patterns
- **Never hardcode defaults.** Every secret requires explicit environment configuration
- **Never share secrets.** Secrets are provisioned per-environment and per-developer
- **Rotate on incident.** Any suspected exposure triggers immediate rotation

### 3.3 `.env.example` as Source of Truth

The `.env.example` file at the project root documents every required environment variable with:
- Variable name
- Purpose description
- Placeholder value (e.g., `your-supabase-url`)
- Whether it is required or optional

Developers copy `.env.example` to `.env.local` and fill in real values.

### 3.4 Git Protection

The following patterns are in `.gitignore` to prevent accidental commits:

```gitignore
# Environment files
.env
.env.local
.env.development
.env.production
.env.staging

# Secrets and credentials
*.key
*.pem
*.p12
*.pfx
credentials.json
service-account.json
```

## 4. Secret Rotation Procedure

### 4.1 Scheduled Rotation (Quarterly)

1. **Identify**: Review the secret inventory and identify secrets due for rotation
2. **Generate**: Create new secret values using secure random generation
3. **Update storage**: Replace the old value in all environment stores (Railway, Vercel, GitHub Secrets)
4. **Deploy**: Trigger a deployment to pick up the new secret
5. **Verify**: Run health check endpoints to confirm connectivity with new credentials
6. **Deprecate old**: After 24 hours of stable operation, invalidate the old secret
7. **Document**: Record the rotation in the security change log

### 4.2 Incident-Driven Rotation (Emergency)

1. **Revoke immediately**: Invalidate the compromised secret at the provider
2. **Generate new**: Create a replacement secret
3. **Update everywhere**: Deploy new secret to all affected environments
4. **Verify access**: Confirm all services reconnect successfully
5. **Audit exposure**: Check git history, logs, and CI artifacts for traces of the old secret
6. **Postmortem**: Document the incident, root cause, and preventative measures

### 4.3 Rotation Commands

```bash
# Generate a secure random secret (JWT, API keys)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Verify JWT secret works after rotation
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

## 5. Prevention Controls

### 5.1 Automated Detection

| Tool | Stage | Action |
|---|---|---|
| **trufflehog** | Pre-commit hook | Scans staged files for high-entropy strings and known secret patterns. Blocks commit if secrets detected. |
| **trufflehog** | CI security job | Scans entire repository history for exposed secrets. Fails CI pipeline on findings. |
| **GitLeaks** | CI security job (optional) | Git-based secret detection as secondary check. |
| **ESLint plugin** | Pre-commit (frontend) | Detects hardcoded API keys in TypeScript/React code. |

### 5.2 Code Review Checklist for Secrets

Every PR must pass these secret-related checks:
- [ ] No environment variables hardcoded in source files
- [ ] No API keys, tokens, or passwords visible in code changes
- [ ] No `.env` files included in the commit
- [ ] No secrets logged via `print()`, `console.log()`, or structured logger
- [ ] New environment variables added to `.env.example`
- [ ] New environment variables documented in this file's Secret Inventory
- [ ] New secrets classified per the data classification policy

### 5.3 `.gitignore` Patterns for Secrets

Beyond the standard `.env` patterns, the `.gitignore` blocks:

```gitignore
# Credential files
**/credentials.json
**/service-account.json
**/*.p12
**/*.pfx

# IDE-specific secret storage
.idea/secrets/
.vscode/secrets/

# Build artifacts that may embed secrets
**/__pycache__/
**/.next/
```

## 6. Incident Response for Secret Leak

### 6.1 Detection

Secret leaks are detected through:
- **Pre-commit hooks**: trufflehog blocks the commit containing the secret
- **CI pipeline**: trufflehog scan fails and notifies the team
- **Manual discovery**: Developer notices a secret in git history or logs
- **Provider alert**: Cloud provider (Supabase, Anthropic) notifies of unusual access patterns

### 6.2 Response Procedure

If a secret is accidentally committed to the repository:

| Step | Action | Owner | Time Target |
|---|---|---|---|
| 1 | **Revoke**: Immediately invalidate the compromised secret at the source (Supabase, Anthropic, etc.) | Developer | 15 minutes |
| 2 | **Generate**: Create a new secret value | Developer | 15 minutes |
| 3 | **Update**: Replace old value in Railway, Vercel, and GitHub Secrets | Developer | 30 minutes |
| 4 | **Deploy**: Push an emergency deployment with the new secret | DevOps | 30 minutes |
| 5 | **Verify**: Confirm health checks pass and services reconnect | Developer | 15 minutes |
| 6 | **Purge**: Remove the secret from git history using `git filter-branch` or BFG Repo-Cleaner | Developer | 1 hour |
| 7 | **Force push**: Update remote branches with cleaned history (coordinate with team) | Developer | 30 minutes |
| 8 | **Audit**: Check CI logs, build artifacts, and cached copies for traces of the secret | Developer | 1 hour |
| 9 | **Document**: Write a postmortem with timeline, impact assessment, and preventative measures | Developer | After resolution |

### 6.3 Git History Cleanup Commands

```bash
# Option 1: BFG Repo-Cleaner (recommended for speed)
java -jar bfg.jar --replace-text passwords.txt my-repo.git

# Option 2: git filter-branch (for targeted removal)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.local" \
  --prune-empty --tag-name-filter cat -- --all

# After cleanup, force push all branches
git push origin --force --all
git push origin --force --tags
```

### 6.4 Prevention Verification

After any secret incident, verify prevention controls are effective:
- [ ] trufflehog correctly detects the exposed secret pattern
- [ ] CI secret scan would have caught the leak if pre-commit was bypassed
- [ ] `.gitignore` patterns cover the leaked file type
- [ ] All developers acknowledge the incident and updated procedures

## Related Documents

| Document | Purpose |
|---|---|
| [Supply Chain Security](supply-chain-security.md) | Dependency scanning and vulnerability management |
| [SDL](../security/sdl.md) | Secure Development Lifecycle â€” Phase 4 (Implementation) covers secret handling |
| [Security Architecture](../security/24_Security.md) | Enterprise security architecture â€” Section 5 (Authentication & Authorization) |
| [FastAPI Hardening](../security/hardening/fastapi.md) | Backend JWT validation and API key auth |
| [AGENTS.md](../../AGENTS.md) | Master project reference â€” Section 23 (Security Compliance), Section 13 (Environment Setup) |

