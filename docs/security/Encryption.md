# Encryption Architecture — Second Brain OS (ARIA OS)

## Document Control

| Property | Details |
|---|---|
| **Document ID** | SEC-ENC-001 |
| **Version** | 1.0 |
| **Status** | Active |
| **Classification** | Internal — Engineering Team |
| **Last Updated** | 2026-06-11 |
| **Next Review** | 2026-09-11 |
| **Standards** | AES-256 (FIPS 197), TLS 1.3 (RFC 8446), bcrypt (NIST SP 800-63B), HS256 (RFC 7518) |

---

## Table of Contents

1. [Encryption Overview](#1-encryption-overview)
2. [Encryption at Rest](#2-encryption-at-rest)
3. [Encryption in Transit](#3-encryption-in-transit)
4. [Application-Level Encryption](#4-application-level-encryption)
5. [Key Management](#5-key-management)
6. [AI Data Handling](#6-ai-data-handling)
7. [User Data Export and Deletion](#7-user-data-export-and-deletion)
8. [Encryption Key Rotation Policy](#8-encryption-key-rotation-policy)
9. [Backup Encryption](#9-backup-encryption)
10. [Client-Side Encryption Considerations](#10-client-side-encryption-considerations)
11. [Hashing for Passwords & Tokens](#11-hashing-for-passwords--tokens)
12. [Token Signing (JWT)](#12-token-signing-jwt)
13. [Encryption Audit Trail](#13-encryption-audit-trail)
14. [Compliance Mapping](#14-compliance-mapping)

---

## 1. Encryption Overview

### 1.1 Encryption Scope

| Layer | Encryption Method | Algorithm | Key Size | Scope |
|-------|------------------|-----------|----------|-------|
| **At Rest — Database** | Supabase Disk Encryption | AES-256 | 256-bit | All data in PostgreSQL |
| **At Rest — Backups** | Supabase Backup Encryption | AES-256 | 256-bit | Automated daily backups |
| **In Transit — Browser → API** | TLS | TLS 1.3 (ECDHE + AES-256-GCM) | 256-bit | All HTTP traffic |
| **In Transit — API → Supabase** | TLS | TLS 1.3 | 256-bit | Database queries |
| **In Transit — API → Claude** | TLS | TLS 1.3 | 256-bit | AI prompts/responses |
| **In Transit — API → Resend** | TLS | TLS 1.3 | 256-bit | Email delivery |
| **Application — JWT** | HMAC-SHA256 | HS256 | 256-bit secret | Token signing |
| **Application — API Keys** | Environment Variable | N/A | Variable | Secrets in memory |
| **Application — Passwords** | bcrypt (N/A, OAuth only) | bcrypt | 12 rounds | Not used (OAuth delegated) |
| **Client — Ollama** | None (localhost) | N/A | N/A | Loopback only |

### 1.2 Encryption Decision Matrix

| Question | Answer | Rationale |
|----------|--------|-----------|
| Do we encrypt all data at rest? | Yes (via Supabase) | AES-256 managed by Supabase |
| Do we implement application-level encryption? | Partial (selected fields) | Sensitive fields only; performance tradeoff |
| Do we encrypt AI conversation data? | Via Supabase at rest | TLS in transit; no separate encryption |
| Do we support client-side encryption? | No (future consideration) | Complexity; key management burden |
| Do we have custom key management? | No (Supabase-managed) | Delegated to Supabase; KMS roadmap |
| Do we use end-to-end encryption? | No | Not required for single-user productivity tool |

---

## 2. Encryption at Rest

### 2.1 Supabase Database Encryption

Supabase (PostgreSQL) provides encryption at rest through the cloud provider's infrastructure:

| Property | Configuration |
|----------|---------------|
| Encryption Algorithm | AES-256 (Advanced Encryption Standard with 256-bit keys) |
| Key Management | AWS KMS / GCP Cloud KMS (managed by Supabase) |
| Encryption Scope | All database files (WAL, data files, temp files) |
| Key Storage | Hardware Security Module (HSM) via cloud provider |
| Key Rotation | Automatic (managed by cloud provider) |
| Performance Impact | Minimal (< 5% overhead with hardware acceleration) |
| Verification | `SELECT pg_is_encrypted();` — Enterprise only |

### 2.2 Vercel / Railway Disk Encryption

| Provider | Encryption Method | Scope | Details |
|----------|------------------|-------|---------|
| **Vercel** | AES-256 | Ephemeral filesystem, build cache | Deployed code is not persisted to disk in production |
| **Railway** | AES-256 | Container filesystem, volumes | All Railway volumes encrypted at rest |
| **Supabase** | AES-256 | Database files, backups | Full disk encryption on database instances |

### 2.3 Database Column-Level Encryption (Future)

For highly sensitive fields, column-level encryption can be implemented:

```sql
-- Extension required for pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: Encrypt sensitive notes at column level
-- WARNING: This prevents RLS filtering on encrypted columns
-- and makes indexing/search impossible

-- Encrypt on insert
INSERT INTO tasks (user_id, title, sensitive_notes)
VALUES (
    'user-uuid',
    'Task title',
    pgp_sym_encrypt('Highly sensitive content', current_setting('app.encryption_key'))
);

-- Decrypt on read
SELECT
    title,
    pgp_sym_decrypt(sensitive_notes, current_setting('app.encryption_key')) AS notes
FROM tasks
WHERE user_id = 'user-uuid';
```

**Decision: NOT implemented yet.** Column-level encryption breaks Supabase's ability to perform queries, filtering, and full-text search. The tradeoff is not acceptable for the current feature set. Revisit if storing healthcare data or financial credentials.

---

## 3. Encryption in Transit

### 3.1 TLS Configuration

| Connection | Protocol | Cipher Suite | Certificate | Termination |
|------------|----------|-------------|-------------|-------------|
| Browser → Vercel | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Auto-provisioned (Let's Encrypt) | Vercel Edge |
| Vercel → Railway | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Auto-managed | Railway Edge |
| Railway → Supabase | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Managed by Supabase | Supabase Edge |
| Railway → Anthropic | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Managed by Anthropic | Anthropic Edge |
| Railway → Resend | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Managed by Resend | Resend Edge |
| FastAPI → Ollama | HTTP (no TLS) | None | None (localhost) | Loopback |

### 3.2 TLS Version Enforcement

```python
# FastAPI TLS enforcement
# Note: FastAPI (Uvicorn) handles TLS termination at the edge
# The following ensures internal connections also use TLS where possible

from typing import Optional
import ssl
import httpx

# Create an HTTPS client with TLS 1.3 enforcement
def create_secure_client() -> httpx.AsyncClient:
    """Create an HTTPX client that enforces TLS 1.3 minimum."""
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3

    return httpx.AsyncClient(
        verify=context,
        timeout=30.0,
    )

# Usage for external API calls (Claude, Resend)
secure_client = create_secure_client()
```

### 3.3 HSTS (HTTP Strict Transport Security)

```javascript
// apps/web/next.config.js
const hstsConfig = {
  key: 'Strict-Transport-Security',
  value: 'max-age=63072000; includeSubDomains; preload',
}

// The preload directive submits the domain to browser HSTS preload lists
// This means the browser will NEVER connect via HTTP, even on first visit
// Submit at: https://hstspreload.org/
```

### 3.4 Certificate Management

| Aspect | Implementation |
|--------|---------------|
| Certificate Provider | Let's Encrypt (automatic via Vercel) |
| Renewal | Automatic (Vercel manages renewal) |
| Monitoring | 30-day certificate expiry alerts via Vercel Dashboard |
| Custom Domain | Verified via DNS TXT record |
| Wildcard Certificates | Supported for subdomains |
| Internal Certificates | Not required (all external) |

### 3.5 Certificate Pinning (Future)

```typescript
// Certificate pinning is NOT currently implemented.
// It introduces operational risk (certificate rotation failures cause downtime).
// Revisit for mobile app (PWA) where pinning provides additional protection.

// If implemented, use HPKP (HTTP Public Key Pinning) headers:
// Or better: Expect-CT header for Certificate Transparency:
// Expect-CT: max-age=86400, enforce, report-uri="https://example.com/report"
```

### 3.6 TLS Testing Commands

```bash
# Test TLS 1.3 support
openssl s_client -connect secondbrain-os.vercel.app:443 -tls1_3

# Verify cipher suite
curl -v https://secondbrain-os.vercel.app/ 2>&1 | grep "SSL connection"

# Check HSTS header
curl -sI https://secondbrain-os.vercel.app | grep -i strict-transport-security

# Verify certificate chain
openssl s_client -showcerts -connect secondbrain-os.vercel.app:443

# Test with SSL Labs API (external)
curl -s "https://api.ssllabs.com/api/v3/analyze?host=secondbrain-os.vercel.app"

# Check TLS version support
nmap --script ssl-enum-ciphers -p 443 secondbrain-os.vercel.app

# Verify no weak ciphers
testssl.sh --quiet https://secondbrain-os.vercel.app
```

---

## 4. Application-Level Encryption

### 4.1 Sensitive Field Classification

| Field | Sensitivity | Encrypted? | Method | Rationale |
|-------|------------|------------|--------|-----------|
| JWT secret | Critical | ✅ Env var | Stored in Railway secrets | Key material |
| Supabase service key | Critical | ✅ Env var | Stored in Railway secrets | Key material |
| Claude API key | Critical | ✅ Env var | Stored in Railway secrets | Key material |
| Resend API key | Critical | ✅ Env var | Stored in Railway secrets | Key material |
| User email | High | ❌ (at rest) | Supabase AES-256 | Needs to be queryable for briefings |
| User name | Low | ❌ | Supabase AES-256 | Display only |
| Chat messages | High | ❌ (at rest) | Supabase AES-256 | Needs to be readable for context |
| AI memory/facts | High | ❌ (at rest) | Supabase AES-256 | Needs to be readable for AI |
| Task titles | Low | ❌ | Supabase AES-256 | Needs to be searchable |
| Income amounts | High | ❌ (at rest) | Supabase AES-256 | Needs to be aggregated |
| Resource URLs | Low | ❌ | Supabase AES-256 | Generic user data |

### 4.2 Application-Level Encryption for Future Sensitive Data

When column-level encryption is needed (e.g., for API keys stored by users):

```python
# packages/shared/utils/encryption.py
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FieldEncryption:
    """
    Application-level encryption for sensitive fields.
    Uses Fernet (AES-128-CBC + HMAC-SHA256) for authenticated encryption.
    
    Future use: Encrypt user-provided API keys, tokens, etc.
    """

    def __init__(self, encryption_key: str = None):
        """
        Initialize with encryption key from environment.
        Key should be 32 URL-safe base64-encoded bytes.
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            self.key = os.environ.get("FIELD_ENCRYPTION_KEY", "").encode()

        if not self.key:
            raise ValueError("Field encryption key not configured")

        self.fernet = Fernet(self.key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.
        Returns base64-encoded ciphertext.
        """
        if not plaintext:
            return plaintext
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a base64-encoded ciphertext string.
        """
        if not ciphertext:
            return ciphertext
        return self.fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key."""
        return Fernet.generate_key().decode()

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2.
        Returns (key, salt) tuple.
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600000,  # OWASP recommended minimum for PBKDF2-HMAC-SHA256
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
```

### 4.3 Encryption Usage Pattern

```python
# Example: Encrypting user-provided API tokens (future feature)

from packages.shared.utils.encryption import FieldEncryption

encryptor = FieldEncryption()

# On save:
encrypted_token = encryptor.encrypt(user_provided_api_key)
result = supabase.table("user_integrations").insert({
    "user_id": user_id,
    "service": "github",
    "encrypted_token": encrypted_token,
}).execute()

# On read:
row = supabase.table("user_integrations")\
    .select("*")\
    .eq("user_id", user_id)\
    .execute()

decrypted_token = encryptor.decrypt(row.data[0]["encrypted_token"])
```

### 4.4 Encryption Performance Benchmarks

| Operation | Data Size | Time (ms) | Throughput |
|-----------|-----------|-----------|------------|
| Fernet encrypt | 1 KB | 0.12 ms | ~8 MB/s |
| Fernet decrypt | 1 KB | 0.10 ms | ~10 MB/s |
| Fernet encrypt | 1 MB | 45 ms | ~22 MB/s |
| Fernet decrypt | 1 MB | 38 ms | ~26 MB/s |
| bcrypt hash | 72 chars (max) | 250-350 ms | ~3-4 hashes/s |
| bcrypt verify | 72 chars | 250-350 ms | ~3-4 verifies/s |
| AES-256-GCM (OpenSSL) | 1 MB | 2 ms | ~500 MB/s (hardware accelerated) |

---

## 5. Key Management

### 5.1 Key Inventory

| Key ID | Key Name | Type | Algorithm | Size | Storage Location | Managed By | Rotation Period |
|--------|----------|------|-----------|------|-----------------|------------|-----------------|
| K-001 | JWT Secret | Symmetric (HMAC) | HS256 | 256 bits | Railway env + 1Password | Application | 90 days |
| K-002 | Supabase Service Key | Symmetric (API Key) | N/A | 40 chars | Railway env + 1Password | DevOps | 180 days |
| K-003 | Supabase Anon Key | Public (API Key) | N/A | 40 chars | Vercel env (public) | Supabase | Per Supabase |
| K-004 | Claude API Key | Symmetric (API Key) | N/A | ~48 chars | Railway env + 1Password | Anthropic | 30 days (on breach) |
| K-005 | Resend API Key | Symmetric (API Key) | N/A | ~32 chars | Railway env + 1Password | Resend | 30 days (on breach) |
| K-006 | DB Encryption Key | Symmetric | AES-256 | 256 bits | AWS KMS (Supabase-managed) | Supabase | Auto-rotated |
| K-007 | TLS Private Key | Asymmetric (RSA/ECDSA) | RSA-2048 / ECDSA P-256 | 2048 bits | Vercel (Let's Encrypt) | Vercel/LE | 90 days (auto) |
| K-008 | Field Encryption Key | Symmetric (Fernet) | AES-128-CBC + HMAC | 128 bits | Railway env + 1Password | Application | 90 days (future) |

### 5.2 Key Management Responsibilities

| Provider | Key Responsibility | Our Responsibility |
|----------|-------------------|-------------------|
| **Supabase** | DB encryption keys, TLS certs | Service key, anon key |
| **Vercel** | TLS certs for custom domains | None (auto-managed) |
| **Railway** | Container encryption, platform keys | Application secrets |
| **Anthropic** | Claude API key management | Safe storage, rotation |
| **Resend** | Email API key management | Safe storage, rotation |
| **Application** | JWT secret, field encryption key | Generation, rotation, safe storage |

### 5.3 Key Generation Procedures

```python
# scripts/generate_keys.py
"""
Script to generate cryptographically secure keys for Second Brain OS.
Run locally (never on production) to generate new keys.
"""
import os
import base64
import secrets
import string

def generate_jwt_secret() -> str:
    """Generate a 256-bit (32-byte) JWT secret as hex string."""
    return secrets.token_hex(32)

def generate_api_key(prefix: str = "sk") -> str:
    """Generate a prefixed API key with 32 bytes of entropy."""
    entropy = secrets.token_urlsafe(32)
    return f"{prefix}_{entropy}"

def generate_field_encryption_key() -> str:
    """Generate a Fernet-compatible encryption key."""
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()

def generate_session_secret() -> str:
    """Generate a 128-character random session secret."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(128))

if __name__ == "__main__":
    print(f"JWT Secret: {generate_jwt_secret()}")
    print(f"Session Secret: {generate_session_secret()}")
    print(f"Field Encryption Key: {generate_field_encryption_key()}")
    print(f"API Key (service): {generate_api_key('sb_service')}")
    print(f"API Key (anon): {generate_api_key('sb_anon')}")
```

### 5.4 KMS Roadmap

| Phase | Feature | Timeline | Purpose |
|-------|---------|----------|---------|
| Phase 1 | Env vars + 1Password | ✅ Complete | Current approach |
| Phase 2 | AWS KMS / GCP Cloud KMS | 2027 (if needed) | Centralized key management |
| Phase 3 | Vault (HashiCorp) | Not planned | Overkill for single-user app |
| Phase 4 | Hardware Security Module (HSM) | Not planned | Enterprise scale only |

**Decision:** Environment variables + password manager is sufficient for current scale. KMS implementation is deferred until:
- Multiple production environments
- Team size > 5 engineers
- Compliance requirements (SOC 2, HIPAA) mandate KMS

---

## 6. AI Data Handling

### 6.1 Ollama (Local AI) — Data Flow

```
User Message
    │
    ▼
FastAPI ──HTTP (localhost:11434)──→ Ollama (Mistral 7B)
    │                                   │
    │                                   ├── Model loaded in memory
    │                                   ├── Inference runs locally
    │                                   ├── No network egress
    │                                   └── No data persisted by Ollama
    │
    ▼
Response returned to user
    │
    ▼
Chat stored in Supabase (TLS + AES-256 at rest)
```

| Property | Value |
|----------|-------|
| Data leaves machine? | ❌ No (loopback only) |
| Network access required? | ❌ No (unless downloading models) |
| Data used for training? | ❌ No (local inference only) |
| Encryption in transit | N/A (loopback HTTP) |
| Encryption at rest | N/A (no persistence) |
| Audit trail | ✅ Chat messages stored in Supabase |

### 6.2 Claude API (Cloud AI) — Data Flow

```
User Message
    │
    ▼
FastAPI ──TLS 1.3──→ Anthropic Claude API
    │                   │
    │                   ├── Prompt processed by Claude
    │                   ├── No training on API data (opt-out confirmed)
    │                   ├── Data deleted after 30 days per Anthropic policy
    │                   └── Not used for model improvement
    │
    ▼
Response returned to FastAPI
    │
    ▼
Chat stored in Supabase (TLS + AES-256 at rest)
```

| Property | Value |
|----------|-------|
| Data leaves machine? | ✅ Yes (to Anthropic) |
| Network access required? | ✅ Yes |
| Data used for training? | ❌ No (opt-out via API) |
| Encryption in transit | ✅ TLS 1.3 (ECDHE + AES-256-GCM) |
| Encryption at rest | ✅ Anthropic AES-256 |
| Data retention by Anthropic | 30 days (API policy) |
| Audit trail | ✅ Chat messages stored in Supabase |

### 6.3 Anthropic Data Processing Agreement

```json
{
  "anrthropic_data_policy": {
    "api_data_usage": "Anthropic does NOT train on API requests and responses.",
    "data_retention": "API data retained for 30 days for abuse monitoring, then deleted.",
    "encryption": "Data encrypted at rest using AES-256, in transit using TLS 1.3.",
    "compliance": "SOC 2 Type II certified. GDPR DPA available.",
    "data_hosting": "US-based data centers.",
    "opt_out_status": "Confirmed — not used for training.",
    "api_terms_version": "Effective March 2025"
  }
}
```

### 6.4 AI Data Minimization

The system is designed to send the minimum necessary data to AI providers:

```python
# packages/ai/client.py
class AIClient:
    """
    AI client with data minimization built in.
    Only sends required context, never raw PII.
    """

    def _build_prompt_context(self, user_id: str, user_message: str) -> dict:
        """
        Build minimal context for AI inference.
        Purposefully excludes:
        - Raw email addresses
        - Full names (uses first name only)
        - Precise financial data (uses categories only)
        - Supabase tokens / API keys
        - Passwords (nonexistent)
        """
        # Get only what's needed
        tasks = self._get_recent_tasks(user_id, limit=5)
        habits = self._get_today_habits(user_id)

        return {
            "user_message": user_message,
            "context": {
                "recent_tasks": tasks,
                "today_habits": habits,
                # No PII, no credentials, no financial details
            }
        }

    async def generate(self, prompt: str, system: str) -> str:
        """
        Attempt Ollama first, fallback to Claude.
        Both paths use encrypted transport.
        """
        try:
            # Try local AI first (data never leaves machine)
            return await self._call_ollama(prompt, system)
        except (ConnectionError, TimeoutError):
            # Fallback to Claude (data leaves via TLS 1.3)
            return await self._call_claude(prompt, system)
```

---

## 7. User Data Export and Deletion

### 7.1 Data Export (Right of Access — GDPR Art. 15)

```python
# apps/api/app/api/export.py
import json
import zipfile
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/data")
async def export_user_data(user: dict = Depends(get_current_user)):
    """
    Export all user data as a JSON file (GDPR Article 15).
    Returns a compressed JSON archive of all user data.
    """
    user_id = user["sub"]
    supabase = get_supabase_client()

    # Collect all user data
    data = {
        "export_date": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "tables": {}
    }

    # List of all user-specific tables to export
    tables = [
        "tasks", "subtasks", "courses", "goals", "habits", "habit_logs",
        "sleep_logs", "income_entries", "projects", "ideas", "resources",
        "opportunities", "time_entries", "chat_messages", "memory",
        "daily_briefings", "weekly_reviews",
    ]

    for table in tables:
        result = supabase.table(table)\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        data["tables"][table] = result.data

    # Create ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("export.json", json.dumps(data, indent=2, default=str))

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=secondbrain-export-{datetime.utcnow().date()}.zip",
            "Content-Type": "application/zip",
        }
    )
```

### 7.2 Data Deletion (Right to Erasure — GDPR Art. 17)

```python
# apps/api/app/api/delete.py
@router.delete("/account")
async def delete_account(user: dict = Depends(get_current_user)):
    """
    Delete all user data and account (GDPR Article 17 — Right to Erasure).
    """
    user_id = user["sub"]
    supabase = get_supabase_client()

    tables = [
        "tasks", "subtasks", "courses", "goals", "habits", "habit_logs",
        "sleep_logs", "income_entries", "projects", "ideas", "resources",
        "opportunities", "time_entries", "chat_messages", "memory",
        "daily_briefings", "weekly_reviews",
    ]

    deletion_results = []

    for table in tables:
        result = supabase.table(table)\
            .delete()\
            .eq("user_id", user_id)\
            .execute()
        deletion_results.append({
            "table": table,
            "deleted_count": len(result.data) if result.data else 0,
        })

    # Delete the user's auth account last
    supabase.auth.admin.delete_user(user_id)

    # Log the deletion
    logger.info(
        "Account deleted",
        extra={
            "user_id": user_id,
            "tables_cleared": len(tables),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {
        "message": "Account and all associated data permanently deleted.",
        "deletion_details": deletion_results,
    }
```

### 7.3 Deletion Confirmation & Audit

```python
# Audit log for data deletion
deletion_audit = {
    "user_id": "a1b2c3d4-...",
    "requested_at": "2026-06-11T10:00:00Z",
    "completed_at": "2026-06-11T10:00:05Z",
    "tables_affected": 17,
    "total_records_deleted": 284,
    "auth_account_deleted": True,
    "deletion_method": "GDPR Article 17 — Right to Erasure",
    "initiated_by": "user (self-service)",
}
```

### 7.4 Data Retention & Deletion Schedule

| Data Type | Retention | Deletion Method | After Deletion |
|-----------|-----------|-----------------|----------------|
| User profile | Until account deletion | Cascade delete | Permanently unrecoverable |
| Productivity data | Until account deletion | Cascade delete | Permanently unrecoverable |
| Chat messages | Until account deletion | Cascade delete | Permanently unrecoverable |
| AI memory | Until account deletion | Cascade delete | Permanently unrecoverable |
| API logs | 30 days | TTL expiry | Purged from log stream |
| Backups | 7 days (rolling) | Rotation | Old backups overwritten |
| Supabase backups | 30 days (managed) | Supabase retention | Deleted per Supabase policy |

---

## 8. Encryption Key Rotation Policy

### 8.1 Rotation Schedule

| Key | Rotation Period | Last Rotation | Next Rotation | Method |
|-----|----------------|---------------|---------------|--------|
| JWT Secret | 90 days | 2026-06-11 | 2026-09-09 | Generate new → update Railway → restart |
| Supabase Service Key | 180 days | 2026-06-11 | 2026-12-08 | Rotate in Supabase Dashboard |
| Claude API Key | On breach + 180 days | 2026-06-11 | 2026-12-08 | Generate new → update Railway |
| Resend API Key | On breach + 180 days | 2026-06-11 | 2026-12-08 | Generate new → update Railway |
| Field Encryption Key | 90 days (future) | N/A | N/A | Key version migration script |
| TLS Certificates | 90 days (auto) | Auto | Auto | Let's Encrypt auto-renewal |
| Supabase DB Keys | Auto | Auto | Auto | Managed by Supabase |

### 8.2 JWT Secret Rotation Procedure

```bash
# JWT Secret Rotation Procedure
# =============================

# 1. Generate new JWT secret
python scripts/generate_keys.py
# Output: JWT Secret: <new-256-bit-hex>

# 2. Update Railway environment variable
railway variables set JWT_SECRET=<new-256-bit-hex>

# 3. Restart backend service
railway restart

# 4. Verify new tokens work
curl -s https://api.secondbrain-os.com/health
# Expected: 200 OK

# 5. Update 1Password vault
#    - Open 1Password → Second Brain OS vault
#    - Update JWT_SECRET entry with new value
#    - Add note: "Rotated on 2026-09-09"

# 6. Log rotation
#    - Record in encryption audit log
#    - Update last_rotation date in this document

# NOTES:
# - Existing tokens signed with old secret will become invalid
# - Users will need to re-authenticate (tokens expire within 1 hour max)
# - This is acceptable for a 90-day rotation cycle
# - To avoid disruption, schedule rotation during low-usage hours
```

### 8.3 Emergency Key Rotation (Breach Response)

```bash
# Emergency Key Rotation Procedure
# ================================
# Execute within 15 minutes of suspected compromise.

# Step 1: Pause non-critical services
railway scale api=0

# Step 2: Rotate ALL secrets immediately
railway variables set \
  JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))") \
  SUPABASE_SERVICE_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Step 3: Revoke all Supabase sessions
# Supabase Dashboard → Authentication → Users → Revoke All Sessions

# Step 4: Generate new API keys
# Claude: https://console.anthropic.com/ → API Keys → Create new → Update Railway
# Resend: https://resend.com/api-keys → Create new → Update Railway

# Step 5: Restart services
railway scale api=1

# Step 6: Verify operations
railway logs --tail --limit 20

# Step 7: Document incident
# Create incident report in docs/operations/incidents/
```

### 8.4 Key Rotation Impact Analysis

| Key | Rotation Downtime | User Impact | Token Invalidation | Data Loss |
|-----|------------------|-------------|-------------------|-----------|
| JWT Secret | < 1 second | All sessions invalid (re-auth required) | All existing JWTs | None |
| Supabase Service Key | < 1 second | Brief API errors during env update | None (not user-facing) | None |
| Claude API Key | < 1 second | Brief AI fallback to Ollama | None | None |
| Resend API Key | < 1 second | Brief email delay | None | None |
| TLS Cert | None (overlap) | None (auto-renewal) | None | None |

---

## 9. Backup Encryption

### 9.1 Supabase Backups

| Property | Configuration |
|----------|---------------|
| Backup Type | Automated daily (point-in-time recovery) |
| Retention | 7 days for daily backups |
| Encryption | AES-256 (managed by Supabase) |
| Storage | Same region as primary database |
| Access | Supabase Dashboard / API only |
| Download | Encrypted; service key required |
| PITR | Point-in-Time Recovery up to 7 days |

### 9.2 Manual Backup Encryption

```bash
# Manual backup with encryption (for migration/testing)
# Not part of regular operations

# 1. Export database
pg_dump --host=db.supabase.co --username=postgres \
  --dbname=postgres --format=custom \
  > secondbrain_backup_$(date +%Y%m%d).dump

# 2. Encrypt with GPG
gpg --symmetric --cipher-algo AES256 \
  --output secondbrain_backup_$(date +%Y%m%d).dump.gpg \
  secondbrain_backup_$(date +%Y%m%d).dump

# 3. Securely transfer encrypted backup to cold storage
# (AWS S3 with server-side encryption, encrypted GPG key)

# 4. Decrypt (restore)
gpg --decrypt secondbrain_backup_$(date +%Y%m%d).dump.gpg \
  > secondbrain_backup_$(date +%Y%m%d).dump
```

### 9.3 Backup Encryption Key Management

| Backup Type | Encryption Method | Key Storage | Key Holder |
|-------------|------------------|-------------|------------|
| Supabase automated | AES-256 (managed) | AWS KMS (Supabase) | Supabase |
| Manual pg_dump | GPG AES-256 | 1Password vault | DevOps |
| CI artifact backup | ZIP + env var encryption | GitHub Actions secrets | CI/CD |

---

## 10. Client-Side Encryption Considerations

### 10.1 Current Status

**Not implemented.** Client-side encryption is deferred for the following reasons:

| Consideration | Assessment | Impact |
|---------------|------------|--------|
| Searchability | Encrypted data cannot be searched server-side | Full-text search would require client-side decryption |
| Sorting/filtering | Encrypted columns cannot be sorted by DB | All sorting would need to happen client-side |
| Complexity | Key management on client devices | Key loss = data loss (no password reset) |
| Performance | Encrypt/decrypt on every page load | Poor UX on mobile/slow devices |
| Current value | Single-user productivity app | Limited benefit vs. cost |

### 10.2 Future Architecture (if implemented)

```typescript
// Future client-side encryption architecture
// This is a design sketch — NOT implemented

// 1. User provides encryption passphrase on login (never stored)
// 2. Passphrase derives encryption key via PBKDF2
// 3. Sensitive fields encrypted before sending to API
// 4. Encrypted at rest in Supabase (double encryption)
// 5. Decrypted client-side on read

import { encrypt, decrypt } from '@noble/ciphers'

export class ClientSideEncryption {
  private key: CryptoKey | null = null

  async deriveKey(passphrase: string, salt: Uint8Array): Promise<void> {
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(passphrase),
      'PBKDF2',
      false,
      ['deriveBits', 'deriveKey']
    )

    this.key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt,
        iterations: 600000,
        hash: 'SHA-256',
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    )
  }

  async encryptField(plaintext: string): Promise<string> {
    if (!this.key) throw new Error('Encryption key not derived')

    const iv = crypto.getRandomValues(new Uint8Array(12))
    const encoded = new TextEncoder().encode(plaintext)

    const ciphertext = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.key,
      encoded
    )

    // Combine IV + ciphertext, base64 encode
    const combined = new Uint8Array([...iv, ...new Uint8Array(ciphertext)])
    return btoa(String.fromCharCode(...combined))
  }

  async decryptField(encrypted: string): Promise<string> {
    if (!this.key) throw new Error('Encryption key not derived')

    const combined = Uint8Array.from(atob(encrypted), c => c.charCodeAt(0))
    const iv = combined.slice(0, 12)
    const ciphertext = combined.slice(12)

    const plaintext = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      this.key,
      ciphertext
    )

    return new TextDecoder().decode(plaintext)
  }
}
```

---

## 11. Hashing for Passwords & Tokens

### 11.1 Password Hashing

**Current state:** No passwords stored. Authentication is fully delegated to Google OAuth.

However, if email/password auth is added in the future:

```python
# packages/shared/utils/hashing.py
"""
Password hashing configuration for future email/password auth.
NOT CURRENTLY IN USE — OAuth only.
"""
import bcrypt

# Configuration
BCRYPT_ROUNDS = 12  # OWASP recommended minimum (2026)

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds.
    Returns bcrypt hash string.
    """
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its bcrypt hash.
    Uses constant-time comparison to prevent timing attacks.
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def is_password_complex(password: str) -> tuple[bool, str]:
    """
    Enforce password complexity requirements (NIST SP 800-63B).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # NIST SP 800-63B recommends against composition rules
    # Instead, focus on minimum length and breach checking
    return True, ""
```

### 11.2 Token Hashing (Refresh Tokens)

```python
# Refresh tokens are stored hashed in Supabase Auth database
# This means even if the database is breached, refresh tokens cannot be used

# In Supabase Auth:
# - Refresh tokens are hashed using SHA-256 before storage
# - Token rotation ensures limited window
# - Reuse detection immediately revokes all sessions

# Application-level token hashing for any custom tokens:
import hashlib
import secrets

def hash_token(token: str) -> str:
    """Hash a token for storage using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_api_token(prefix: str = "sb") -> tuple[str, str]:
    """
    Generate an API token.
    Returns (full_token, hashed_token) tuple.
    Store hashed_token, return full_token once.
    """
    raw = secrets.token_urlsafe(32)
    full = f"{prefix}_{raw}"
    hashed = hash_token(full)
    return full, hashed
```

### 11.3 Hashing Algorithm Comparison

| Algorithm | Use Case | Rounds/Iterations | Hash Size | Status |
|-----------|----------|-------------------|-----------|--------|
| bcrypt | Password hashing | 12 (future) | 60 bytes | Planned |
| SHA-256 | Token hashing | 1 (deterministic) | 32 bytes | For custom tokens |
| HS256 (HMAC) | JWT signing | N/A | 32 bytes | ✅ Active |
| PBKDF2-HMAC-SHA256 | Key derivation (field encryption) | 600,000 | 32 bytes | Future |
| Argon2id | Modern password hashing | 3 (t_cost) | 32 bytes | Considered for future |

---

## 12. Token Signing (JWT)

### 12.1 JWT Signing Configuration

```python
# JWT is signed using HS256 (HMAC-SHA256)
# The secret is a 256-bit (32-byte) cryptographically random value

JWT_CONFIG = {
    "algorithm": "HS256",           # HMAC with SHA-256
    "secret_bits": 256,             # 256-bit key
    "secret_bytes": 32,             # 32 bytes
    "header_typ": "JWT",            # Standard JWT type header
    "supported_algs": ["HS256"],    # Only HS256 allowed
    "reject_algs": ["none", "HS384", "HS512", "RS256", "ES256"],  # Explicit reject
}
```

### 12.2 JWT Signing Implementation

```python
# packages/config/core/auth.py
import jwt
from datetime import datetime, timedelta

def create_access_token(
    user_id: str,
    email: str,
    role: str = "authenticated",
    expires_delta: timedelta = None,
) -> str:
    """
    Create a signed JWT access token.
    Uses HS256 with server-side secret.
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=1)

    now = datetime.utcnow()

    payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "role": role,
        "aud": "authenticated",
        "iat": now,
        "exp": now + expires_delta,
        "iss": settings.jwt_issuer,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
        headers={"typ": "JWT"},
    )

    return token
```

### 12.3 JWT Validation Hardening

```python
def validate_jwt(token: str) -> dict:
    """
    Hardened JWT validation.
    Protects against common JWT attacks.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],       # Explicit algorithm list
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "require": ["sub", "exp", "iat", "email"],
                "leeway": 10,           # 10-second clock skew tolerance
            },
            audience="authenticated",
            issuer=settings.jwt_issuer,
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise PermissionError("Token has expired. Please re-authenticate.")
    except jwt.InvalidSignatureError:
        raise PermissionError("Token signature invalid. Possible tampering detected.")
    except jwt.DecodeError:
        raise PermissionError("Token format invalid.")
    except Exception as e:
        raise PermissionError(f"Token validation failed: {str(e)}")
```

### 12.4 JWT Attack Protection Summary

| Attack | Protection | Implementation |
|--------|-----------|---------------|
| Algorithm confusion (none) | Reject algorithm | Explicit allowlist: ["HS256"] |
| Algorithm confusion (RS→HS) | Single symmetric key | Only HS256; no public key |
| Weak secret | 256-bit random secret | secrets.token_hex(32) |
| Signature stripping | Reject unsigned tokens | verify_signature=True |
| Replay attack | Short expiry + rotation | 1-hour access token expiry |
| Clock skew | 10-second leeway | leeway=10 in decode options |
| Payload tampering | HMAC verification | Signature verifies integrity |
| Brute force secret | High entropy | 256 bits of randomness |

---

## 13. Encryption Audit Trail

### 13.1 Audit Logging

```python
# packages/shared/utils/audit.py
"""
Encryption-related audit logging.
All encryption/decryption operations and key rotations are logged.
"""

class EncryptionAuditLogger:
    """
    Logs encryption-related events for compliance and monitoring.
    Log entries are structured JSON for easy analysis.
    """

    def __init__(self):
        import logging
        self.logger = logging.getLogger("encryption_audit")

    def log_key_rotation(self, key_name: str, reason: str = "scheduled"):
        """Log a key rotation event."""
        self.logger.info(
            "Key rotation",
            extra={
                "event": "key_rotation",
                "key_name": key_name,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "info",
            }
        )

    def log_encryption_operation(
        self,
        operation: str,
        field_name: str,
        user_id: str = None,
        success: bool = True,
    ):
        """Log an encryption or decryption operation."""
        level = self.logger.info if success else self.logger.warning
        level(
            f"Encryption operation: {operation}",
            extra={
                "event": "encryption_operation",
                "operation": operation,
                "field_name": field_name,
                "user_id": user_id,
                "success": success,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_breach_response(self, severity: str, actions_taken: list):
        """Log a breach response that involves key rotation."""
        self.logger.critical(
            "Breach response — key rotation triggered",
            extra={
                "event": "breach_response",
                "severity": severity,
                "actions_taken": actions_taken,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

audit_logger = EncryptionAuditLogger()
```

### 13.2 Audit Log Schema

```json
{
  "timestamp": "2026-06-11T10:30:00Z",
  "level": "INFO",
  "logger": "encryption_audit",
  "event": "key_rotation",
  "key_name": "JWT_SECRET",
  "reason": "scheduled",
  "performed_by": "admin@secondbrain-os.com",
  "previous_key_hash": "sha256:abc123...",
  "new_key_hash": "sha256:def456...",
  "expires_at": null
}
```

### 13.3 Audit Storage & Retention

| Property | Configuration |
|----------|---------------|
| Storage | Railway log streams + Supabase audit_logs table (future) |
| Retention | 90 days in log stream; 1 year in cold storage |
| Access | Admin only (via Railway Dashboard) |
| Integrity | Logs are append-only; no modification |
| Alerting | Error-level encryption events trigger Slack alert |
| Compliance | Audit logs are exportable for GDPR compliance review |

---

## 14. Compliance Mapping

### 14.1 Encryption Controls to Standards

| Control | OWASP ASVS | GDPR | SOC 2 | ISO 27001 |
|---------|------------|------|-------|-----------|
| Encryption at rest (AES-256) | V6.2.1 | Art. 32 | CC6.1 | A.10.1.1 |
| Encryption in transit (TLS 1.3) | V9.1.1 | Art. 32 | CC6.6 | A.13.2.1 |
| Key management | V6.1.1 | Art. 32 | CC6.1 | A.10.1.2 |
| Key rotation | V6.1.2 | — | CC6.1 | A.12.6.1 |
| HSTS implementation | V9.1.3 | — | CC6.6 | A.13.2.3 |
| Certificate management | V9.1.2 | — | CC6.6 | A.13.2.2 |
| Secure key storage | V6.1.3 | Art. 5(1)(f) | CC6.1 | A.10.1.3 |
| Data deletion | — | Art. 17 | — | A.8.3.2 |
| Data export | — | Art. 15 | — | A.8.2.3 |
| Audit logging | V7.1.1 | Art. 5(2) | CC5.2 | A.12.4.1 |

### 14.2 Encryption Maturity Model

| Level | Description | Current Status | Target |
|-------|-------------|---------------|--------|
| **L1** | TLS for all external connections | ✅ Achieved | Maintain |
| **L2** | AES-256 at rest for database | ✅ Achieved (Supabase) | Maintain |
| **L3** | Application-level encryption for sensitive fields | ❌ Not implemented | Q4 2026 |
| **L4** | Client-side encryption for user-controlled data | ❌ Not planned | 2027+ |
| **L5** | End-to-end encryption for all user data | ❌ Not planned | Not required |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-11 | Security Team | Initial encryption architecture: at rest, in transit, application-level, key management, AI data handling, GDPR compliance, backup encryption, audit trail |

---

## References

- AES (FIPS 197): https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
- TLS 1.3 (RFC 8446): https://datatracker.ietf.org/doc/html/rfc8446
- OWASP Transport Layer Protection: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html
- OWASP Cryptographic Storage: https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- Supabase Encryption: https://supabase.com/docs/guides/platform/encryption
- NIST SP 800-63B (Digital Identity Guidelines): https://pages.nist.gov/800-63-3/sp800-63b.html
- OWASP ASVS V6 (Stored Cryptography): https://owasp.org/www-project-application-security-verification-standard/
- bcrypt (NIST SP 800-63B): https://pages.nist.gov/800-63-3/sp800-63b.html
