# Documentation Ownership Matrix â€” Second Brain OS

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-OWN-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Internal â€” Operations |
| Owner | Principal Product Manager |
| Last Updated | 2026-07-10 |
| Next Review | 2026-10-10 |
| Review Cycle | Quarterly |
| Approving Authority | Product Lead |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-10 | Principal Product Manager | Initial documentation ownership matrix with role-based assignments |

---

## 1. Ownership Model

Documentation ownership follows a **primary + backup** model:

| Role | Abbreviation | Responsibilities |
|---|---|---|
| **Primary Owner** | PO | Accountable for accuracy, completeness, and timely reviews. First point of contact for questions. |
| **Backup Owner** | BO | Covers during PO absence. Reviews PRs that touch owned docs. Can trigger emergency reviews. |

**Ownership principles:**
- Every document has exactly one Primary Owner and one Backup Owner
- Owners review their docs on the prescribed cadence (see [Review Schedule](documentation-review-schedule.md))
- Ownership changes require an update to this matrix + announcement in project channel
- Owners are responsible for keeping their docs aligned with code changes in their domain

---

## 2. Complete Ownership Table

### 2.1 Product Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Project Vision | `00_ProjectVision.md` | Principal Product Manager | AI Systems Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| PRD | `02_PRD.md` | Principal Product Manager | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| BRD | `03_BRD.md` | Principal Product Manager | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| SRS | `04_SRS.md` | Principal Product Manager | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Features | `03_Features.md`, `05_Features.md` | Principal Product Manager | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| User Stories | `06_UserStories.md` | Principal Product Manager | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Personas | `Personas.md` | Principal Product Manager | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Competitive Analysis | `CompetitiveAnalysis.md` | Principal Product Manager | AI Systems Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Market Research | `MarketResearch.md` | Principal Product Manager | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Monetization | `Monetization.md` | Principal Product Manager | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Roadmap | `Roadmap.md` | Principal Product Manager | AI Systems Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Success Metrics | `SuccessMetrics.md` | Principal Product Manager | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Stakeholders | `Stakeholders.md` | Principal Product Manager | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Risks | `Risks.md` | Principal Product Manager | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Decision Log | `DecisionLog.md` | Principal Product Manager | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Business Docs | `business/*.md` | Principal Product Manager | AI Systems Architect | Quarterly | 2026-07-10 | 2026-10-10 |

### 2.2 Engineering Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| System Architecture | `12_Architecture.md`, `13_SystemArchitecture.md`, `46_Architecture_Update.md` | Principal Software Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| API Reference | `17_API.md`, `REST.md`, `ErrorCodes.md`, `Versioning.md` | Staff Backend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Database Schema | `15_Database.md`, `ERD.md`, `Schema.md`, `Indexes.md`, `RLS.md` | Staff Backend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Tech Stack | `11_TechStack.md` | Principal Software Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Agent Architecture | `14_AgentArchitecture.md`, `AgentOrchestration.md` | AI Systems Architect | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| ADRs | `adr/ADR-*.md` (15 files) | Principal Software Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Integration Specs | `integrations/*.md` (10 files) | Staff Backend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Module Spec | `modules/ModulesImplementationSpec.md` | Principal Software Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Feature Flags | `FeatureFlags.md` | Staff Backend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Caching Strategy | `CachingStrategy.md` | Principal Software Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Performance | `45_PerformanceScalability.md` | Principal Software Architect | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| CORS / Auth | `Controllers.md`, `Services.md`, `Repositories.md` | Staff Backend Engineer | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Background Workers | `BackgroundWorkers.md`, `CronJobs.md`, `Schedulers.md` | Staff Backend Engineer | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |

