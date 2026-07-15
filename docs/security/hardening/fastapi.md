# FastAPI Security Hardening Guide — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | SEC-HFA-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal — Security |
| **Owner** | Developer |
| **Related Docs** | [SEC-HSU-001](supabase.md), [SEC-HNE-001](nextjs.md), Threat Model (`docs/security/ThreatModel.md`) |

---

## Hardening Checklist

### 1. Rate Limiting

| Item | Status | Verification |
|---|---|---|
| Global rate limiter middleware active | ✅ **Configured** | `grep -n "RateLimiter" apps/api/main.py` |
| Configurable max requests per window | ✅ **Configured** | `grep "RATE_LIMIT_MAX" .env.example` — default 100 |
| Configurable window duration | ✅ **Configured** | `grep "RATE_LIMIT_WINDOW" .env.example` — default 60s |
| Per-endpoint rate limits for AI endpoints | ✅ **Configured** | `grep -n "EndpointRateLimiter" packages/shared/utils/rate_limiter.py` — chat limited to 30 req/min |
| Retry-After header set on 429 | ✅ **Configured** | `rate_limiter.py:dispatch()` — returns with `Retry-After` |

**Verification command:**
```bash
# Check rate limiter is registered in middleware stack
python -c "from shared.utils.rate_limiter import RateLimiter; print('RateLimiter available')"

# Test rate limiting
for i in $(seq 1 110); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/health; done | sort | uniq -c
```

---

### 2. CORS Configuration

| Item | Status | Verification |
|---|---|---|
| CORS middleware enabled | ✅ **Configured** | `CORSMiddleware` registered in `main.py:67` |
| Allowed origins from env config | ✅ **Configured** | `settings.cors_origins` — comma-separated in `.env` |
| No wildcard origins in production | ⚠️ **Verify** | Check `CORS_ORIGINS` env var — must not contain `*` |
| Proper allowed methods list | ✅ **Configured** | `["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]` |
| Credentials support enabled | ✅ **Configured** | `allow_credentials=True` |

**Verification command:**
```bash
# Check CORS origins in settings
python -c "from config.core.config import settings; print(settings.cors_origins)"

# Test CORS preflight
curl -s -o /dev/null -w "%{http_code}" -X OPTIONS -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" http://localhost:8000/api/v1/health
```

---

### 3. Input Validation (Pydantic)

| Item | Status | Verification |
|---|---|---|
| All request bodies use Pydantic schemas | ✅ **Configured** | All 31 routers use `database/schemas/` models |
| Schemas defined in `database/schemas/` | ✅ **Configured** | 18+ schema files — never inline in routes |
| Error responses use standardized schema | ✅ **Configured** | `database/schemas/error_response.py` |
| Strict type validation enabled | ✅ **Configured** | Pydantic v2 strict mode |
| String length constraints enforced | ⚠️ **Verify per-schema** | Check `min_length` / `max_length` on `database/schemas/task.py` |

**Verification command:**
```bash
# Run schema validation tests
python -m pytest tests/test_schemas.py -v

# Check all schemas have validation
python -c "
from database.schemas.task import TaskCreate
s = TaskCreate.model_json_schema()
required = s.get('required', [])
print(f'TaskCreate required fields: {required}')
"
```

---

### 4. JWT Token Validation

| Item | Status | Verification |
|---|---|---|
| JWT verification on all protected routes | ✅ **Configured** | Via `Depends(get_current_user())` on all 31 routers |
| Token expiry enforced | ✅ **Configured** | `settings.access_token_expire_minutes` (default 60) |
| HS256 signing algorithm | ✅ **Configured** | `settings.jwt_algorithm = "HS256"` |
| Token cached with 60s TTL | ✅ **Configured** | `@cached(ttl=60)` on `_verify_supabase_token()` |
| JWT secret from env variable | ✅ **Configured** | `settings.jwt_secret` — never hardcoded |
| API key support for machine auth | ✅ **Configured** | `api_key_auth.py` — token prefix `sb_` |
| WWW-Authenticate header on 401 | ✅ **Configured** | `auth.py:36` — `headers={"WWW-Authenticate": "Bearer"}` |

