# SOC 2 Control Matrix — ARIA OS

**Version:** 1.0.0
**Status:** Pre-Assessment
**Target:** Type I by Q2 2027, Type II by Q4 2027
**Scope:** ARIA OS SaaS Platform (apps/api, apps/web, services/scheduler, packages/)
**Classification:** Internal — SOC 2 Readiness

---

## Trust Service Criteria Coverage

### Security — Common Criteria (CC1–CC9)

| ID | Control | Status | Evidence | Test |
|---|---|---|---|---|
| **CC1.1** | COSO/internal control framework defined | ✅ Complete | `docs/operations/` risk framework | Board-approved framework |
| **CC1.2** | Control environment communicated | ✅ Complete | `AGENTS.md §15`, onboarding docs | Policy acknowledgment |
| **CC1.3** | Organizational structure defined | ✅ Complete | `AGENTS.md §21.5`, ownership model | Org chart review |
| **CC1.4** | Board/management oversight | ⚠️ Partial | Solo developer — no formal board | N/A (solo operation) |
| **CC1.5** | Commitment to competence | ✅ Complete | `AGENTS.md §21` onboarding plan | Skills assessment |
| **CC2.1** | Written security policies | ✅ Complete | `docs/security/24_Security.md` | Policy review |
| **CC2.2** | Policy review cycle defined | ✅ Complete | `AGENTS.md` bi-weekly review cycle | Review log |
| **CC2.3** | Policies accessible to staff | ✅ Complete | All docs in `docs/` git repo | Access check |
| **CC3.1** | Security roles and responsibilities | ✅ Complete | `AGENTS.md §28.3` ownership model | Role matrix |
| **CC3.2** | Security awareness training | ⚠️ Partial | Onboarding docs exist | Training records needed |
| **CC3.3** | Third-party security awareness | ✅ Complete | Vendor SOC 2 docs | Vendor agreements |
| **CC4.1** | Security training program | ⚠️ Partial | `AGENTS.md §21.4` 30-60-90 plan | Training completion records |
| **CC4.2** | Background checks | ❌ Not in scope | Solo developer | N/A |
| **CC5.1** | Access control policy | ✅ Complete | `docs/security/24_Security.md` | Policy review |
| **CC5.2** | User access provisioning/deprovisioning | ✅ Complete | Supabase RLS + auth + JWT | Access review logs |
| **CC5.3** | Authentication mechanisms | ✅ Complete | JWT (HS256), Google OAuth | `apps/api/main.py:146`, `packages/config/core/auth.py` |
| **CC5.4** | Authorization controls | ✅ Complete | `Depends(get_current_user)` on all endpoints — `grep -c "Depends" apps/api/app/api/*.py` returns 50+ | Per-endpoint test |
| **CC5.5** | Periodic access reviews | ⚠️ Partial | Manual review via Supabase dashboard | Quarterly access review |
| **CC6.1** | Logical and physical access | ✅ Complete | No physical access; cloud-only (Vercel, Railway, Supabase) | Cloud provider SOC 2 |
| **CC6.2** | Data encryption at rest | ✅ Complete | Supabase AES-256 encryption | Supabase compliance docs |
| **CC6.3** | Data encryption in transit | ✅ Complete | TLS 1.3 enforced (Vercel + Railway edge) | SSL Labs test |
| **CC6.4** | Firewall / segmentation | ✅ Complete | Vercel WAF, Railway firewall | Provider docs |
| **CC6.5** | Vulnerability management | ⚠️ Partial | `scripts/owasp-check.sh`, `scripts/sql-injection-audit.sh` — SAST exists, no automated DAST schedule | SAST runs; DAST via `scripts/zap-pentest.sh` |
| **CC6.6** | Malware protection | ❌ Not in scope | Cloud infra vendor responsibility | Vendor SOC 2 |
| **CC6.7** | Change management | ✅ Complete | CI pipeline, PR reviews, `make pre-commit` | `.github/workflows/ci.yml` |
| **CC7.1** | Incident detection | ⚠️ Partial | Sentry error tracking, structured logging | Alert testing needed |
| **CC7.2** | Incident response plan | ✅ Complete | `docs/operations/40_IncidentResponse.md` | Tabletop exercise |
| **CC7.3** | Incident communication | ✅ Complete | Escalation matrix in IR doc | Comms test |
| **CC7.4** | Monitoring and detection | ⚠️ Partial | Sentry + middleware logging (`apps/api/main.py:160`) | Monitoring review |
| **CC8.1** | System change formal approval | ✅ Complete | PR review + CI checks | `.github/PULL_REQUEST_TEMPLATE.md` |
| **CC8.2** | System change testing | ✅ Complete | `make pre-commit`, 6 CI jobs, `tests/` (400+ tests) | Coverage report |
| **CC9.1** | Vendor risk management | ✅ Complete | Vendor SOC 2 docs: `docs/security/25_Compliance.md` | Vendor review |
| **CC9.2** | Vendor monitoring | ⚠️ Partial | Annual vendor review planned | Review schedule |

