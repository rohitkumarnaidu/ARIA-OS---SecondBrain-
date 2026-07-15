# Documentation Master Index — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | OPS-IDX-001 |
| Version | 2.1.0 |
| Status | Approved |
| Date | 2026-07-12 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Quick Stats](#2-quick-stats)
- [3. Category Summary](#3-category-summary)
- [4. Document ID Registry](#4-document-id-registry)
- [5. Full Document Catalog by Category](#5-full-document-catalog-by-category)
  - [5.1 Architecture (4 files)](#51-architecture-4-files)
  - [5.2 AI (48 files)](#52-ai-48-files)
  - [5.3 Business (2 files)](#53-business-2-files)
  - [5.4 Compliance (3 files)](#54-compliance-3-files)
  - [5.5 Design (54 files)](#55-design-54-files)
  - [5.6 Devops (15 files)](#56-devops-15-files)
  - [5.7 Engineering (102 files)](#57-engineering-102-files)
  - [5.8 Frontend (6 files)](#58-frontend-6-files)
  - [5.9 Operations (43 files)](#59-operations-43-files)
  - [5.10 Product (28 files)](#510-product-28-files)
  - [5.11 QA (12 files)](#511-qa-12-files)
  - [5.12 Quickstart (1 file)](#512-quickstart-1-file)
  - [5.13 Security (18 files)](#513-security-18-files)
  - [5.14 Governance (10 files)](#514-governance-10-files)
- [5.15 Admin (1 file)](#515-admin-1-file)
- [5.16 User Guide (17 files)](#516-user-guide-17-files)
- [5.17 Learning Paths (4 files)](#517-learning-paths-4-files)
- [5.18 Postmortems (2 files)](#518-postmortems-2-files)
- [5.19 Root Legal (3 files)](#519-root-legal-3-files)
- [5.20 Scripts & Tooling (7 files)](#520-scripts--tooling-7-files)
- [5.21 Enterprise (3 files)](#521-enterprise-3-files)
- [5.22 Performance (1 file)](#522-performance-1-file)
- [5.23 Requirements (1 file)](#523-requirements-1-file)
- [6. Quick-Start Reading Guide by Role](#6-quick-start-reading-guide-by-role)
- [7. Relationship Diagram](#7-relationship-diagram)
- [8. Document Naming Conventions](#8-document-naming-conventions)
- [9. Maintenance and Governance](#9-maintenance-and-governance)
- [10. References](#10-references)

---

## 1. Executive Summary

This document is the authoritative index and cross-reference for all documentation in the Second Brain OS project. It lists every documentation file across 19 categories, provides Document ID mapping, category summaries, and a reading guide organised by role. The index is maintained as part of the documentation governance process and should be updated whenever a document is added, removed, or renamed.

---

## 2. Quick Stats

| Metric | Value |
|---|---|---|
| Total documentation files | ~383 |
| Documentation categories | 23 (Architecture, AI, Business, Compliance, Design, Devops, Engineering, Enterprise, Frontend, Governance, Learning Paths, Operations, Performance, Postmortems, Product, QA, Quickstart, Requirements, Root Legal, Security, Scripts & Tooling, User Guide, Admin) |
| Document IDs registered | ~370 (all files now have structured IDs after Doc ID migration) |
| Estimated total lines | ~265,000+ |
| Estimated total size | ~15 MB |
| Architecture Decision Records (ADRs) | 15 (all with Document Control tables) |
| Architecture model docs | 4 (C4 Context, Container, Component, data flow diagrams) |
| Wireframe files | 8 |
| Workflow architecture files | 12 |
| Integration specifications | 10 |
| Skills AI sub-documents | 12 |
| Security policies | 5 (vulnerability mgmt, incident response, data classification, pen test report, vulnerability inventory) |
| Security hardening guides | 3 (Supabase, Next.js, FastAPI) |
| Compliance documents | 3 (GDPR ROPA, SOC 2 Readiness, DPIA) |
| OpenAPI reference pages | 1,184 lines covering 31 routers, ~120 endpoints |
| Root-level docs | 4 (`docs/quickstart.md`, `PRIVACY.md`, `TERMS.md`, `COOKIE-POLICY.md`) |
| Governance documents | 9 (governance/ directory) |
| User Guide documents | 17 (user-guide/ directory) |
| Admin documents | 1 (admin/ directory) |
| Learning Path documents | 4 (learning-paths/ directory) |
| Postmortem documents | 2 (postmortems/ directory) |

---

## 3. Category Summary

| Category | File Count | Directory Path | Primary Focus |
|---|:---:|:---|:---|
| AI | 48 | `docs/ai/` | Agent specifications, memory architecture, prompt system, knowledge graph, skills, evaluation, AI observability, prompt engineering guide, AI incident response, skills system, MCP architecture |
| Architecture | 4 | `docs/architecture/` | C4 model, ERD, deployment diagrams, data flow diagrams, architecture decision log index |
| Business | 2 | `docs/business/` | Executive summary, business model, pitch deck |
| Compliance | 3 | `docs/compliance/` | GDPR ROPA, SOC 2 readiness, Data Protection Impact Assessment |
| Design | 54 | `docs/design/` | UI/UX, design system, tokens, wireframes, workflow architecture, branding, motion |
| Devops | 15 | `docs/devops/` | Deployment, CI/CD, Docker, Kubernetes, Terraform, release management, rollback, runbooks, production deployment, backup verification |
| Engineering | 102 | `docs/engineering/` | Architecture, database, API (incl. OpenAPI reference, error catalog), agents, integration, ADRs, frontend architecture, modules, API integration guide, supply chain security, secrets management, coding standards, plugin system, SDK reference |
| Enterprise | 3 | `docs/enterprise/` | Compliance checklist, enterprise maturity roadmap, technical debt register |
| Frontend | 6 | `docs/frontend/` | Folder structure, rendering, SEO, implementation backlog, state management, component library |
| Governance | 9 | `docs/governance/` | Documentation standards, change management, ownership matrix, review schedule, maturity model, doc templates, glossary |
| Learning Paths | 4 | `docs/learning-paths/` | Developer learning paths (frontend, backend, AI agent) |
| Operations | 43 | `docs/operations/` | Runbooks, monitoring, analytics, alerts, KPIs, SLAs, incident response, playbooks, firefighter runbooks, error budget |
| Performance | 1 | `docs/performance/` | Capacity planning guide |
| Postmortems | 2 | `docs/postmortems/` | Incident postmortem reports and template |
| Product | 28 | `docs/product/` | Vision, PRD, BRD, SRS, features, user stories, personas, roadmap, market research, KPI dashboard |
| QA | 12 | `docs/qa/` | Testing strategy, E2E, performance, load, stress, security, accessibility, chaos |
| Requirements | 1 | `docs/requirements/` | Requirements traceability matrix (ISO 9001 / CMMI) |
| Security | 18 | `docs/security/` | Security architecture, compliance, data privacy, threat model, SOC 2, encryption, vulnerability management, pen test reports, policies, SDL, hardening guides (Supabase, Next.js, FastAPI) |
| Quickstart | 1 | `docs/` | `quickstart.md` — 10-minute developer setup |
| Root Legal | 3 | `<repo root>/` | Privacy policy, terms of service, cookie policy |
| Scripts & Tooling | 7 | `scripts/`, `.markdownlint.jsonc`, `.github/`, `.pre-commit-config.yaml`, `Makefile` | Doc ID migration scripts, validation, CI link-check, pre-commit hooks, Makefile targets |
| User Guide | 17 | `docs/user-guide/` | End-user documentation for tasks, habits, sleep, chat/AI, features, FAQ, courses, goals, ideas, income, opportunities, projects, resources, time tracking, weekly review |

| **Total** | **~370** | **`docs/` + root + scripts** | — |

---

## 4. Document ID Registry

This section lists all structured Document IDs found across the documentation corpus. Legacy files using the `SB-` prefix are noted. New files use the `{CATEGORY}-{3LETTER}-{3DIGIT}` format.

### 4.1 Architecture Documents

| Document ID | File Path | Status |
|---|---|---|
| ARCH-C4-001 | `docs/architecture/README.md` | Active |
| ARCH-ERD-001 | `docs/architecture/database-erd.md` | Active |
| ARCH-DL-001 | `docs/architecture/decision-log.md` | Active |
| ARCH-DFD-001 | `docs/architecture/data-flow-diagrams.md` | Active |

### 4.2 AI Documents

| Document ID | File Path | Status |
|---|---|---|
| AI-AGNT-001 | `docs/ai/20_Agent.md` | Active |
| AI-AIN-001 | `docs/ai/19_AI_Instructions.md` | YELLOW |
| AI-PRM-001 | `docs/ai/21_Prompts.md` | YELLOW |
| AI-MEM-001 | `docs/ai/22_MemoryArchitecture.md` | YELLOW |
| AI-KG-001 | `docs/ai/23_KnowledgeGraph.md` | YELLOW |
| AI-SKL-001 | `docs/ai/36_Skills.md` | YELLOW |
| AI-EVL-001 | `docs/ai/AIEvaluation.md` | YELLOW |
| AI-MDL-001 | `docs/ai/AIModels.md` | YELLOW |
| AI-AGT-001 | `docs/ai/BriefingAgent.md` | YELLOW |
| AI-CTX-001 | `docs/ai/ContextEngine.md` | YELLOW |
| AI-EMB-006 | `docs/ai/Embeddings.md` | YELLOW |
| AI-GRD-001 | `docs/ai/Guardrails.md` | YELLOW |
| AI-HAL-002 | `docs/ai/HallucinationHandling.md` | YELLOW |
| AI-AGT-006 | `docs/ai/LearningAgent.md` | YELLOW |
| AI-LTM-004 | `docs/ai/LongTermMemory.md` | YELLOW |
| AI-AGT-005 | `docs/ai/MemoryAgent.md` | YELLOW |
| AI-MCP-007 | `docs/ai/MemoryCompression.md` | YELLOW |
| AI-MRT-008 | `docs/ai/MemoryRetrieval.md` | YELLOW |
| AI-AGT-007 | `docs/ai/NudgeAgent.md` | YELLOW |
| AI-AGT-008 | `docs/ai/OpportunityMatchingAgent.md` | YELLOW |
| AI-AGT-009 | `docs/ai/OpportunityRadarAgent.md` | YELLOW |
| AI-PVR-001 | `docs/ai/PromptVersioning.md` | YELLOW |
| AI-RAG-001 | `docs/ai/RAGArchitecture.md` | YELLOW |
| AI-AGT-010 | `docs/ai/RoadmapAgent.md` | YELLOW |
| AI-SEM-001 | `docs/ai/SemanticMemory.md` | YELLOW |
| AI-STM-001 | `docs/ai/ShortTermMemory.md` | YELLOW |
| AI-AGT-011 | `docs/ai/SleepAgent.md` | YELLOW |
| AI-AGT-012 | `docs/ai/TaskAgent.md` | YELLOW |
| AI-TLC-001 | `docs/ai/ToolCalling.md` | YELLOW |
| AI-AGT-002 | `docs/ai/WeeklyReviewAgent.md` | YELLOW |
| AI-AII-001 | `docs/ai/AIInsights.md` | Active (moved from operations/) |
| AI-OBS-001 | `docs/ai/AIObservability.md` | Active (moved from operations/) |
| AI-PEG-001 | `docs/ai/prompt-engineering-guide.md` | Active |
| AI-IR-001 | `docs/ai/AIIncidentResponse.md` | Active |
| AI-MCP-001 | `docs/ai/MCP-Architecture.md` | Active |
| AI-SKS-001 | `docs/ai/skills-system.md` | Active |
| AI-SKA-001 | `docs/ai/skills/SkillAgent.md` | YELLOW |
| AI-SKY-001 | `docs/ai/skills/SkillAnalytics.md` | YELLOW |
| AI-SKS-001 | `docs/ai/skills/SkillAssessment.md` | YELLOW |
| AI-SKE-001 | `docs/ai/skills/SkillAuditEnterprise.md` | YELLOW |
| AI-SKD-001 | `docs/ai/skills/SkillDatabaseArchitecture.md` | YELLOW |
| AI-SKV-001 | `docs/ai/skills/SkillEvidence.md` | YELLOW |
| AI-SKG-001 | `docs/ai/skills/SkillGraphArchitecture.md` | YELLOW |
| AI-SKI-001 | `docs/ai/skills/SkillIntelligence.md` | YELLOW |
| AI-SKM-001 | `docs/ai/skills/SkillMarketIntelligence.md` | YELLOW |
| AI-SKO-001 | `docs/ai/skills/SkillOpportunityMatching.md` | YELLOW |
| AI-SKR-001 | `docs/ai/skills/SkillRoadmapEngine.md` | YELLOW |
| AI-SKS-002 | `docs/ai/skills/skills.md` | YELLOW |

### 4.3 Business Documents

| Document ID | File Path | Status |
|---|---|---|
| BIZ-EXEC-001 | `docs/business/executive-summary.md` | Active |

### 4.4 Compliance Documents

| Document ID | File Path | Status |
|---|---|---|
| COMP-GDPR-001 | `docs/compliance/gdpr-ropa.md` | Active |
| COMP-SOC2-001 | `docs/compliance/soc2-readiness-report.md` | Active |
| COMP-DPIA-001 | `docs/compliance/dpia.md` | Active |

### 4.5 Design Documents

| Document ID | File Path | Status |
|---|---|---|
| DSG-DESIGN-009 | `docs/design/09_Design.md` | Deleted (merged into `08_UIUX.md`) |
| DSG-DS-010 | `docs/design/10_DesignSystem.md` | Active |
| DSG-UIUX-008 | `docs/design/08_UIUX.md` | Active |
| DSG-ANM-007 | `docs/design/AnimationGuidelines.md` | Active |
| DSG-CHT-006 | `docs/design/Charts.md` | Active |
| DSG-CLR-001 | `docs/design/Colors.md` | Active |
| DSG-DRK-001 | `docs/design/DarkMode.md` | Active |
| DSG-ICN-004 | `docs/design/Icons.md` | Active |
| DSG-LYT-005 | `docs/design/Layouts.md` | Active |
| DSG-MIC-002 | `docs/design/MicroInteractions.md` | Active |
| DSG-SPC-003 | `docs/design/Spacing.md` | Active |
| DSG-TYP-002 | `docs/design/Typography.md` | Active |
| DSG-STY-001 | `docs/design/StyleGuide.md` | Active |
| DSG-FSC-001 | `docs/design/FrontendScreenFlows.md` | Active |
| DSG-DSN-001 | `docs/design/Design.md` | Active |
| DSG-DSS-001 | `docs/design/DesignSystem.md` | Active |
| DSG-ADS-001 | `docs/design/ARCHIVED_DesignStrategy.md` | Archived |
| DSG-CIR-001 | `docs/design/Competitive_Intelligence_Report.md` | Active |
| DSG-AEFD-001 | `docs/design/ARCHIVED_Enterprise_Frontend_Discovery_Report.md` | Archived |
| DSG-AEF2-001 | `docs/design/ARCHIVED_Enterprise_Frontend_Discovery_Report_v2.md` | Archived |
| DSG-EFD3-001 | `docs/design/Enterprise_Frontend_Discovery_Report_v3.md` | Active |
| DSG-FIG-001 | `docs/design/FigmaGovernance.md` | Active |
| DSG-INF-001 | `docs/design/InformationArchitecture.md` | Active |
| DSG-MAC-001 | `docs/design/MotionArchitecture.md` | Active |
| DSG-PAR-001 | `docs/design/ProductArchitecture.md` | Active |
| DSG-A11Y-001 | `docs/design/FrontendAccessibilityGuide.md` | Active |
| DSG-OBS-001 | `docs/design/FrontendObservabilityGuide.md` | Active |
| DSG-TOK-001 | `docs/design/35_DesignTokens.md` | YELLOW |
| DSG-CSP-001 | `docs/design/37_ComponentSpec.md` | YELLOW |
| — | `docs/design/Accessibility.md` | Deleted (superseded by FrontendAccessibilityGuide.md) |
| DSG-BRD-001 | `docs/design/Branding.md` | YELLOW |
| DSG-ADSR-001 | `docs/design/ARCHIVED_DesignSystemResearch.md` | Archived |
| DSG-MOS-001 | `docs/design/MotionSystem.md` | YELLOW |
| DSG-RSP-001 | `docs/design/ResponsiveRules.md` | YELLOW |
| DSG-UJA-001 | `docs/design/UserJourneyArchitecture.md` | YELLOW |
| DSG-WSI-001 | `docs/design/wireframes/00_WIREFRAME_SYSTEM_INDEX.md` | YELLOW |
| DSG-WF1-001 | `docs/design/wireframes/01_APPLICATION_SHELL_AND_NAVIGATION.md` | YELLOW |
| DSG-WF2-001 | `docs/design/wireframes/02_DASHBOARD_WIREFRAMES.md` | YELLOW |
| DSG-WF3-001 | `docs/design/wireframes/03_TASKS_AND_COURSES_WIREFRAMES.md` | YELLOW |
| DSG-WF4-001 | `docs/design/wireframes/04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md` | YELLOW |
| DSG-WF5-001 | `docs/design/wireframes/05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md` | YELLOW |
| DSG-WF6-001 | `docs/design/wireframes/06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md` | YELLOW |
| DSG-WF7-001 | `docs/design/wireframes/07_SUPPLEMENT_AI_MODULES_STATES.md` | YELLOW |
| DSG-WFA1-001 | `docs/design/WorkflowArchitecture/01-UserFlows.md` | YELLOW |
| DSG-WFA2-001 | `docs/design/WorkflowArchitecture/02-FeatureFlows.md` | YELLOW |
| DSG-WFA3-001 | `docs/design/WorkflowArchitecture/03-SupportingScreens.md` | YELLOW |
| DSG-WFA4-001 | `docs/design/WorkflowArchitecture/04-MultiStepExperiences.md` | YELLOW |
| DSG-WFA5-001 | `docs/design/WorkflowArchitecture/05-Notifications.md` | YELLOW |
| DSG-WFA6-001 | `docs/design/WorkflowArchitecture/06-Search.md` | YELLOW |
| DSG-WFA7-001 | `docs/design/WorkflowArchitecture/07-AIAgentExperiences.md` | YELLOW |
| DSG-WFA8-001 | `docs/design/WorkflowArchitecture/08-Collaboration.md` | YELLOW |
| DSG-WFA9-001 | `docs/design/WorkflowArchitecture/09-Settings.md` | YELLOW |
| DSG-WFA10-001 | `docs/design/WorkflowArchitecture/10-EnterpriseReadiness.md` | YELLOW |
| DSG-WFA11-001 | `docs/design/WorkflowArchitecture/11-ResponsiveBehavior.md` | YELLOW |
| DSG-WFA12-001 | `docs/design/WorkflowArchitecture/12-FutureExpansion.md` | YELLOW |
| DSG-WFA0-001 | `docs/design/WorkflowArchitecture/README.md` | YELLOW |
| — | `docs/design/tokens/tokens-studio.json` | Legacy |

### 4.6 DevOps Documents

| Document ID | File Path | Status |
|---|---|---|
| SB-DEVOPS-REL-001 | `docs/devops/38_ReleaseManagement.md` | Active |
| DVO-CI-011 | `docs/devops/CI.md` | Active |
| DVO-CD-012 | `docs/devops/CD.md` | Active |
| DVO-TERRA-013 | `docs/devops/Terraform.md` | Active |
| DVO-GHA-014 | `docs/devops/GitHubActions.md` | Active |
| DVO-ROLL-015 | `docs/devops/Rollback.md` | Active |
| DVO-DEP-001 | `docs/devops/26_Deployment.md` | YELLOW |
| DVO-DVO-001 | `docs/devops/27_DevOps.md` | YELLOW |
| DVO-CDN-001 | `docs/devops/CDNStrategy.md` | YELLOW |
| DVO-DCK-001 | `docs/devops/Docker.md` | YELLOW |
| DVO-ENV-001 | `docs/devops/Environments.md` | YELLOW |
| DVO-INF-001 | `docs/devops/Infrastructure.md` | YELLOW |
| DVO-KUB-001 | `docs/devops/Kubernetes.md` | YELLOW |
| DVO-PROD-016 | `docs/devops/production-deployment.md` | Active (moved from operations/) |
| DVO-BAK-017 | `docs/devops/backup-verification-procedure.md` | Active |

### 4.7 Governance Documents

| Document ID | File Path | Status |
|---|---|---|
| OPS-STD-001 | `docs/governance/01_DocumentationStandards.md` | Active (moved from operations/48_) |
| OPS-CHG-002 | `docs/governance/02_ChangeManagement.md` | Active (moved from operations/49_) |
| OPS-OWN-013 | `docs/governance/documentation-ownership.md` | Active (moved from operations/) |
| OPS-REV-014 | `docs/governance/documentation-review-schedule.md` | Active (moved from operations/) |
| GOV-DMM-001 | `docs/governance/documentation-maturity-model.md` | Active |
| GOV-README-001 | `docs/governance/README.md` | Active |
| GOV-TPL-ARC-001 | `docs/governance/templates/template-architecture.md` | Active |
| GOV-TPL-API-001 | `docs/governance/templates/template-api-endpoint.md` | Active |
| GOV-TPL-GDE-001 | `docs/governance/templates/template-guide.md` | Active |
| GOV-GLO-001 | `docs/governance/glossary.md` | Active |

### 4.8 Engineering Documents

#### 4.8.1 Engineering — Core

| Document ID | File Path | Status |
|---|---|---|
| SB-ARCH-UPDATE-046 | `docs/engineering/46_Architecture_Update.md` | Active |
| ENG-TSK-001 | `docs/engineering/11_TechStack.md` | YELLOW |
| ENG-MIS-001 | `docs/engineering/modules/ModulesImplementationSpec.md` | Active |
| FE-COMP-001 | `docs/engineering/FrontendComponentLibrary.md` | Active |
| FE-FETCH-001 | `docs/engineering/FrontendDataFetching.md` | Active |
| FE-PERF-001 | `docs/engineering/FrontendPerformanceGuide.md` | Active |
| FE-SEC-001 | `docs/engineering/FrontendSecurityGuide.md` | Active |
| FE-FORM-001 | `docs/engineering/FormArchitecture.md` | Active |
| FE-AIUX-001 | `docs/engineering/FrontendAIUXPatterns.md` | Active |
| FE-TEST-001 | `docs/engineering/FrontendTestingStrategy.md` | Active |
| ENG-FOP-001 | `docs/engineering/FrontendOfflinePWA.md` | Active |
| ENG-FRN-001 | `docs/engineering/FrontendRoutingNavigation.md` | Active |
| INT-SUP-008 | `docs/engineering/integrations/Supabase.md` | Active |
| INT-GIT-002 | `docs/engineering/integrations/GitHub.md` | Active |
| INT-YTB-003 | `docs/engineering/integrations/YouTube.md` | Active |
| INT-NTF-010 | `docs/engineering/integrations/Notifications.md` | Active |
| ENG-TSK-001 | `docs/engineering/11_TechStack.md` | YELLOW |
| ENG-ARC-001 | `docs/engineering/12_Architecture.md` | YELLOW |
| — | `docs/engineering/13_SystemArchitecture.md` | Deleted (absorbed into `12_Architecture.md`) |
| ENG-AAR-001 | `docs/engineering/14_AgentArchitecture.md` | YELLOW |
| ENG-DB-001 | `docs/engineering/15_Database.md` | YELLOW |
| ENG-DGV-001 | `docs/engineering/16_DataGovernance.md` | YELLOW |
| ENG-API-002 | `docs/engineering/17_API.md` | YELLOW |
| ENG-EVT-001 | `docs/engineering/18_Events.md` | YELLOW |
| ENG-IAR-001 | `docs/engineering/37_IntegrationArchitecture.md` | YELLOW |
| ENG-PER-001 | `docs/engineering/45_PerformanceScalability.md` | YELLOW |
| ENG-ADR-001 | `docs/engineering/adr/ADR-001-monorepo-over-multi-repo.md` | Active |
| ENG-ADR-002 | `docs/engineering/adr/ADR-002-supabase-over-custom-backend-db.md` | Active |
| ENG-ADR-003 | `docs/engineering/adr/ADR-003-ollama-primary-claude-fallback.md` | Active |
| ENG-ADR04-001 | `docs/engineering/adr/ADR-004-in-process-agents-over-microservices.md` | Active |
| ENG-ADR-005 | `docs/engineering/adr/ADR-005-zustand-over-redux.md` | Active |
| ENG-ADR06-001 | `docs/engineering/adr/ADR-006-apscheduler-over-celery.md` | Active |
| ENG-ADR-007 | `docs/engineering/adr/ADR-007-pwa-over-native-mobile.md` | Active |
| ENG-ADR08-001 | `docs/engineering/adr/ADR-008-no-event-bus-in-alpha.md` | Active |
| ENG-ADR09-001 | `docs/engineering/adr/ADR-009-prompt-loader.md` | Active |
| ENG-ADR10-001 | `docs/engineering/adr/ADR-010-ai-provider-failover.md` | Active |
| ENG-ADR11-001 | `docs/engineering/adr/ADR-011-graceful-degradation.md` | Active |
| ENG-ADR12-001 | `docs/engineering/adr/ADR-012-api-versioning-strategy.md` | Active |
| ENG-ADR13-001 | `docs/engineering/adr/ADR-013-secret-management.md` | Active |
| ENG-ADR14-001 | `docs/engineering/adr/ADR-014-testing-philosophy.md` | Active |
| ENG-ADR15-001 | `docs/engineering/adr/ADR-015-resilience-patterns.md` | Active |
| ENG-AGO-001 | `docs/engineering/AgentOrchestration.md` | YELLOW |
| ENG-AGW-001 | `docs/engineering/ApiGateway.md` | YELLOW |
| ENG-BAR-001 | `docs/engineering/BackendArchitecture.md` | YELLOW |
| ENG-BKW-001 | `docs/engineering/BackgroundWorkers.md` | YELLOW |
| ENG-BKS-001 | `docs/engineering/BackupStrategy.md` | YELLOW |
| ENG-BL-001 | `docs/engineering/BusinessLogic.md` | YELLOW |
| ENG-CCH-001 | `docs/engineering/CachingStrategy.md` | YELLOW |
| ENG-CFG-001 | `docs/engineering/ConfigurationManagement.md` | YELLOW |
| ENG-CON-001 | `docs/engineering/Constraints.md` | YELLOW |
| ENG-CTR-001 | `docs/engineering/Controllers.md` | YELLOW |
| ENG-CRN-001 | `docs/engineering/CronJobs.md` | YELLOW |
| ENG-ENT-001 | `docs/engineering/EnterprisePlan.md` | YELLOW |
| ENG-ERD-001 | `docs/engineering/ERD.md` | YELLOW |
| ENG-ERR-001 | `docs/engineering/ErrorCodes.md` | YELLOW |
| ENG-FFL-001 | `docs/engineering/FeatureFlags.md` | YELLOW |
| ENG-FAR-001 | `docs/engineering/FrontendArchitecture.md` | YELLOW |
| ENG-FTR-001 | `docs/engineering/FrontendTechnicalResearch.md` | YELLOW |
| ENG-FNC-001 | `docs/engineering/Functions.md` | YELLOW |
| ENG-HST-001 | `docs/engineering/HistoryTables.md` | YELLOW |
| ENG-IDX-001 | `docs/engineering/Indexes.md` | YELLOW |
| INT-CLA-001 | `docs/engineering/integrations/Claude.md` | YELLOW |
| INT-EML-001 | `docs/engineering/integrations/Email.md` | YELLOW |
| INT-GEM-001 | `docs/engineering/integrations/Gemini.md` | YELLOW |
| INT-GGL-001 | `docs/engineering/integrations/Google.md` | YELLOW |
| INT-OLL-001 | `docs/engineering/integrations/Ollama.md` | YELLOW |
| INT-OPN-001 | `docs/engineering/integrations/OpenAI.md` | YELLOW |
| ENG-I18-001 | `docs/engineering/Internationalization.md` | YELLOW |
| ENG-MVW-001 | `docs/engineering/MaterializedViews.md` | YELLOW |
| ENG-MSR-001 | `docs/engineering/Microservices.md` | YELLOW |
| ENG-MGR-001 | `docs/engineering/MigrationStrategy.md` | YELLOW |
| ENG-NTF-001 | `docs/engineering/NotificationSystem.md` | YELLOW |
| ENG-OFF-001 | `docs/engineering/OfflineFirstArchitecture.md` | YELLOW |
| ENG-PAR-001 | `docs/engineering/PermissionsAndRoles.md` | YELLOW |
| ENG-POL-001 | `docs/engineering/Policies.md` | YELLOW |
| ENG-QUE-001 | `docs/engineering/QueueArchitecture.md` | YELLOW |
| ENG-RTL-001 | `docs/engineering/RateLimiting.md` | YELLOW |
| ENG-RTM-001 | `docs/engineering/Realtime.md` | YELLOW |
| ENG-RTA-001 | `docs/engineering/RealtimeArchitecture.md` | YELLOW |
| ENG-REP-001 | `docs/engineering/Repositories.md` | YELLOW |
| ENG-RST-001 | `docs/engineering/REST.md` | YELLOW |
| ENG-RLS-001 | `docs/engineering/RLS.md` | YELLOW |
| ENG-SCH-001 | `docs/engineering/Schedulers.md` | YELLOW |
| ENG-SCH-002 | `docs/engineering/Schema.md` | YELLOW |
| ENG-SRC-001 | `docs/engineering/SearchArchitecture.md` | YELLOW |
| ENG-SRV-001 | `docs/engineering/ServerActions.md` | YELLOW |
| ENG-SVC-001 | `docs/engineering/Services.md` | YELLOW |
| ENG-SMM-001 | `docs/engineering/StateManagement.md` | YELLOW |
| ENG-TRG-001 | `docs/engineering/Triggers.md` | YELLOW |
| ENG-VAL-001 | `docs/engineering/Validation.md` | YELLOW |
| ENG-VDB-001 | `docs/engineering/VectorDatabase.md` | YELLOW |
| ENG-VRS-001 | `docs/engineering/Versioning.md` | YELLOW |
| ENG-VWS-001 | `docs/engineering/Views.md` | YELLOW |
| ENG-WHK-001 | `docs/engineering/Webhooks.md` | YELLOW |
| ENG-WFE-001 | `docs/engineering/WorkflowEngine.md` | YELLOW |
| ENG-CST-001 | `docs/engineering/coding-standards.md` | Active |
| ENG-PLUG-001 | `docs/engineering/plugin-system.md` | Active |

#### 4.8.2 Engineering — API Reference

| Document ID | File Path | Status |
|---|---|---|
| ENG-API-001 | `docs/engineering/api/openapi-reference.md` | Active |
| ENG-RATE-001 | `docs/engineering/api/rate-limiting.md` | Active |
| ENG-API-CHANGELOG-001 | `docs/engineering/api/changelog.md` | Active |
| ENG-AIG-002 | `docs/engineering/api-integration-guide.md` | Active |
| ENG-ERRCAT-001 | `docs/engineering/api/error-catalog.md` | Active |
| ENG-SDK-001 | `docs/engineering/api/sdk-reference.md` | Active |

| ENG-SCS-001 | `docs/engineering/supply-chain-security.md` | Active |
| ENG-SMG-001 | `docs/engineering/secrets-management.md` | Active |

### 4.9 Frontend Documents

| Document ID | File Path | Status |
|---|---|---|
| FE-FS-001 | `docs/frontend/FolderStructure.md` | Active |
| FE-RS-001 | `docs/frontend/RenderingStrategy.md` | Active |
| FE-SEO-001 | `docs/frontend/SEO.md` | Active |
| FE-IBL-001 | `docs/frontend/IMPLEMENTATION_BACKLOG.md` | YELLOW |
| FE-SM-001 | `docs/frontend/StateManagement.md` | Active |
| FE-CL-001 | `docs/frontend/ComponentLibrary.md` | Active |

### 4.10 Operations Documents

| Document ID | File Path | Status |
|---|---|---|
| SB-OPS-ANL-001 | `docs/operations/30_Analytics.md` | Active |
| SB-OPS-MON-001 | `docs/operations/32_Monitoring.md` | Active |
| SB-RUNBOOKS-001 | `docs/operations/39_Runbooks.md` | Active |
| SB-ROADMAP-001 | `docs/operations/33_Roadmap.md` | Active |
| SB-DR-001 | `docs/operations/41_DisasterRecovery.md` | Active |
| SB-SLA-001 | `docs/operations/43_SLA.md` | Active |
| OPS-KPI-012 | `docs/operations/KPIs.md` | Active |
| OPS-TRC-001 | `docs/operations/Tracing.md` | Active |
| OPS-DSH-002 | `docs/operations/Dashboards.md` | Active |
| OPS-ALR-003 | `docs/operations/Alerts.md` | Active |
| OPS-SNT-004 | `docs/operations/Sentry.md` | Active |
| OPS-PST-005 | `docs/operations/PostHog.md` | Active (Draft) |
| OPS-PLB-006 | `docs/operations/Playbooks.md` | Active |
| OPS-MNT-007 | `docs/operations/Maintenance.md` | Active |
| OPS-SUP-008 | `docs/operations/Support.md` | Active |
| OPS-FNL-009 | `docs/operations/Funnels.md` | Active |
| OPS-EVT-010 | `docs/operations/Events.md` | Active |
| OPS-RPT-011 | `docs/operations/Reports.md` | Active |
| OPS-FFR-015 | `docs/operations/firefighter-runbooks.md` | Active |
| OPS-OBS-001 | `docs/operations/31_Observability.md` | YELLOW |
| OPS-BLG-001 | `docs/operations/34_Backlog.md` | YELLOW |
| OPS-IR-001 | `docs/operations/40_IncidentResponse.md` | YELLOW |
| OPS-RSK-001 | `docs/operations/42_RiskManagement.md` | YELLOW |
| OPS-DON-001 | `docs/operations/44_DeveloperOnboarding.md` | YELLOW |
| OPS-CST-001 | `docs/operations/47_CostManagement.md` | YELLOW |
| — | `docs/operations/49_ChangeManagement.md` | Moved to `governance/02_ChangeManagement.md` |
| OPS-TDB-001 | `docs/operations/50_TechnicalDebt.md` | YELLOW |
| OPS-AUD-001 | `docs/operations/AuditLogs.md` | YELLOW |
| OPS-CNT-001 | `docs/operations/Contributing.md` | YELLOW |
| — | `docs/operations/DataRetention.md` | Deleted (consolidated into security/25_DataRetentionPolicy.md) |
| — | `docs/operations/DataRetentionPolicy.md` | Deleted (consolidated into security/25_DataRetentionPolicy.md) |
| OPS-DOD-001 | `docs/operations/DefinitionOfDone.md` | YELLOW |
| OPS-DEP-001 | `docs/operations/Dependencies.md` | YELLOW |
| OPS-DPM-001 | `docs/operations/DependencyManagement.md` | YELLOW |
| OPS-GIT-001 | `docs/operations/GitWorkflow.md` | YELLOW |
| OPS-IMP-001 | `docs/operations/IMPLEMENTATION_STATUS.md` | YELLOW |
| OPS-INR-001 | `docs/operations/InnovationRadar.md` | YELLOW |
| OPS-MM-001 | `docs/operations/MaturityModel.md` | YELLOW |
| — | `docs/operations/PromptVersioning.md` | Deleted (duplicate of ai/PromptVersioning.md) |
| OPS-SCL-001 | `docs/operations/ScalingPlan.md` | YELLOW |
| OPS-SOC-001 | `docs/operations/SOC2Readiness.md` | YELLOW |
| OPS-SPR-001 | `docs/operations/SprintPlan.md` | YELLOW |
| OPS-SRV-001 | `docs/operations/SprintReview.md` | YELLOW |
| OPS-TBR-001 | `docs/operations/TaskBreakdown.md` | YELLOW |
| OPS-TDB-002 | `docs/operations/TechnicalDebt.md` | YELLOW |
| OPS-EB-001 | `docs/operations/error-budget.md` | Active |

### 4.11 Product Documents

| Document ID | File Path | Status |
|---|---|---|
| PRD-PVD-001 | `docs/product/00_ProjectVision.md` | Active |
| PRD-AUD-001 | `docs/product/01_CurrentStateAudit.md` | Active |
| SB-PRD-001 | `docs/product/02_PRD.md` | Active |
| SB-BRD-001 | `docs/product/03_BRD.md` | Active |
| SB-FEAT-001 | `docs/product/03_Features.md` | Active |
| SB-SRS-001 | `docs/product/04_SRS.md` | Active |
| SB-US-001 | `docs/product/06_UserStories.md` | Active |
| SB-AC-001 | `docs/product/07_AcceptanceCriteria.md` | Active |
| SB-PERS-001 | `docs/product/Personas.md` | Active |
| SB-ROADMAP-001 | `docs/product/Roadmap.md` | Active |
| SB-CA-001 | `docs/product/CompetitiveAnalysis.md` | Active |
| SB-MON-001 | `docs/product/Monetization.md` | Active |
| SB-UF-001 | `docs/product/UserFlows.md` | Active |
| PRD-VP-002 | `docs/product/ValueProposition.md` | Active |
| PRD-MET-003 | `docs/product/SuccessMetrics.md` | Active |
| PRD-SH-007 | `docs/product/Stakeholders.md` | Active |
| PRD-RIS-007 | `docs/product/Risks.md` | Active |
| PRD-DEC-008 | `docs/product/DecisionLog.md` | Active |
| PRD-RTM-009 | `docs/product/RequirementsTraceabilityMatrix.md` | Active |
| PRD-AC-010 | `docs/product/AcceptanceCriteria.md` | Deleted (redirect stub — see 07_AcceptanceCriteria.md) |
| PRD-STG-001 | `docs/product/ProductStrategy.md` | Active |
| PRD-MIS-001 | `docs/product/Mission.md` | Active |
| PRD-GOL-002 | `docs/product/Goals.md` | Active |
| PRD-SCO-004 | `docs/product/ProjectScope.md` | Active |
| PRD-GLO-005 | `docs/product/Glossary.md` | Active |
| PRD-ASM-006 | `docs/product/Assumptions.md` | Active |
| PRD-CON-006 | `docs/product/Constraints.md` | Active |
| PRD-MR-003 | `docs/product/MarketResearch.md` | Active |
| PRD-KPI-001 | `docs/product/KPI-dashboard.md` | Active |
| — | `docs/product/05_Features.md` | Deleted (redirect stub — see 03_Features.md) |

### 4.12 QA Documents

| Document ID | File Path | Status |
|---|---|---|
| QA-TEST-STRAT-001 | `docs/qa/28_Testing.md` | Active |
| QA-PROC-001 | `docs/qa/29_QA.md` | Deleted (merged into `28_Testing.md`) |
| QA-INT-001 | `docs/qa/IntegrationTesting.md` | Active |
| QA-ACC-002 | `docs/qa/AccessibilityTesting.md` | Active |
| QA-UAT-006 | `docs/qa/UAT.md` | Active |
| QA-CHS-007 | `docs/qa/ChaosTesting.md` | Active |
| QA-RGT-008 | `docs/qa/RegressionTesting.md` | Active |
| QA-SCT-009 | `docs/qa/SecurityTesting.md` | Active |
| QA-LDT-010 | `docs/qa/LoadTesting.md` | Active |
| QA-STR-011 | `docs/qa/StressTesting.md` | Active |
| — | `docs/qa/E2ETesting.md` | Legacy |
| — | `docs/qa/E2ETestPlan.md` | Legacy |
| — | `docs/qa/PerformanceTesting.md` | Legacy |
| — | `docs/qa/UnitTesting.md` | Deleted (redirect stub — see 28_Testing.md) |

### 4.13 Security Documents

| Document ID | File Path | Status |
|---|---|---|
| SEC-SEC-001 | `docs/security/24_Security.md` | Active |
| SEC-COM-001 | `docs/security/25_Compliance.md` | Active |
| SEC-VULM-001 | `docs/security/policies/vulnerability-management.md` | Active |
| SEC-VULN-001 | `docs/security/VulnerabilityInventory.md` | Active |
| SEC-IR-001 | `docs/security/policies/incident-response.md` | Active |
| SEC-DC-001 | `docs/security/policies/data-classification.md` | Active |
| SEC-PEN-001 | `docs/security/reports/penetration-test-report.md` | Active |
| SEC-DRP-001 | `docs/security/25_DataRetentionPolicy.md` | YELLOW |
| SEC-DPR-001 | `docs/security/46_DataPrivacy.md` | YELLOW |
| SEC-AUTH-001 | `docs/security/AuthArchitecture.md` | YELLOW |
| SEC-ENC-001 | `docs/security/Encryption.md` | YELLOW |
| SEC-SECRETS-001 | `docs/security/SecretsManagement.md` | YELLOW |
| SEC-SOC2-001 | `docs/security/soc2_control_matrix.md` | YELLOW |
| SEC-TM-001 | `docs/security/ThreatModel.md` | YELLOW |
| SEC-SDL-001 | `docs/security/sdl.md` | Active |
| SEC-HRD-SUP-001 | `docs/security/hardening/supabase.md` | Active |
| SEC-HRD-NX-001 | `docs/security/hardening/nextjs.md` | Active |
| SEC-HRD-FA-001 | `docs/security/hardening/fastapi.md` | Active |

### 4.14 User Guide

| Document ID | File Path | Status |
|---|---|---|
| USR-GS-001 | `docs/user-guide/getting-started.md` | Active |
| USR-FO-001 | `docs/user-guide/features-overview.md` | Active |
| USR-TSK-001 | `docs/user-guide/tasks.md` | Active |
| USR-HBT-001 | `docs/user-guide/habits.md` | Active |
| USR-SLP-001 | `docs/user-guide/sleep.md` | Active |
| USR-CHT-001 | `docs/user-guide/chat-and-ai.md` | Active |
| USR-FAQ-001 | `docs/user-guide/FAQ.md` | Active |
| USR-README-001 | `docs/user-guide/README.md` | Active |
| USR-CRS-001 | `docs/user-guide/courses.md` | Active |
| USR-GLS-001 | `docs/user-guide/goals.md` | Active |
| USR-IDEA-001 | `docs/user-guide/ideas.md` | Active |
| USR-INC-001 | `docs/user-guide/income.md` | Active |
| USR-OPP-001 | `docs/user-guide/opportunities.md` | Active |
| USR-PRJ-001 | `docs/user-guide/projects.md` | Active |
| USR-RSC-001 | `docs/user-guide/resources.md` | Active |
| USR-TTR-001 | `docs/user-guide/time-tracking.md` | Active |
| USR-WRV-001 | `docs/user-guide/weekly-review.md` | Active |

### 4.15 Admin

| Document ID | File Path | Status |
|---|---|---|
| ADM-INDEX-001 | `docs/admin/README.md` | Active |

### 4.16 Learning Paths

| Document ID | File Path | Status |
|---|---|---|
| LRN-README-001 | `docs/learning-paths/README.md` | Active |
| LRN-FE-001 | `docs/learning-paths/frontend-dev.md` | Active |
| LRN-BE-001 | `docs/learning-paths/backend-dev.md` | Active |
| LRN-AI-001 | `docs/learning-paths/ai-agent-dev.md` | Active |

### 4.16 Postmortems

| Document ID | File Path | Status |
|---|---|---|
| PM-TPL-001 | `docs/postmortems/template.md` | Active |
| PM-DRL-001 | `docs/postmortems/drill-001.md` | Active |

### 4.17 Quickstart

| Document ID | File Path | Status |
|---|---|---|
| QST-001 | `docs/quickstart.md` | Active |

### 4.18 Scripts & Tooling

| Document ID | File Path | Status |
|---|---|---|
| SCR-MID-001 | `scripts/migrate-doc-ids.ps1` | Active |
| SCR-VID-001 | `scripts/validate-doc-ids.py` | Active |
| SCR-MLK-001 | `.markdownlint.jsonc` | Active |
| SCR-CLK-001 | `scripts/check-links.ps1` | Active |
| SCR-CLP-001 | `.github/workflows/ci.yml` (link-check job) | Active |
| SCR-PRE-001 | `.pre-commit-config.yaml` (doc hooks) | Active |
| SCR-MKF-001 | `Makefile` (validate-docs, validate-links, validate-doc-ids targets) | Active |

### 4.19 Enterprise Documents

| Document ID | File Path | Status |
|---|---|---|
| ENT-CMP-001 | `docs/enterprise/compliance-checklist.md` | Active |
| ENT-RDM-001 | `docs/enterprise/enterprise-roadmap.md` | Active |
| ENT-TDB-001 | `docs/enterprise/technical-debt-register.md` | Active |

### 4.20 Performance Documents

| Document ID | File Path | Status |
|---|---|---|
| PERF-CAP-001 | `docs/performance/capacity-planning.md` | Active |

### 4.21 Requirements Documents

| Document ID | File Path | Status |
|---|---|---|
| REQ-RTM-001 | `docs/requirements/requirements-traceability-matrix.md` | Active |

### 4.23 Root Legal Documents

| Document ID | File Path | Status |
|---|---|---|
| LEG-PRIV-001 | `PRIVACY.md` | Active |
| LEG-TERM-001 | `TERMS.md` | Active |
| LEG-COOK-001 | `COOKIE-POLICY.md` | Active |

---

## 5. Full Document Catalog by Category

### 5.1 Architecture (4 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `architecture/README.md` | ARCH-C4-001 | C4 model overview and architecture index | `database-erd.md`, `decision-log.md` |
| `architecture/database-erd.md` | ARCH-ERD-001 | Database entity relationship diagram | `engineering/15_Database.md` |
| `architecture/decision-log.md` | ARCH-DL-001 | Architecture decision log index | `engineering/adr/ADR-*.md` |
| `architecture/data-flow-diagrams.md` | ARCH-DFD-001 | System data flow diagrams | `engineering/12_Architecture.md` |

### 5.2 AI (48 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `ai/19_AI_Instructions.md` | — | AI system instructions and methodology | `20_Agent.md` |
| `ai/20_Agent.md` | SB-AGENT-001 | Comprehensive agent specification (239KB) | All agent docs |
| `ai/21_Prompts.md` | — | Prompt engineering guide | `10_PromptSystem.md` |
| `ai/22_MemoryArchitecture.md` | — | Memory system architecture | `LongTermMemory.md`, `ShortTermMemory.md` |
| `ai/23_KnowledgeGraph.md` | — | Knowledge graph design | `Embeddings.md`, `RAGArchitecture.md` |
| `ai/36_Skills.md` | — | Skills module overview | `ai/skills/` subdirectory |
| `ai/AIEvaluation.md` | — | AI output quality evaluation | `HallucinationHandling.md` |
| `ai/AIModels.md` | — | AI model selection and comparison | `AIModels.md` |
| `ai/BriefingAgent.md` | — | Daily briefing agent spec | `10_AgentSpec.md`, `prompts/agents/briefing_agent.md` |
| `ai/ContextEngine.md` | — | Context assembly for AI | `prompts/templates/context_assembly.md` |
| `ai/Embeddings.md` | — | Embedding generation and storage | `RAGArchitecture.md`, `VectorDatabase.md` |
| `ai/Guardrails.md` | — | Safety guardrails for AI | `prompts/system/guardrails.md` |
| `ai/HallucinationHandling.md` | — | Hallucination detection and mitigation | `AIEvaluation.md` |
| `ai/LearningAgent.md` | — | Learning pattern detection agent | `20_Agent.md`, `LearningAgent.md` |
| `ai/LongTermMemory.md` | — | Long-term memory storage | `MemoryArchitecture.md`, `MemoryCompression.md` |
| `ai/MemoryAgent.md` | — | Memory consolidation agent | `20_Agent.md`, `MemoryAgent.md` |
| `ai/MemoryCompression.md` | — | Memory compression techniques | `LongTermMemory.md` |
| `ai/MemoryRetrieval.md` | — | Memory retrieval strategies | `SemanticMemory.md`, `ShortTermMemory.md` |
| `ai/NudgeAgent.md` | — | Course/habit nudge agent | `20_Agent.md`, `prompts/agents/nudge_agent.md` |
| `ai/OpportunityMatchingAgent.md` | — | Opportunity scoring engine | `20_Agent.md`, `OpportunityRadarAgent.md` |
| `ai/OpportunityRadarAgent.md` | — | Opportunity matching agent | `20_Agent.md`, `prompts/agents/opportunity_radar_agent.md` |
| `ai/PromptVersioning.md` | — | Prompt versioning strategy | `PromptLoader.md`, `scripts/validate_prompts.py` |
| `ai/RAGArchitecture.md` | — | Retrieval-augmented generation design | `Embeddings.md`, `KnowledgeGraph.md` |
| `ai/RoadmapAgent.md` | — | Skill roadmap optimizer agent | `20_Agent.md`, `prompts/agents/roadmap_agent.md` |
| `ai/SemanticMemory.md` | — | Semantic memory implementation | `MemoryRetrieval.md`, `KnowledgeGraph.md` |
| `ai/ShortTermMemory.md` | — | Short-term / working memory | `MemoryRetrieval.md`, `ContextEngine.md` |
| `ai/SleepAgent.md` | — | Sleep analysis and wind-down agent | `20_Agent.md`, `prompts/agents/sleep_agent.md` |
| `ai/TaskAgent.md` | — | Task breakdown and analysis agent | `20_Agent.md`, `prompts/agents/task_agent.md` |
| `ai/ToolCalling.md` | — | AI tool-calling architecture | `AgentOrchestration.md`, `Functions.md` |
| `ai/WeeklyReviewAgent.md` | — | Weekly review generator agent | `20_Agent.md`, `prompts/agents/weekly_review_agent.md` |
| `ai/skills/SkillAgent.md` | — | Skills agent specification | `skills.md` |
| `ai/skills/SkillAnalytics.md` | — | Skills analytics and metrics | `SkillAssessment.md` |
| `ai/skills/SkillAssessment.md` | — | Skills assessment methodology | `SkillEvidence.md` |
| `ai/skills/SkillAuditEnterprise.md` | — | Enterprise skills audit | `SkillIntelligence.md` |
| `ai/skills/SkillDatabaseArchitecture.md` | — | Skills database schema | `SkillGraphArchitecture.md` |
| `ai/skills/SkillEvidence.md` | — | Skills evidence collection | `SkillAssessment.md` |
| `ai/skills/SkillGraphArchitecture.md` | — | Skills knowledge graph | `SkillDatabaseArchitecture.md` |
| `ai/skills/SkillIntelligence.md` | — | Skills market intelligence | `SkillMarketIntelligence.md` |
| `ai/skills/SkillMarketIntelligence.md` | — | Skills market data | `SkillIntelligence.md` |
| `ai/skills/SkillOpportunityMatching.md` | — | Skills opportunity matching | `OpportunityMatchingAgent.md` |
| `ai/skills/SkillRoadmapEngine.md` | — | Skills roadmap engine | `RoadmapAgent.md` |
| `ai/skills-system.md` | AI-SKS-001 | Skills system architecture and design | `skills/` subdirectory |
| `ai/skills/skills.md` | — | Skills module overview | All `ai/skills/*` |
| `ai/AIInsights.md` | OPS-AII-012 | AI-powered insights (moved from operations/) | `Agents.md`, `Reports.md`, `MemoryArchitecture.md` |
| `ai/AIObservability.md` | — | AI-specific observability (moved from operations/) | `ai/AIInsights.md`, `Tracing.md`, `Monitoring.md` |
| `ai/prompt-engineering-guide.md` | AI-PEG-001 | Prompt engineering best practices and patterns | `prompts/`, `PromptVersioning.md`, `PromptLoader.md` |
| `ai/AIIncidentResponse.md` | AI-IR-001 | AI-specific incident response procedures | `AIInsights.md`, `AIObservability.md`, `operations/40_IncidentResponse.md` |
| `ai/MCP-Architecture.md` | AI-MCP-001 | Model Context Protocol server architecture for external AI integration | `AgentArchitecture.md`, `ToolCalling.md`, `PromptLoader.md` |

### 5.3 Business (1 file)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `business/executive-summary.md` | BIZ-EXEC-001 | 12-section investor-ready executive summary | `product/02_PRD.md`, `product/03_BRD.md` |

### 5.4 Compliance (3 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `compliance/gdpr-ropa.md` | COMP-GDPR-ROPA-001 | GDPR Article 30 Record of Processing Activities | `security/24_Security.md`, `security/25_Compliance.md` |
| `compliance/soc2-readiness-report.md` | COMP-SOC2-001 | SOC 2 readiness assessment and 4-phase roadmap | `security/soc2_control_matrix.md` |
| `compliance/dpia.md` | COMP-DPIA-001 | Data Protection Impact Assessment for AI processing | `compliance/gdpr-ropa.md`, `ai/20_Agent.md` |

### 5.5 Design (35 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `design/08_UIUX.md` | DSG-UIUX-008 | UI/UX design philosophy (1,440 lines, merged from 09_Design.md) | `10_DesignSystem.md` |
| `design/10_DesignSystem.md` | DSG-DS-010 | Design system documentation (1,059 lines, expanded) | `35_DesignTokens.md`, `37_ComponentSpec.md` |
| `design/35_DesignTokens.md` | — | Design token specification | `Colors.md`, `Typography.md`, `Spacing.md` |
| `design/37_ComponentSpec.md` | — | Component specification | `10_DesignSystem.md`, `FrontendComponentLibrary.md` |
| `design/AnimationGuidelines.md` | DSG-ANM-007 | Animation and motion principles | `MotionArchitecture.md`, `MotionSystem.md` |
| `design/Branding.md` | — | Brand identity guidelines | `StyleGuide.md`, `Colors.md` |
| `design/Charts.md` | DSG-CHT-006 | Chart and data visualisation design | `Analytics.md`, `Dashboards.md` |
| `design/Colors.md` | DSG-CLR-001 | Colour system and tokens | `DarkMode.md`, `DesignTokens.md` |
| `design/Competitive_Intelligence_Report.md` | SB-CI-001 | Competitor UX analysis | `DesignStrategy.md`, `MarketResearch.md` |
| `design/DarkMode.md` | DSG-DRK-001 | Dark mode implementation | `Colors.md`, `DesignSystem.md` |
| `design/Design.md` | SB-DESIGN-ARCH-001 | Design architecture overview | `DesignStrategy.md`, `ProductArchitecture.md` |
| `design/ARCHIVED_DesignStrategy.md` | SB-DESIGN-STRAT-001 | Strategic design direction (archived) | `Design.md`, `Competitive_Intelligence_Report.md` |
| `design/DesignSystem.md` | SB-DESIGN-SYS-001 | Design system foundation | `10_DesignSystem.md`, `35_DesignTokens.md` |
| `design/ARCHIVED_DesignSystemResearch.md` | — | Design system research findings (archived) | `DesignSystem.md` |
| `design/ARCHIVED_Enterprise_Frontend_Discovery_Report.md` | SB-DISCOVERY-001 | Frontend technology discovery (archived) | `Enterprise_Frontend_Discovery_Report_v3.md` |
| `design/ARCHIVED_Enterprise_Frontend_Discovery_Report_v2.md` | SB-DISCOVERY-002 | Frontend discovery v2 (archived) | `Enterprise_Frontend_Discovery_Report_v3.md` |
| `design/Enterprise_Frontend_Discovery_Report_v3.md` | SB-DISCOVERY-003 | Frontend discovery v3 (final) | `Enterprise_Frontend_Discovery_Report.md` |
| `design/FigmaGovernance.md` | SB-FIGMA-GOV-001 | Figma file organisation | `DesignSystem.md`, `10_DesignSystem.md` |
| `design/FrontendAccessibilityGuide.md` | SB-A11Y-REF-001 | Frontend accessibility implementation | `38_Testing.md`, `QA_ACC.md` |
| `design/FrontendObservabilityGuide.md` | SB-OBS-REF-001 | Frontend observability | `Observability.md`, `Monitoring.md` |
| `design/FrontendScreenFlows.md` | DES-SF-001 | Screen flow documentation | `wireframes/`, `WorkflowArchitecture/` |
| `design/Icons.md` | DSG-ICN-004 | Icon system and usage | `Branding.md`, `DesignSystem.md` |
| `design/InformationArchitecture.md` | SB-IA-001 | Site structure and navigation | `UserJourneyArchitecture.md`, `WireframesIndex.md` |
| `design/Layouts.md` | DSG-LYT-005 | Layout grid and page structure | `Spacing.md`, `ResponsiveRules.md` |
| `design/MicroInteractions.md` | DSG-MIC-002 | Micro-interaction design | `AnimationGuidelines.md`, `MotionSystem.md` |
| `design/MotionArchitecture.md` | SB-MOTION-ARCH-001 | Motion system architecture | `MotionSystem.md`, `AnimationGuidelines.md` |
| `design/MotionSystem.md` | — | Motion system implementation | `MotionArchitecture.md`, `MicroInteractions.md` |
| `design/ProductArchitecture.md` | SB-ARCH-001 | Product architecture overview | `Engineering_Architecture.md` |
| `design/ResponsiveRules.md` | — | Responsive design breakpoints | `Layouts.md`, `Frontend_AppShell.md` |
| `design/Spacing.md` | DSG-SPC-003 | Spacing scale and grid | `Layouts.md`, `DesignTokens.md` |
| `design/StyleGuide.md` | DS-SG-001 | Comprehensive style guide | `Branding.md`, `Colors.md`, `Typography.md` |
| `design/Typography.md` | DSG-TYP-002 | Typography system | `StyleGuide.md`, `DesignTokens.md` |
| `design/UserJourneyArchitecture.md` | — | User journey mapping | `InformationArchitecture.md`, `WorkflowArchitecture/` |
| `design/wireframes/` | — | Wireframe index + 7 wireframe specs | `FrontendScreenFlows.md` |
| `design/WorkflowArchitecture/` | — | Workflow architecture (12 files) | `UserJourneyArchitecture.md` |
| `design/tokens/tokens-studio.json` | — | Design tokens in Tokens Studio format | `35_DesignTokens.md` |

### 5.6 DevOps (16 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `devops/26_Deployment.md` | — | Deployment strategy and process | `CD.md`, `Environments.md` |
| `devops/27_DevOps.md` | — | DevOps practices overview | `CI.md`, `CD.md` |
| `devops/38_ReleaseManagement.md` | SB-DEVOPS-REL-001 | Release management process | `CD.md`, `Rollback.md` |
| `devops/CD.md` | DVO-CD-012 | Continuous delivery pipeline | `CI.md`, `Deployment.md` |
| `devops/CDNStrategy.md` | — | CDN and asset delivery | `Deployment.md`, `PerformanceScalability.md` |
| `devops/CI.md` | DVO-CI-011 | Continuous integration pipeline | `CD.md`, `GitHubActions.md` |
| `devops/Docker.md` | — | Docker containerisation | `Kubernetes.md`, `Infrastructure.md` |
| `devops/Environments.md` | — | Environment configuration | `Deployment.md`, `ConfigurationManagement.md` |
| `devops/GitHubActions.md` | DVO-GHA-014 | GitHub Actions workflows | `CI.md`, `CD.md` |
| `devops/Infrastructure.md` | — | Infrastructure overview | `Terraform.md`, `Kubernetes.md` |
| `devops/Kubernetes.md` | — | Kubernetes orchestration (future) | `Docker.md`, `Infrastructure.md` |
| `devops/Rollback.md` | DVO-ROLL-015 | Rollback procedures | `Deployment.md`, `ReleaseManagement.md` |
| `devops/Terraform.md` | DVO-TERRA-013 | Infrastructure as Code | `Infrastructure.md`, `Environments.md` |
| `devops/production-deployment.md` | DVO-PROD-016 | Production deployment runbook (moved from operations/) | `CD.md`, `Rollback.md`, `CI.md` |
| `devops/backup-verification-procedure.md` | DVO-BAK-017 | Database backup verification procedure | `BackupStrategy.md`, `DisasterRecovery.md` |

### 5.7 Engineering (102 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `engineering/11_TechStack.md` | — | Technology stack overview | `12_Architecture.md` |
| `engineering/12_Architecture.md` | — | System architecture (~790 lines, expanded, absorbed 13_SystemArchitecture.md) | `46_Architecture_Update.md` |
| `engineering/14_AgentArchitecture.md` | — | AI agent architecture | `AgentOrchestration.md`, `AgentSpec.md` |
| `engineering/15_Database.md` | — | Database index (49-line index, replaced 1,168-line legacy doc) | Split into modular refs under `database/` |
| `engineering/16_DataGovernance.md` | — | Data governance policies | `security/25_DataRetentionPolicy.md`, `DataPrivacy.md` |
| `engineering/17_API.md` | — | API design and reference | `REST.md`, `Versioning.md`, `ErrorCodes.md` |
| `engineering/18_Events.md` | — | Event-driven architecture | `Webhooks.md`, `Realtime.md` |
| `engineering/37_IntegrationArchitecture.md` | — | Integration architecture | `integrations/` |
| `engineering/45_PerformanceScalability.md` | — | Performance and scalability | `RateLimiting.md`, `CachingStrategy.md` |
| `engineering/46_Architecture_Update.md` | SB-ARCH-UPDATE-046 | Architecture update tracking | `12_Architecture.md` |
| `engineering/api-integration-guide.md` | ENG-AIG-002 | API integration patterns and examples | `17_API.md`, `integrations/`, `api/openapi-reference.md`, `api/error-catalog.md` |
| `engineering/api/error-catalog.md` | ENG-ERRCAT-001 | Standardized error codes, messages, and handling patterns | `17_API.md`, `ErrorCodes.md`, `api/openapi-reference.md` |
| `engineering/AgentOrchestration.md` | — | Agent orchestration flow | `14_AgentArchitecture.md`, `AgentSpec.md` |
| `engineering/ApiGateway.md` | — | API gateway design | `17_API.md`, `Controllers.md` |
| `engineering/BackendArchitecture.md` | — | Backend service architecture | `Services.md`, `Controllers.md` |
| `engineering/BackgroundWorkers.md` | — | Background job processing | `CronJobs.md`, `QueueArchitecture.md` |
| `engineering/BackupStrategy.md` | — | Database backup strategy | `41_DisasterRecovery.md`, `DataGovernance.md` |
| `engineering/BusinessLogic.md` | — | Business logic layer | `Services.md`, `Validation.md` |
| `engineering/CachingStrategy.md` | — | Caching architecture | `RateLimiting.md`, `PerformanceScalability.md` |
| `engineering/ConfigurationManagement.md` | — | Configuration management | `Environments.md`, `SecretManagement.md` |
| `engineering/Constraints.md` | — | Engineering constraints | `TechStack.md`, `Architecture.md` |
| `engineering/Controllers.md` | — | Controller layer design | `Routes.md`, `Services.md` |
| `engineering/CronJobs.md` | — | Cron job specifications | `Schedulers.md`, `BackgroundWorkers.md` |
| `engineering/EnterprisePlan.md` | — | Enterprise feature plan | `ProductRoadmap.md`, `ScalingPlan.md` |
| `engineering/ERD.md` | — | Entity Relationship Diagram | `15_Database.md`, `Schema.md` |
| `engineering/ErrorCodes.md` | — | Error code reference | `17_API.md`, `Validation.md` |
| `engineering/FeatureFlags.md` | — | Feature flag system | `API_FeatureFlags.md` |
| `engineering/FormArchitecture.md` | FE-FORM-001 | Form handling architecture | `FrontendComponentLibrary.md`, `Validation.md` |
| `engineering/FrontendAIUXPatterns.md` | FE-AIUX-001 | AI-specific UI/UX patterns | `AgentArchitecture.md`, `10_DesignSystem.md` |
| `engineering/FrontendArchitecture.md` | — | Frontend architecture | `FrontendComponentLibrary.md`, `StateManagement.md` |
| `engineering/FrontendComponentLibrary.md` | FE-COMP-001 | Component library documentation | `37_ComponentSpec.md`, `DesignSystem.md` |
| `engineering/FrontendDataFetching.md` | FE-FETCH-001 | Data fetching patterns | `ServerActions.md`, `StateManagement.md` |
| `engineering/FrontendOfflinePWA.md` | ENG-FOP-001 | Offline/PWA implementation | `ServiceWorker.md`, `OfflineFirstArchitecture.md` |
| `engineering/FrontendPerformanceGuide.md` | FE-PERF-001 | Frontend performance optimisation | `RenderingStrategy.md`, `PerformanceScalability.md` |
| `engineering/FrontendRoutingNavigation.md` | ENG-FRN-001 | Routing and navigation | `FrontendArchitecture.md`, `InformationArchitecture.md` |
| `engineering/FrontendSecurityGuide.md` | FE-SEC-001 | Frontend security best practices | `Security.md`, `FrontendSecurityGuide.md` |
| `engineering/FrontendTechnicalResearch.md` | — | Frontend technology research | `TechStack.md` |
| `engineering/FrontendTestingStrategy.md` | FE-TEST-001 | Frontend testing approach | `Testing_Strategy.md`, `E2ETesting.md` |
| `engineering/Functions.md` | — | Serverless functions | `ServerActions.md`, `BackgroundWorkers.md` |
| `engineering/HistoryTables.md` | — | Audit history table design | `AuditLogs.md`, `Triggers.md` |
| `engineering/Indexes.md` | — | Database index strategy | `15_Database.md`, `PerformanceScalability.md` |
| `engineering/Internationalization.md` | — | i18n strategy | `FrontendArchitecture.md` |
| `engineering/MaterializedViews.md` | — | Materialized view design | `Views.md`, `Analytics.md` |
| `engineering/Microservices.md` | — | Microservices architecture (future) | `Architecture.md`, `EnterprisePlan.md` |
| `engineering/MigrationStrategy.md` | — | Data migration strategy | `BackupStrategy.md`, `Versioning.md` |
| `engineering/NotificationSystem.md` | — | Notification system design | `integrations/Notifications.md` |
| `engineering/OfflineFirstArchitecture.md` | — | Offline-first approach | `FrontendOfflinePWA.md`, `Realtime.md` |
| `engineering/PermissionsAndRoles.md` | — | Permissions model | `RLS.md`, `AuthArchitecture.md` |
| `engineering/Policies.md` | — | Database policies | `RLS.md`, `Triggers.md` |
| `engineering/QueueArchitecture.md` | — | Queue and message architecture | `BackgroundWorkers.md`, `Webhooks.md` |
| `engineering/RateLimiting.md` | — | Rate limiting implementation | `API.md`, `PerformanceScalability.md` |
| `engineering/Realtime.md` | — | Realtime features | `RealtimeArchitecture.md`, `Webhooks.md` |
| `engineering/RealtimeArchitecture.md` | — | Realtime architecture | `Realtime.md`, `Supabase.md` |
| `engineering/Repositories.md` | — | Repository pattern | `Services.md`, `BusinessLogic.md` |
| `engineering/REST.md` | — | RESTful API design | `17_API.md`, `Versioning.md` |
| `engineering/RLS.md` | — | Row Level Security policies | `15_Database.md`, `Policies.md` |
| `engineering/Schedulers.md` | — | Scheduler architecture | `CronJobs.md`, `BackgroundWorkers.md` |
| `engineering/Schema.md` | — | Database schema reference | `15_Database.md`, `ERD.md` |
| `engineering/SearchArchitecture.md` | — | Search functionality | `VectorDatabase.md`, `Indexes.md` |
| `engineering/ServerActions.md` | — | Server Actions (Next.js) | `FrontendDataFetching.md` |
| `engineering/Services.md` | — | Service layer architecture | `Repositories.md`, `BusinessLogic.md` |
| `engineering/StateManagement.md` | — | State management (Zustand) | `FrontendArchitecture.md`, `ADR-005.md` |
| `engineering/Triggers.md` | — | Database triggers | `Policies.md`, `HistoryTables.md` |
| `engineering/Validation.md` | — | Input validation strategy | `FormArchitecture.md`, `ErrorCodes.md` |
| `engineering/VectorDatabase.md` | — | Vector database for embeddings | `Embeddings.md`, `SearchArchitecture.md` |
| `engineering/Versioning.md` | — | API versioning strategy | `17_API.md`, `REST.md` |
| `engineering/Views.md` | — | Database views | `MaterializedViews.md`, `Schema.md` |
| `engineering/Webhooks.md` | — | Webhook system | `Events.md`, `QueueArchitecture.md` |
| `engineering/WorkflowEngine.md` | — | Workflow engine design | `AgentOrchestration.md`, `StateManagement.md` |
| `engineering/coding-standards.md` | ENG-CST-001 | Coding standards for Python, TypeScript, YAML, SQL | `AGENTS.md §4`, `engineering/plugin-system.md` |
| `engineering/plugin-system.md` | ENG-PLUG-001 | Plugin system architecture and extension framework | `engineering/12_Architecture.md`, `engineering/Constraints.md` |
| `engineering/api/sdk-reference.md` | ENG-SDK-001 | Python and TypeScript SDK reference for ARIA OS API | `engineering/17_API.md`, `engineering/api/openapi-reference.md` |
| `engineering/adr/ADR-*.md` (15 files) | — | Architecture Decision Records | All engineering docs |
| `engineering/integrations/*.md` (10 files) | — | Third-party integration specs | `37_IntegrationArchitecture.md` |
| `engineering/modules/ModulesImplementationSpec.md` | ENG-MIS-001 | Module implementation spec | `15_Database.md`, `17_API.md` |
| `engineering/supply-chain-security.md` | ENG-SCS-001 | Supply chain security practices | `devops/Docker.md`, `security/24_Security.md` |
| `engineering/secrets-management.md` | ENG-SMG-001 | Secrets management and rotation | `security/Encryption.md`, `ConfigurationManagement.md` |

### 5.8 Frontend (6 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `frontend/FolderStructure.md` | FE-FS-001 | Frontend folder organisation | `FrontendArchitecture.md` |
| `frontend/IMPLEMENTATION_BACKLOG.md` | — | Frontend implementation backlog | `SprintPlan.md`, `Backlog.md` |
| `frontend/RenderingStrategy.md` | FE-RS-001 | Client/server rendering decisions | `FrontendPerformanceGuide.md`, `SEO.md` |
| `frontend/SEO.md` | FE-SEO-001 | SEO strategy and implementation | `RenderingStrategy.md` |
| `frontend/StateManagement.md` | FE-SM-001 | State management architecture (Zustand, TanStack Query, IndexedDB) | `frontend/FolderStructure.md`, `frontend/RenderingStrategy.md` |
| `frontend/ComponentLibrary.md` | FE-CL-001 | Component library following atomic design (40+ UI primitives, Storybook 7) | `frontend/StateManagement.md`, `design/10_DesignSystem.md` |

### 5.9 Operations (43 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `operations/30_Analytics.md` | SB-OPS-ANL-001 | Analytics architecture and pipeline | `Events.md`, `Funnels.md`, `PostHog.md` |
| `operations/31_Observability.md` | — | Observability architecture | `Tracing.md`, `Monitoring.md`, `Dashboards.md` |
| `operations/32_Monitoring.md` | SB-OPS-MON-001 | Monitoring infrastructure | `Dashboards.md`, `Alerts.md`, `Sentry.md` |
| `operations/33_Roadmap.md` | SB-ROADMAP-001 | Product roadmap | `Product_Roadmap.md`, `Backlog.md` |
| `operations/34_Backlog.md` | — | Feature and bug backlog | `SprintPlan.md`, `Roadmap.md` |
| `operations/39_Runbooks.md` | SB-RUNBOOKS-001 | Operational runbooks | `Playbooks.md`, `IncidentResponse.md` |
| `operations/40_IncidentResponse.md` | — | Incident response procedures | `Alerts.md`, `Runbooks.md`, `Playbooks.md` |
| `operations/41_DisasterRecovery.md` | SB-DR-001 | Disaster recovery plan | `BackupStrategy.md`, `Playbooks.md` |
| `operations/42_RiskManagement.md` | — | Risk management framework | `Security_Risk.md`, `DisasterRecovery.md` |
| `operations/43_SLA.md` | SB-SLA-001 | Service level agreements | `Support.md`, `Alerts.md` |
| `operations/44_DeveloperOnboarding.md` | — | Developer onboarding guide | `Contributing.md`, `GitWorkflow.md` |
| `operations/47_CostManagement.md` | — | Cost tracking and optimisation | `ScalingPlan.md`, `Infrastructure.md` |
| `operations/50_TechnicalDebt.md` | — | Technical debt register | `SprintPlan.md`, `Maintenance.md` |
| `operations/AuditLogs.md` | — | Audit trail logging | `HistoryTables.md`, `Security.md` |
| `operations/Contributing.md` | — | Contribution guidelines | `DeveloperOnboarding.md`, `GitWorkflow.md` |
| `operations/DataRetention.md` | — | Data retention overview | Deleted — consolidated into `security/25_DataRetentionPolicy.md` |
| `operations/DataRetentionPolicy.md` | — | Data retention policy details | Deleted — consolidated into `security/25_DataRetentionPolicy.md` |
| `operations/DefinitionOfDone.md` | — | Definition of Done checklist | `AcceptanceCriteria.md`, `SprintReview.md` |
| `operations/Dependencies.md` | — | Project dependencies overview | `DependencyManagement.md`, `TechStack.md` |
| `operations/DependencyManagement.md` | — | Dependency update process | `Dependencies.md`, `Maintenance.md` |
| `operations/GitWorkflow.md` | — | Git branch strategy | `Contributing.md`, `DeveloperOnboarding.md` |
| `operations/IMPLEMENTATION_STATUS.md` | — | Implementation status tracker | `Roadmap.md`, `SprintPlan.md` |
| `operations/InnovationRadar.md` | — | Technology innovation tracking | `Roadmap.md`, `MaturityModel.md` |
| `operations/KPIs.md` | OPS-KPI-012 | Key Performance Indicators | `Funnels.md`, `SuccessMetrics.md` |
| `operations/MaturityModel.md` | — | Operations maturity assessment | `ScalingPlan.md`, `EnterprisePlan.md` |
| `operations/PromptVersioning.md` | — | Prompt versioning (operations view) | Deleted — duplicate of `ai/PromptVersioning.md` |
| `operations/ScalingPlan.md` | — | Scaling strategy | `MaturityModel.md`, `EnterprisePlan.md` |
| `operations/SOC2Readiness.md` | — | SOC 2 compliance readiness | `Compliance.md`, `Security.md` |
| `operations/SprintPlan.md` | — | Sprint planning | `Backlog.md`, `SprintReview.md` |
| `operations/SprintReview.md` | — | Sprint review process | `SprintPlan.md`, `DefinitionOfDone.md` |
| `operations/TaskBreakdown.md` | — | Task breakdown methodology | `SprintPlan.md`, `Backlog.md` |
| `operations/TechnicalDebt.md` | — | Technical debt details | `TechnicalDebt.md` (duplicate), `Maintenance.md` |
| `operations/Tracing.md` | OPS-TRC-001 | Distributed tracing | `Observability.md`, `Sentry.md` |
| `operations/Dashboards.md` | OPS-DSH-002 | Monitoring dashboards | `Monitoring.md`, `Alerts.md` |
| `operations/Alerts.md` | OPS-ALR-003 | Alerting system | `Dashboards.md`, `Sentry.md`, `IncidentResponse.md` |
| `operations/Sentry.md` | OPS-SNT-004 | Sentry error tracking | `Alerts.md`, `Tracing.md`, `Monitoring.md` |
| `operations/PostHog.md` | OPS-PST-005 | PostHog product analytics (planned) | `Analytics.md`, `Events.md`, `Funnels.md` |
| `operations/Playbooks.md` | OPS-PLB-006 | Operational playbooks | `Runbooks.md`, `Maintenance.md`, `Support.md` |
| `operations/Maintenance.md` | OPS-MNT-007 | Maintenance procedures | `Playbooks.md`, `ChangeManagement.md` |
| `operations/Support.md` | OPS-SUP-008 | Support processes | `SLA.md`, `Contributing.md` |
| `operations/Funnels.md` | OPS-FNL-009 | Conversion funnels | `Analytics.md`, `Events.md`, `KPIs.md` |
| `operations/Events.md` | OPS-EVT-010 | Event tracking specification | `Analytics.md`, `Funnels.md`, `PostHog.md` |
| `operations/Reports.md` | OPS-RPT-011 | Reporting system | `Analytics.md`, `Funnels.md` |
| `operations/firefighter-runbooks.md` | OPS-FFR-015 | Firefighter rotation runbooks (on-call procedures) | `Runbooks.md`, `Playbooks.md`, `IncidentResponse.md` |
| `operations/error-budget.md` | OPS-EB-001 | Error budget policy and tracking | `KPIs.md`, `SLA.md`, `Alerts.md` |

### 5.10 Product (28 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `product/00_ProjectVision.md` | SB-PVD-001 | Project vision and mission | `Mission.md`, `ProductStrategy.md` |
| `product/01_CurrentStateAudit.md` | SB-AUDIT-001 | Current state assessment | `ImplementationStatus.md`, `TechnicalDebt.md` |
| `product/02_PRD.md` | SB-PRD-001 | Product Requirements Document | `SRS.md`, `BRD.md` |
| `product/03_BRD.md` | SB-BRD-001 | Business Requirements Document | `PRD.md` |
| `product/04_SRS.md` | SB-SRS-001 | Software Requirements Specification | `PRD.md`, `AcceptanceCriteria.md` |
| `product/06_UserStories.md` | SB-US-001 | User stories collection | `AcceptanceCriteria.md`, `UseCases.md` |
| `product/07_AcceptanceCriteria.md` | SB-AC-001 | Acceptance criteria | `UserStories.md`, `DefinitionOfDone.md` |
| `product/Assumptions.md` | PRD-ASM-006 | Project assumptions | `Constraints.md`, `Risks.md` |
| `product/CompetitiveAnalysis.md` | SB-CA-001 | Competitive landscape | `MarketResearch.md`, `ValueProposition.md` |
| `product/Constraints.md` | PRD-CON-006 | Project constraints | `Assumptions.md`, `Risks.md` |
| `product/DecisionLog.md` | PRD-DEC-008 | Key product decisions | `ADRs.md`, `Changelog.md` |
| `product/Glossary.md` | PRD-GLO-005 | Project glossary | `DocumentationStandards.md` |
| `product/Goals.md` | PRD-GOL-002 | Product goals and objectives | `KPIs.md`, `SuccessMetrics.md` |
| `product/MarketResearch.md` | PRD-MR-003 | Market research findings | `CompetitiveAnalysis.md`, `Personas.md` |
| `product/Mission.md` | PRD-MIS-001 | Product mission statement | `ProjectVision.md`, `ValueProposition.md` |
| `product/Monetization.md` | SB-MON-001 | Monetisation strategy | `Pricing.md`, `EnterprisePlan.md` |
| `product/Personas.md` | SB-PERS-001 | User personas | `UserStories.md`, `UserFlows.md` |
| `product/ProductStrategy.md` | PRD-STG-001 | Product strategy | `ProjectVision.md`, `Roadmap.md` |
| `product/ProjectScope.md` | PRD-SCO-004 | Project scope definition | `Constraints.md`, `SRS.md` |
| `product/RequirementsTraceabilityMatrix.md` | PRD-RTM-009 | Requirements traceability | `SRS.md`, `AcceptanceCriteria.md` |
| `product/Risks.md` | PRD-RIS-007 | Product risks register | `Assumptions.md`, `RiskManagement.md` |
| `product/Roadmap.md` | SB-ROADMAP-001 | Product roadmap | `Operations_Roadmap.md`, `SprintPlan.md` |
| `product/Stakeholders.md` | PRD-SH-007 | Stakeholder registry | `Personas.md`, `DecisionLog.md` |
| `product/SuccessMetrics.md` | PRD-MET-003 | Success metrics | `KPIs.md`, `Goals.md` |
| `product/UseCases.md` | SB-UC-001 | Use case descriptions | `UserStories.md`, `UserFlows.md` |
| `product/UserFlows.md` | SB-UF-001 | User flow diagrams | `UseCases.md`, `WorkflowArchitecture/` |
| `product/ValueProposition.md` | PRD-VP-002 | Value proposition | `Mission.md`, `CompetitiveAnalysis.md` |
| `product/KPI-dashboard.md` | PRD-KPI-001 | KPI dashboard with targets and measurement methods | `SuccessMetrics.md`, `operations/KPIs.md`, `operations/error-budget.md` |

### 5.11 QA (12 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `qa/28_Testing.md` | QA-TEST-STRAT-001 | Overall testing strategy (4,384 lines, merged from 29_QA.md) | `IntegrationTesting.md`, `E2ETesting.md` |
| `qa/AccessibilityTesting.md` | QA-ACC-002 | Accessibility testing (WCAG AA) | `E2ETesting.md`, `FrontendAccessibilityGuide.md` |
| `qa/ChaosTesting.md` | QA-CHS-007 | Chaos engineering tests | `StressTesting.md`, `SecurityTesting.md` |
| `qa/E2ETesting.md` | — | End-to-end testing with Playwright | `Testing.md`, `IntegrationTesting.md` |
| `qa/E2ETestPlan.md` | — | E2E test plan and scenarios | `E2ETesting.md` |
| `qa/IntegrationTesting.md` | QA-INT-001 | Integration testing approach | `Testing.md`, `UnitTesting.md` |
| `qa/LoadTesting.md` | QA-LDT-010 | Load and performance testing | `StressTesting.md`, `PerformanceTesting.md` |
| `qa/PerformanceTesting.md` | — | Performance testing specifications | `LoadTesting.md`, `StressTesting.md` |
| `qa/RegressionTesting.md` | QA-RGT-008 | Regression testing process | `E2ETesting.md`, `CI.md` |
| `qa/SecurityTesting.md` | QA-SCT-009 | Security testing procedures | `Security.md`, `ChaosTesting.md` |
| `qa/StressTesting.md` | QA-STR-011 | Stress and spike testing | `LoadTesting.md`, `ChaosTesting.md` |
| `qa/UAT.md` | QA-UAT-006 | User Acceptance Testing | `AcceptanceCriteria.md` |

### 5.12 Quickstart (1 file)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `quickstart.md` | QST-001 | 3-command developer setup cheat sheet | `AGENTS.md`, `operations/44_DeveloperOnboarding.md` |

### 5.13 Security (18 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `security/24_Security.md` | SB-SEC-001 | Security architecture | `Compliance.md`, `ThreatModel.md` |
| `security/25_Compliance.md` | SB-COMP-001 | Compliance framework | `Security.md`, `SOC2Readiness.md` |
| `security/25_DataRetentionPolicy.md` | — | Data retention policy (authoritative) | `DataPrivacy.md` |
| `security/46_DataPrivacy.md` | — | Data privacy principles | `Compliance.md`, `DataRetentionPolicy.md` |
| `security/AuthArchitecture.md` | — | Authentication architecture | `Security.md`, `Encryption.md` |
| `security/Encryption.md` | — | Encryption standards | `Security.md`, `SecretsManagement.md` |
| `security/SecretsManagement.md` | — | Secrets management | `Encryption.md`, `ConfigurationManagement.md` |
| `security/soc2_control_matrix.md` | — | SOC 2 control mapping | `Compliance.md`, `SOC2Readiness.md` |
| `security/ThreatModel.md` | — | Threat modelling | `Security.md`, `SecurityTesting.md` |
| `security/VulnerabilityInventory.md` | SEC-VULN-INV-001 | Known vulnerability register (v2.0.0) | `ThreatModel.md`, `policies/vulnerability-management.md` |
| `security/policies/vulnerability-management.md` | SEC-VULN-001 | Vulnerability lifecycle policy (CVSS, SLAs) | `VulnerabilityInventory.md`, `security/24_Security.md` |
| `security/sdl.md` | SEC-SDL-001 | Security Development Lifecycle (SDL) practices | `24_Security.md`, `Compliance.md` |
| `security/hardening/supabase.md` | SEC-HRD-SUP-001 | Supabase hardening guide | `24_Security.md`, `engineering/15_Database.md` |
| `security/hardening/nextjs.md` | SEC-HRD-NX-001 | Next.js frontend hardening guide | `24_Security.md`, `engineering/FrontendSecurityGuide.md` |
| `security/hardening/fastapi.md` | SEC-HRD-FA-001 | FastAPI backend hardening guide | `24_Security.md`, `engineering/BackendArchitecture.md` |

### 5.14 Governance (10 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `governance/README.md` | GOV-README-001 | Governance directory overview and index | All `governance/` files |
| `governance/01_DocumentationStandards.md` | OPS-STD-001 | Documentation standards and style guide (moved from operations/48_) | `DOCUMENTATION_INDEX.md`, `documentation-ownership.md` |
| `governance/02_ChangeManagement.md` | OPS-CHG-002 | Change management process (moved from operations/49_) | `01_DocumentationStandards.md`, `devops/ReleaseManagement.md` |
| `governance/documentation-ownership.md` | OPS-OWN-013 | 8-role ownership matrix for ~280 docs (moved from operations/) | `documentation-review-schedule.md`, `01_DocumentationStandards.md` |
| `governance/documentation-review-schedule.md` | OPS-REV-014 | 3-tier review cadence for documentation (moved from operations/) | `documentation-ownership.md`, `01_DocumentationStandards.md` |
| `governance/documentation-maturity-model.md` | GOV-DMM-001 | Documentation maturity assessment framework | `01_DocumentationStandards.md`, `documentation-ownership.md` |
| `governance/templates/template-architecture.md` | GOV-TPL-ARC-001 | Architecture document template | `01_DocumentationStandards.md` |
| `governance/templates/template-api-endpoint.md` | GOV-TPL-API-001 | API endpoint documentation template | `01_DocumentationStandards.md` |
| `governance/templates/template-guide.md` | GOV-TPL-GDE-001 | General guide/process document template | `01_DocumentationStandards.md` |
| `governance/glossary.md` | GOV-GLO-001 | Project-wide acronym and term glossary | `product/Glossary.md`, `01_DocumentationStandards.md` |

### 5.15 Admin (1 file)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `admin/README.md` | ADM-INDEX-001 | Admin panel architecture, endpoints, security, deployment | `engineering/12_Architecture.md`, `security/24_Security.md`, `operations/39_Runbooks.md` |

### 5.16 User Guide (17 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `user-guide/README.md` | USR-README-001 | User guide directory overview | All `user-guide/` files |
| `user-guide/getting-started.md` | USR-GS-001 | Getting started guide for end users | `user-guide/features-overview.md` |
| `user-guide/features-overview.md` | USR-FO-001 | Overview of all available features | `user-guide/getting-started.md`, `product/03_Features.md` |
| `user-guide/tasks.md` | USR-TSK-001 | Task management user guide | `user-guide/features-overview.md` |
| `user-guide/habits.md` | USR-HBT-001 | Habit tracking user guide | `user-guide/features-overview.md` |
| `user-guide/sleep.md` | USR-SLP-001 | Sleep tracking user guide | `user-guide/features-overview.md` |
| `user-guide/chat-and-ai.md` | USR-CHT-001 | Chat and AI features user guide | `user-guide/features-overview.md`, `ai/20_Agent.md` |
| `user-guide/FAQ.md` | USR-FAQ-001 | Frequently asked questions | All `user-guide/` files |
| `user-guide/courses.md` | USR-CRS-001 | Course tracking across platforms | `user-guide/goals.md`, `user-guide/tasks.md` |
| `user-guide/goals.md` | USR-GLS-001 | Goal management and roadmap | `user-guide/courses.md`, `user-guide/tasks.md`, `user-guide/projects.md` |
| `user-guide/ideas.md` | USR-IDEA-001 | Idea vault and pipeline management | `user-guide/projects.md`, `user-guide/features-overview.md` |
| `user-guide/income.md` | USR-INC-001 | Income tracking and hourly rates | `user-guide/features-overview.md` |
| `user-guide/opportunities.md` | USR-OPP-001 | Opportunity radar and matching | `user-guide/goals.md`, `user-guide/features-overview.md` |
| `user-guide/projects.md` | USR-PRJ-001 | Project management with phases | `user-guide/goals.md`, `user-guide/ideas.md` |
| `user-guide/resources.md` | USR-RSC-001 | Resource library and tagging | `user-guide/features-overview.md` |
| `user-guide/time-tracking.md` | USR-TTR-001 | Time tracking and Pomodoro | `user-guide/tasks.md`, `user-guide/features-overview.md` |
| `user-guide/weekly-review.md` | USR-WRV-001 | Weekly review and AI summary | `user-guide/features-overview.md`, `user-guide/goals.md` |

### 5.17 Learning Paths (4 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `learning-paths/README.md` | LRN-README-001 | Learning paths directory overview | All `learning-paths/` files |
| `learning-paths/frontend-dev.md` | LRN-FE-001 | Frontend developer learning path | `frontend/FolderStructure.md`, `engineering/FrontendComponentLibrary.md` |
| `learning-paths/backend-dev.md` | LRN-BE-001 | Backend developer learning path | `engineering/11_TechStack.md`, `engineering/17_API.md` |
| `learning-paths/ai-agent-dev.md` | LRN-AI-001 | AI/agent developer learning path | `ai/20_Agent.md`, `packages/ai/prompt_loader.py` |

### 5.18 Postmortems (2 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `postmortems/template.md` | PM-TPL-001 | Incident postmortem report template | `operations/40_IncidentResponse.md` |
| `postmortems/drill-001.md` | PM-DRL-001 | First tabletop exercise/drill report | `postmortems/template.md` |

### 5.19 Root Legal (3 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `PRIVACY.md` | LEG-PRIV-001 | Privacy policy for Second Brain OS | `TERMS.md`, `COOKIE-POLICY.md` |
| `TERMS.md` | LEG-TERM-001 | Terms of service for Second Brain OS | `PRIVACY.md`, `COOKIE-POLICY.md` |
| `COOKIE-POLICY.md` | LEG-COOK-001 | Cookie policy for Second Brain OS | `PRIVACY.md`, `TERMS.md` |

### 5.20 Scripts & Tooling (7 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `scripts/migrate-doc-ids.ps1` | SCR-MID-001 | PowerShell script to migrate legacy doc IDs to standardized format across all 340 files | `scripts/validate-doc-ids.py`, `.markdownlint.jsonc` |
| `scripts/validate-doc-ids.py` | SCR-VID-001 | Python validator to verify Document ID compliance across all docs | `scripts/migrate-doc-ids.ps1`, `.markdownlint.jsonc` |
| `scripts/check-links.ps1` | SCR-CLK-001 | PowerShell link checker for broken relative/absolute links in markdown docs | `Makefile`, `.pre-commit-config.yaml` |
| `.markdownlint.jsonc` | SCR-MLK-001 | markdownlint configuration enforcing doc standards (MD041, MD022, line length, etc.) | `scripts/validate-doc-ids.py`, `docs/governance/01_DocumentationStandards.md` |
| `.github/workflows/ci.yml` (link-check job) | SCR-CLP-001 | CI job that runs link checking on every push/PR to main branch | `scripts/check-links.ps1`, `Makefile` |
| `.pre-commit-config.yaml` (doc hooks) | SCR-PRE-001 | Pre-commit hooks for link checking and doc ID validation before commits | `scripts/validate-doc-ids.py`, `scripts/check-links.ps1` |
| `Makefile` (validate targets) | SCR-MKF-001 | Makefile targets: `validate-docs`, `validate-links`, `validate-doc-ids` | `.github/workflows/ci.yml`, `.pre-commit-config.yaml` |

### 5.21 Enterprise (3 files)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `enterprise/compliance-checklist.md` | ENT-CMP-001 | Enterprise compliance checklist (GDPR, SOC 2, ISO 27001) | `enterprise/enterprise-roadmap.md`, `security/soc2_control_matrix.md` |
| `enterprise/enterprise-roadmap.md` | ENT-RDM-001 | Enterprise maturity roadmap (Q3 2026–Q2 2027) | `enterprise/compliance-checklist.md`, `enterprise/technical-debt-register.md` |
| `enterprise/technical-debt-register.md` | ENT-TDB-001 | Technical debt register with 15 tracked items | `enterprise/enterprise-roadmap.md`, `engineering/adr/` |

### 5.22 Performance (1 file)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `performance/capacity-planning.md` | PERF-CAP-001 | Capacity planning guide with growth thresholds, bottleneck analysis, scaling triggers, and cost projections | `AGENTS.md §26`, `devops/Deployment.md` |

### 5.23 Requirements (1 file)

| File Name | Document ID | Purpose | Related Documents |
|---|---|---|---|
| `requirements/requirements-traceability-matrix.md` | REQ-RTM-001 | Requirements traceability matrix (ISO 9001/CMMI) with 48 requirements traced across FR, NFR, SEC, and AI categories | `product/02_PRD.md`, `product/04_SRS.md`, `engineering/adr/`, `enterprise/compliance-checklist.md` |

---

## 6. Quick-Start Reading Guide by Role

### 6.1 New Developer

| Order | Document | Why |
|---|---|---|
| 1 | `AGENTS.md` (root) | Master reference: architecture, conventions, commands |
| 2 | `docs/operations/44_DeveloperOnboarding.md` | Setup guide and 30-60-90 day plan |
| 3 | `docs/engineering/11_TechStack.md` | Technology choices and rationale |
| 4 | `docs/engineering/12_Architecture.md` | System architecture overview |
| 5 | `docs/product/00_ProjectVision.md` | Product vision and goals |
| 6 | `docs/governance/01_DocumentationStandards.md` | Documentation conventions |

### 6.2 Backend Developer

| Order | Document | Why |
|---|---|---|
| 1 | `docs/engineering/17_API.md` | API design and all endpoints |
| 2 | `docs/engineering/15_Database.md` | Database schema and relationships |
| 3 | `docs/engineering/14_AgentArchitecture.md` | AI agent architecture |
| 4 | `docs/engineering/REST.md` | RESTful API conventions |
| 5 | `docs/engineering/RLS.md` | Row-level security policies |
| 6 | `docs/engineering/ErrorCodes.md` | Error handling standards |
| 7 | `docs/engineering/adr/ADR-*.md` | Architecture decisions (15 files) |

### 6.3 Frontend Developer

| Order | Document | Why |
|---|---|---|
| 1 | `docs/frontend/FolderStructure.md` | Project structure |
| 2 | `docs/frontend/RenderingStrategy.md` | Rendering decisions |
| 3 | `docs/design/10_DesignSystem.md` | Design tokens and components |
| 4 | `docs/design/08_UIUX.md` | UI/UX philosophy |
| 5 | `docs/engineering/FrontendComponentLibrary.md` | Component library |
| 6 | `docs/engineering/FrontendDataFetching.md` | Data fetching patterns |
| 7 | `docs/engineering/StateManagement.md` | Zustand store architecture |

### 6.4 AI / ML Engineer

| Order | Document | Why |
|---|---|---|
| 1 | `docs/ai/20_Agent.md` | Complete agent specification (239KB) |
| 2 | `docs/engineering/14_AgentArchitecture.md` | Agent system architecture |
| 3 | `docs/ai/22_MemoryArchitecture.md` | Memory system |
| 4 | `docs/ai/23_KnowledgeGraph.md` | Knowledge graph design |
| 5 | `packages/ai/prompt_loader.py` | PromptLoader implementation |
| 6 | `prompts/` (directory) | All prompt templates |
| 7 | `docs/ai/RAGArchitecture.md` | RAG architecture |

### 6.5 DevOps / SRE

| Order | Document | Why |
|---|---|---|
| 1 | `docs/devops/26_Deployment.md` | Deployment process |
| 2 | `docs/devops/CI.md` | CI pipeline |
| 3 | `docs/devops/CD.md` | CD pipeline |
| 4 | `docs/devops/Infrastructure.md` | Infrastructure overview |
| 5 | `docs/devops/Docker.md` | Docker configuration |
| 6 | `docs/operations/39_Runbooks.md` | Operational runbooks |
| 7 | `docs/operations/Playbooks.md` | Operational playbooks |

### 6.6 Product Manager

| Order | Document | Why |
|---|---|---|
| 1 | `docs/product/00_ProjectVision.md` | Product vision |
| 2 | `docs/product/02_PRD.md` | Product requirements |
| 3 | `docs/product/ProductStrategy.md` | Strategic direction |
| 4 | `docs/product/06_UserStories.md` | User stories |
| 5 | `docs/product/Personas.md` | User personas |
| 6 | `docs/operations/33_Roadmap.md` | Product roadmap |

### 6.7 Quality Assurance

| Order | Document | Why |
|---|---|---|
| 1 | `docs/qa/28_Testing.md` | Overall testing strategy |
| 2 | `docs/qa/IntegrationTesting.md` | Integration test approach |
| 3 | `docs/qa/E2ETesting.md` | E2E testing with Playwright |
| 4 | `docs/qa/AccessibilityTesting.md` | Accessibility testing |
| 5 | `docs/qa/RegressionTesting.md` | Regression test process |
| 6 | `docs/qa/LoadTesting.md` | Load and performance testing |

### 6.8 Security Engineer

| Order | Document | Why |
|---|---|---|
| 1 | `docs/security/24_Security.md` | Security architecture |
| 2 | `docs/security/25_Compliance.md` | Compliance framework |
| 3 | `docs/security/ThreatModel.md` | Threat model |
| 4 | `docs/security/AuthArchitecture.md` | Authentication design |
| 5 | `docs/security/Encryption.md` | Encryption standards |
| 6 | `docs/security/soc2_control_matrix.md` | SOC 2 controls |

---

## 7. Relationship Diagram

```mermaid
graph TD
    subgraph Product["Product Layer"]
        Vision[Project Vision]
        PRD[PRD / BRD / SRS]
        Features[Features]
        Stories[User Stories]
        Personas[User Personas]
        Roadmap[Product Roadmap]
    end

    subgraph Design["Design Layer"]
        UIUX[UI/UX Guidelines]
        DS[Design System]
        Tokens[Design Tokens]
        Wireframes[Wireframes]
        Workflows[Workflow Architecture]
    end

    subgraph Engineering["Engineering Layer"]
        Architecture[System Architecture]
        ADR[ADRs - 15 files]
        API[API Design]
        DB[Database Schema]
        Agents[Agent Architecture]
        Integrations[10 Integration Specs]
        Modules[Module Implementation]
    end

    subgraph AI["AI Layer"]
        AgentSpec[Agent Spec]
        Prompts[22 Prompt Files]
        Memory[Memory Architecture]
        KnowledgeGraph[Knowledge Graph]
        RAG[RAG Architecture]
        Skills[Skills System]
    end

    subgraph Frontend["Frontend Layer"]
        FolderStructure[Folder Structure]
        Rendering[Rendering Strategy]
        Components[Component Library]
        State[State Management]
    end

    subgraph Operations["Operations Layer"]
        Monitoring[Monitoring]
        Dashboards[Dashboards]
        Alerts[Alerts]
        Tracing[Tracing]
        Runbooks[Runbooks]
        Playbooks[Playbooks]
        KPIs[KPIs]
        SLA[SLAs]
        Analytics[Analytics]
        Events[Events]
        Funnels[Funnels]
        Reports[Reports]
        AIInsights[AI Insights]
        Support[Support]
        Maintenance[Maintenance]
    end

    subgraph QA["QA Layer"]
        TestStrategy[Testing Strategy]
        IntegrationTest[Integration Testing]
        E2E[E2E Testing]
        A11y[Accessibility Testing]
        LoadTest[Load Testing]
        SecurityTest[Security Testing]
    end

    subgraph Security["Security Layer"]
        Security[Security Architecture]
        Compliance[Compliance]
        ThreatModel[Threat Model]
        SOC2[SOC 2 Controls]
        Privacy[Data Privacy]
    end

    subgraph DevOps["DevOps Layer"]
        Deployment[Deployment]
        CI[CI Pipeline]
        CD[CD Pipeline]
        Docker[Docker]
        Infra[Infrastructure]
    end

    %% Cross-layer relationships
    Product --> Design
    Product --> Engineering
    Design --> Engineering
    Design --> Frontend
    Engineering --> Frontend
    Engineering --> AI
    Engineering --> Operations
    Engineering --> DevOps
    Operations --> QA
    QA --> Engineering
    Security --> Engineering
    Security --> DevOps
    AI --> Operations
    Frontend --> QA
```

---

## 8. Document Naming Conventions

### 8.1 Legacy Naming (Existing)

Existing documents use the `{NN}_{Name}` prefix format (e.g., `00_ProjectVision.md`, `08_UIUX.md`, `24_Security.md`). These prefixes denote original numbering and should be preserved for backward compatibility and cross-referencing.

### 8.2 New Document Naming

New documents follow these rules:

- **No numbered prefixes** in filenames
- Use PascalCase for multi-word names (e.g., `IntegrationTesting.md`, `AccessibilityTesting.md`)
- Keep names concise but descriptive (2-4 words)
- Use underscores only for legacy files that already have them

### 8.3 Document ID Format

New documents use the format: `{CATEGORY}-{3LETTER}-{3DIGIT}`

| Category Prefix | 3-Letter Code | Example |
|---|---|---|
| Operations | TRC, DSH, ALR, SNT, PST, PLB, MNT, SUP, FNL, EVT, RPT, AII, KPI, STD, IDX | OPS-TRC-001 |
| QA | INT, ACC, UAT, CHS, RGT, SCT, LDT, STR | QA-INT-001 |
| Design | DSG (prefix), CI, IA, ARCH, STRAT | DSG-CLR-001 |
| Devops | DVO | DVO-CI-011 |
| Engineering | FE (frontend), ENG (general), INT (integrations) | FE-COMP-001 |
| Security | SB-SEC, SB-COMP | SB-SEC-001 |
| Product | PRD, SB-PVD, SB-BRD | PRD-VP-002 |

---

## 9. Maintenance and Governance

### 9.1 Index Maintenance

This index must be updated whenever:
- A new document is added to any `docs/` subdirectory
- An existing document is renamed or removed
- A Document ID is assigned or changed
- A document's status changes

### 9.2 Review Cadence

| Review Type | Frequency | Responsibility |
|---|---|---|
| Full index audit | Monthly | Developer |
| Document addition/removal | On change | Developer |
| Cross-reference verification | Quarterly | Developer |
| Broken link check | Monthly | CI pipeline |

### 9.3 Quality Standards

As defined in `docs/governance/01_DocumentationStandards.md`:
- All documents must have a Document Control table
- All documents should follow the 20-section enterprise template (where applicable)
- All cross-references must use relative paths
- Documents should include Mermaid diagrams where architecture or workflows are described
- Documentation templates available in `docs/governance/templates/` for architecture, API endpoints, and guides

---

## 10. References

| Reference | Description |
|---|---|
| `docs/governance/01_DocumentationStandards.md` | Documentation standards and style guide |
| `AGENTS.md` | AI agent master reference |
| `docs/operations/DefinitionOfDone.md` | Definition of Done (includes doc requirements) |
| `docs/product/Glossary.md` | Project glossary |
| `docs/governance/documentation-ownership.md` | Documentation ownership matrix |
| `docs/governance/documentation-review-schedule.md` | Documentation review cadence |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|---|
| 1.0.0 | 2026-07-10 | Developer | Initial master documentation index |
| 1.1.0 | 2026-07-11 | Developer | Applied cleanup: removed 10 deleted stub/merged files, added 20 new files (governance/, api-integration-guide, prompt-engineering-guide, AIIncidentResponse, backup-verification-procedure, firefighter-runbooks, 3 root legal), updated moved files (AIInsights, AIObservability, production-deployment, documentation-ownership, review-schedule, standards, change-management), updated all counts (282 total across 15 categories), incorporated 4 archived files, reflected 5 rewritten files with expanded line counts |
| 1.2.0 | 2026-07-11 | Developer | Doc ID migration: all 340 files now have standardized Document IDs in Section 4 registry — added IDs for 15 ADRs, 30+ legacy AI docs (YELLOW status), 20+ design wireframes/workflow docs, 10+ operations legacy docs, 10+ engineering legacy docs, 15+ security/integration docs, and 10+ other migrated files. Added new Scripts & Tooling section (4.15 registry + 5.16 catalog) documenting migrate-doc-ids.ps1, validate-doc-ids.py, check-links.ps1, .markdownlint.jsonc, CI link-check job, pre-commit hooks, and Makefile targets. Updated Quick Stats (340 files, ~250K lines). |
| 2.0.0 | 2026-07-12 | Developer | Phase 4 final update: added 3 new categories (User Guide 8 files, Learning Paths 4 files, Postmortems 2 files), added 6 new files (skills-system.md, data-flow-diagrams.md, sdl.md, error-budget.md, error-catalog.md, KPI-dashboard.md), added 3 security hardening guides, created 4 new P3 docs (supply-chain-security, secrets-management, glossary, KPI-dashboard). Bumped to 19 categories, ~350 total files, ~260K lines. All counts, registries, and catalog entries updated. |
| **2.1.0** | **2026-07-12** | **Developer** | **Added 3 new documentation categories (Enterprise, Performance, Requirements) with 6 new files catalogued: business-model.md, requirements-traceability-matrix.md, and 3 pre-existing enterprise/performance files now registered. Updated category count to 22, total file count to ~356, and version bump.** |
