# Technical Debt — Second Brain OS (ARIA OS) — Updated

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-TD-003 |
| Version | 2.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Technical Debt Inventory

This document tracks all known technical debt items, categorized by severity (Critical, High, Medium, Low), with remediation plans and deadlines.

---

## 2. Debt Summary

| Severity | Count | Total Effort (hrs) | Remediation SLAs |
|---|---|---|---|
| Critical | 0 | 0 | Fix within 7 days |
| High | 2 | 6 | Fix within 30 days |
| Medium | 5 | 18 | Fix within 90 days |
| Low | 7 | 14 | Fix within 180 days |
| **Total** | **14** | **38** | |

---

## 3. Critical Items (None)

All items closed. Previous critical items resolved:
- ~~`main.py` monolithic file~~ → Split into modular routers
- ~~No type annotations~~ → 100% typed
- ~~No tests~~ → 2795+ tests

---

## 4. High Severity

### TD-H01: Auto-generated Stubs without Tests
| Field | Value |
|---|---|
| Location | `packages/shared/utils/` (3 files) |
| Issue | Files generated from templates lack edge-case tests |
| Impact | Coverage gap, potential regression exposure |
| Effort | 4 hrs |
| Priority | High |

**Remediation:** Write unit tests for all auto-generated stubs by Jul 25.

### TD-H02: No Secrets Scanning in CI
| Field | Value |
|---|---|
| Location | `.github/workflows/ci.yml` |
| Issue | No automated scan for leaked credentials |
| Impact | Security risk, SOC 2 gap |
| Effort | 2 hrs |
| Priority | High |

**Remediation:** Add truffleHog or Gitleaks to CI by Jul 25.

---

## 5. Medium Severity

### TD-M01: No Load Testing in CI
**Location:** `tests/performance/`  
**Issue:** k6 scripts exist but not integrated into CI pipeline  
**Impact:** Performance regression risk  
**Effort:** 4 hrs

### TD-M02: No Visual Regression Testing
**Location:** `apps/web/`  
**Issue:** UI changes can break layouts without detection  
**Impact:** UX quality risk  
**Effort:** 6 hrs

### TD-M03: Inconsistent Error Response Formats
**Location:** `apps/api/app/api/` (3 routers)  
**Issue:** Some endpoints return `{"detail": msg}` instead of full error schema  
**Impact:** Client-side error handling inconsistency  
**Effort:** 3 hrs

### TD-M04: No SBOM Generation
**Location:** CI pipeline  
**Issue:** No software bill of materials generated for audit  
**Impact:** Supply chain transparency gap  
**Effort:** 2 hrs

### TD-M05: Storybook Stories Missing for 6 Components
**Location:** `apps/web/stories/`  
**Issue:** Components added without corresponding stories  
**Impact:** Visual documentation gap  
**Effort:** 3 hrs

---

## 6. Low Severity

| ID | Item | Location | Effort | Target |
|---|---|---|---|---|
| TD-L01 | Unused imports in 4 files | `packages/ai/agents/` | 1 hr | Aug 15 |
| TD-L02 | CSS class ordering inconsistent | `apps/web/components/` | 3 hrs | Sep 1 |
| TD-L03 | Console.log in 2 components | `apps/web/app/` | 0.5 hr | Aug 1 |
| TD-L04 | No CONTRIBUTING.md setup guide | Root | 2 hrs | Sep 15 |
| TD-L05 | Docker images not optimized (layer caching) | `apps/*/Dockerfile` | 3 hrs | Sep 30 |
| TD-L06 | API docs lack curl examples | `docs/engineering/17_API.md` | 3 hrs | Sep 30 |
| TD-L07 | End-to-end tests flaky under load | `apps/web/e2e/` | 1.5 hrs | Sep 15 |

---

## 7. Debt Trend

| Quarter | Critical | High | Medium | Low | Total | Effort (hrs) |
|---|---|---|---|---|---|---|
| Q1 2026 | 3 | 5 | 8 | 10 | 26 | 85 |
| Q2 2026 | 1 | 3 | 6 | 8 | 18 | 55 |
| Q3 2026 | 0 | 2 | 5 | 7 | 14 | 38 |
| Q4 2026 (Target) | 0 | 0 | 2 | 4 | 6 | 15 |

---

## 8. Remediation Prioritization

Priority matrix scored as: Impact × Urgency (1-10). Score determines remediation order.

| Item | Impact | Urgency | Score | Order |
|---|---|---|---|---|
| TD-H01 (Stubs) | 6 | 8 | 48 | 1 |
| TD-H02 (Secrets) | 9 | 5 | 45 | 2 |
| TD-M01 (Load Tests) | 5 | 6 | 30 | 3 |
| TD-M02 (Visual Regression) | 5 | 5 | 25 | 4 |
| TD-M03 (Error Formats) | 4 | 5 | 20 | 5 |
| TD-M04 (SBOM) | 3 | 5 | 15 | 6 |
| TD-M05 (Stories) | 3 | 4 | 12 | 7 |

---

## 9. References

| Document | Location |
|---|---|
| Maturity Model | MaturityModel.md |
| Testing Standards | AGENTS.md Section 16 |
| CI/CD Pipeline | AGENTS.md Section 17 |