**Verification command:**
```bash
# Test JWT validation
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid-token" http://localhost:8000/api/v1/tasks
# Expected: 401

# Check token expiry config
python -c "from config.core.config import settings; print(f'Token expiry: {settings.access_token_expire_minutes} min')"
```

---

### 5. CSRF Protection

| Item | Status | Verification |
|---|---|---|
| CSRF middleware registered | ✅ **Configured** | `CSRFMiddleware` in `main.py:71` |
| Token validation on mutation methods | ✅ **Configured** | POST, PUT, DELETE, PATCH checked |
| CSRF token generation endpoint | ✅ **Configured** | Via Supabase auth (double-submit cookie pattern) |
| Safe methods (GET, HEAD, OPTIONS) exempt | ✅ **Configured** | Standard HTTP method filtering |

**Verification command:**
```bash
# Test CSRF rejection
curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{}' http://localhost:8000/api/v1/tasks
# Expected: 403 if no CSRF token

# Check CSRF middleware source
python -c "from shared.utils.csrf import CSRFMiddleware; print('CSRF middleware available')"
```

---

### 6. SQL Injection Prevention

| Item | Status | Verification |
|---|---|---|
| Supabase SDK used for all queries | ✅ **Configured** | No raw SQL in application code |
| Parameterized queries via `.eq()`, `.in_()` | ✅ **Configured** | All queries use Supabase query builder |
| RLS enforces user isolation | ✅ **Configured** | All 17 user tables have RLS policies |
| No raw SQL interpolation | ✅ **Configured** | `grep -r "\.execute(sql" apps/` — should return nothing |
| SQL injection audit script available | ✅ **Configured** | `scripts/sql-injection-audit.sh` |

**Verification command:**
```bash
# Run SQL injection auditor
bash scripts/sql-injection-audit.sh

# Check for any raw SQL usage
grep -rn "\.execute(" apps/api/ --include="*.py" | grep -v "supabase" | grep -v "\.execute()"
```

---

### 7. Dependency Scanning

| Item | Status | Verification |
|---|---|---|
| npm audit integrated in CI | ✅ **Configured** | `.github/workflows/ci.yml` — high severity check |
| Trivy vulnerability scan in CI | ✅ **Configured** | Security job scans all Docker images |
| Dependabot active on GitHub | ✅ **Configured** | `.github/dependabot.yml` — npm, pip, docker |
| Python dependency check in CI | ⚠️ **Partial** | `pip-audit` recommended — not yet in CI |
| OWASP dependency check available | ✅ **Configured** | `scripts/owasp-check.sh` |
| PIN versions in requirements.txt | ✅ **Configured** | All `requirements.txt` files pin exact versions |

**Verification command:**
```bash
# Check Dependabot config
cat .github/dependabot.yml

# Run OWASP check
bash scripts/owasp-check.sh

# Check Python deps for known vulnerabilities
pip-audit  # requires `pip install pip-audit`
```

---

### 8. Logging Best Practices

| Item | Status | Verification |
|---|---|---|
| Structured JSON logging | ✅ **Configured** | `shared/utils/logger.py` — JSON format with timestamp, level, message |
| Request ID on every log entry | ✅ **Configured** | UUID v4 generated per request in middleware |
| No secrets in logs | ✅ **Configured** | Logs exclude `Authorization` header |
| Sentry integration for errors | ✅ **Configured** | `sentry_sdk` initialized in `main.py:61` |
| Logtail handler registered | ✅ **Configured** | `_logtail_handler` in logger setup |
| Separate log levels per environment | ✅ **Configured** | `settings.log_level` — DEBUG in dev, INFO in prod |
| Mutation audit logging | ✅ **Configured** | `audit_middleware_dispatch()` logs all mutations |

**Verification command:**
```bash
# Check log format
python -c "
from shared.utils.logger import logger
logger.info('Verification test', extra={'check': 'logging'})
print('Structured logging functional')
"

# Check Sentry integration
python -c "from config.core.config import settings; print(f'Sentry DSN configured: {bool(settings.sentry_dsn)}')"
```

---

### 9. Secrets Management

