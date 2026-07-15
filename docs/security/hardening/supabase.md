# Supabase Security Hardening Guide — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | SEC-HSU-001 |
| **Version** | 1.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal — Security |
| **Owner** | Developer |
| **Related Docs** | [SEC-HFA-001](fastapi.md), [SEC-HNE-001](nextjs.md), Database Schema (`docs/engineering/15_Database.md`), RLS Policies (`docs/engineering/Policies.md`) |

---

## Hardening Checklist

### 1. Row-Level Security (RLS) Policies

| Item | Status | Verification |
|---|---|---|
| RLS enabled on all user-owned tables | ✅ **Configured** | All 17 user tables have `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` |
| User isolation policy on every table | ✅ **Configured** | `FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id)` |
| No table allows cross-user reads | ✅ **Configured** | Verified in `docs/engineering/Policies.md` |
| Service role key restricted to backend | ⚠️ **Verify** | Service key (`SUPABASE_SERVICE_KEY`) used only server-side |
| Anonymous key has minimal permissions | ⚠️ **Verify** | Anon key (`SUPABASE_KEY`) limited to authenticated read |

**Verification steps:**
```sql
-- Run in Supabase SQL Editor to verify RLS is enabled
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename NOT LIKE '_prisma_migrations'
ORDER BY tablename;
-- Expected: all user tables show rowsecurity = true

-- Check RLS policies per table
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

### 2. Auth Provider Settings

| Item | Status | Verification |
|---|---|---|
| Google OAuth configured | ✅ **Configured** | Provider enabled in Supabase Dashboard |
| Redirect URIs match app domains | ⚠️ **Verify** | Check Supabase Dashboard → Authentication → Providers → Google |
| OAuth client secret stored in env | ✅ **Configured** | `GOOGLE_CLIENT_SECRET` in `.env` |
| Additional providers disabled if unused | ⚠️ **Verify** | Check Dashboard — disable GitHub, Discord, etc. if not used |
| Rate limiting on auth endpoints | ✅ **Configured** | Supabase handles auth rate limiting natively |

**Verification steps:**
```bash
# Check OAuth redirect URIs in Supabase Dashboard
# Navigate to: Authentication → Providers → Google
# Expected: http://localhost:3000, https://secondbrain-os.vercel.app

# Verify OAuth flow end-to-end
curl -s -o /dev/null -w "%{redirect_url}" "https://<project>.supabase.co/auth/v1/authorize?provider=google&redirect_to=http://localhost:3000"
```

---

### 3. Session Management

| Item | Status | Verification |
|---|---|---|
| JWT access token expiry configured | ✅ **Configured** | `settings.access_token_expire_minutes = 60` |
| Refresh token rotation enabled | ✅ **Configured** | Supabase default — `refresh_token` rotates on use |
| Session timeout enforced | ⚠️ **Needs Review** | Consider adding idle session timeout (e.g., 24h) |
| Token revocation on logout | ✅ **Configured** | `supabase.auth.signOut()` revokes session |
| API key revocation supported | ✅ **Configured** | `api_key_auth.py` — keys stored in `user_api_keys` table |

**Verification steps:**
```python
# Test session expiry
python -c "
from config.core.config import settings
print(f'Access token expiry: {settings.access_token_expire_minutes} min')
print(f'JWT algorithm: {settings.jwt_algorithm}')
print(f'Max retries: {settings.jwt_max_retries if hasattr(settings, \"jwt_max_retries\") else \"default\"}')
"
```

---

### 4. API Key Management

| Item | Status | Verification |
|---|---|---|
| `SUPABASE_URL` from environment | ✅ **Configured** | `settings.supabase_url` |
| `SUPABASE_KEY` (anon) from environment | ✅ **Configured** | `settings.supabase_key` |
| `SUPABASE_SERVICE_KEY` from environment | ✅ **Configured** | `settings.supabase_service_key` |
| Service key never exposed to client | ✅ **Configured** | Server-side only — `config/core/supabase.py` |
| Key rotation policy documented | ⚠️ **Needs Configuration** | Document rotation schedule in runbook |

**Verification steps:**
```bash
# Check that service key is NOT in frontend code
grep -rn "SUPABASE_SERVICE_KEY\|service_key" apps/web/ --include="*.{ts,tsx,js}" | wc -l
# Expected: 0