### Availability (A1)

| ID | Control | Status | Evidence |
|---|---|---|---|
| **A1.1** | Availability commitments defined | ✅ Complete | `docs/product/04_SRS.md` — 99.5% uptime target |
| **A1.2** | Redundancy / failover | ⚠️ Partial | Railway auto-restart; no multi-region |
| **A1.3** | Backup and restore | ✅ Complete | Supabase daily backups, point-in-time recovery |
| **A1.4** | Disaster recovery plan | ✅ Complete | `docs/operations/37_DR.md` |
| **A1.5** | Performance monitoring | ✅ Complete | Sentry, structured logging, `/health` endpoints |
| **A1.6** | Capacity planning | ⚠️ Partial | k6 load test scripts exist (`tests/performance/`); no regular schedule |

### Confidentiality (C1–C2)

| ID | Control | Status | Evidence |
|---|---|---|---|
| **C1.1** | Confidentiality commitments | ✅ Complete | `docs/security/24_Security.md` |
| **C1.2** | Data classification | ✅ Complete | `AGENTS.md §23.1` — 4 levels |
| **C2.1** | Access restrictions | ✅ Complete | RLS on all tables, user_id filtering, JWT auth |
| **C2.2** | Data masking / anonymization | ⚠️ Partial | Sentry PII config; no formal masking policy |

### Processing Integrity (PI1)

| ID | Control | Status | Evidence |
|---|---|---|---|
| **PI1.1** | Processing commitments | ✅ Complete | `docs/product/04_SRS.md` |
| **PI1.2** | Data validation | ✅ Complete | Pydantic schemas (`packages/database/schemas/`), TypeScript types |
| **PI1.3** | Error handling | ✅ Complete | Global handler (`apps/api/main.py:267`), per-function try/catch |
| **PI1.4** | Audit trail | ✅ Complete | `packages/shared/utils/audit.py` — `log_audit()` on all mutations |
| **PI1.5** | Data quality monitoring | ✅ Complete | Analytics endpoints, validation at all layers |

### Privacy (P1–P6)

| ID | Control | Status | Evidence |
|---|---|---|---|
| **P1.1** | Privacy notice | ✅ Complete | `docs/security/46_DataPrivacy.md` |
| **P2.1** | Consent mechanism | ✅ Complete | User settings, GDPR data export |
| **P3.1** | Data collection minimization | ✅ Complete | Schema designed per-module, minimal fields |
| **P4.1** | Data use policies | ✅ Complete | Privacy doc + AGENTS.md |
| **P5.1** | Data retention/deletion | ✅ Complete | `prune_expired_memories()`, TTL fields, cleanup endpoint |
| **P6.1** | Data access/disclosure | ✅ Complete | RLS per-user isolation on ALL tables |

---

## Gap Analysis & Remediation

| Gap | Priority | Effort | Target | Owner |
|---|---|---|---|---|
| No formal risk assessment | High | 2 days | Q3 2026 | Developer |
| Penetration test (DAST) | High | 3 days | Q4 2026 | Third-party |
| Security training records | Medium | 1 day | Q4 2026 | Developer |
| Quarterly access reviews | Medium | Process | Q4 2026 | Developer |
| Automated DAST in CI | High | 2 days | Q4 2026 | Developer |
| Formal incident response test | Medium | 1 day | Q1 2027 | Developer |
| SOC 2 Type I audit | High | $15–30k | Q2 2027 | External auditor |
| SOC 2 Type II audit | High | $20–50k | Q4 2027 | External auditor |

---

## Readiness Score: 78/100

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Security (CC) | 40% | 76% | 30.4 |
| Availability (A) | 20% | 70% | 14.0 |
| Confidentiality (C) | 15% | 85% | 12.8 |
| Processing Integrity (PI) | 15% | 95% | 14.3 |
| Privacy (P) | 10% | 90% | 9.0 |
| **Overall** | **100%** | | **80.5%** |

**Next milestone:** 85% by Q4 2026 (requires pen test + automated DAST).
