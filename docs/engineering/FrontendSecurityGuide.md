# Frontend Security Guide â€” Second Brain OS

| Field | Value |
|---|---|
| Document ID | ENG-FSC-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-12 |
| Applies To | `apps/web/` â€” Frontend security patterns |

---

## Table of Contents

1. [Security Principles](#1-security-principles)
2. [Content Security Policy](#2-content-security-policy)
3. [XSS Prevention](#3-xss-prevention)
4. [CSRF Protection](#4-csrf-protection)
5. [Authentication Token Management](#5-authentication-token-management)
6. [Environment Variable Safety](#6-environment-variable-safety)
7. [Dependency Security](#7-dependency-security)
8. [Secure Data Handling](#8-secure-data-handling)
9. [HTTP Security Headers](#9-http-security-headers)
10. [Security Checklist](#10-security-checklist)

---

## 1. Security Principles

### 1.1 Frontend Security Boundaries

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      BROWSER (Untrusted)                         â”‚
â”‚                                                                   â”‚
â”‚  âŒ Never trust user input                                        â”‚
â”‚  âŒ Never expose secrets (API keys, JWT secrets)                  â”‚
â”‚  âŒ Never store sensitive data in plain text                      â”‚
â”‚  âœ… Validate ALL input client-side AND server-side                â”‚
â”‚  âœ… Sanitize output for XSS prevention                            â”‚
â”‚  âœ… Use CSP as defense-in-depth                                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                          â”‚
                                                          â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   SUPABASE / BACKEND (Trusted)                    â”‚
â”‚                                                                   â”‚
â”‚  âœ… RLS policies enforce row-level access                         â”‚
â”‚  âœ… Server validates all mutations                                â”‚
â”‚  âœ… Secrets stored server-side only                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 1.2 Threat Model (Frontend-Specific)

| Threat | Impact | Likelihood | Mitigation |
|---|---|---|---|
| XSS via user input | Data theft, session hijack | Medium | React auto-escaping, CSP, sanitize rich text |
| CSRF via malicious site | Unauthorized actions | Low | Supabase JWT in headers, SameSite cookies |
| Token theft via XSS | Full account access | Low | HttpOnly cookies, short-lived tokens |
| Data exposure via console | Privacy leak | Medium | Never log tokens, strip sensitive data |
| Dependency vulnerabilities | Varies | Medium | `npm audit` in CI, lockfile, Dependabot |
| Man-in-the-middle | Data interception | Low | HTTPS everywhere, HSTS |
| localStorage XSS | Preference manipulation | Medium | Never store tokens in localStorage |

---

## Frontend Security Layers

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'background': '#0A0B0F',
      'primaryColor': '#6366F1',
      'secondaryColor': '#818CF8',
      'tertiaryColor': '#13151A',
      'primaryTextColor': '#F1F5F9',
      'lineColor': '#6366F1',
      'primaryBorderColor': '#6366F1',
      'secondaryBorderColor': '#818CF8',
      'tertiaryBorderColor': '#00FFA3'
    }
  }
}%%
flowchart LR
    L1["TLS / HTTPS"] --> L2["Content Security Policy"]
    L2 --> L3["Input Sanitization"]
    L3 --> L4["Authentication (JWT)"]
    L4 --> L5["CSRF Protection"]
    L5 --> L6["RLS Policies"]
    L6 --> L7["Audit Logging"]

    L1 -.->|"Layer 1: Transport"| T1["Encrypt all traffic<br/>HSTS headers"]
    L2 -.->|"Layer 2: Browser"| T2["Restrict script sources<br/>Block inline eval"]
    L3 -.->|"Layer 3: Input"| T3["React auto-escaping<br/>Sanitize rich text"]
    L4 -.->|"Layer 4: Identity"| T4["Short-lived tokens<br/>HttpOnly cookies"]
    L5 -.->|"Layer 5: Request"| T5["SameSite cookies<br/>Anti-forgery tokens"]
    L6 -.->|"Layer 6: Data"| T6["Supabase RLS<br/>user_id filtering"]
    L7 -.->|"Layer 7: Audit"| T7["Request logging<br/>Anomaly detection"]

    style L1 fill:#6366F1,color:#F1F5F9
    style L2 fill:#818CF8,color:#F1F5F9
    style L3 fill:#6366F1,color:#F1F5F9
    style L4 fill:#818CF8,color:#F1F5F9
    style L5 fill:#6366F1,color:#F1F5F9
    style L6 fill:#818CF8,color:#F1F5F9
    style L7 fill:#00FFA3,color:#0A0B0F
    style T1 fill:#13151A,color:#94A3B8,stroke:#334155
    style T2 fill:#13151A,color:#94A3B8,stroke:#334155
    style T3 fill:#13151A,color:#94A3B8,stroke:#334155
    style T4 fill:#13151A,color:#94A3B8,stroke:#334155
    style T5 fill:#13151A,color:#94A3B8,stroke:#334155
    style T6 fill:#13151A,color:#94A3B8,stroke:#334155
    style T7 fill:#13151A,color:#94A3B8,stroke:#334155
```

## 2. Content Security Policy

### 2.1 Current CSP Directives

```javascript
// next.config.js
const cspDirectives = [
  "default-src 'self'",
  // Scripts: need 'unsafe-eval' for three.js, 'unsafe-inline' for Next.js
  "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
  // Styles: Tailwind + Framer Motion inject inline styles
  "style-src 'self' 'unsafe-inline'",
  // Images: Supabase storage, GitHub avatars, YouTube thumbnails
  "img-src 'self' data: blob: https://*.supabase.co https://avatars.githubusercontent.com https://img.youtube.com",
  // Fonts: self-hosted + Google Fonts fallback
  "font-src 'self' data: https://fonts.gstatic.com",
  // Connections: Supabase (REST + WebSocket), Backend, Anthropic API
  "connect-src 'self' https://*.supabase.co wss://*.supabase.co http://localhost:8000 https://api.anthropic.com",
  // Frames: Supabase Auth UI
  "frame-src 'self' https://*.supabase.co",
  // Media: self-hosted
  "media-src 'self'",
  // Workers: service worker
  "worker-src 'self'",
  // Base URL restriction
  "base-uri 'self'",
  // Form submissions: self only
  "form-action 'self'",
]

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Content-Security-Policy', value: cspDirectives.join('; ') },
        ],
      },
    ]
  },
}
```

### 2.2 CSP Testing

```bash
# Enable reporting-only mode during development
"Content-Security-Policy-Report-Only": "..."
# Monitor violations via browser console or reporting endpoint

# Use CSP Evaluator
# https://csp-evaluator.withgoogle.com/
```

---

## 3. XSS Prevention

### 3.1 React's Built-in Protection

```typescript
// âœ… SAFE: React auto-escapes JSX expressions
<div>{userInput}</div>
// Result: <div>&lt;script&gt;alert('xss')&lt;/script&gt;</div>

// âœ… SAFE: Props/attributes are escaped
<img src={userInput} alt="user" />
// Even if userInput = "javascript:alert(1)", React renders as string, not executed
```

### 3.2 Danger Zones

```typescript
// âŒ CRITICAL: dangerouslySetInnerHTML
function Unsafe({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />
}

// âœ… SAFE ALTERNATIVE: Use DOMPurify for rich text
import DOMPurify from 'isomorphic-dompurify'

function SafeRichText({ html }: { html: string }) {
  const sanitized = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  })
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />
}

// âŒ CRITICAL: href with user-controlled input
<a href={userInput}>Click</a>
// userInput could be "javascript:alert(1)"

// âœ… SAFE: Validate URL scheme
function safeUrl(url: string) {
  try {
    const parsed = new URL(url)
    return ['http:', 'https:', 'mailto:'].includes(parsed.protocol)
  } catch {
    return false
  }
}
{userInput && safeUrl(userInput) && <a href={userInput}>Link</a>}
```

### 3.3 Input Sanitization Rules

| Input Type | Sanitization | Method |
|---|---|---|
| Text content | None needed | React auto-escapes |
| URLs | Validate protocol | `new URL()` check |
| HTML (rich text) | Strip dangerous tags | `DOMPurify.sanitize()` |
| SVG | Strip scripts | DOMPurify or avoid |
| JSON | Parse safely | `JSON.parse()` with try/catch |
| File names | Strip path separators | `.replace(/[\/\\]/g, '')` |

### 3.4 Trusted Types (Future)

```typescript
// Phase 2: Enable Trusted Types for additional XSS protection
// next.config.js
headers: [
  {
    key: 'Content-Security-Policy',
    value: "require-trusted-types-for 'script'",
  },
]
```

---

## 4. CSRF Protection

### 4.1 How Supabase Handles CSRF

```
Browser Request:
â”œâ”€â”€ Cookie: sb-session (HttpOnly, SameSite=Lax)
â”œâ”€â”€ Header: apikey (anon_key)
â””â”€â”€ Header: Authorization: Bearer <access_token>

Supabase validates:
1. Session cookie signature
2. Access token matches session
3. RLS policy for requested table
```

### 4.2 CSRF Prevention Rules

```typescript
// âœ… ALWAYS: Include auth headers in API calls
const { data, error } = await supabase.from('tasks').select('*')
// Supabase SDK automatically includes anon_key + access_token

// âœ… ALWAYS: Use POST/DELETE/PUT for mutations (not GET)
// âœ… NEVER: Use URL query params for mutations
// Example of what NOT to do:
// GET /api/tasks/delete?id=1  â† CSRF-vulnerable!
```

### 4.3 SameSite Cookie Configuration

```typescript
// Supabase SSR client handles this automatically
// The session cookie uses SameSite=Lax by default
export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

---

## 5. Authentication Token Management

### 5.1 Token Lifecycle

```
User logs in via Google OAuth
        â”‚
        â–¼
Supabase returns:
â”œâ”€â”€ access_token (JWT, 1 hour expiry)
â”œâ”€â”€ refresh_token (long-lived)
â””â”€â”€ provider_token (Google, for APIs)
        â”‚
        â–¼
Stored in:
â”œâ”€â”€ access_token â†’ Supabase Auth state (in-memory)
â”œâ”€â”€ refresh_token â†’ HttpOnly cookie (sb-session)
â””â”€â”€ provider_token â†’ In-memory (not persisted)
        â”‚
        â–¼
On expiry:
â”œâ”€â”€ Supabase auto-refreshes using refresh_token
â”œâ”€â”€ New access_token issued transparently
â””â”€â”€ No user interaction needed
```

### 5.2 Token Safety Rules

```typescript
// âœ… SAFE: Supabase SDK auto-attaches token
const { data } = await supabase.from('tasks').select('*')

// âœ… SAFE: Get token for backend API calls
const { data: { session } } = await supabase.auth.getSession()
const token = session?.access_token

// âŒ CRITICAL: NEVER store in localStorage
localStorage.setItem('auth_token', token)  // â† XSS-vulnerable!

// âŒ CRITICAL: NEVER log tokens
console.log(token)  // â† Would expose in production logs

// âœ… SAFE: Use token only in Authorization header
headers: {
  'Authorization': `Bearer ${session.access_token}`,
}
```

### 5.3 Session Refresh Handling

```typescript
// hooks/useAuth.ts â€” handles session lifecycle
export function useAuth() {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check existing session (auto-refreshes if needed)
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes (sign in/out, token refresh)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])
}
```

---

## 6. Environment Variable Safety

### 6.1 Public vs Private Variables

```bash
# .env.local (gitignored â€” NEVER COMMIT)
# Public variables (NEXT_PUBLIC_ prefix â†’ exposed to browser)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJ...  # Public anon key
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEVTOOLS=true

# Private variables (no prefix â†’ server-side only, NEVER in browser)
SUPABASE_SERVICE_KEY=eyJhbGciOiJ...  # Secret service key â€” NEVER expose
CLAUDE_API_KEY=sk-ant-...              # Secret â€” server-side only
JWT_SECRET=your-jwt-secret             # Secret â€” server-side only
```

### 6.2 Environment Variable Rules

```typescript
// âœ… SAFE: Public variable (available in browser)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!

// âŒ CRITICAL: Private variable in client component
// This will be `undefined` in the browser!
const apiKey = process.env.SUPABASE_SERVICE_KEY

// âœ… SAFE: Private variables only in:
// 1. Server Components (app/page.tsx without 'use client')
// 2. API routes (app/api/*/route.ts)
// 3. next.config.js
// 4. middleware.ts

// âœ… SAFE: Server Component accessing private vars
export default async function ServerPage() {
  const apiKey = process.env.SUPABASE_SERVICE_KEY  // Safe â€” only runs on server
  // ...
}
```

---

## 7. Dependency Security

### 7.1 Audit Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/apps/web"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
    # Group non-breaking updates
    groups:
      react:
        patterns: ["react*", "react-dom*"]
      next:
        patterns: ["next*"]
```

### 7.2 npm Audit in CI

```bash
# Run in CI â€” fail on high/critical vulnerabilities
npm audit --audit-level=high

# Review and resolve
npm audit fix           # Auto-fix non-breaking
npm audit fix --force   # Force fix (may break semver)
npm ls <package>        # Check dependency tree
```

### 7.3 Lockfile Security

```bash
# ALWAYS commit package-lock.json
# It locks exact versions, preventing supply chain attacks

# Verify integrity on install
npm ci  # Clean install using lockfile (CI only)

# Check for malicious packages
npx @socketsecurity/cli scan
```

### 7.4 Known Safe Versions

| Package | Min Safe Version | Notes |
|---|---|---|
| `next` | 14.2.0+ | CVE-2024-34351 fixed in 14.2.0 |
| `next-auth` / Supabase | Latest | Auth handled by Supabase SDK |
| `zod` | 3.22+ | Validation library |
| `framer-motion` | 10.18+ | Animation lib, no known critical CVEs |
| `@supabase/supabase-js` | 2.39+ | API client, auto-updated |

---

## 8. Secure Data Handling

### 8.1 What NOT to Log

```typescript
// âŒ CRITICAL: Never log these
console.log(session.access_token)       // JWT tokens
console.log(user.email)                 // PII
console.log(error.response?.data)       // Raw API errors (may contain tokens)
console.log(config.supabaseServiceKey)  // API keys
console.log(localStorage.getItem('draft_task'))  // User data in logs

// âœ… SAFE: Log these instead
console.log('[Auth] User signed in')
console.log('[Tasks] Fetch completed:', data?.length, 'items')
console.log('[Error] Task creation failed:', error.code)
```

### 8.2 localStorage Safety

```typescript
// âœ… SAFE to store in localStorage:
// - UI preferences (theme, sidebar state)
// - Form drafts (temporary, no sensitive data)
// - Non-sensitive cache

// âŒ NEVER store in localStorage:
// - Auth tokens or sessions
// - API keys
// - PII (emails, phone numbers)
// - Financial data (raw amounts)

// Zustand persist middleware â€” only persist non-sensitive data
export const usePreferences = create(
  persist(
    (set) => ({
      theme: 'cyberpunk',       // âœ… Safe
      sidebarCollapsed: false,  // âœ… Safe
      defaultTaskFilter: 'all', // âœ… Safe
    }),
    {
      name: 'aria-preferences',
      partialize: (state) => ({
        // Only persist safe fields
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
)
```

### 8.3 User Data Display Rules

```typescript
// Display rules for user data
function UserProfile({ user }: { user: User }) {
  return (
    <div>
      <Avatar src={user.avatar_url} />  {/* âœ… Display safely */}
      <h2>{user.name}</h2>              {/* âœ… React-escaped */}
      {/* {user.email} */}               {/* âš ï¸ Display only if necessary */}
      {/* NEVER display: session tokens, API keys, raw database IDs */}
    </div>
  )
}
```

---

## 9. HTTP Security Headers

### 9.1 Complete Header Configuration

```javascript
// next.config.js
const securityHeaders = [
  // Prevent MIME type sniffing
  { key: 'X-Content-Type-Options', value: 'nosniff' },

  // Prevent clickjacking
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },

  // Enable XSS filter (legacy browsers)
  { key: 'X-XSS-Protection', value: '1; mode=block' },

  // HSTS â€” force HTTPS
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },

  // Referrer policy
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },

  // Permissions policy â€” restrict browser features
  { key: 'Permissions-Policy', value: [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'interest-cohort=()',
  ].join(', ') },

  // Content Security Policy (see Section 2)
  { key: 'Content-Security-Policy', value: cspDirectives.join('; ') },
]

module.exports = {
  async headers() {
    return [
      { source: '/(.*)', headers: securityHeaders },
      // Cache static assets aggressively
      {
        source: '/:all*(svg|png|jpg|jpeg|webp|woff|woff2)',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
    ]
  },
}
```

### 9.2 Header Validation

```bash
# Test headers using curl
curl -I https://your-app.vercel.app

# Expected response headers:
# Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# Content-Security-Policy: default-src 'self'; ...
# Referrer-Policy: strict-origin-when-cross-origin

# Use securityheaders.com for full audit
```

---

## 10. Security Checklist

### 10.1 Pre-Deployment Checklist

- [ ] CSP headers configured and tested
- [ ] All secrets in environment variables (not in code)
- [ ] No `NEXT_PUBLIC_` prefix on private variables
- [ ] `npm audit` passes (no high/critical vulnerabilities)
- [ ] No console.log of tokens or PII
- [ ] localStorage only stores non-sensitive data
- [ ] All forms use Supabase SDK (auto-CSRF protection)
- [ ] `dangerouslySetInnerHTML` not used without `DOMPurify`
- [ ] HTTPS enabled (Vercel/Railway defaults)
- [ ] HSTS configured

### 10.2 CI Security Gates

```yaml
# .github/workflows/ci.yml â€” security job
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
    - run: npm ci
    - run: npm audit --audit-level=high
    - run: npx eslint-plugin-security .
```

### 10.3 Incident Response (Security)

| Issue | Detection | Response |
|---|---|---|
| Token leak | Logs / user report | Revoke tokens via Supabase Dashboard |
| XSS vulnerability | CSP report / audit | Patch + deploy hotfix |
| Dependency CVE | Dependabot / npm audit | Update package, review usage |
| Suspicious activity | Supabase Audit Logs | Review logs, contact support |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-12 | Developer | Initial frontend security guide |