| Item | Status | Verification |
|---|---|---|
| All secrets from environment variables | ✅ **Configured** | `config.core.config.settings` reads from env |
| `.env` files in `.gitignore` | ✅ **Configured** | Confirmed in `.gitignore` |
| `.env.example` documents all vars | ✅ **Configured** | Comprehensive example file at root |
| No hardcoded credentials in code | ✅ **Configured** | `grep -r "password\|secret\|api_key" apps/ --include="*.py" | grep -v ".env" | grep -v "settings\."` |
| API keys stored server-side only | ✅ **Configured** | `settings.claude_api_key` — never exposed to frontend |
| Secrets rotated regularly | ⚠️ **Manual** | No automated rotation policy — document schedule in runbook |

**Verification command:**
```bash
# Check for accidentally committed secrets
git log --all --oneline --diff-filter=A -- '*.env'
git grep -n "SUPABASE_KEY\|CLAUDE_API_KEY\|JWT_SECRET" -- ':!.env.example'

# Verify env var loading
python -c "from config.core.config import settings; print(f'Secrets loaded: JWT={bool(settings.jwt_secret)}, Supabase={bool(settings.supabase_url)}')"
```

---

### 10. Security Headers

| Item | Status | Verification |
|---|---|---|
| `X-Content-Type-Options: nosniff` | ⚠️ **Needs Configuration** | Add via middleware or reverse proxy |
| `X-Frame-Options: DENY` | ⚠️ **Needs Configuration** | Add via middleware or reverse proxy |
| `X-XSS-Protection: 1; mode=block` | ⚠️ **Needs Configuration** | Add via middleware or reverse proxy |
| `Strict-Transport-Security` (HSTS) | ⚠️ **Needs Configuration** | Add via middleware or reverse proxy (Vercel edge) |
| `Content-Security-Policy` header | ⚠️ **Needs Configuration** | Configure in Next.js — see `nextjs.md` |
| `Referrer-Policy: strict-origin-when-cross-origin` | ⚠️ **Needs Configuration** | Recommended for production |
| `Permissions-Policy` header | ⚠️ **Needs Configuration** | Restrict camera/mic/geolocation |

**Recommended middleware addition (`main.py`):**

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response
```

**Verification command:**
```bash
# Check current security headers
curl -s -I http://localhost:8000/api/v1/health | grep -iE "x-content|x-frame|x-xss|strict-transport|content-security|referrer|permissions"

# Security Headers checker (production)
curl -s -I https://api.secondbrain-os.com/api/v1/health | grep -iE "x-content|x-frame|x-xss|strict-transport"
```

---

## Summary

| Category | Configured | Needs Config | Total |
|---|---|---|---|
| Rate Limiting | 5 | 0 | 5 |
| CORS Configuration | 4 | 1 | 5 |
| Input Validation | 4 | 1 | 5 |
| JWT Token Validation | 6 | 0 | 6 |
| CSRF Protection | 4 | 0 | 4 |
| SQL Injection Prevention | 5 | 0 | 5 |
| Dependency Scanning | 4 | 1 | 5 |
| Logging Best Practices | 6 | 0 | 6 |
| Secrets Management | 5 | 1 | 6 |
| Security Headers | 0 | 6 | 6 |
| **Total** | **43** | **10** | **53** |

**Configuration rate: 81.1%** — Prioritize security headers and dependency auditing before production launch.

---

## Related Documents

| Document | Purpose |
|---|---|
| [SDL](../sdl.md) | Secure Development Lifecycle — overarching security methodology |
| [Supabase Hardening](supabase.md) | Supabase-specific security hardening checklist |
| [Next.js Hardening](nextjs.md) | Next.js-specific security hardening checklist |
| [Security Architecture](../../security/24_Security.md) | Enterprise security architecture — Section 7 (API Security) |
| [Threat Model](../../security/ThreatModel.md) | STRIDE threat model for the full system |
| [Supply Chain Security](../../engineering/supply-chain-security.md) | Dependency scanning and vulnerability management |
| [Secrets Management](../../engineering/secrets-management.md) | Environment variable and API key management |
| [AGENTS.md](../../../AGENTS.md) | Master project reference — Section 23 (Security Compliance) |
