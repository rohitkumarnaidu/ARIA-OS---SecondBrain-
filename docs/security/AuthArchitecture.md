# Authentication Architecture — Second Brain OS (ARIA OS)

## Document Control

| Property | Details |
|---|---|
| **Document ID** | SEC-AUTH-001 |
| **Version** | 1.0 |
| **Status** | Active |
| **Classification** | Internal — Engineering Team |
| **Last Updated** | 2026-06-11 |
| **Next Review** | 2026-09-11 |
| **Standards** | OAuth 2.0, OpenID Connect, OWASP ASVS V2/V3 |

---

## Table of Contents

1. [Authentication Flow Overview](#1-authentication-flow-overview)
2. [Sign-In Flow](#2-sign-in-flow)
3. [Sign-Out Flow](#3-sign-out-flow)
4. [Session Management](#4-session-management)
5. [JWT Payload Schema & Validation](#5-jwt-payload-schema--validation)
6. [Token Validation Middleware](#6-token-validation-middleware)
7. [Role-Based Access Control](#7-role-based-access-control)
8. [Multi-Device Session Handling](#8-multi-device-session-handling)
9. [OAuth Scopes & Permissions](#9-oauth-scopes--permissions)
10. [Supabase Auth Integration](#10-supabase-auth-integration)
11. [Security Headers](#11-security-headers)
12. [Rate Limiting on Auth Endpoints](#12-rate-limiting-on-auth-endpoints)
13. [Brute Force Protection](#13-brute-force-protection)
14. [MFA Roadmap](#14-mfa-roadmap)
15. [Auth Testing Scenarios](#15-auth-testing-scenarios)
16. [Appendix: Code Reference](#16-appendix-code-reference)

---

## 1. Authentication Flow Overview

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Second Brain OS Auth Flow                      │
│                                                                       │
│  Browser                          Backend (FastAPI)    Supabase Auth  │
│    │                                    │                    │        │
│    │ 1. Click "Sign in with Google"     │                    │        │
│    │───────────────────────────────────────────────────────→│        │
│    │                                    │                    │        │
│    │ 2. Redirect to Google OAuth        │                    │        │
│    │←───────────────────────────────────────────────────────│        │
│    │                                    │                    │        │
│    │ 3. Google consent screen           │                    │        │
│    │──→                                 │                    │        │
│    │    │                                │                    │        │
│    │ 4. Auth code callback (PKCE)       │                    │        │
│    │───────────────────────────────────────────────────────→│        │
│    │                                    │                    │        │
│    │ 5. Exchange code for tokens        │                    │        │
│    │                                    │                    │──→     │
│    │ 6. JWT issued                      │                    │←──     │
│    │←───────────────────────────────────────────────────────│        │
│    │                                    │                    │        │
│    │ 7. API request with JWT            │                    │        │
│    │───────────────────────────────────→│                    │        │
│    │                                    │                    │        │
│    │ 8. Validate JWT                    │                    │        │
│    │                                    │───────────────────→│        │
│    │ 9. Return user data                │                    │        │
│    │←───────────────────────────────────│                    │        │
│    │                                    │                    │        │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth Provider | Supabase Auth | Delegates complexity; built-in RLS integration; social login |
| OAuth Provider | Google (primary) | Highest user adoption; security-hardened; MFA built-in |
| Token Format | JWT (JSON Web Token) | Industry standard; stateless; self-contained |
| Signing Algorithm | HS256 | Simple; sufficient for single-service backend |
| Token Transport | Bearer in Authorization header | Standard; avoids CSRF on cookie-based auth |
| Session Storage | HTTP-only cookie | Prevents XSS token theft |
| Refresh Mechanism | Supabase auto-refresh | No manual refresh token handling |
| Password Storage | N/A (OAuth only) | No passwords stored; eliminates hashing risk |

---

## 2. Sign-In Flow

### 2.1 Step-by-Step Sequence

```
Step 1: User clicks "Sign In with Google"
──────────────────────────────────────────
Frontend calls:
  supabase.auth.signInWithOAuth({ provider: 'google' })

Step 2: Redirect to Google OAuth consent
──────────────────────────────────────────
Supabase Auth constructs OAuth URL with:
  - client_id: Supabase OAuth app ID
  - redirect_uri: {supabase_url}/auth/v1/callback
  - response_type: code
  - scope: openid email profile
  - state: random anti-CSRF token
  - code_challenge: SHA-256 hash of code_verifier (PKCE)

Step 3: User consents on Google
──────────────────────────────────────────
User grants: email address, display name, profile photo.
Google generates authorization code.

Step 4: Authorization code callback
──────────────────────────────────────────
Google redirects to:
  {supabase_url}/auth/v1/callback?code=AUTH_CODE&state=STATE_TOKEN

Step 5: Exchange code for session
──────────────────────────────────────────
Supabase Auth exchanges authorization code for:
  - access_token (JWT): Short-lived (1 hour default)
  - refresh_token: Long-lived (for token rotation)
  - provider_token: Google OAuth access token

Step 6: JWT issued to client
──────────────────────────────────────────
Supabase returns JWT via redirect with:
  - Fragment parameters (#access_token=...&refresh_token=...)
  - URL is cleared of fragments immediately via postMessage
  - Session stored in HTTP-only cookie
  - Client now has authenticated session

Step 7: API calls use JWT
──────────────────────────────────────────
Frontend includes JWT in Authorization:
  Authorization: Bearer <jwt>

Backend validates JWT via Supabase Auth:
  GET {supabase_url}/auth/v1/user
  Headers: Authorization: Bearer <jwt>
```

### 2.2 Frontend Implementation

```typescript
// apps/web/lib/auth.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      },
    },
  })
  if (error) throw error
  return data
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

export async function getSession() {
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error) throw error
  return session
}
```

### 2.3 Auth Callback Handler

```typescript
// apps/web/app/auth/callback/route.ts
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  if (code) {
    const supabase = createRouteHandlerClient({ cookies })
    await supabase.auth.exchangeCodeForSession(code)
  }

  return NextResponse.redirect(new URL('/dashboard', request.url))
}
```

### 2.4 Session Listener

```typescript
// apps/web/components/providers/session-provider.tsx
'use client'
import { createClient } from '@supabase/supabase-js'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === 'SIGNED_OUT') {
          router.push('/login')
        }
        if (event === 'TOKEN_REFRESHED') {
          // Session refreshed; no action needed
          console.debug('[Auth] Token refreshed')
        }
      }
    )

    return () => subscription.unsubscribe()
  }, [router, supabase.auth])

  return <>{children}</>
}
```

### 2.5 Authentication Redirection

```typescript
// apps/web/middleware.ts
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })

  const { data: { session } } = await supabase.auth.getSession()

  // Protected routes require session
  const protectedPaths = [
    '/dashboard', '/tasks', '/courses', '/goals',
    '/habits', '/sleep', '/income', '/ideas',
    '/projects', '/resources', '/opportunities',
    '/chat', '/time', '/automation',
  ]

  const isProtected = protectedPaths.some(path =>
    req.nextUrl.pathname.startsWith(path)
  )

  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  // Already authenticated users skip login
  if (req.nextUrl.pathname === '/login' && session) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return res
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

---

## 3. Sign-Out Flow

### 3.1 Sign-Out Sequence

```
Step 1: User clicks "Sign Out"
────────────────────────────────
Frontend calls: supabase.auth.signOut()

Step 2: Clear local session
────────────────────────────────
Supabase client:
  - Clears access_token from memory
  - Clears refresh_token from storage
  - Revokes session on Supabase Auth server

Step 3: Post-sign-out redirect
────────────────────────────────
Frontend redirects to /login
Middleware detects no session, allows access to /login

Step 4: Token invalidation
────────────────────────────────
Supabase Auth marks session as revoked:
  - Access token no longer valid
  - Refresh token cannot be used for rotation
  - Any open subscriptions are closed
  - RLS policies block access with revoked token
```

### 3.2 Full Sign-Out Implementation

```typescript
// apps/web/app/auth/signout/route.ts
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function POST() {
  const supabase = createRouteHandlerClient({ cookies })

  // Sign out from Supabase Auth
  const { error } = await supabase.auth.signOut()

  // Clear all auth cookies
  const response = NextResponse.redirect(new URL('/login', request.url))
  response.cookies.set('sb-access-token', '', { maxAge: 0 })
  response.cookies.set('sb-refresh-token', '', { maxAge: 0 })

  if (error) {
    console.error('[Auth] Sign-out failed:', error)
    // Still redirect to login even on error (best-effort cleanup)
  }

  return response
}
```

### 3.3 Sign-Out Edge Cases

| Scenario | Behavior | Implementation |
|----------|----------|---------------|
| User closes tab without signing out | Session remains valid (7-day expiry) | Automatic cleanup via middleware |
| Network failure during sign-out | Frontend clears local session; server session persists until expiry | Logout button always cleans up locally first |
| Token already expired | signOut() succeeds immediately | No server call needed for expired tokens |
| Multiple tabs open | Only current tab triggers sign-out; other tabs detect via session listener onAuthStateChange event | SessionProvider handles cross-tab sync |

---

## 4. Session Management

### 4.1 Session Lifecycle

```
User Sign-In
    │
    ▼
┌──────────────────────────────┐
│   Access Token (JWT)        │  ← Expires: 1 hour (configurable)
│   Refresh Token             │  ← Expires: 7 days (configurable)
└──────────────────────────────┘
    │
    ├── Access token expires ──→ Auto-refresh via refresh token ──→ New JWT issued
    │
    ├── Refresh token expires ──→ User must re-authenticate
    │
    ├── User signs out ──────────→ Both tokens revoked immediately
    │
    └── Inactivity > threshold ──→ Session expires at token TTL
```

### 4.2 Session Configuration

```typescript
// Supabase Auth Settings (configured in Supabase Dashboard)
{
  "SITE_URL": "https://secondbrain-os.vercel.app",
  "ADDITIONAL_REDIRECT_URLS": ["http://localhost:3000"],
  "JWT_EXPIRY": 3600,           // 1 hour (seconds)
  "REFRESH_TOKEN_EXPIRY": 604800, // 7 days (seconds)
  "SESSION_INACTIVITY_TIMEOUT": 3600, // 1 hour
  "SESSION_MINIMUM_LIFETIME": 120, // 2 minutes (minimum)
  "SAML_EXPIRY": 86400,         // 24 hours
  "DB_EXTERNAL_AUTH": "verified",  // Require verified email for DB access
  "MAILER_AUTOCONFIRM": true,    // Auto-confirm email (OAuth verified)
  "RATE_LIMIT_TOKEN_REFRESH": 30  // Token refresh requests per hour
}
```

### 4.3 Token Refresh Flow

```typescript
// Automatic refresh handled by Supabase client SDK
// No manual refresh needed for standard use

// Supabase client automatically:
// 1. Monitors access token expiry
// 2. Calls /auth/v1/token when token is about to expire
// 3. Exchanges refresh_token for new access_token
// 4. Stores new tokens
// 5. Replays any failed requests with new token

// Manual refresh if needed:
export async function refreshSession() {
  const { data: { session }, error } = await supabase.auth.refreshSession()
  if (error) {
    // Refresh failed; redirect to login
    window.location.href = '/login'
  }
  return session
}
```

### 4.4 Refresh Token Rotation

Supabase Auth implements automatic refresh token rotation:

| Property | Value | Rationale |
|----------|-------|-----------|
| Rotation trigger | Each refresh token usage | Limits window of stolen token |
| Old token validity | Immediately revoked on rotation | Stolen + used token = invalid |
| Reuse detection | Detected from old token use | If old token reused after rotation, all sessions revoked |
| Rotation window | 5 minutes before expiry | Pre-expiry refresh avoids service disruption |
| Maximum refresh chain | Unlimited | Users stay signed in across 7 days |

```python
# Refresh token rotation is handled by Supabase Auth server
# The client flow:
# 1. Client sends refresh_token to /auth/v1/token?grant_type=refresh_token
# 2. Supabase validates refresh_token, issues new access_token + new refresh_token
# 3. Old refresh_token is invalidated
# 4. If old refresh_token is reused (stolen), all user sessions are revoked
# 5. Client receives response, updates local token storage
```

### 4.5 Session Cookie Configuration

```typescript
// Supabase Auth cookie configuration
const SESSION_COOKIE_OPTIONS = {
  name: 'sb-session',
  lifetime: 60 * 60 * 24 * 7,  // 7 days
  domain: process.env.NEXT_PUBLIC_SITE_DOMAIN,  // e.g., secondbrain-os.vercel.app
  path: '/',
  sameSite: 'lax' as const,     // CSRF protection
  httpOnly: true,               // XSS protection
  secure: true,                 // HTTPS only
}
```

---

## 5. JWT Payload Schema & Validation

### 5.1 JWT Structure

A JWT consists of three Base64Url-encoded parts separated by dots:
```
header.payload.signature
```

### 5.2 JWT Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### 5.3 JWT Payload

```json
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@gmail.com",
  "role": "authenticated",
  "aud": "authenticated",
  "iat": 1718100000,
  "exp": 1718103600,
  "iss": "https://[project].supabase.co/auth/v1",
  "provider": "google",
  "custom_claims": {
    "global_name": "John Doe",
    "avatar_url": "https://lh3.googleusercontent.com/a/...",
    "hd": "gmail.com"
  }
}
```

### 5.4 Claim Definitions

| Claim | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `sub` | UUIDv4 | ✅ | Subject (user UUID) | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `user_id` | UUIDv4 | ✅ | User identifier (matches sub) | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `email` | String | ✅ | User email from Google | `user@gmail.com` |
| `role` | Enum | ✅ | User role | `authenticated` or `admin` |
| `aud` | String | ✅ | Audience | `authenticated` |
| `iat` | Unix timestamp | ✅ | Issued at | `1718100000` |
| `exp` | Unix timestamp | ✅ | Expiration | `1718103600` |
| `iss` | URL | ✅ | Issuer | `https://[project].supabase.co/auth/v1` |
| `provider` | String | ✅ | OAuth provider | `google` |
| `custom_claims` | Object | Optional | User metadata | `{ "global_name": "John Doe" }` |

### 5.5 JWT Signature Validation

```python
# packages/config/core/auth.py
import jwt
from datetime import datetime, timedelta
from pydantic_settings import BaseSettings

class AuthSettings(BaseSettings):
    jwt_secret: str = "change-me-to-random-256-bit-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1 hour
    refresh_token_expire_days: int = 7
    jwt_issuer: str = "https://[project].supabase.co/auth/v1"

settings = AuthSettings()

def validate_jwt(token: str) -> dict:
    """
    Validate JWT token and return payload.
    Raises jwt.PyJWTError on invalid token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["sub", "exp", "iat", "email"],
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("Token has expired")
    except jwt.InvalidAudienceError:
        raise PermissionError("Invalid token audience")
    except jwt.InvalidIssuerError:
        raise PermissionError("Invalid token issuer")
    except jwt.PyJWTError as e:
        raise PermissionError(f"Invalid token: {str(e)}")
```

### 5.6 JWT Validation Rules

| Rule | Enforcement | Purpose |
|------|-------------|---------|
| Algorithm check | Only HS256 allowed | Algorithm confusion attack prevention |
| Expiration check | `exp` must be in future | Replay attack window limitation |
| Issued at check | `iat` must be in past | Token creation time validation |
| Subject check | `sub` must be non-empty UUIDv4 | User identification |
| Signature check | HMAC-SHA256 with secret | Tamper prevention |
| Issuer check | Must match Supabase URL | Cross-project token rejection |
| Audience check | Must be "authenticated" | Token scope validation |

### 5.7 Prohibited JWT Attacks & Mitigations

| Attack | Description | Mitigation |
|--------|-------------|------------|
| Algorithm confusion (alg:none) | Attacker sets `"alg":"none"` to bypass verification | Library rejects `none` algorithm |
| Algorithm confusion (RS256→HS256) | Attacker uses public key as HMAC secret | Single HS256 symmetric key; no public key exposure |
| Sub claim manipulation | Attacker modifies sub to access another user | JWT signature validation; server-side user_id verification |
| Exp claim extension | Attacker modifies exp to extend token lifetime | Signature validation prevents tampering |
| Token replay | Attacker captures and reuses JWT | Short expiry (1 hour); refresh token rotation |
| Cross-project token reuse | Token from one Supabase project used in another | Issuer validation prevents cross-project use |

---

## 6. Token Validation Middleware

### 6.1 FastAPI Dependency

```python
# packages/config/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency for protected routes.
    Validates JWT and returns user payload.

    Usage:
        @router.get("/tasks")
        async def list_tasks(user: dict = Depends(get_current_user)):
            ...
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Validate JWT locally (faster)
        payload = validate_jwt(token)

        # Optionally verify with Supabase Auth server (if you need latest state)
        # supabase = get_supabase_client()
        # user = supabase.auth.get_user(token)
        # return user.user

        return payload
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )


# Optional dependency for admin-only routes
async def get_admin_user(
    user: dict = Depends(get_current_user),
) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
```

### 6.2 Route Protection Patterns

```python
# apps/api/app/api/tasks.py
from fastapi import APIRouter, Depends
from packages.config.core.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/")
async def list_tasks(user: dict = Depends(get_current_user)):
    """List all tasks for authenticated user."""
    user_id = user["sub"]
    # All queries filtered by user_id
    data = supabase.table("tasks")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    return data.data


@router.post("/")
async def create_task(
    task: TaskCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new task."""
    user_id = user["sub"]
    result = supabase.table("tasks").insert({
        **task.model_dump(),
        "user_id": user_id,
    }).execute()
    return result.data[0]
```

### 6.3 Public vs. Protected Routes

| Route | Type | Auth Required | Notes |
|-------|------|---------------|-------|
| `/api/auth/**` | Public | No | Auth is handled by Supabase directly |
| `/api/tasks/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/courses/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/goals/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/habits/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/sleep/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/income/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/ideas/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/projects/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/resources/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/opportunities/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/time/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/chat/**` | Protected | Yes | JWT required; user_id filtering |
| `/api/automation/**` | Protected | Yes | JWT required; user_id filtering |
| `/health` | Public | No | Health check |

### 6.4 Supabase Auth Dependency (Alternative)

```python
# Alternative: Validate with Supabase Auth server (slower but always current)
async def get_current_user_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        # If token is expired, try local validation for stale data
        # or return 401 prompting re-auth
        raise HTTPException(status_code=401, detail="Session expired")
```

---

## 7. Role-Based Access Control

### 7.1 Role Definitions

| Role | Permissions | Routes | Default |
|------|-------------|--------|---------|
| `anonymous` | None (public pages only) | `/login`, `/`, public assets | Assigned before sign-in |
| `authenticated` | Own data CRUD; AI chat; scheduler triggers | All protected routes | Assigned after Google OAuth |
| `admin` | Everything + user management; system config; logs | All routes + admin panel | Manually assigned in Supabase |

### 7.2 Role Assignment

```sql
-- Roles are managed through Supabase Auth
-- Default: All authenticated users get 'authenticated' role
-- Admin: Manually set in user_metadata or custom claims

-- Set admin role via Supabase Dashboard or API:
UPDATE auth.users SET role = 'admin' WHERE email = 'admin@example.com';

-- Or via raw_user_meta_data:
UPDATE auth.users
SET raw_user_meta_data = raw_user_meta_data || '{"role": "admin"}'
WHERE email = 'admin@example.com';
```

### 7.3 Admin Validation in Routes

```python
# packages/config/core/auth.py

async def get_admin_user(
    user: dict = Depends(get_current_user),
) -> dict:
    """Dependency for admin-only routes."""
    role = user.get("role") or user.get("user_metadata", {}).get("role", "authenticated")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )
    return user


# Usage in admin routes:
@router.get("/admin/users")
async def list_all_users(
    admin: dict = Depends(get_admin_user),
):
    """List all users (admin only)."""
    data = supabase.table("users").select("*").execute()
    return data.data
```

### 7.4 Frontend Route Guard

```typescript
// apps/web/components/auth/role-guard.tsx
'use client'
import { useRouter } from 'next/navigation'
import { createClient } from '@supabase/supabase-js'
import { useEffect, useState } from 'react'

type AllowedRole = 'authenticated' | 'admin'

export function RoleGuard({
  children,
  allowedRoles = ['authenticated'],
}: {
  children: React.ReactNode
  allowedRoles?: AllowedRole[]
}) {
  const router = useRouter()
  const [authorized, setAuthorized] = useState(false)

  useEffect(() => {
    async function checkAuth() {
      const supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      )
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        router.push('/login')
        return
      }

      const userRole = session.user?.user_metadata?.role || 'authenticated'
      if (!allowedRoles.includes(userRole)) {
        router.push('/403')
        return
      }

      setAuthorized(true)
    }
    checkAuth()
  }, [router, allowedRoles])

  if (!authorized) return null
  return <>{children}</>
}
```

---

## 8. Multi-Device Session Handling

### 8.1 Session Model

| Property | Value |
|----------|-------|
| Concurrent sessions | Unlimited |
| Session identification | JWT `jti` (JWT ID) claim |
| Session listing | Supabase `auth.sessions` table |
| Session revocation | Per-session via JWT ID or bulk per user |
| Cross-device sync | Real-time via Supabase Realtime subscriptions |

### 8.2 Session Listing & Revocation (Admin)

```typescript
// Admin API: List all sessions for a user
export async function adminListSessions(userId: string) {
  const { data, error } = await supabase
    .from('sessions')  // auth.sessions view
    .select('*')
    .eq('user_id', userId)
  return { data, error }
}

// Admin API: Revoke a specific session
export async function adminRevokeSession(sessionId: string) {
  const { error } = await supabase.auth.admin.deleteUser(sessionId)
  return { error }
}

// User API: List own sessions
export async function listMySessions() {
  const { data, error } = await supabase.rpc('list_user_sessions')
  return { data, error }
}
```

### 8.3 Session Management UI

```typescript
// apps/web/app/settings/sessions/page.tsx
'use client'
import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

type Session = {
  id: string
  created_at: string
  last_active: string
  user_agent: string
  ip_address: string
  is_current: boolean
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    try {
      const response = await fetch('/api/sessions')
      const data = await response.json()
      setSessions(data)
    } catch (err) {
      console.error('[Sessions] Failed to load:', err)
    } finally {
      setLoading(false)
    }
  }

  async function revokeSession(sessionId: string) {
    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' })
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch (err) {
      console.error('[Sessions] Revoke failed:', err)
    }
  }

  if (loading) return <div>Loading sessions...</div>

  return (
    <div className="space-y-4">
      <h1 className="text-gradient">Active Sessions</h1>
      {sessions.map(session => (
        <Card key={session.id} className="p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-medium">
                {session.user_agent || 'Unknown device'}
                {session.is_current && (
                  <span className="text-accent-neon ml-2">(Current)</span>
                )}
              </p>
              <p className="text-text-secondary text-sm">
                Last active: {new Date(session.last_active).toLocaleString()}
              </p>
              <p className="text-text-secondary text-sm">
                IP: {session.ip_address}
              </p>
            </div>
            {!session.is_current && (
              <Button
                variant="danger"
                onClick={() => revokeSession(session.id)}
              >
                Revoke
              </Button>
            )}
          </div>
        </Card>
      ))}
    </div>
  )
}
```

---

## 9. OAuth Scopes & Permissions

### 9.1 Requested Scopes

| Scope | Data Retrieved | Required | Justification |
|-------|---------------|----------|---------------|
| `openid` | Subject identifier | ✅ | OpenID Connect standard |
| `email` | User email address | ✅ | Account identification, notifications |
| `profile` | Display name, avatar URL | ✅ | Personalization, UI display |

### 9.2 Google OAuth Consent Screen

```
Second Brain OS would like to:
  ✓ View your email address
  ✓ View your basic profile info

Data accessed:
  - Name: Displayed in the application
  - Email address: Account identification, briefing delivery
  - Profile photo: Profile avatar

This does NOT give Second Brain OS access to:
  - Google Drive
  - Gmail content
  - Google Calendar
  - YouTube account
  - Any other Google service
```

### 9.3 Data Minimization

Second Brain OS requests the minimum scopes required for functionality:

| Scope | Usage | Stored? | Retention |
|-------|-------|---------|-----------|
| `openid` | Authentication only | No (sub used as UUID) | — |
| `email` | Account ID, email delivery (briefings) | Yes (`users` table) | Until account deletion |
| `profile` | Display name, avatar | Yes (`users` table) | Until account deletion |

---

## 10. Supabase Auth Integration

### 10.1 Supabase Auth Configuration

```typescript
// apps/web/lib/supabase/client.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce',
    storage: {
      getItem: (key) => {
        if (typeof window === 'undefined') return null
        return window.localStorage.getItem(key)
      },
      setItem: (key, value) => {
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, value)
        }
      },
      removeItem: (key) => {
        if (typeof window !== 'undefined') {
          window.localStorage.removeItem(key)
        }
      },
    },
  },
})
```

### 10.2 Server-Side Supabase Client

```typescript
// apps/web/lib/supabase/server.ts
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'

export function createServerSupabase() {
  return createServerComponentClient({ cookies })
}

// Usage in server components:
export default async function DashboardPage() {
  const supabase = createServerSupabase()
  const { data: { session } } = await supabase.auth.getSession()
  const { data: tasks } = await supabase
    .from('tasks')
    .select('*')
    .eq('user_id', session?.user.id)
  return <div>...</div>
}
```

### 10.3 Supabase Auth UI (Social Login Component)

```typescript
// apps/web/components/auth/social-login.tsx
'use client'
import { useState } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Button } from '@/components/ui/button'

export function SocialLogin() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )

  async function handleGoogleSignIn() {
    setLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })
      if (error) throw error
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <Button
        variant="primary"
        onClick={handleGoogleSignIn}
        disabled={loading}
      >
        {loading ? 'Redirecting to Google...' : 'Sign in with Google'}
      </Button>
      {error && (
        <p className="text-accent-danger text-sm">{error}</p>
      )}
    </div>
  )
}
```

---

## 11. Security Headers

### 11.1 Next.js Security Headers Configuration

```javascript
// apps/web/next.config.js
const securityHeaders = [
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
  },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",  // unsafe-eval for Next.js
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https://lh3.googleusercontent.com https://avatars.githubusercontent.com",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://*.supabase.co https://*.vercel.app https://*.railway.app https://api.anthropic.com",
      "frame-src 'self' https://*.supabase.co https://accounts.google.com",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
]

/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
}

module.exports = nextConfig
```

### 11.2 FastAPI Security Headers Middleware

```python
# apps/api/main.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "0"  # Deprecated but harmless
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### 11.3 Security Headers Verification

```bash
# Verify security headers with curl
curl -sI https://secondbrain-os.vercel.app | grep -iE '^(strict-transport-security|x-frame-options|x-content-type-options|content-security-policy|referrer-policy|permissions-policy)'

# Expected output:
# strict-transport-security: max-age=63072000; includeSubDomains; preload
# x-frame-options: DENY
# x-content-type-options: nosniff
# content-security-policy: default-src 'self'; ...
# referrer-policy: strict-origin-when-cross-origin
# permissions-policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
```

### 11.4 Headers Purpose & Effectiveness

| Header | Purpose | Attack Prevented | Risk if Missing |
|--------|---------|-----------------|-----------------|
| `Strict-Transport-Security` | Force HTTPS for 2 years | SSL stripping, MITM | **High** — downgrade attack |
| `X-Frame-Options: DENY` | Prevent embedding in iframes | Clickjacking | **Medium** — UI redress |
| `X-Content-Type-Options: nosniff` | Prevent MIME type sniffing | Content-type confusion | **Medium** — drive-by download |
| `Content-Security-Policy` | Restrict resource sources | XSS, data injection | **Critical** — script injection |
| `Referrer-Policy` | Control referrer header | Information leakage | **Low** — cross-origin referrer |
| `Permissions-Policy` | Disable browser features | API abuse, fingerprinting | **Low** — privacy risk |

---

## 12. Rate Limiting on Auth Endpoints

### 12.1 Auth Endpoint Rate Limits

| Endpoint | Limit | Window | Purpose |
|----------|-------|--------|---------|
| POST /auth/v1/token?grant_type=password | 5 req | 60s | Prevent brute force |
| POST /auth/v1/token?grant_type=refresh_token | 30 req | 3600s (1 hour) | Limit refresh abuse |
| POST /auth/v1/logout | 60 req | 60s | Prevent logout spam |
| GET /auth/v1/user | 120 req | 60s | Normal API usage |
| All auth endpoints | 300 req | 60s | Global auth rate limit |

### 12.2 Application-Level Rate Limiting

```python
# packages/shared/utils/rate_limiter.py
import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate-limit auth-related paths
        if not request.url.path.startswith("/auth"):
            return await call_next(request)

        client_ip = request.client.host

        # Determine limits based on endpoint
        if "grant_type=password" in str(request.url):
            max_requests, window = 5, 60
        elif "grant_type=refresh_token" in str(request.url):
            max_requests, window = 30, 3600
        else:
            max_requests, window = 60, 60

        now = time.time()
        window_start = now - window

        # Clean old entries
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > window_start
        ]

        # Check limit
        if len(self.requests[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many authentication requests. Please wait before trying again.",
            )

        self.requests[client_ip].append(now)
        return await call_next(request)
```

---

## 13. Brute Force Protection

### 13.1 Protection Layers

| Layer | Mechanism | Threshold | Response |
|-------|-----------|-----------|----------|
| Network | Railway/Vercel WAF | 1000 req/min from single IP | IP blocked for 15 min |
| Application | Rate limiter | 5 failed attempts / 60s | 429 response |
| Supabase Auth | Built-in rate limiting | 10 failed attempts / 5 min | Account temporarily locked |
| Google OAuth | Google's own protection | Varies | CAPTCHA or block |
| Monitoring | Alert on >10 failed attempts/user | Alert triggered | Manual investigation |

### 13.2 Account Lockout Implementation

```python
# packages/shared/utils/security.py
import time
from typing import Dict, Tuple

class BruteForceProtection:
    """
    In-memory brute force protection.
    For production, use Redis for distributed tracking.
    """

    def __init__(self):
        self.attempts: Dict[str, list[float]] = {}
        self.locked_until: Dict[str, float] = {}
        self.MAX_ATTEMPTS = 5
        self.WINDOW = 300  # 5 minutes
        self.LOCKOUT_DURATION = 900  # 15 minutes

    def record_failed_attempt(self, identifier: str) -> bool:
        """Record failed login attempt. Returns True if account is now locked."""
        now = time.time()

        if identifier not in self.attempts:
            self.attempts[identifier] = []

        # Clean old attempts
        self.attempts[identifier] = [
            t for t in self.attempts[identifier]
            if t > now - self.WINDOW
        ]

        self.attempts[identifier].append(now)

        if len(self.attempts[identifier]) >= self.MAX_ATTEMPTS:
            self.locked_until[identifier] = now + self.LOCKOUT_DURATION
            return True  # Account locked

        return False

    def is_locked(self, identifier: str) -> bool:
        """Check if account is currently locked."""
        if identifier in self.locked_until:
            if time.time() < self.locked_until[identifier]:
                return True
            # Lockout expired
            del self.locked_until[identifier]
            self.attempts.pop(identifier, None)
        return False

    def reset(self, identifier: str):
        """Reset on successful authentication."""
        self.attempts.pop(identifier, None)
        self.locked_until.pop(identifier, None)

brute_force = BruteForceProtection()
```

### 13.3 Brute Force Alerting

```python
# packages/shared/utils/security.py (continued)

async def notify_brute_force_alert(identifier: str, attempt_count: int):
    """
    Send alert when brute force threshold is exceeded.
    Integration with monitoring/alerting system.
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.warning(
        "Brute force detection",
        extra={
            "identifier": identifier,
            "attempt_count": attempt_count,
            "action": "account_locked",
            "lockout_duration": 900,
        }
    )
    # In production: send alert to PagerDuty / Slack / Email
    # await send_alert(channel="security", message=f"Brute force detected for {identifier}")
```

---

## 14. MFA Roadmap

### 14.1 Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Google OAuth | ✅ Live | Relies on Google's MFA |
| Email OTP | ❌ Planned | Fallback for non-Google users |
| TOTP (Authenticator) | ❌ Planned | Time-based one-time passwords |
| SMS OTP | ❌ Not planned | Cost and security concerns |
| Hardware keys (WebAuthn) | ❌ Future | Post-MVP |
| Backup codes | ❌ Planned | For TOTP recovery |

### 14.2 Implementation Plan

| Phase | Feature | Timeline | Effort |
|-------|---------|----------|--------|
| Phase 1 | Google OAuth MFA (enforced by Google) | ✅ Complete | Minimal |
| Phase 2 | Email OTP as backup auth method | Q3 2026 | 2 weeks |
| Phase 3 | TOTP with authenticator app | Q4 2026 | 3 weeks |
| Phase 4 | MFA enforcement toggle (user setting) | Q4 2026 | 1 week |
| Phase 5 | WebAuthn (passkeys) | 2027 | 4 weeks |

### 14.3 TOTP Implementation Sketch

```typescript
// apps/web/app/settings/security/mfa-setup.tsx
'use client'
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export function MfaSetup() {
  const [step, setStep] = useState<'intro' | 'qr' | 'verify' | 'done'>('intro')
  const [secret, setSecret] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [verificationCode, setVerificationCode] = useState('')

  async function startSetup() {
    const response = await fetch('/api/auth/mfa/setup', { method: 'POST' })
    const data = await response.json()
    setSecret(data.secret)
    setQrCode(data.qr_code_url)
    setStep('qr')
  }

  async function verifyCode() {
    const response = await fetch('/api/auth/mfa/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: verificationCode, secret }),
    })
    if (response.ok) {
      setStep('done')
    }
  }

  return (
    <Card className="p-6">
      <h2 className="card-title">Two-Factor Authentication (TOTP)</h2>
      {step === 'intro' && (
        <div className="space-y-4">
          <p>Add an extra layer of security using an authenticator app like Google Authenticator or Authy.</p>
          <Button variant="primary" onClick={startSetup}>Set Up 2FA</Button>
        </div>
      )}
      {step === 'qr' && (
        <div className="space-y-4">
          <p>Scan this QR code with your authenticator app:</p>
          <img src={qrCode} alt="TOTP QR Code" className="w-48 h-48 mx-auto" />
          <p className="text-text-secondary text-sm">
            Can't scan? Manual code: <code className="text-accent-primary">{secret}</code>
          </p>
        </div>
      )}
      {step === 'verify' && (
        <div className="space-y-4">
          <p>Enter the 6-digit code from your authenticator app:</p>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            className="input"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
          />
          <Button variant="primary" onClick={verifyCode}>Verify</Button>
        </div>
      )}
      {step === 'done' && (
        <div className="space-y-4">
          <p className="text-accent-neon">✅ Two-factor authentication is now enabled.</p>
          <p>Save your backup codes in case you lose access to your authenticator app.</p>
          <Button variant="secondary" onClick={() => {/* download backup codes */}}>
            Download Backup Codes
          </Button>
        </div>
      )}
    </Card>
  )
}
```

---

## 15. Auth Testing Scenarios

### 15.1 Test Matrix

| Test ID | Scenario | Expected Result | Type |
|---------|----------|-----------------|------|
| AUTH-01 | Successful Google OAuth sign-in | JWT issued, session created, redirect to dashboard | Happy path |
| AUTH-02 | Sign-in with cancelled Google consent | Redirect back to login page, no session created | Negative |
| AUTH-03 | Access protected route without JWT | 401 Unauthorized, redirect to login | Negative |
| AUTH-04 | Access protected route with expired JWT | 401 Unauthorized, auto-refresh attempted, redirect if fail | Negative |
| AUTH-05 | Access protected route with valid JWT | 200 OK, data returned | Happy path |
| AUTH-06 | Sign-out from active session | Session cleared, redirect to login, API access revoked | Happy path |
| AUTH-07 | Sign-out with expired session | Session cleared locally, no server error | Negative |
| AUTH-08 | Refresh token rotation | New access + refresh tokens issued, old invalid | Happy path |
| AUTH-09 | Refresh token replay (stolen token) | All sessions revoked, user must re-auth | Security |
| AUTH-10 | JWT with forged signature | 401 Unauthorized, token rejected | Security |
| AUTH-11 | JWT with alg:none | 401 Unauthorized, library rejects | Security |
| AUTH-12 | JWT with modified sub claim | 401 Unauthorized, signature mismatch | Security |
| AUTH-13 | Multiple concurrent sessions | All sessions valid independently | Happy path |
| AUTH-14 | Revoke one of multiple sessions | Only revoked session invalidated, others valid | Happy path |
| AUTH-15 | Rate limiting on sign-in (5 req/min) | 429 after 5 failed attempts in 60s | Security |
| AUTH-16 | Brute force lockout (5 failed in 5min) | Account locked for 15 minutes | Security |
| AUTH-17 | CORS preflight (OPTIONS) | Correct CORS headers returned | Security |
| AUTH-18 | XSS attempt in callback URL | Redirect to safe path, no XSS execution | Security |
| AUTH-19 | CSRF on auth callback (missing state param) | OAuth callback rejected | Security |
| AUTH-20 | Cross-project JWT reuse | JWT from different Supabase project rejected | Security |

### 15.2 Automated Auth Test (Python)

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_protected_route_without_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/tasks")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


@pytest.mark.asyncio
async def test_protected_route_with_expired_token():
    expired_jwt = "fake-jwt-token-string-for-testingInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {expired_jwt}"}
        )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_jwt_alg_none_attack():
    # Token with alg: none
    malicious_jwt = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyMTIzIn0."
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {malicious_jwt}"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cors_preflight():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/api/tasks",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers


@pytest.mark.asyncio
async def test_rate_limiting():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        responses = []
        for _ in range(10):
            response = await client.get(
                "/api/tasks",
                headers={"Authorization": "Bearer invalid-token"}
            )
            responses.append(response.status_code)
    # Some requests should be rate-limited
    assert 429 in responses
```

### 15.3 Manual Auth Test Cases

```bash
# Manual testing with curl

# 1. Test protected route without token
curl -s https://api.secondbrain-os.com/api/tasks
# Expected: 401 {"detail":"Authentication required"}

# 2. Test with valid JWT
curl -s https://api.secondbrain-os.com/api/tasks \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
# Expected: 200 [...]

# 3. Test CORS
curl -s -I -X OPTIONS https://api.secondbrain-os.com/api/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"
# Expected: Access-Control-Allow-Origin: *

# 4. Test rate limiting
for i in $(seq 1 60); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    https://api.secondbrain-os.com/api/tasks \
    -H "Authorization: Bearer invalid"
done
# Expected: Eventually starts returning 429

# 5. Verify security headers
curl -sI https://secondbrain-os.vercel.app | grep -i strict-transport-security
# Expected: Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

---

## 16. Appendix: Code Reference

### 16.1 Key Files

| File | Purpose |
|------|---------|
| `apps/web/middleware.ts` | Next.js middleware for route protection |
| `apps/web/lib/supabase/client.ts` | Supabase client initialization |
| `apps/web/lib/supabase/server.ts` | Server-side Supabase client |
| `apps/web/app/auth/callback/route.ts` | OAuth callback handler |
| `apps/web/components/auth/social-login.tsx` | Google sign-in button |
| `apps/web/components/providers/session-provider.tsx` | Session state management |
| `packages/config/core/auth.py` | JWT validation, get_current_user dependency |
| `packages/shared/utils/rate_limiter.py` | Rate limiting middleware |
| `packages/shared/utils/security.py` | Brute force protection, input sanitization |

### 16.2 Dependency Versions

| Package | Version | Purpose |
|---------|---------|---------|
| `@supabase/supabase-js` | ^2.39.0 | Supabase client SDK |
| `@supabase/auth-helpers-nextjs` | ^0.8.0 | Next.js auth helpers |
| `@supabase/ssr` | ^0.1.0 | Server-side rendering auth |
| `PyJWT` | ^2.8.0 | JWT encoding/decoding |
| `python-jose` | ^3.3.0 | JOSE standards (alternative) |
| `httpx` | ^0.25.0 | Async HTTP client for testing |
| `pytest-asyncio` | ^0.23.0 | Async test support |

### 16.3 Common Errors & Troubleshooting

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `AuthApiError: invalid flow` | PKCE flow requires code_challenge | Ensure `flowType: 'pkce'` in client config |
| `401: invalid jwt` | JWT expired or malformed | Verify JWT_SECRET matches Supabase JWT secret |
| `Auth session missing` | Cookie not set correctly | Check cookie domain/path configuration |
| `403: row-level security violation` | user_id not in query | Add `.eq('user_id', user.id)` to all queries |
| `TypeError: Cannot read properties of null (reading 'access_token')` | Session not initialized | Check `getSession()` before using token |
| `ERR_TOO_MANY_REDIRECTS` | Middleware redirect loop | Verify public routes excluded from matcher |
| `429 Too Many Requests` | Rate limit exceeded | Wait 60s; check for aggressive retry logic |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-11 | Security Team | Initial auth architecture: OAuth flow, JWT lifecycle, session management, RBAC, MFA roadmap, security headers, rate limiting, brute force protection, test scenarios |

---

## References

- Supabase Auth Documentation: https://supabase.com/docs/guides/auth
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
- JWT.io: https://jwt.io/
- OWASP Authentication Cheatsheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Session Management Cheatsheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- OAuth 2.0 for Browser-Based Apps (BCP): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps
- PKCE (RFC 7636): https://datatracker.ietf.org/doc/html/rfc7636