# Check that service key is NOT in client-side env files
grep "SUPABASE_SERVICE_KEY" apps/web/.env* 2>/dev/null || echo "No service key in frontend env files"
```

---

### 5. Network Restrictions

| Item | Status | Verification |
|---|---|---|
| Database connection limited to trusted sources | ⚠️ **Needs Configuration** | Enable in Supabase Dashboard → Database → Network Restrictions |
| IPv4 CIDR restrictions set | ⚠️ **Needs Configuration** | Restrict to Railway/Vercel egress IPs |
| IPv6 support verified | ⚠️ **Needs Configuration** | Check if provider supports IPv6 egress |
| SSL enforced for all connections | ✅ **Configured** | Supabase enforces TLS 1.2+ by default |

**Verification steps:**
```bash
# Check if network restrictions are enabled
# Supabase Dashboard → Database → Network Restrictions
# Expected: IP restrictions enabled for production

# Verify TLS connection
openssl s_client -connect <project>.supabase.co:5432 -servername <project>.supabase.co 2>&1 | grep "SSL handshake"
```

---

### 6. Backup Configuration

| Item | Status | Verification |
|---|---|---|
| Automated daily backups enabled | ✅ **Configured** | Supabase Pro plan includes daily backups |
| Point-in-time recovery (PITR) | ⚠️ **Needs Configuration** | Available on Pro plan — enable in Dashboard |
| Backup retention period verified | ✅ **Configured** | 7 days on Pro plan, 30 days on Team plan |
| Backup restore procedure documented | ⚠️ **Needs Configuration** | Document in runbook (`docs/operations/39_Runbooks.md`) |
| Pre-deployment backup procedure | ⚠️ **Needs Configuration** | `pg_dump` before schema migrations |

**Verification steps:**
```bash
# Check backup schedule
# Supabase Dashboard → Database → Backups
# Expected: Daily backup listed with timestamp

# Manual backup command (pre-migration)
pg_dump --dbname=postgresql://<user>:<password>@<host>:<port>/<db> --format=custom -f pre_migration_backup.dump
```

---

### 7. Audit Logging

| Item | Status | Verification |
|---|---|---|
| Supabase audit logs enabled | ✅ **Configured** | Available on Pro plan (Supabase Dashboard → Logs) |
| Application-level audit trail | ✅ **Configured** | `packages/shared/utils/audit.py` — logs all mutations |
| Audit retention period set | ⚠️ **Needs Review** | Check current retention (default: 7 days in Logs) |
| Authentication events logged | ✅ **Configured** | Supabase Auth logs all login/signup/logout events |
| Failed auth attempts tracked | ✅ **Configured** | Available in Supabase Auth Analytics |

**Verification steps:**
```bash
# Verify audit middleware is active
grep -n "audit_middleware_dispatch" apps/api/main.py

# Check audit log structure
python -c "
from shared.utils.audit import audit_middleware_dispatch
import inspect
src = inspect.getsource(audit_middleware_dispatch)
print('Audit middleware source loaded successfully')
"

# Query audit logs (Supabase SQL Editor)
-- SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;
```

---

## Quick Reference: Environment Variables

| Variable | Purpose | Required | Secured |
|---|---|---|---|
| `SUPABASE_URL` | Project URL | ✅ Yes | No (public) |
| `SUPABASE_KEY` | Anon key (public) | ✅ Yes | No (client-safe) |
| `SUPABASE_SERVICE_KEY` | Service role key (secret) | ✅ Yes | **Yes — server only** |
| `JWT_SECRET` | JWT signing secret | ✅ Yes | **Yes — never exposed** |
| `JWT_ALGORITHM` | JWT algorithm | ✅ Yes | No (HS256) |

---

## Production Checklist

Before production cutover, verify these Supabase items:

- [ ] RLS policies reviewed and tested on all 17 user tables
- [ ] Network restrictions enabled (source IP filtering)
- [ ] Automated backups confirmed running
- [ ] Point-in-time recovery enabled (PITR)
- [ ] Service role key rotation completed
- [ ] Auth provider redirect URIs updated for production domain
- [ ] Anonymous key permissions limited to `authenticated` role only
- [ ] Database connection pooling configured (PgBouncer)
- [ ] Supabase project has `app.secondbrain-os.com` in allowed origins
- [ ] Audit logs retention configured for compliance requirements

---

## Related Documents

| Document | Purpose |
|---|---|
| [SDL](../sdl.md) | Secure Development Lifecycle — overarching security methodology |
| [FastAPI Hardening](fastapi.md) | FastAPI-specific security hardening checklist |
| [Next.js Hardening](nextjs.md) | Next.js-specific security hardening checklist |
| [Security Architecture](../../security/24_Security.md) | Enterprise security architecture — Section 8 (Data Security) |
| [Database Schema](../../engineering/15_Database.md) | All tables, RLS policies, indexes |
| [AGENTS.md](../../../AGENTS.md) | Master project reference — Section 7 (Database Schema), Section 23 (Security Compliance) |
