# Requirements Traceability Matrix — Second Brain OS (ARIA OS)

## Document Control

| Field | Value |
|---|---|
| Document ID | PRD-RTM-009 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## 1. Purpose

The Requirements Traceability Matrix (RTM) maps every functional and non-functional requirement to its source document, implementation component, test coverage, and verification status. This ensures 100% requirement coverage and enables impact analysis for changes.

---

## 2. Traceability Key

| Prefix | Source |
|---|---|
| FR | Feature Requirement (PRD → Features.md) |
| NFR | Non-Functional Requirement (SRS) |
| UC | User Story (UserStories.md) |
| AC | Acceptance Criteria |
| AG | AI Agent requirement (Agent spec) |

---

## 3. Functional Requirements Matrix

### 3.1 Tasks Module

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-T01 | Create task with title, desc, priority, status, due date | UC-001 | tasks.py | test_api_endpoints.py | ✅ |
| FR-T02 | List tasks with pagination, filter by status | UC-002 | tasks.py | test_api_endpoints.py | ✅ |
| FR-T03 | Update task fields | UC-003 | tasks.py | test_api_endpoints.py | ✅ |
| FR-T04 | Delete task | UC-004 | tasks.py | test_api_endpoints.py | ✅ |
| FR-T05 | Mark task complete | UC-005 | tasks.py | test_api_endpoints.py | ✅ |
| FR-T06 | AI break down task into subtasks | AG-A01 | task_agent.py | test_agents.py | ✅ |

### 3.2 Courses Module

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-C01 | Create course with name, code, credits, semester | UC-006 | courses.py | test_api_endpoints.py | ✅ |
| FR-C02 | Update course progress, grade, status | UC-007 | courses.py | test_api_endpoints.py | ✅ |
| FR-C03 | Auto-compute CGPA/SGPA from courses | UC-008 | courses.py | test_api_endpoints.py | ✅ |
| FR-C04 | Nudge on course progress (AI) | AG-A14 | nudge_agent.py | test_agents.py | ✅ |

### 3.3 Goals Module

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-G01 | Create goal with title, description, milestones | UC-009 | goals.py | test_api_endpoints.py | ✅ |
| FR-G02 | Update goal progress, status | UC-010 | goals.py | test_api_endpoints.py | ✅ |
| FR-G03 | Skill roadmap optimization (AI) | AG-A08 | roadmap_agent.py | test_agents.py | ✅ |

### 3.4 Habits Module

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-H01 | Create habit with frequency, type | UC-011 | habits.py | test_api_endpoints.py | ✅ |
| FR-H02 | Log daily habit completion | UC-012 | habit_logs (implicit) | test_api_endpoints.py | ✅ |
| FR-H03 | Track streak (current, longest) | UC-013 | habit_logs (implicit) | test_api_endpoints.py | ✅ |
| FR-H04 | Missed habit detection (cron) | AG-A12 | scheduler crons | test_scheduler.py | ✅ |

### 3.5 Sleep Module

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-S01 | Log sleep with time, duration, quality | UC-014 | sleep.py | test_api_endpoints.py | ✅ |
| FR-S02 | Compute sleep score and debt | UC-015 | sleep.py | test_api_endpoints.py | ✅ |
| FR-S03 | AI wind-down message (bedtime) | AG-A13 | sleep_agent.py | test_agents.py | ✅ |

### 3.6 AI Agent Modules

| ID | Requirement | Source | Component | Test File | Status |
|---|---|---|---|---|---|
| FR-A01 | Daily briefing generation (7 AM) | AG-A09 | briefing_agent.py | test_agents.py | ✅ |
| FR-A02 | Weekly review generation (Sun 8 PM) | AG-A10 | weekly_review_agent.py | test_agents.py | ✅ |
| FR-A03 | Memory consolidation (background) | AG-A02 | memory_agent.py | test_agents.py | ✅ |
| FR-A04 | Pattern learning (daily) | AG-A03 | learning_agent.py | test_agents.py | ✅ |
| FR-A05 | Opportunity radar matching (6 AM) | AG-A06 | opportunity_agent.py | test_agents.py | ✅ |
| FR-A06 | Task breakdown (on-demand) | AG-A01 | task_agent.py | test_agents.py | ✅ |
| FR-A07 | Nudge generation (6 PM) | AG-A14 | nudge_agent.py | test_agents.py | ✅ |
| FR-A08 | Skill roadmap optimization | AG-A08 | roadmap_agent.py | test_agents.py | ✅ |
| FR-A09 | Sleep analysis + wind-down | AG-A13 | sleep_agent.py | test_agents.py | ✅ |
| FR-A10 | Opportunity scoring (on-demand) | AG-A15 | opportunity_matching_agent.py | test_agents.py | ✅ |

---

## 4. Non-Functional Requirements Matrix

| ID | Requirement | Source | SLO | Test | Status |
|---|---|---|---|---|---|
| NFR-01 | API p95 latency < 500ms | SRS | 500ms | test_api_endpoints.py | ✅ |
| NFR-02 | AI response < 30s | SRS | 30s | test_llm_client.py | ✅ |
| NFR-03 | DB query < 200ms | SRS | 200ms | test_config_core.py | ✅ |
| NFR-04 | Frontend TTI < 3s | SRS | 3s | Lighthouse CI | ✅ |
| NFR-05 | Offline PWA support | SRS | Cache-first | E2E tests | ✅ |
| NFR-06 | RLS on all tables | SRS | 100% | test_shared_utils.py | ✅ |
| NFR-07 | Auth on all endpoints | SRS | 100% | test_api_routes_advanced.py | ✅ |
| NFR-08 | Coverage >= 85% | SRS | 85% | pytest --cov | ✅ |
| NFR-09 | No ny in TypeScript | Code style | 100% | tsc --noEmit | ✅ |
| NFR-10 | Python formatting (Black) | Code style | 100% | black --check | ✅ |

---

## 5. Coverage Summary

| Category | Total | Covered | Coverage % |
|---|---|---|---|
| Functional Requirements | 41 | 41 | 100% |
| Non-Functional Requirements | 10 | 10 | 100% |
| User Stories | 15 | 15 | 100% |
| AI Agent requirements | 10 | 10 | 100% |
| API Endpoints | 76 | 76 | 100% |
| **Total** | **152** | **152** | **100%** |

---

## 6. Verification Methods

| Method | Description | Used For |
|---|---|---|
| UT | Unit Test (pytest) | All Python modules |
| API | API test (pytest mocked) | All 31 routers |
| E2E | Playwright spec | Frontend user flows |
| LINT | Linter analysis | Code style, type checking |
| LH | Lighthouse CI | Frontend performance |
| PEN | Penetration test | Security requirements |
| VAL | Frontmatter validation | Prompt files |

---

## 7. Impact Analysis

When a requirement changes, this RTM enables:
1. **Identify all affected components** via the Component column
2. **Find all relevant tests** to update via Test File column
3. **Assess source document changes** via Source column
4. **Update verification status** in Status column

---

## 8. References

| Document | Location |
|---|---|
| Features | Features.md |
| User Stories | UserStories.md |
| Acceptance Criteria | AcceptanceCriteria.md |
| SRS | 04_SRS.md |
| Agent Spec | docs/ai/20_Agent.md |
| Test Inventory | 	ests/ |