### 2.3 Frontend & Design Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Frontend Architecture | `FrontendArchitecture.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Component Library | `FrontendComponentLibrary.md`, `37_ComponentSpec.md` | Staff Frontend Engineer | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Design System | `10_DesignSystem.md`, `DesignSystem.md`, `35_DesignTokens.md` | Staff Frontend Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| UI/UX | `08_UIUX.md`, `09_Design.md`, `StyleGuide.md` | Staff Frontend Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Design Tokens | `Colors.md`, `Typography.md`, `Spacing.md`, `Icons.md`, `Charts.md` | Staff Frontend Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Wireframes | `wireframes/*.md` (8 files) | Staff Frontend Engineer | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Workflow Architecture | `WorkflowArchitecture/*.md` (12 files) | Staff Frontend Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Motion | `MotionArchitecture.md`, `MotionSystem.md`, `AnimationGuidelines.md` | Staff Frontend Engineer | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Accessibility | `FrontendAccessibilityGuide.md`, `Accessibility.md` | Staff Frontend Engineer | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Folder Structure | `Frontend/FolderStructure.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Rendering Strategy | `Frontend/RenderingStrategy.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| SEO | `Frontend/SEO.md` | Staff Frontend Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Data Fetching | `FrontendDataFetching.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| State Management | `StateManagement.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Frontend Security | `FrontendSecurityGuide.md` | Staff Frontend Engineer | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Frontend Performance | `FrontendPerformanceGuide.md` | Staff Frontend Engineer | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| PWA / Offline | `FrontendOfflinePWA.md`, `OfflineFirstArchitecture.md` | Staff Frontend Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |

### 2.4 AI & Prompt Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Agent Specification | `20_Agent.md` (239KB) | AI Systems Architect | Principal Product Manager | Monthly | 2026-06-11 | 2026-07-11 |
| AI Instructions | `19_AI_Instructions.md` | AI Systems Architect | Principal Product Manager | Monthly | 2026-06-11 | 2026-07-11 |
| Memory Architecture | `22_MemoryArchitecture.md`, `LongTermMemory.md`, `ShortTermMemory.md`, `SemanticMemory.md`, `MemoryCompression.md`, `MemoryRetrieval.md` | AI Systems Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Knowledge Graph | `23_KnowledgeGraph.md`, `Embeddings.md`, `RAGArchitecture.md` | AI Systems Architect | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Skills Module | `36_Skills.md`, `skills/*.md` (12 files) | AI Systems Architect | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Prompt Versioning | `PromptVersioning.md` | AI Systems Architect | QA Director | Monthly | 2026-06-11 | 2026-07-11 |
| Agent Prompt Files | `prompts/agents/*.md` (10 files) | AI Systems Architect | QA Director | Monthly | 2026-06-11 | 2026-07-11 |
| System Prompts | `prompts/system/*.md` (2 files) | AI Systems Architect | Staff Security Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Template Prompts | `prompts/templates/*.md` (2 files) | AI Systems Architect | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| AI Evaluation | `AIEvaluation.md`, `HallucinationHandling.md`, `Guardrails.md` | AI Systems Architect | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| AI Models | `AIModels.md`, `ToolCalling.md` | AI Systems Architect | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |

### 2.5 Security & Compliance Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Security Architecture | `24_Security.md` | Staff Security Engineer | Principal Software Architect | Monthly | 2026-06-11 | 2026-07-11 |
| Compliance | `25_Compliance.md` | Staff Security Engineer | Principal Product Manager | Monthly | 2026-06-11 | 2026-07-11 |
| Data Privacy | `46_DataPrivacy.md`, `25_DataRetentionPolicy.md` | Staff Security Engineer | Principal Software Architect | Monthly | 2026-06-11 | 2026-07-11 |
| Threat Model | `ThreatModel.md` | Staff Security Engineer | Principal Software Architect | Monthly | 2026-06-11 | 2026-07-11 |
| Auth Architecture | `AuthArchitecture.md` | Staff Security Engineer | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Encryption | `Encryption.md` | Staff Security Engineer | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Secrets Management | `SecretsManagement.md` | Staff Security Engineer | Staff DevOps Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| SOC 2 | `soc2_control_matrix.md` | Staff Security Engineer | Principal Product Manager | Monthly | 2026-06-11 | 2026-07-11 |
| Vulnerability Inventory | `VulnerabilityInventory.md` | Staff Security Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |

