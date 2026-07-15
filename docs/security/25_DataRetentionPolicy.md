# Data Retention Policy

> **Document ID:SEC-DRP-001 SB-SEC-DRP-001
> **Version:** 1.0.0
> **Last Updated:** 2026-06-22
> **Status:** Active
> **Classification:** Internal

---

## 1. Purpose

This policy defines data retention periods for all data stored in ARIA OS. It ensures compliance with GDPR, SOC 2, and internal data governance requirements.

---

## 2. Data Categories & Retention Periods

| Category | Examples | Retention | Deletion Action |
|---|---|---|---|
| **User Profile** | Email, name, preferences | Account lifetime + 90 days | Anonymize after 90d inactivity |
| **Core Content** | Tasks, goals, habits, projects | Account lifetime | Hard delete on account closure |
| **Activity Logs** | Habit logs, time entries, sleep | 24 months | Aggregated â†’ raw deleted |
| **Chat History** | AI conversations | 12 months | Summarized â†’ raw deleted |
| **Audit Logs** | All mutations | 36 months (statutory) | Archived to cold storage |
| **Session Data** | JWT tokens, refresh tokens | Token expiry + 24h | Hard delete on expiry |
| **Analytics** | Usage metrics, page views | 24 months | Aggregated only after 24m |
| **Error Logs** | Sentry, server errors | 90 days | Hard delete |
| **Backups** | Database snapshots | 30 days (daily) | Recycled |
| **API Keys** | Rotated keys | 24h old key lifetime | Hard delete after 24h |

---

## 3. Deletion Mechanisms

| Data Type | Mechanism | Trigger |
|---|---|---|
| User data | `DELETE FROM ... WHERE user_id = ?` | Account deletion request |
| Aged-out data | Cron job: weekly purges | Retention period exceeded |
| Anonymized data | Hash user_id, clear PII fields | Inactivity threshold |

---

## 4. GDPR Compliance

### 4.1 Right to Access
- Endpoint: `GET /api/v1/data-export`
- Response: JSON with all user data across 27 tables
- SLA: Within 30 days of request

### 4.2 Right to Deletion
- Endpoint: `POST /api/v1/auth/delete-account`
- Process: Cascade delete all user data
- SLA: Within 30 days of request
- Exception: Audit logs retained for 36 months (anonymized)

### 4.3 Right to Rectification
- Handled via standard CRUD endpoints for each module
- All mutations tracked in audit logs

---

## 5. Backup Policy

| Backup Type | Frequency | Retention | Storage |
|---|---|---|---|
| Full DB | Daily | 30 days | Supabase automated backups |
| Point-in-time | Continuous | 7 days | Supabase PITR |
| Export | Monthly | 12 months | Encrypted S3 bucket |

---

## 6. Data Deletion Procedures

### Automated (Cron Jobs)
- Daily: Expired session data (`expires_at < NOW()`)
- Weekly: Aged-out logs exceeding retention
- Monthly: Anonymize inactive user accounts (>90d)

### Manual (User-Initiated)
1. User requests account deletion via settings
2. System confirms identity (re-auth required)
3. System schedules deletion within 48h grace period
4. Cron executes cascade delete
5. Confirmation email sent
6. Audit log entry created (anonymized)

---

## 7. Policy Review

This policy is reviewed bi-annually (June, December) by the development team.
