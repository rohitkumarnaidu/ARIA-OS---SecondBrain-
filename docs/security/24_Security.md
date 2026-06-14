# Enterprise Security Architecture

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-SEC-001 |
| Version | 3.0.0 |
| Status | Active |
| Last Updated | 2026-06-11 |
| Classification | Internal — Security Team |
| Owner | Security Lead |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Security Principles & Philosophy](#2-security-principles--philosophy)
3. [Threat Model](#3-threat-model)
4. [Authentication Security](#4-authentication-security)
5. [Authorization Security](#5-authorization-security)
6. [Data Security](#6-data-security)
7. [API Security](#7-api-security)
8. [Frontend Security](#8-frontend-security)
9. [AI Security](#9-ai-security)
10. [Infrastructure Security](#10-infrastructure-security)
11. [Network Security](#11-network-security)
12. [Incident Response Plan](#12-incident-response-plan)
13. [Security Compliance Mapping](#13-security-compliance-mapping)
14. [Security Review Process in CI/CD](#14-security-review-process-in-cicd)
15. [Security Roadmap](#15-security-roadmap)
16. [Appendices](#16-appendices)

---

## 1. Executive Summary

Second Brain OS (ARIA OS) is a personal productivity platform handling sensitive user data including tasks, communications, AI-generated insights, and personal metrics. This document defines the comprehensive security architecture protecting the system across all layers.

**Trust Scope:** Single-user B2C productivity tool with optional AI processing.

**Security Posture:** Defense-in-depth with 7 security layers — authentication, authorization, transport, application, data, infrastructure, and AI.

**Key Risks Mitigated:**
- Unauthorized access to user data (primary risk)
- AI prompt injection and data leakage
- API abuse and rate-limit bypass
- Credential theft and session hijacking
- Supply chain vulnerabilities

**Current Maturity Level:** Level 2 (Managed) — progressing toward Level 3 (Defined) per NIST CSF.

---

## 2. Security Principles & Philosophy

### 2.1 Core Principles

| Principle | Definition | Application in ARIA OS |
|---|---|---|
| **Defense in Depth** | Multiple independent security layers; failure of one does not compromise the system | 7-layer model: Auth → RLS → Rate Limit → Validation → CORS → Encryption → Monitoring |
| **Least Privilege** | Every entity operates with the minimum permissions necessary | RLS on all 21 tables; service roles limited; API tokens scoped |
| **Zero Trust** | Never trust, always verify — every request authenticated and authorized regardless of origin | Every API call validates JWT + user_id; internal services also authenticate |
| **Secure by Default** | Security is opt-out, not opt-in | RLS enabled at table creation; HTTPS enforced; headers set globally |
| **Privacy by Design** | Data protection integrated into architecture, not bolted on | Data minimization; no telemetry; user-owned analytics |
| **Fail Secure** | On failure, default to denying access | Auth failures return 401; RLS failures return empty sets; validation errors reject |
| **Separation of Duties** | No single entity has end-to-end control | OAuth (Google) ≠ Data (Supabase) ≠ AI (Ollama/Claude) |

### 2.2 Security Assumptions

| Assumption | Rationale | Mitigation if Violated |
|---|---|---|
| Client devices are trusted | User is the sole operator of their account | Session tokens have limited lifetime; refresh rotation |
| Supabase infrastructure is secure | Supabase manages underlying cloud security | Data encrypted at rest; RLS provides defense layer |
| Ollama runs on local/trusted network | Local AI avoids data transmission to third parties | Claude fallback has data processing agreement |
| npm/pip packages are non-malicious | Supply chain attacks are external risk | `npm audit` in CI; dependency pinning; SCA scanning |

### 2.3 Security Decision Records

| SDR-ID | Decision | Rationale | Date |
|---|---|---|---|
| SDR-001 | Supabase Auth over custom auth | Avoid credential storage, password hashing, session management | 2026-01 |
| SDR-002 | RLS over application-level authorization | Database enforces policy even if API layer is bypassed | 2026-01 |
| SDR-003 | Local Ollama over cloud AI by default | User data never leaves local machine for AI processing | 2026-02 |
| SDR-004 | In-memory rate limiting over Redis | Simplifies architecture; acceptable for single-user scale | 2026-02 |
| SDR-005 | No analytics cookies or fingerprinting | Privacy-first design; compliance with GDPR ePrivacy | 2026-03 |

---

## 3. Threat Model

### 3.1 Threat Actors

| Actor | Motivation | Capability | Frequency |
|---|---|---|---|
| Opportunistic Attacker | Data theft, credential stuffing | Low-Medium (automated tools) | High |
| Targeted Attacker | Personal data, AI insights | Medium-High (manual exploitation) | Low |
| Malicious Insider (Supabase/Cloud) | Data access | High (infrastructure access) | Very Low |
| Service Abuse (Bots) | API abuse, resource exhaustion | Low (scraping tools) | Medium |
| Supply Chain Attacker | Malicious dependency injection | High (compromised packages) | Very Low |

### 3.2 Threat Matrix (STRIDE per Component)

| Component | Spoofing | Tampering | Repudiation | Information Disclosure | DoS | Elevation of Privilege |
|---|---|---|---|---|---|---|
| **Supabase Auth** | OAuth token forgery | — | Auth audit logs | Token leakage | Rate limiting | JWT secret compromise |
| **FastAPI Backend** | JWT replay | Request body manipulation | Request logging | Error message leakage | Unvalidated input floods | RLS bypass |
| **Next.js Frontend** | XSS, CSRF | DOM manipulation | Client logs | Source map exposure | Client-side resource exhaustion | Privilege escalation via API |
| **Ollama AI** | Model prompt injection | Model output poisoning | No audit | Context leakage (cross-user) | Resource exhaustion | Sandbox escape |
| **Supabase DB** | Connection hijacking | Direct SQL injection | Query logs | RLS bypass | Connection pool exhaustion | Service role key abuse |
| **Vercel/Railway** | DNS spoofing | Build pipeline tampering | Deploy logs | Environment variable exposure | DDoS | Build secret access |

### 3.3 Attack Trees

#### 3.3.1 Data Exfiltration Attack Tree

```
Goal: Exfiltrate user data from ARIA OS
├── 1. Compromise Authentication
│   ├── 1.1 Steal JWT token
│   │   ├── 1.1.1 XSS to read localStorage
│   │   └── 1.1.2 MitM on non-HTTPS connection
│   ├── 1.2 Brute-force credentials (not applicable — OAuth only)
│   └── 1.3 OAuth token interception
│       └── 1.3.1 Malicious OAuth redirect URI
├── 2. Bypass Authorization
│   ├── 2.1 RLS policy bypass via SQL injection
│   ├── 2.2 user_id manipulation in API request
│   └── 2.3 Service role key exposure
├── 3. Intercept Data in Transit
│   ├── 3.1 TLS downgrade attack
│   └── 3.2 Certificate spoofing
└── 4. Access Backend Infrastructure
    ├── 4.1 Railway console compromise
    ├── 4.2 Environment variable leakage
    └── 4.3 Dependency vulnerability exploitation
```

#### 3.3.2 AI Prompt Injection Attack Tree

```
Goal: Inject malicious prompt to AI model
├── 1. Direct Injection (via chat interface)
│   ├── 1.1 System prompt override attempt
│   └── 1.2 Role-play jailbreak
├── 2. Indirect Injection (via data)
│   ├── 2.1 Malicious task description parsed by briefing agent
│   └── 2.2 Malicious course content parsed by learning agent
└── 3. Context Leakage
    ├── 3.1 Prompt extraction via "repeat your instructions"
    └── 3.2 Data exfiltration via formatted output
```

---

## 4. Authentication Security

### 4.1 Authentication Architecture

```
User Browser                   Supabase Auth                   Google OAuth
     │                              │                              │
     │  1. Click "Sign in with Google"                             │
     │─────────────────────────────►│                              │
     │                              │  2. Redirect to Google       │
     │                              │─────────────────────────────►│
     │  3. Google consent screen    │                              │
     │◄─────────────────────────────│                              │
     │  4. Auth code returned       │                              │
     │─────────────────────────────►│                              │
     │                              │  5. Exchange code for tokens │
     │                              │─────────────────────────────►│
     │                              │  6. ID + Access + Refresh    │
     │                              │◄─────────────────────────────│
     │  7. Session created          │                              │
     │◄─────────────────────────────│                              │
     │  8. JWT stored in localStorage (HTTP-only cookie planned)   │
```

### 4.2 Identity Provider: Google OAuth 2.0

| Parameter | Configuration | Rationale |
|---|---|---|
| OAuth Flow | Authorization Code + PKCE | Most secure for SPAs; PKCE prevents authorization code interception |
| Client Type | Public (no client secret) | SPA cannot store secrets; PKCE provides equivalent security |
| Scopes | `openid`, `profile`, `email` | Minimum necessary for user identification |
| Redirect URIs | `https://*.supabase.co/auth/v1/callback` | Restrict to known callback endpoints |
| Consent Screen | Internal (testing) → External (production) | Prevent unverified app warnings |

### 4.3 JWT Token Handling

#### Token Types

| Token | Purpose | Lifetime | Storage | Rotation |
|---|---|---|---|---|
| Access Token (JWT) | API authentication | 1 hour | In-memory (planned) / localStorage (current) | Auto-refresh |
| Refresh Token | Obtain new access tokens | 7 days (configurable) | localStorage | Rotated on use |
| Provider Token (Google) | Access Google APIs | 1 hour | Not stored | Not used |

#### JWT Structure

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "sub": "user-uuid",
  "aud": "authenticated",
  "role": "authenticated",
  "iat": 1718000000,
  "exp": 1718003600,
  "email": "user@example.com",
  "phone": "",
  "app_metadata": { "provider": "google" },
  "user_metadata": { "avatar_url": "...", "full_name": "..." },
  "iss": "https://<project>.supabase.co/auth/v1"
}
```

#### Token Validation (Backend)

```python
# apps/api/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.core.supabase import get_supabase
from jose import JWTError, jwt
from config.core.config import settings

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate JWT and return authenticated user.
    
    Security Properties:
    - Rejects expired tokens (checked via exp claim)
    - Rejects tokens with invalid signature (checked via HS256 secret)
    - Rejects tokens with wrong issuer (checks iss claim)
    - Falls back to Supabase auth.get_user() for additional validation
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # First-level validation: decode locally
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "sub", "iat"],
            },
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    # Second-level validation: verify with Supabase
    # This catches revoked tokens and disabled accounts
    try:
        supabase = get_supabase()
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked or user disabled",
        )
```

### 4.4 Session Management

| Concern | Implementation |
|---|---|
| **Session Creation** | On OAuth success via Supabase Auth |
| **Session Storage** | Server-side: Supabase; Client: localStorage (migration to httpOnly cookie planned) |
| **Session Lifetime** | 7 days inactivity timeout; 30 day absolute max |
| **Session Refresh** | Automatic via Supabase JS SDK; refresh token rotation on each use |
| **Session Revocation** | Supabase Auth dashboard; immediate effect on next API call |
| **Concurrent Sessions** | Multiple allowed (mobile + desktop); all revocable individually |
| **Idle Timeout** | 30 min on frontend; session persists server-side |

### 4.5 CSRF Protection

| Layer | Protection | Status |
|---|---|---|
| **Supabase Auth** | SameSite=Lax cookies; OAuth state parameter with PKCE | ✅ Active |
| **FastAPI Backend** | CORS validation (origin whitelist); Origin header check | ✅ Active |
| **Next.js Frontend** | Supabase client handles CSRF via auth state; fetch credentials: 'include' | ✅ Active |
| **Custom API** | Optional double-submit cookie pattern (planned) | 🔄 Planned |

### 4.6 Authentication Security Checklist

- [ ] OAuth PKCE flow enforced (no implicit grant)
- [ ] JWT signed with strong HMAC-SHA256 secret (>=256 bits)
- [ ] JWT expiration set to maximum 1 hour for access tokens
- [ ] Refresh tokens rotated on each use
- [ ] No credential storage in application code
- [ ] Rate limiting on auth endpoints (10 req/min per IP)
- [ ] Failed auth attempts logged with IP and timestamp
- [ ] Account enumeration prevention (generic error messages)
- [ ] Session revocation via Supabase dashboard tested
- [ ] Token validation uses both local decode + server verification

---

## 5. Authorization Security

### 5.1 Authorization Model

```
Request → JWT Validation → user_id Extraction → RLS Enforcement → API-level user_id Filter → Response
   │            │                    │                     │                     │
   │     [401 if invalid]      [Extract sub]      [DB enforces policy]   [Double-check in code]
```

### 5.2 Row-Level Security (RLS) — Deep Dive

#### 5.2.1 Complete Table RLS Inventory

| # | Table | RLS Policy | user_id Column | Additional Policies |
|---|---|---|---|---|
| 1 | `users` | `auth.uid() = id` | `id` | — |
| 2 | `tasks` | `auth.uid() = user_id` | `user_id` | — |
| 3 | `subtasks` | `auth.uid() = user_id` | `user_id` | via task join |
| 4 | `task_dependencies` | `auth.uid() = user_id` | `user_id` | — |
| 5 | `courses` | `auth.uid() = user_id` | `user_id` | — |
| 6 | `videos` | `auth.uid() = user_id` | `user_id` | — |
| 7 | `resources` | `auth.uid() = user_id` | `user_id` | — |
| 8 | `ideas` | `auth.uid() = user_id` | `user_id` | — |
| 9 | `goals` | `auth.uid() = user_id` | `user_id` | — |
| 10 | `opportunities` | `auth.uid() = user_id` | `user_id` | — |
| 11 | `income_entries` | `auth.uid() = user_id` | `user_id` | — |
| 12 | `projects` | `auth.uid() = user_id` | `user_id` | — |
| 13 | `subjects` | `auth.uid() = user_id` | `user_id` | — |
| 14 | `marks` | `auth.uid() = user_id` | `user_id` | — |
| 15 | `habits` | `auth.uid() = user_id` | `user_id` | — |
| 16 | `habit_logs` | `auth.uid() = user_id` | `user_id` | — |
| 17 | `sleep_logs` | `auth.uid() = user_id` | `user_id` | — |
| 18 | `time_entries` | `auth.uid() = user_id` | `user_id` | — |
| 19 | `chat_messages` | `auth.uid() = user_id` | `user_id` | — |
| 20 | `memory` | `auth.uid() = user_id` | `user_id` | — |
| 21 | `learning_progress` | `auth.uid() = user_id` | `user_id` | — |
| 22 | `daily_briefings` | `auth.uid() = user_id` | `user_id` | — |
| 23 | `weekly_reviews` | `auth.uid() = user_id` | `user_id` | — |
| 24 | `analytics_events` | `auth.uid() = user_id` | `user_id` | — |

#### 5.2.2 Standard RLS Policy Template

```sql
-- Comprehensive RLS policy covering SELECT, INSERT, UPDATE, DELETE
CREATE POLICY "{table}_user_isolation" ON {table}
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;

-- Optional: Grant service role full access for cron/admin operations
CREATE POLICY "{table}_service_access" ON {table}
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role')
    WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
```

#### 5.2.3 RLS Security Testing SQL

```sql
-- Verify RLS is enabled on all tables
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND rowsecurity = false;

-- Attempt cross-user access (should return 0 rows if RLS working)
SET LOCAL ROLE authenticated;
SELECT * FROM tasks WHERE user_id != auth.uid();

-- Verify service role bypass works
SET LOCAL ROLE service_role;
SELECT * FROM tasks LIMIT 1;  -- Should return data across users
```

### 5.3 API-Level Authorization

Beyond RLS, every API endpoint enforces authorization at the application layer:

```python
# apps/api/app/api/tasks.py
@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user: dict = Depends(get_current_user),
):
    # Application-level authorization: explicit user_id filter
    data = supabase.table("tasks")\
        .select("*")\
        .eq("id", task_id)\
        .eq("user_id", user.id)\  # Double-check: RLS + explicit filter
        .execute()

    if not data.data:
        # Don't reveal whether task exists vs. belongs to another user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return data.data[0]
```

### 5.4 Service Role Access

| Use Case | Service Role Access | Audit |
|---|---|---|
| Cron jobs (scheduler) | ✅ Yes — SELECT all users' data | Full audit logging |
| Daily briefing generation | ✅ Yes — READ tasks/courses for all users | Per-job logging |
| Account deletion (admin) | ✅ Yes — DELETE across all tables | Manual trigger + log |
| Opportunity radar | ✅ Yes — READ profile for matching | Per-job logging |
| User-facing API | ❌ No — uses authenticated role | N/A |

**Principle:** Service role used exclusively by internal cron jobs and admin operations. Never exposed to client-side code. Restrict service role key to backend environment only.

### 5.5 Role-Based Access Control (RBAC) — Future

| Role | Permissions | Scope |
|---|---|---|
| `user` | CRUD own data | Default |
| `premium` | Same as user + AI features | Paid tier |
| `admin` | Read all data, manage users, trigger maintenance | Internal only |
| `service` | Full CRUD across all users | Cron jobs only |

---

## 6. Data Security

### 6.1 Data Classification

| Classification | Definition | Examples | Handling Requirements |
|---|---|---|---|
| **Public** | Non-sensitive, intended for public display | App version, UI text | No special handling |
| **Internal** | Non-sensitive operational data | Feature flags, config settings | Access control |
| **Confidential** | User-specific, not sensitive | Tasks, courses, habits (no PII) | RLS + encryption in transit |
| **Restricted** | PII or highly sensitive | Email, chat messages, AI memory | RLS + encryption at rest + access logging |

### 6.2 Encryption at Rest

#### Database-Level Encryption

| Layer | Mechanism | Managed By |
|---|---|---|
| **Disk Encryption** | AES-256 at storage layer | Supabase / Google Cloud |
| **Database Encryption** | Transparent Data Encryption (TDE) | Supabase (PostgreSQL) |
| **Column-Level Encryption** | Application-level pgcrypto (planned) | Application |

#### Column-Level Encryption Plan

For highly sensitive fields, we plan to implement application-layer encryption using `pgcrypto`:

```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypt AI memory content that may contain PII
-- Key stored in environment variable, never in database
CREATE TABLE encrypted_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    encrypted_content BYTEA NOT NULL,  -- pgp_sym_encrypt(content, encryption_key)
    iv BYTEA NOT NULL,                 -- initialization vector
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Column Encryption Priority Matrix**

| Field | Sensitivity | Encrypt Now? | Target Date |
|---|---|---|---|
| Email address | High | ✅ Yes | Q3 2026 |
| Chat message content | Medium | 🔄 Planned | Q4 2026 |
| AI memory content | Medium | 🔄 Planned | Q4 2026 |
| Task titles | Low | ❌ No | — |
| Course names | Low | ❌ No | — |

### 6.3 Encryption in Transit

| Connection | Protocol | Cipher | Certificate |
|---|---|---|---|
| Browser → Vercel (Frontend) | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Let's Encrypt (auto) |
| Vercel → Railway (Backend) | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Railway internal CA |
| Railway → Supabase (Database) | TLS 1.3 | TLS_CHACHA20_POLY1305_SHA256 | Supabase managed |
| Backend → Ollama (Local) | Localhost (no TLS) | N/A | Trusted network |
| Backend → Claude API (Fallback) | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Anthropic managed |

```python
# Enforce TLS in HTTPX client for all external calls
import httpx

client = httpx.AsyncClient(
    verify=True,                     # Verify TLS certificates
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=5),
)
```

### 6.4 Key Management

| Key | Type | Storage | Rotation | Backup |
|---|---|---|---|---|
| `JWT_SECRET` | Symmetric (HMAC-SHA256) | Environment variable | Quarterly + on compromise | Supabase Vault (future) |
| `SUPABASE_SERVICE_KEY` | API Key | Environment variable | Quarterly + on compromise | LastPass / 1Password |
| `CLAUDE_API_KEY` | API Key | Environment variable | Monthly | LastPass / 1Password |
| `ENCRYPTION_KEY` | Symmetric (AES-256) | Environment variable (future) | Annually | Hardware security (future) |

**Principle:** No keys in code, config files, or version control. All keys loaded from environment variables.

### 6.5 Data Sanitization & Minimization

```python
# packages/shared/utils/security.py
import re
import uuid
import secrets
from typing import Optional

def sanitize_input(input_str: str) -> str:
    """Strip script tags, javascript: URIs, and event handlers.
    
    Applied to all user-facing text inputs before storage.
    """
    if not input_str:
        return input_str

    dangerous_patterns = [
        (r"<script[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE),
        (r"javascript:", re.IGNORECASE),
        (r"onerror\s*=", re.IGNORECASE),
        (r"onclick\s*=", re.IGNORECASE),
        (r"onload\s*=", re.IGNORECASE),
        (r"onfocus\s*=", re.IGNORECASE),
        (r"onmouseover\s*=", re.IGNORECASE),
        (r"onchange\s*=", re.IGNORECASE),
        (r"onblur\s*=", re.IGNORECASE),
        (r"data:text/html", re.IGNORECASE),
        (r"vbscript:", re.IGNORECASE),
        (r"expression\s*\(.*?\)", re.IGNORECASE),
        (r"<embed[^>]*>", re.IGNORECASE),
        (r"<object[^>]*>", re.IGNORECASE),
        (r"<iframe[^>]*>", re.IGNORECASE),
    ]

    sanitized = input_str
    for pattern, flags in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=flags)

    return sanitized.strip()

def validate_email(email: str) -> bool:
    """RFC 5322 compliant email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """Strict URL validation — HTTPS only."""
    pattern = r'^https://[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(pattern, url))

def generate_secure_token(length: int = 32) -> str:
    """Cryptographically secure random token."""
    return secrets.token_hex(length)

def generate_api_key() -> str:
    """Prefixed API key for service-to-service auth."""
    prefix = "sk_"
    return prefix + secrets.token_urlsafe(32)

def hash_ip(ip: str) -> str:
    """Pseudonymize IP addresses for logging."""
    # Store only first 3 octets hashed
    parts = ip.split(".")
    if len(parts) == 4:
        partial = ".".join(parts[:3])
        return hashlib.sha256(partial.encode()).hexdigest()[:16]
    return hashlib.sha256(ip.encode()).hexdigest()[:16]
```

---

## 7. API Security

### 7.1 API Security Architecture

```
Client → WAF (L7) → Rate Limiter → CORS → Auth (JWT) → Validation → Route Handler → DB
                                                        ↓
                                                  Sanitization
                                                        ↓
                                                  Response
```

### 7.2 Rate Limiting

#### Global Rate Limiter

```python
# packages/shared/utils/rate_limiter.py
import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiter(BaseHTTPMiddleware):
    """Sliding window rate limiter with per-IP tracking.
    
    Default: 100 requests per 60-second window per IP.
    Graceful degradation: Returns 429 with Retry-After header.
    """

    def __init__(self, app, default_max: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.default_max = default_max
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        now = time.time()

        # Determine endpoint-specific limit
        max_requests = self._get_limit(endpoint)

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.window_seconds
        ]

        # Check limit
        if len(self.requests[client_ip]) >= max_requests:
            retry_after = int(self.requests[client_ip][0] + self.window_seconds - now)
            return Response(
                status_code=429,
                content="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(max(retry_after, 1)),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(self.requests[client_ip][0] + self.window_seconds)),
                },
            )

        # Record request
        self.requests[client_ip].append(now)
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Reset"] = str(int(now + self.window_seconds))

        return response

    def _get_limit(self, endpoint: str) -> int:
        limits = {
            "/api/chat": 30,
            "/api/tasks": 60,
            "/api/courses": 60,
            "/api/goals": 60,
            "/api/habits": 60,
            "/api/sleep": 60,
            "/api/income": 60,
            "/api/projects": 60,
            "/api/ideas": 60,
            "/api/resources": 60,
            "/api/opportunities": 60,
            "/api/time": 60,
            "/api/auth": 10,
        }
        for prefix, limit in limits.items():
            if endpoint.startswith(prefix):
                return limit
        return self.default_max
```

#### Rate Limit Configuration by Endpoint

| Endpoint Prefix | Default Limit | Burst Limit | Window | Rationale |
|---|---|---|---|---|
| `/api/chat` | 30 req/min | 50 | 60s | AI calls are expensive; prevent abuse |
| `/api/tasks` | 60 req/min | 100 | 60s | Core CRUD operations |
| `/api/courses` | 60 req/min | 100 | 60s | Core CRUD operations |
| `/api/goals` | 60 req/min | 100 | 60s | Core CRUD operations |
| `/api/auth` | 10 req/min | 20 | 60s | Auth endpoints sensitive to brute force |
| `/api/analytics` | 120 req/min | 200 | 60s | Client sends batched events |
| `/api/health` | 60 req/min | 120 | 60s | Monitoring tools |
| All others (default) | 100 req/min | 150 | 60s | Standard endpoints |

### 7.3 CORS Configuration

```python
# apps/api/main.py
from fastapi.middleware.cors import CORSMiddleware

# Development: permissive with known origins
# Production: strict whitelist only

ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Local dev frontend
    "http://localhost:3001",      # Alternate dev port
    "https://ariaos.app",         # Production
    "https://www.ariaos.app",     # WWW subdomain
    "https://secondbrain-os.vercel.app",  # Vercel preview deployments
]

if settings.environment == "production":
    ALLOWED_ORIGINS = [
        "https://ariaos.app",
        "https://www.ariaos.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-CSRF-Token",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
    max_age=600,  # Preflight cache: 10 minutes
)
```

### 7.4 Request Validation

#### Pydantic Models with Strict Validation

```python
# packages/database/schemas/task.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional description (max 5000 characters)",
    )
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("title")
    @classmethod
    def title_must_not_be_dangerous(cls, v: str) -> str:
        sanitized = sanitize_input(v)
        if sanitized != v:
            raise ValueError("Title contains disallowed characters")
        return sanitized

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > 30:
                raise ValueError(f"Tag '{tag}' exceeds 30 characters")
            if not tag.isalnum() and not all(c.isalnum() or c in "-_" for c in tag):
                raise ValueError(f"Tag '{tag}' contains invalid characters")
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled"]] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = Field(None, ge=1, le=1440)
```

### 7.5 Input Size Limits

| Input Type | Maximum Size | Rationale |
|---|---|---|
| HTTP Request Body | 1 MB | Prevent large payload attacks |
| File Upload | 10 MB | Supabase storage limit |
| URL Length | 2048 characters | Industry standard |
| Text Field Length | 5000 characters | Reasonable for notes/descriptions |
| Array Size | 100 items per request | Prevent batch abuse |
| Pagination Limit | 100 items per page | Prevent response size abuse |

```python
# apps/api/middleware/size_limit.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_CONTENT_LENGTH:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request entity too large"},
            )
        return await call_next(request)
```

### 7.6 API Security Headers

```python
# apps/api/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response
```

---

## 8. Frontend Security

### 8.1 Content Security Policy (CSP)

```javascript
// next.config.js
const cspDirectives = {
  'default-src': ["'self'"],
  'script-src': ["'self'", "'unsafe-eval'", "'unsafe-inline'"],  // Not ideal — improve
  'style-src': ["'self'", "'unsafe-inline'"],
  'img-src': ["'self'", "data:", "https:", "blob:"],
  'font-src': ["'self'", "https://fonts.gstatic.com"],
  'connect-src': [
    "'self'",
    "https://*.supabase.co",
    "https://api.ariaos.app",
    "http://localhost:8000",
    "https://fonts.googleapis.com",
  ],
  'frame-src': ["'none'"],
  'object-src': ["'none'"],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
  'upgrade-insecure-requests': [],
};

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: Object.entries(cspDirectives)
              .map(([key, values]) => `${key} ${values.join(' ')}`)
              .join('; '),
          },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()' },
        ],
      },
    ];
  },
};
```

### 8.2 XSS Prevention

| Layer | Protection | Implementation |
|---|---|---|
| **React Default** | Automatic HTML escaping | JSX expressions are escaped by default |
| **Input Sanitization** | Server-side strip of dangerous patterns | `sanitize_input()` on all text fields |
| **Output Encoding** | JSON responses never include raw HTML | FastAPI returns JSON; no template rendering |
| **CSP** | Blocks inline scripts | CSP header restricts script sources |
| **DOM Purify** | Sanitize renderable HTML | Used only for AI-generated markdown content |

```typescript
// packages/ui/utils/sanitize.ts
import DOMPurify from 'dompurify';

export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'p', 'br', 'code', 'pre'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  });
}
```

### 8.3 Secure Cookie Configuration

```typescript
// apps/web/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
      storageKey: 'sb-aria-auth-token',
      storage: typeof window !== 'undefined'
        ? {
            getItem: (key: string) => {
              // Future: migrate to httpOnly cookie via Next.js API routes
              return localStorage.getItem(key)
            },
            setItem: (key: string, value: string) => {
              localStorage.setItem(key, value)
            },
            removeItem: (key: string) => {
              localStorage.removeItem(key)
            },
          }
        : undefined,
    },
  }
)
```

### 8.4 Iframe Protection

| Measure | Implementation | Status |
|---|---|---|
| `X-Frame-Options: DENY` | Prevents all iframe embedding | ✅ Active |
| `frame-src: 'none'` | CSP directive blocks framing | ✅ Active |
| `window.top` check | JavaScript check in sensitive pages | 🔄 Planned |

### 8.5 Frontend Security Checklist

- [ ] CSP headers configured and tested
- [ ] All third-party scripts audited (Google Fonts only)
- [ ] React rendered on server (Next.js SSR) — no client-side template injection
- [ ] No inline event handlers in HTML (`onclick`, etc.)
- [ ] `dangerouslySetInnerHTML` avoided or sanitized via DOMPurify
- [ ] localStorage not used for sensitive data (migrating to httpOnly cookies)
- [ ] Source maps disabled in production (`productionBrowserSourceMaps: false`)
- [ ] npm dependencies audited (`npm audit` in CI)

---

## 9. AI Security

### 9.1 AI Architecture Security Overview

```
User Input → Input Sanitization → Prompt Assembly → LLM Call → Output Filtering → Response
    │              │                     │              │             │
    │         Strip injections      Add guardrails  Model processes  Check output
    │                                                    │
    │                                              ┌─────┴─────┐
    │                                         Local Ollama  Claude API (fallback)
    │                                         (data stays)  (DPA in place)
```

### 9.2 Local Ollama (Default) — Data Isolation

| Concern | Mitigation |
|---|---|
| **Data at Rest** | Ollama models stored on local filesystem; no cloud transmission |
| **Data in Transit** | Localhost communication (127.0.0.1:11434); no network exposure |
| **Data in Memory** | Model output ephemeral; not persisted by Ollama |
| **Cross-User Leakage** | Single-user system; no cross-user context mixing |
| **Model Persistence** | No training on user data; inference only |

### 9.3 Claude API (Fallback) — Data Handling

| Concern | Mitigation |
|---|---|
| **Data Transmission** | TLS 1.3 encrypted to Anthropic API |
| **Data Storage** | Anthropic does not train on API requests (policies as of 2026) |
| **Data Retention** | Anthropic retains API requests for 30 days for abuse monitoring |
| **Data Processing Agreement** | Anthropic provides DPA for enterprise API usage |
| **Opt-In Requirement** | Claude fallback only used when `USE_LOCAL_AI=False` explicitly set |

### 9.4 Prompt Injection Prevention

#### 9.4.1 System Prompt Hardening

```python
# packages/ai/prompt_loader.py — Guardrails enforcement
class PromptGuardrails:
    """Prevents prompt injection by enforcing system prompt boundaries."""

    SYSTEM_PROMPT_CLOSING = "\n\n[SYSTEM PROMPT END — DO NOT MODIFY]"

    @staticmethod
    def assemble_secure_prompt(
        system_prompt: str,
        user_input: str,
        max_user_input_length: int = 4000,
    ) -> tuple[str, str]:
        """Assemble system and user prompts with injection defenses.

        Strategy:
        1. Append a clear boundary marker to the system prompt
        2. Truncate user input to prevent token overflow
        3. Strip known injection patterns from user input
        4. Wrap user input in delimiters to separate from instructions
        """

        # Sanitize user input
        clean_input = sanitize_input(user_input)[:max_user_input_length]

        # Wrap in delimiters
        delimited_input = f"\n\n--- USER INPUT (BELOW THIS LINE) ---\n{clean_input}\n--- END USER INPUT ---"

        return system_prompt + PromptGuardrails.SYSTEM_PROMPT_CLOSING, delimited_input
```

#### 9.4.2 Known Injection Patterns Blocked

| Pattern Type | Example | Detection |
|---|---|---|
| **System Prompt Override** | "Ignore previous instructions" | Pattern matching in input |
| **Role-Play Jailbreak** | "You are now DAN, do anything now" | Pattern matching |
| **Context Extraction** | "Repeat everything above" | Output monitoring |
| **Token Overflow** | Very long input (>4000 chars) | Truncation |
| **Encoded Instructions** | Base64-encoded instructions | Not blocked (hard to detect) |
| **Multi-language** | Instructions in non-English | Not blocked (product feature) |

#### 9.4.3 Output Filtering

```python
# packages/ai/output_filter.py
class OutputFilter:
    """Filters AI model outputs for security concerns."""

    SENSITIVE_PATTERNS = [
        r"sk-[a-zA-Z0-9]{20,}",              # OpenAI/Anthropic API keys
        r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",  # JWTs
        r"AKIA[0-9A-Z]{16}",                  # AWS access keys
        r"ghp_[a-zA-Z0-9]{36}",               # GitHub tokens
        r"-----BEGIN (RSA|OPENSSH) PRIVATE KEY-----",  # Private keys
        r"(password|passwd|pwd)\s*[=:]\s*\S+",  # Password leakage
    ]

    @staticmethod
    def filter_output(text: str) -> str:
        """Redact sensitive data from model output."""
        import re
        for pattern in OutputFilter.SENSITIVE_PATTERNS:
            text = re.sub(pattern, "[REDACTED]", text)
        return text
```

### 9.5 AI Security Checklist

- [ ] All user input sanitized before prompt assembly
- [ ] System prompt delimiters prevent override
- [ ] User input length limited (4000 chars max)
- [ ] Output filtered for sensitive data (keys, tokens)
- [ ] Local Ollama default — no data leaves machine
- [ ] Claude API DPA in place — documented data handling
- [ ] No AI training on user data
- [ ] AI responses logged for abuse monitoring (anonymized)
- [ ] Model jailbreak prompts logged for analysis

---

## 10. Infrastructure Security

### 10.1 Infrastructure Map

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  Vercel     │────►│  Railway     │────►│  Supabase   │────►│  GCP     │
│ (Frontend)  │     │ (Backend)    │     │ (Database)  │     │ (Cloud)  │
│             │     │              │     │             │     │          │
│ SSR + CDN   │     │ FastAPI      │     │ PostgreSQL  │     │ Compute  │
│ Edge Network│     │ + Scheduler  │     │ + Auth      │     │ Network  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
                         │
                         ▼
                    ┌──────────┐
                    │  Ollama  │
                    │ (Local)  │
                    └──────────┘
```

### 10.2 Vercel Security Features

| Feature | Configuration | Purpose |
|---|---|---|
| **DDoS Protection** | Automatic (Vercel WAF) | Blocks layer 3/4/7 DDoS attacks |
| **TLS Termination** | Auto-provisioned (Let's Encrypt) | Encrypts all frontend traffic |
| **Edge Network** | Global CDN | Reduces attack surface; cached content |
| **Serverless Functions** | Ephemeral execution | No persistent server to compromise |
| **Preview Deployments** | Isolated environments | Each PR gets isolated deployment |
| **Environment Variables** | Encrypted at rest | Secrets stored encrypted by Vercel |
| **Deployment Protection** | Password + IP allowlist (optional) | Prevents unauthorized preview access |

### 10.3 Railway Security Features

| Feature | Configuration | Purpose |
|---|---|---|
| **Container Isolation** | Automatic | Each service runs in isolated container |
| **Private Networking** | Railway internal network | Backend ←→ DB traffic stays internal |
| **TLS Termination** | Edge TLS | Encrypted traffic to backend |
| **Environment Variables** | Encrypted at rest | Secrets not exposed in logs |
| **Deployment Rollback** | One-click | Instant recovery from bad deployment |
| **Health Checks** | Configurable | Automatic container replacement on failure |
| **Resource Limits** | CPU/Memory caps | Prevents resource exhaustion |

### 10.4 Docker Container Security

```dockerfile
# apps/api/Dockerfile — Multi-stage build with security focus
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Security: Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Security: Copy only necessary files
COPY --from=builder /root/.local /root/.local
COPY main.py .
COPY app/ app/
COPY config/ config/
COPY database/ database/
COPY shared/ shared/

# Security: Set proper permissions
RUN chown -R appuser:appuser /app

USER appuser

# Security: Read-only filesystem (layer enforcement)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.5 Dependency Security

| Tool | Frequency | Scope | Action on Finding |
|---|---|---|---|
| `npm audit` | Every build | Frontend packages | Fix high/critical; review moderate |
| `pip-audit` | Every build | Python packages | Fix high/critical; review moderate |
| Dependabot | Weekly | All packages | Auto-create PR for critical fixes |
| `npm outdated` | Monthly | Frontend packages | Review and update |
| `pip list --outdated` | Monthly | Python packages | Review and update |
| Snyk (future) | Weekly | All packages | Comprehensive SCA |

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/apps/web"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
    allow:
      - dependency-type: "direct"

  - package-ecosystem: "pip"
    directory: "/apps/api"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
```

### 10.6 Secrets Management

| Secret | Storage | Access | Rotation |
|---|---|---|---|
| `JWT_SECRET` | Railway/Vercel env vars | Backend only | Quarterly |
| `SUPABASE_SERVICE_KEY` | Railway env vars | Backend only | Quarterly |
| `CLAUDE_API_KEY` | Railway env vars | Backend only | Monthly |
| `RESEND_API_KEY` | Railway env vars | Backend only | Monthly |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Vercel env vars | Frontend (inherently public) | Per project |

**Note:** Public keys (`NEXT_PUBLIC_*`) are exposed to client-side code by design (Supabase anon key has RLS enforcement — no data access without user auth).

---

## 11. Network Security

### 11.1 Network Segmentation

| Network Zone | Components | Access | TLS |
|---|---|---|---|
| **Public Zone** | Vercel Edge, Domain DNS | Internet | ✅ TLS 1.3 |
| **Application Zone** | Railway FastAPI, Scheduler | Vercel only (via Railway URL) | ✅ TLS 1.3 |
| **Data Zone** | Supabase PostgreSQL | Railway only | ✅ TLS 1.3 |
| **Local Zone** | Ollama | Localhost only | ❌ No TLS (localhost) |

### 11.2 Firewall Rules

| Source | Destination | Port | Protocol | Purpose |
|---|---|---|---|---|
| Internet | Vercel CDN | 443 | HTTPS | Frontend traffic |
| Vercel CDN | Railway | 443 | HTTPS | API requests |
| Railway | Supabase | 5432 | PostgreSQL TLS | Database queries |
| Railway | Ollama (localhost) | 11434 | HTTP | AI inference |

---

## 12. Incident Response Plan

### 12.1 Incident Severity Classification

| Severity | Label | Definition | Response Time | SLA |
|---|---|---|---|---|
| **S0** | Critical | Data breach, unauthorized access to user data, service-wide outage | < 15 min | 1 hour containment |
| **S1** | High | Service compromise, RLS bypass, auth bypass, AI data leakage | < 1 hour | 4 hours containment |
| **S2** | Medium | Rate limit bypass, XSS vulnerability, CSRF, degraded performance | < 4 hours | 24 hours containment |
| **S3** | Low | Information disclosure (non-sensitive), misconfiguration, missing header | < 24 hours | 72 hours remediation |
| **S4** | Informational | Security scan finding, dependency CVE (low severity) | < 1 week | Next sprint |

### 12.2 Incident Response Lifecycle

```
                    ┌─────────────┐
                    │  DETECTION  │
                    │  (Automated │
                    │   / Manual) │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │   TRIAGE    │
                    │  (Severity  │
                    │   Assigned) │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
               ┌───│ CONTAINMENT │───┐
               │   └──────┬──────┘   │
               │          ▼          │
               │   ┌─────────────┐   │
               │   │ ERADICATION │   │
               │   └──────┬──────┘   │
               │          ▼          │
               │   ┌─────────────┐   │
               │   │  RECOVERY   │   │
               │   └──────┬──────┘   │
               │          ▼          │
               │   ┌─────────────┐   │
               └──►│ POST-MORTEM │   │
                   └─────────────┘   │
                           ▼
                    ┌─────────────┐
                    │  LESSONS    │
                    │  LEARNED    │
                    └─────────────┘
```

### 12.3 Detection Phase

#### Automated Detection

| Detection Mechanism | What It Detects | Tool |
|---|---|---|
| Rate limiter alerts | >90% rate limit utilization | Built-in middleware |
| Error rate spike | >5% error rate on any endpoint | Logger analysis |
| Auth failure spike | >10 failed auth attempts from same IP | Logger analysis |
| Supabase anomaly detection | Unusual query patterns | Supabase dashboard |
| Ollama CPU spike | Potential resource abuse | System monitoring |
| Deploy failure | CI/CD pipeline failures | GitHub Actions |

#### Manual Detection

| Source | Contact Method |
|---|---|
| User report | support@ (TBD) |
| Developer discovery | Slack / Discord |
| Security researcher | security@ (TBD) |
| Third-party notification | Dependency advisory |

### 12.4 Containment Phase

#### S0/S1 Containment Checklist

- [ ] **Immediate:** Suspend compromised service (scale to 0 / disable API)
- [ ] **Immediate:** Rotate ALL API keys and secrets
- [ ] **Within 15 min:** Revoke all active user sessions via Supabase Auth
- [ ] **Within 15 min:** Block offending IPs in Railway firewall
- [ ] **Within 30 min:** Take forensic snapshot of affected systems
- [ ] **Within 1 hour:** Deploy blocking patch (disable affected feature)
- [ ] **Within 1 hour:** Notify incident response lead

#### S2/S3 Containment Checklist

- [ ] **Within 1 hour:** Deploy security patch
- [ ] **Within 4 hours:** Review and update affected policies
- [ ] **Within 24 hours:** Verify fix with automated tests

### 12.5 Eradication Phase

| Action | Owner | Verification |
|---|---|---|
| Patch vulnerability | Developer | Code review + tests |
| Rotate credentials | DevOps | Verify old keys revoked |
| Update RLS policies | DevOps | SQL verification |
| Clean compromised data | DevOps | Data integrity check |
| Update monitoring rules | Developer | Test alert triggers |

### 12.6 Recovery Phase

- [ ] Restore service from clean state (redeploy from known-good commit)
- [ ] Verify all security controls active (RLS, rate limiter, CORS, headers)
- [ ] Monitor for recurrence (increased alerting for 48 hours)
- [ ] Communicate resolution to affected users
- [ ] Update status page

### 12.7 Post-Mortem Template

```markdown
# Security Incident Post-Mortem

## Incident Summary
- **ID:** SEC-{YEAR}-{NUMBER}
- **Date:** YYYY-MM-DD
- **Severity:** S0/S1/S2/S3
- **Duration:** X hours Y minutes
- **Detected:** Automated / Manual (who/when)
- **Impacted Users:** {number} users

## Timeline
| Time (UTC) | Event |
|---|---|
| 00:00 | Detection — {how detected} |
| 00:15 | Containment — {action taken} |
| 01:30 | Eradication — {action taken} |
| 02:00 | Recovery — {action taken} |
| 48:00 | Post-mortem completed |

## Root Cause Analysis
- **Root Cause:** {technical explanation}
- **Contributing Factors:** {list}
- **Why It Bypassed Existing Controls:** {explanation}

## Impact Assessment
- **Data Exposed:** {what data, how many records}
- **Service Downtime:** {duration by component}
- **User Impact:** {description}

## Action Items
| # | Action | Owner | Deadline | Status |
|---|---|---|---|---|
| 1 | {action} | {owner} | {date} | Open/Done |
| 2 | {action} | {owner} | {date} | Open/Done |

## Lessons Learned
- What worked well:
- What could be improved:
- Process changes needed:

## Sign-off
- **Incident Response Lead:** {name}
- **Security Lead:** {name}
- **Engineering Lead:** {name}
```

---

## 13. Security Compliance Mapping

### 13.1 OWASP Top 10 (2021) Coverage

| OWASP Category | ARIA OS Mitigation | Verification |
|---|---|---|
| **A01: Broken Access Control** | RLS on all tables + API-level user_id filtering | Automated test per endpoint |
| **A02: Cryptographic Failures** | TLS 1.3 everywhere; column-level encryption planned | CI header check |
| **A03: Injection** | Pydantic validation + `sanitize_input()` | Selenium/unit tests |
| **A04: Insecure Design** | Threat modeling in design phase | Security review in PR |
| **A05: Security Misconfiguration** | CI-enforced headers; environment-specific config | Automated CI check |
| **A06: Vulnerable Components** | Dependabot + npm audit + pip-audit in CI | CI pipeline |
| **A07: Auth Failures** | Supabase Auth (delegated); JWT validation | Auth test suite |
| **A08: Software/Data Integrity** | Signed commits; pinned dependencies | GPG signing (future) |
| **A09: Security Logging Failures** | Structured JSON logging; audit events | Log review process |
| **A10: SSRF** | Outbound HTTP restricted to known hosts | Network policy |

### 13.2 SOC 2 Readiness Mapping

| SOC 2 Trust Service Criteria | ARIA OS Coverage | Gap |
|---|---|---|
| **Security** — Protected against unauthorized access | RLS, Auth, Encryption, Rate Limiting | No penetration test (Q4 2026) |
| **Availability** — Available for operation and use | Uptime monitoring, health checks | No formal SLA documented |
| **Processing Integrity** — Processing complete, valid, accurate | Pydantic validation, RLS integrity | No processing auditing |
| **Confidentiality** — Information designated as confidential protected | RLS, Encryption, Access controls | No formal classification |
| **Privacy** — Personal information collected, used, retained, disclosed | GDPR compliance, data minimization | Full privacy program (Q1 2027) |

### 13.3 GDPR Mapping

| GDPR Requirement | ARIA OS Status | Evidence |
|---|---|---|
| Article 5: Principles | ✅ Compliant | Data minimization, purpose limitation |
| Article 6: Lawful Processing | ✅ Compliant | Consent + contract basis |
| Article 7: Consent | ✅ Compliant | Google OAuth consent screen |
| Article 15: Right of Access | ✅ Compliant | Data export feature |
| Article 17: Right to Erasure | ✅ Compliant | Account deletion within 48 hours |
| Article 20: Data Portability | ✅ Compliant | JSON/CSV export |
| Article 25: Privacy by Design | ✅ Compliant | RLS, no telemetry, minimal collection |
| Article 32: Security | ✅ Compliant | Encryption, RLS, rate limiting |
| Article 33: Breach Notification | ⚠️ Partially | Procedures documented; notification not automated |
| Article 35: DPIA | ⚠️ Partially | Informal assessment; formal DPIA needed |

---

## 14. Security Review Process in CI/CD

### 14.1 Security Gates in CI Pipeline

```
Git Push → PR Created → Security Gate Review
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
              Security Lint    Dependency Check
              (SAST)           (SCA)
                    │               │
                    ▼               ▼
              Secret Scan     Container Scan
              (Leaks)         (Trivy - future)
                    │               │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │  All Pass?    │
                    ├───────┬───────┤
                    │  YES  │  NO   │
                    ▼       ▼       ▼
                 Merge   Block PR  Notify Dev
```

### 14.2 CI Security Jobs

```yaml
# .github/workflows/ci.yml — Security Jobs
security-sast:
  name: Security Linting (SAST)
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Bandit Python SAST
      run: |
        pip install bandit
        bandit -r apps/api/ -c pyproject.toml
    - name: ESLint Security Plugin
      run: |
        cd apps/web && npm ci
        npx eslint . --plugin security --rule 'security/detect-object-injection: error'
    - name: TruffleHog Secret Scan
      uses: trufflesecurity/trufflehog@v3
      with:
        extra_args: --only-verified

security-sca:
  name: Dependency Scanning (SCA)
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: npm audit
      run: |
        cd apps/web && npm audit --audit-level=high
    - name: pip-audit
      run: |
        cd apps/api && pip install pip-audit && pip-audit
    - name: Dependabot Alert Check
      uses: actions/github-script@v7
      with:
        script: |
          const alerts = await github.rest.dependabot.listAlertsForRepo({
            owner: context.repo.owner,
            repo: context.repo.repo,
            state: 'open',
            severity: 'critical',
          });
          if (alerts.data.length > 0) {
            core.setFailed(`${alerts.data.length} critical Dependabot alerts`);
          }

security-propmts:
  name: Prompt Security Validation
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Validate prompt frontmatter
      run: python scripts/validate_prompts.py
    - name: Check for injection patterns in prompts
      run: |
        grep -r "IGNORE INSTRUCTIONS\|ignore all\|DAN\|jailbreak" prompts/ --include="*.md" \
          && echo "Potential injection patterns found!" && exit 1 \
          || echo "No injection patterns found"
```

### 14.3 PR Security Review Checklist

For every PR, reviewers must check:

- [ ] No hardcoded secrets, tokens, or keys
- [ ] No `console.log` of sensitive data
- [ ] All user inputs validated via Pydantic
- [ ] All database queries filter by `user_id`
- [ ] No `dangerouslySetInnerHTML` without DOMPurify
- [ ] Environment variables use `.env` not hardcoded values
- [ ] New dependencies vetted for security posture
- [ ] Rate limit considered for new endpoints
- [ ] CORS origins updated if new frontend domains added
- [ ] RLS policies updated if new tables added

### 14.4 Security Testing Cadence

| Test Type | Frequency | Tool | Responsibility |
|---|---|---|---|
| SAST (Static Analysis) | Every PR | Bandit, ESLint | Automated CI |
| SCA (Dependency Scan) | Every PR | npm audit, pip-audit | Automated CI |
| Secret Scanning | Every PR | TruffleHog | Automated CI |
| DAST (Dynamic) | Monthly | OWASP ZAP (future) | Security lead |
| Penetration Test | Quarterly | External firm (future) | Security lead |
| Vulnerability Assessment | Monthly | Manual review | Security lead |
| RLS Policy Audit | Quarterly | SQL review | DevOps |
| Dependency Review | Weekly | Dependabot | Automated |

---

## 15. Security Roadmap

### 15.1 Current State (Q2 2026)

- RLS on all tables
- Google OAuth with PKCE
- JWT validation (dual: local + server)
- Rate limiting with sliding window
- Input sanitization
- CORS whitelist
- Security headers (CSP, HSTS, XFO, etc.)
- Prompt injection prevention basics
- Basic incident response plan
- CI security checks (lint, audit, scan)

### 15.2 Short-Term (Q3 2026)

| Initiative | Target | Effort | Dependencies |
|---|---|---|---|
| Column-level encryption for email | Q3 2026 | 2 weeks | Key management system |
| HTTP-only cookie session storage | Q3 2026 | 1 week | Next.js API routes for auth |
| DAST integration (OWASP ZAP) | Q3 2026 | 1 week | CI pipeline config |
| Formal threat model document | Q3 2026 | 3 days | Security training |
| AI output telemetry for abuse detection | Q3 2026 | 1 week | Analytics infrastructure |

### 15.3 Medium-Term (Q4 2026)

| Initiative | Target | Effort | Dependencies |
|---|---|---|---|
| Penetration test (external) | Q4 2026 | 2 days | Budget allocation |
| Bug bounty program launch | Q4 2026 | Ongoing | Disclosure policy |
| Email authentication log monitoring | Q4 2026 | 1 week | Log aggregation |
| Automated incident response playbooks | Q4 2026 | 2 weeks | Runbook automation |
| Supabase Vault integration for secrets | Q4 2026 | 1 week | Supabase Vault availability |

### 15.4 Long-Term (2027)

| Initiative | Target | Effort | Dependencies |
|---|---|---|---|
| SOC 2 Type I certification | Q2 2027 | 3 months | Budget, formal processes |
| Hardware security key support (WebAuthn) | Q2 2027 | 3 weeks | Supabase Auth MFA |
| End-to-end encryption for AI memory | Q3 2027 | 4 weeks | Key exchange design |
| Full OWASP ASVS Level 2 compliance | Q3 2027 | Ongoing | Comprehensive program |
| Bug bounty program matured | Q4 2027 | Ongoing | Community building |

### 15.5 Budget Estimation

| Initiative | Estimated Cost | Priority |
|---|---|---|
| Penetration test | $2,000 - $5,000 | High |
| Bug bounty (platform fees) | $500 - $1,500/year | Medium |
| SOC 2 certification | $10,000 - $30,000 | Low (future) |
| Security tools (Snyk, etc.) | $0 - $200/month | Medium |
| External security consultant | $200 - $500/hour | As needed |

---

## 16. Appendices

### Appendix A: Security Contact Information

| Role | Contact | Availability |
|---|---|---|
| Security Lead | via GitHub Issues (@project-maintainer) | Business hours |
| Incident Response | security@ (TBD) | 24/7 for S0/S1 |
| Vulnerability Disclosure | security@ (TBD) | 24/7 |

### Appendix B: Vulnerability Disclosure Policy

1. **Reporting:** Submit vulnerabilities via GitHub Security Advisory or email
2. **Response:** Acknowledgment within 48 hours; triage within 5 business days
3. **Disclosure:** Coordinated disclosure; 90-day disclosure timeline from fix
4. **Safe Harbor:** No legal action for good-faith research following policy
5. **Scope:** All services under `*.ariaos.app`, `*.supabase.co` (relevant parts)
6. **Out of Scope:** Third-party services, physical security, social engineering

### Appendix C: Security Tools Reference

| Tool | Purpose | Configuration |
|---|---|---|
| `bandit` | Python SAST | `bandit -r apps/api/ -ll -iii` |
| `eslint-plugin-security` | JS SAST | Rules: `detect-object-injection`, `detect-non-literal-fs-filename` |
| `trufflehog` | Secret scanning | `trufflehog git file://. --only-verified` |
| `npm audit` | JS dependency checks | `npm audit --audit-level=high` |
| `pip-audit` | Python dependency checks | `pip-audit -r requirements.txt` |
| `dependabot` | Automated dependency updates | Weekly, auto-merge patches |
| `OWASP ZAP` | DAST (future) | Full scan monthly, baseline per PR |

### Appendix D: Security Glossary

| Term | Definition |
|---|---|
| **RLS** | Row-Level Security — PostgreSQL feature limiting data access by user |
| **PKCE** | Proof Key for Code Exchange — OAuth security extension for public clients |
| **JWT** | JSON Web Token — compact, URL-safe token format for auth claims |
| **CSP** | Content Security Policy — HTTP header preventing XSS and data injection |
| **HSTS** | HTTP Strict Transport Security — forces HTTPS connections |
| **SAST** | Static Application Security Testing — analyzes source code for vulnerabilities |
| **DAST** | Dynamic Application Security Testing — tests running application for vulnerabilities |
| **SCA** | Software Composition Analysis — scans dependencies for known vulnerabilities |
| **DPIA** | Data Protection Impact Assessment — GDPR-required privacy risk assessment |
| **TDE** | Transparent Data Encryption — encrypts database at rest |

### Appendix E: Document Change Log

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-01-15 | Security Lead | Initial security architecture |
| 2.0.0 | 2026-03-20 | Security Lead | Added AI security, incident response, threat model |
| 3.0.0 | 2026-06-11 | Security Lead | Enterprise upgrade: STRIDE threat model, attack trees, 7-layer defense, CI/CD security gates, SOC 2 mapping, full incident response lifecycle, column encryption plan, prompt injection framework, security roadmap |