### 2.6 DevOps & Infrastructure Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Deployment | `26_Deployment.md` | Staff DevOps Engineer | Site Reliability Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| DevOps | `27_DevOps.md` | Staff DevOps Engineer | Site Reliability Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| CI/CD | `CI.md`, `CD.md` | Staff DevOps Engineer | Site Reliability Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| GitHub Actions | `GitHubActions.md` | Staff DevOps Engineer | Principal Software Architect | Monthly | 2026-06-11 | 2026-07-11 |
| Docker | `Docker.md` | Staff DevOps Engineer | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Kubernetes | `Kubernetes.md` | Staff DevOps Engineer | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Terraform | `Terraform.md` | Staff DevOps Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Release Management | `38_ReleaseManagement.md` | Staff DevOps Engineer | Site Reliability Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Rollback | `Rollback.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Infrastructure | `Infrastructure.md` | Staff DevOps Engineer | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| CDN Strategy | `CDNStrategy.md` | Staff DevOps Engineer | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Environments | `Environments.md` | Staff DevOps Engineer | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |

### 2.7 QA & Testing Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Testing Strategy | `28_Testing.md` | QA Director | Staff Frontend Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| QA Processes | `29_QA.md` | QA Director | Staff Backend Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| E2E Testing | `E2ETesting.md`, `E2ETestPlan.md` | QA Director | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Integration Testing | `IntegrationTesting.md` | QA Director | Staff Backend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Unit Testing | `UnitTesting.md` | QA Director | Principal Software Architect | Quarterly | 2026-06-11 | 2026-09-11 |
| Accessibility Testing | `AccessibilityTesting.md` | QA Director | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Performance Testing | `PerformanceTesting.md`, `LoadTesting.md`, `StressTesting.md` | QA Director | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Security Testing | `SecurityTesting.md` | QA Director | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Chaos Testing | `ChaosTesting.md` | QA Director | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Regression Testing | `RegressionTesting.md` | QA Director | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| UAT | `UAT.md` | QA Director | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |

### 2.8 Operations Documents

| Document Category | Documents Included | Primary Owner | Backup Owner | Review Frequency | Last Reviewed | Next Review Due |
|---|---|---|---|---|---|---|
| Runbooks | `39_Runbooks.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Incident Response | `40_IncidentResponse.md` | Site Reliability Engineer | Staff Security Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Disaster Recovery | `41_DisasterRecovery.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| SLA | `43_SLA.md` | Site Reliability Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Monitoring | `32_Monitoring.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Analytics | `30_Analytics.md` | Site Reliability Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Observability | `31_Observability.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Alerts | `Alerts.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Dashboards | `Dashboards.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Tracing | `Tracing.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Sentry | `Sentry.md` | Site Reliability Engineer | Staff Frontend Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Risk Management | `42_RiskManagement.md` | Site Reliability Engineer | Staff Security Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| KPIs | `KPIs.md` | Site Reliability Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Playbooks | `Playbooks.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Maintenance | `Maintenance.md` | Site Reliability Engineer | Staff DevOps Engineer | Monthly | 2026-06-11 | 2026-07-11 |
| Support | `Support.md` | Site Reliability Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Cost Management | `47_CostManagement.md` | Site Reliability Engineer | Principal Product Manager | Quarterly | 2026-06-11 | 2026-09-11 |
| Developer Onboarding | `44_DeveloperOnboarding.md` | Principal Software Architect | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Documentation Standards | `48_DocumentationStandards.md` | Principal Product Manager | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Change Management | `49_ChangeManagement.md` | Staff DevOps Engineer | Site Reliability Engineer | Quarterly | 2026-06-11 | 2026-09-11 |
| Technical Debt | `50_TechnicalDebt.md` | Principal Software Architect | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| Backlog | `34_Backlog.md`, `SprintPlan.md`, `SprintReview.md` | Principal Product Manager | QA Director | Quarterly | 2026-06-11 | 2026-09-11 |
| AGENTS.md | `AGENTS.md` (root) | Principal Product Manager | Principal Software Architect | Monthly | 2026-06-23 | 2026-07-23 |
| Documentation Index | `DOCUMENTATION_INDEX.md` | Principal Product Manager | QA Director | Monthly | 2026-07-10 | 2026-08-10 |
| Implementation Status | `IMPLEMENTATION_STATUS.md` | Principal Product Manager | Principal Software Architect | Monthly | 2026-06-11 | 2026-07-11 |

---

## 3. Review Process

### 3.1 Standard Review Workflow

```
1. Calendar reminder triggers review
2. Owner reviews document
3. Review checklist completed
4. PR submitted for backup owner
5. Merge and update metrics
```

### 3.2 Review Checklist

For every documentation review, the owner must verify:

- [ ] **Accuracy** â€” Content reflects current codebase/architecture state
- [ ] **Completeness** â€” No missing sections or outdated references
- [ ] **Document Control** â€” Version bumped, last updated date set
- [ ] **Cross-References** â€” All links to other docs are valid (check for moved/renamed files)
- [ ] **Code Alignment** â€” Code examples match current implementation
- [ ] **Naming Conventions** â€” Document IDs, file names follow `01_DocumentationStandards.md`
- [ ] **Broken Links** â€” All internal and external links resolve
- [ ] **Spelling & Grammar** â€” No typos or grammatical errors
- [ ] **Frontmatter** â€” If it's a prompt file, run `make validate-prompts`
- [ ] **Deprecation** â€” Mark legacy docs as deprecated; don't delete them
- [ ] **Related Docs** â€” Notify owners of related docs that may need updates

### 3.3 Review Output

Each review produces:
1. **Pull Request** with changes to the reviewed document
2. **Updated `Last Reviewed` date** in this ownership matrix
3. **Version bump** in the document's control table
4. **CHANGELOG entry** for user-facing documentation changes
5. **Notification** to backup owner and related document owners

---

## 4. Escalation Path

### 4.1 Owner Unavailability

| Duration | Action |
|---|---|
| < 1 week | Backup Owner covers â€” performs review, informs Primary Owner |
| 1-4 weeks | Backup Owner covers full cycle. Primary Owner reviews changes on return |
| > 4 weeks | Product Lead reassigns ownership. Matrix updated. |

### 4.2 Disagreement Resolution

```
Level 1: Primary Owner â†” Backup Owner â€” resolve via discussion/PR comments
Level 2: Principal Product Manager â€” mediates if Level 1 fails
Level 3: Product Lead â€” final decision if mediation fails
```

### 4.3 Emergency Updates

When a critical doc (Runbooks, Security, AGENTS.md) needs immediate update:
1. Any role can open a PR with changes
2. Tag primary + backup owners as reviewers
3. If owners unresponsive (< 4 hours for P0/P1), escalate to Site Reliability Engineer
4. Emergency PRs bypass review cadence but require post-hoc notification to owners

---

## 5. Summary Statistics

| Category | Docs Count | Primary Owner | Average Review Frequency |
|---|---|---|---|
| Product | 30 | Principal Product Manager | Quarterly |
| Engineering | 78 | Principal Software Architect | Quarterly |
| Frontend + Design | 42 | Staff Frontend Engineer | Quarterly |
| AI & Prompts | 27 | AI Systems Architect | Monthly (critical) / Quarterly |
| Security & Compliance | 10 | Staff Security Engineer | Monthly |
| DevOps & Infrastructure | 13 | Staff DevOps Engineer | Monthly (critical) / Quarterly |
| QA & Testing | 14 | QA Director | Monthly (critical) / Quarterly |
| Operations | 47 | Site Reliability Engineer | Monthly (critical) / Quarterly |
| **Total** | **~270** | 8 roles | â€” |
