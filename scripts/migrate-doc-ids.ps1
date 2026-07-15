<#
.SYNOPSIS
  Standardize Document IDs across the Second Brain OS documentation corpus.

.DESCRIPTION
  Scans all *.md files under docs/ and root *.md files, extracts existing
  Document IDs from Document Control tables, and reports which files need
  migration to the standard format: {CATEGORY}-{TOPIC}-{NUM}

  Categories: AI, ARCH, BIZ, COMP, DSG, DVO, ENG, FE, GOV, INT, LEG, OPS,
              PRD, QA, QST, SEC

  By default runs in DRY-RUN mode. Pass -Apply to write changes.

.PARAMETER Apply
  Actually modify files (replace Document IDs in-place). Omit for dry-run.
#>

param([switch]$Apply)

$ErrorActionPreference = "Stop"
$root = "C:\PROJECTS\My SecondBrain\ARIA OS - SecondBrain"
$today = Get-Date -Format "yyyy-MM-dd"

# ────────────────────────────────────────────────────────────────────
# 1.  CATEGORY DIRECTORY MAP
# ────────────────────────────────────────────────────────────────────
$categoryMap = @(
    @{ Dir = "docs\ai\skills";        Cat = "AI"    }
    @{ Dir = "docs\ai";               Cat = "AI"    }
    @{ Dir = "docs\architecture";     Cat = "ARCH"  }
    @{ Dir = "docs\business";         Cat = "BIZ"   }
    @{ Dir = "docs\compliance";       Cat = "COMP"  }
    @{ Dir = "docs\design\wireframes"; Cat = "DSG"  }
    @{ Dir = "docs\design\WorkflowArchitecture"; Cat = "DSG" }
    @{ Dir = "docs\design";           Cat = "DSG"   }
    @{ Dir = "docs\devops";           Cat = "DVO"   }
    @{ Dir = "docs\engineering\adr";  Cat = "ENG"   }
    @{ Dir = "docs\engineering\integrations"; Cat = "INT" }
    @{ Dir = "docs\engineering\api";  Cat = "ENG"   }
    @{ Dir = "docs\engineering\modules"; Cat = "ENG" }
    @{ Dir = "docs\engineering";      Cat = "ENG"   }
    @{ Dir = "docs\frontend";         Cat = "FE"    }
    @{ Dir = "docs\governance\templates"; Cat = "GOV" }
    @{ Dir = "docs\governance";       Cat = "GOV"   }
    @{ Dir = "docs\operations";       Cat = "OPS"   }
    @{ Dir = "docs\product";          Cat = "PRD"   }
    @{ Dir = "docs\qa";               Cat = "QA"    }
    @{ Dir = "docs\security\reports"; Cat = "SEC"   }
    @{ Dir = "docs\security\policies"; Cat = "SEC"  }
    @{ Dir = "docs\security";         Cat = "SEC"   }
    @{ Dir = "docs";                  Cat = "DOC"   }
)

function Get-Category($relDir) {
    foreach ($entry in $categoryMap) {
        if ($relDir -eq $entry.Dir -or $relDir.StartsWith($entry.Dir + "\")) {
            return $entry.Cat
        }
    }
    if ($relDir -eq "docs") { return "DOC" }
    return "LEG"
}

# ────────────────────────────────────────────────────────────────────
# 2.  KNOWN DOCUMENT ID MAPPING (file relpath -> standard ID)
#     Used both to recognise existing standard IDs and to suggest new ones.
# ────────────────────────────────────────────────────────────────────
$knownIds = @{
    # ── Architecture ──
    "architecture\README.md"                       = "ARCH-C4-001"
    "architecture\database-erd.md"                 = "ARCH-ERD-001"
    "architecture\decision-log.md"                 = "ARCH-DLOG-001"

    # ── AI ──
    "ai\19_AI_Instructions.md"                     = "AI-AIN-001"
    "ai\20_Agent.md"                               = "AI-AGNT-001"
    "ai\21_Prompts.md"                             = "AI-PRM-001"
    "ai\22_MemoryArchitecture.md"                  = "AI-MEM-001"
    "ai\23_KnowledgeGraph.md"                      = "AI-KGR-001"
    "ai\36_Skills.md"                              = "AI-SKL-001"
    "ai\AIEvaluation.md"                           = "AI-EVL-001"
    "ai\AIIncidentResponse.md"                     = "AI-IR-001"
    "ai\AIInsights.md"                             = "AI-AII-001"
    "ai\AIModels.md"                               = "AI-MDL-001"
    "ai\AIObservability.md"                        = "AI-OBS-001"
    "ai\BriefingAgent.md"                          = "AI-BAG-001"
    "ai\ContextEngine.md"                          = "AI-CTX-001"
    "ai\Embeddings.md"                             = "AI-EMB-001"
    "ai\Guardrails.md"                             = "AI-GRD-001"
    "ai\HallucinationHandling.md"                  = "AI-HAL-001"
    "ai\LearningAgent.md"                          = "AI-LAG-001"
    "ai\LongTermMemory.md"                         = "AI-LTM-001"
    "ai\MemoryAgent.md"                            = "AI-MAG-001"
    "ai\MemoryCompression.md"                      = "AI-MCP-001"
    "ai\MemoryRetrieval.md"                        = "AI-MRT-001"
    "ai\NudgeAgent.md"                             = "AI-NAG-001"
    "ai\OpportunityMatchingAgent.md"               = "AI-OMA-001"
    "ai\OpportunityRadarAgent.md"                  = "AI-ORA-001"
    "ai\PromptVersioning.md"                       = "AI-PVR-001"
    "ai\prompt-engineering-guide.md"               = "AI-PEG-001"
    "ai\RAGArchitecture.md"                        = "AI-RAG-001"
    "ai\RoadmapAgent.md"                           = "AI-RMA-001"
    "ai\SemanticMemory.md"                         = "AI-SMC-001"
    "ai\ShortTermMemory.md"                        = "AI-STM-001"
    "ai\SleepAgent.md"                             = "AI-SAG-001"
    "ai\TaskAgent.md"                              = "AI-TAG-001"
    "ai\ToolCalling.md"                            = "AI-TLC-001"
    "ai\WeeklyReviewAgent.md"                      = "AI-WRA-001"

    # AI / skills
    "ai\skills\SkillAgent.md"                      = "AI-SKA-001"
    "ai\skills\SkillAnalytics.md"                  = "AI-SKN-001"
    "ai\skills\SkillAssessment.md"                 = "AI-SAS-001"
    "ai\skills\SkillAuditEnterprise.md"            = "AI-SAE-001"
    "ai\skills\SkillDatabaseArchitecture.md"       = "AI-SDB-001"
    "ai\skills\SkillEvidence.md"                   = "AI-SEV-001"
    "ai\skills\SkillGraphArchitecture.md"          = "AI-SGR-001"
    "ai\skills\SkillIntelligence.md"               = "AI-SIN-001"
    "ai\skills\SkillMarketIntelligence.md"         = "AI-SMK-001"
    "ai\skills\SkillOpportunityMatching.md"        = "AI-SOM-001"
    "ai\skills\SkillRoadmapEngine.md"              = "AI-SRE-001"
    "ai\skills\skills.md"                          = "AI-SKL-002"

    # ── Business ──
    "business\executive-summary.md"                = "BIZ-EXEC-001"

    # ── Compliance ──
    "compliance\dpia.md"                           = "COMP-DPIA-001"
    "compliance\gdpr-ropa.md"                      = "COMP-GDPR-001"
    "compliance\soc2-readiness-report.md"          = "COMP-SOC2-001"

    # ── Design ──
    "design\08_UIUX.md"                            = "DSG-UIUX-001"
    "design\10_DesignSystem.md"                    = "DSG-DSYS-001"
    "design\35_DesignTokens.md"                    = "DSG-DTOK-001"
    "design\37_ComponentSpec.md"                   = "DSG-CSP-001"
    "design\AnimationGuidelines.md"                = "DSG-ANM-001"
    "design\Branding.md"                           = "DSG-BRN-001"
    "design\Charts.md"                             = "DSG-CHT-001"
    "design\Colors.md"                             = "DSG-CLR-001"
    "design\DarkMode.md"                           = "DSG-DRK-001"
    "design\Design.md"                             = "DSG-DSN-001"
    "design\DesignSystem.md"                       = "DSG-DSS-001"
    "design\Icons.md"                              = "DSG-ICN-001"
    "design\Layouts.md"                            = "DSG-LYT-001"
    "design\MicroInteractions.md"                  = "DSG-MIC-001"
    "design\MotionSystem.md"                       = "DSG-MSY-001"
    "design\MotionArchitecture.md"                 = "DSG-MAC-001"
    "design\ProductArchitecture.md"                = "DSG-PAR-001"
    "design\ResponsiveRules.md"                    = "DSG-RSP-001"
    "design\Spacing.md"                            = "DSG-SPC-001"
    "design\StyleGuide.md"                         = "DSG-STY-001"
    "design\Typography.md"                         = "DSG-TYP-001"
    "design\UserJourneyArchitecture.md"            = "DSG-UJA-001"
    "design\FrontendScreenFlows.md"                = "DSG-FSC-001"
    "design\FrontendAccessibilityGuide.md"         = "DSG-A11Y-001"
    "design\FrontendObservabilityGuide.md"         = "DSG-OBS-001"
    "design\FigmaGovernance.md"                    = "DSG-FIG-001"
    "design\InformationArchitecture.md"            = "DSG-INF-001"
    "design\Competitive_Intelligence_Report.md"    = "DSG-CIR-001"
    "design\Enterprise_Frontend_Discovery_Report_v3.md" = "DSG-EFD3-001"
    "design\ARCHIVED_DesignStrategy.md"            = "DSG-ADS-001"
    "design\ARCHIVED_DesignSystemResearch.md"      = "DSG-ADSR-001"
    "design\ARCHIVED_Enterprise_Frontend_Discovery_Report.md"  = "DSG-AEFD-001"
    "design\ARCHIVED_Enterprise_Frontend_Discovery_Report_v2.md" = "DSG-AEF2-001"

    # design / wireframes
    "design\wireframes\00_WIREFRAME_SYSTEM_INDEX.md"       = "DSG-WIX-001"
    "design\wireframes\01_APPLICATION_SHELL_AND_NAVIGATION.md" = "DSG-W01-001"
    "design\wireframes\02_DASHBOARD_WIREFRAMES.md"          = "DSG-W02-001"
    "design\wireframes\03_TASKS_AND_COURSES_WIREFRAMES.md"  = "DSG-W03-001"
    "design\wireframes\04_KNOWLEDGE_IDEAS_ROADMAP_WIREFRAMES.md" = "DSG-W04-001"
    "design\wireframes\05_OPPORTUNITY_PROJECTS_INCOME_WIREFRAMES.md" = "DSG-W05-001"
    "design\wireframes\06_ANALYTICS_AI_SETTINGS_STATES_WIREFRAMES.md" = "DSG-W06-001"
    "design\wireframes\07_SUPPLEMENT_AI_MODULES_STATES.md"  = "DSG-W07-001"
    "design\WorkflowArchitecture\README.md"            = "DSG-WFA-001"
    "design\WorkflowArchitecture\01-UserFlows.md"      = "DSG-WF01-001"
    "design\WorkflowArchitecture\02-FeatureFlows.md"   = "DSG-WF02-001"
    "design\WorkflowArchitecture\03-SupportingScreens.md"  = "DSG-WF03-001"
    "design\WorkflowArchitecture\04-MultiStepExperiences.md" = "DSG-WF04-001"
    "design\WorkflowArchitecture\05-Notifications.md"  = "DSG-WF05-001"
    "design\WorkflowArchitecture\06-Search.md"         = "DSG-WF06-001"
    "design\WorkflowArchitecture\07-AIAgentExperiences.md" = "DSG-WF07-001"
    "design\WorkflowArchitecture\08-Collaboration.md"  = "DSG-WF08-001"
    "design\WorkflowArchitecture\09-Settings.md"       = "DSG-WF09-001"
    "design\WorkflowArchitecture\10-EnterpriseReadiness.md" = "DSG-WF10-001"
    "design\WorkflowArchitecture\11-ResponsiveBehavior.md" = "DSG-WF11-001"
    "design\WorkflowArchitecture\12-FutureExpansion.md" = "DSG-WF12-001"

    # ── DevOps ──
    "devops\26_Deployment.md"                      = "DVO-DEP-001"
    "devops\27_DevOps.md"                          = "DVO-DVO-001"
    "devops\38_ReleaseManagement.md"               = "DVO-REL-001"
    "devops\backup-verification-procedure.md"      = "DVO-BKP-001"
    "devops\CD.md"                                 = "DVO-CD-001"
    "devops\CDNStrategy.md"                        = "DVO-CDN-001"
    "devops\CI.md"                                 = "DVO-CI-001"
    "devops\Docker.md"                             = "DVO-DCK-001"
    "devops\Environments.md"                       = "DVO-ENV-001"
    "devops\GitHubActions.md"                      = "DVO-GHA-001"
    "devops\Infrastructure.md"                     = "DVO-INF-001"
    "devops\Kubernetes.md"                         = "DVO-K8S-001"
    "devops\production-deployment.md"              = "DVO-PROD-001"
    "devops\Rollback.md"                           = "DVO-ROL-001"
    "devops\Terraform.md"                          = "DVO-TER-001"

    # ── Engineering ──
    "engineering\11_TechStack.md"                  = "ENG-TSK-001"
    "engineering\12_Architecture.md"               = "ENG-ARC-001"
    "engineering\14_AgentArchitecture.md"          = "ENG-AAC-001"
    "engineering\15_Database.md"                   = "ENG-DB-001"
    "engineering\16_DataGovernance.md"             = "ENG-DGV-001"
    "engineering\17_API.md"                        = "ENG-API-001"
    "engineering\18_Events.md"                     = "ENG-EVT-001"
    "engineering\37_IntegrationArchitecture.md"    = "ENG-INT-001"
    "engineering\45_PerformanceScalability.md"     = "ENG-PER-001"
    "engineering\46_Architecture_Update.md"        = "ENG-ARU-001"
    "engineering\AgentOrchestration.md"            = "ENG-AOR-001"
    "engineering\ApiGateway.md"                    = "ENG-AGW-001"
    "engineering\api-integration-guide.md"         = "ENG-AIG-001"
    "engineering\BackendArchitecture.md"           = "ENG-BAC-001"
    "engineering\BackgroundWorkers.md"             = "ENG-BGW-001"
    "engineering\BackupStrategy.md"                = "ENG-BAK-001"
    "engineering\BusinessLogic.md"                 = "ENG-BLG-001"
    "engineering\CachingStrategy.md"               = "ENG-CAC-001"
    "engineering\ConfigurationManagement.md"       = "ENG-CFG-001"
    "engineering\Constraints.md"                   = "ENG-CON-001"
    "engineering\Controllers.md"                   = "ENG-CTL-001"
    "engineering\CronJobs.md"                      = "ENG-CRN-001"
    "engineering\EnterprisePlan.md"                = "ENG-EPL-001"
    "engineering\ERD.md"                           = "ENG-ERD-001"
    "engineering\ErrorCodes.md"                    = "ENG-ERR-001"
    "engineering\FeatureFlags.md"                  = "ENG-FFL-001"
    "engineering\FormArchitecture.md"              = "ENG-FRM-001"
    "engineering\FrontendArchitecture.md"          = "ENG-FAR-001"
    "engineering\FrontendTechnicalResearch.md"     = "ENG-FTR-001"
    "engineering\FrontendAIUXPatterns.md"          = "ENG-FAI-001"
    "engineering\FrontendComponentLibrary.md"      = "ENG-FCL-001"
    "engineering\FrontendDataFetching.md"          = "ENG-FDF-001"
    "engineering\FrontendOfflinePWA.md"            = "ENG-FOP-001"
    "engineering\FrontendPerformanceGuide.md"      = "ENG-FPF-001"
    "engineering\FrontendRoutingNavigation.md"     = "ENG-FRN-001"
    "engineering\FrontendSecurityGuide.md"         = "ENG-FSC-001"
    "engineering\FrontendTestingStrategy.md"       = "ENG-FTS-001"
    "engineering\Functions.md"                     = "ENG-FNC-001"
    "engineering\HistoryTables.md"                 = "ENG-HST-001"
    "engineering\Indexes.md"                       = "ENG-IDX-001"
    "engineering\Internationalization.md"          = "ENG-I18N-001"
    "engineering\MaterializedViews.md"             = "ENG-MZV-001"
    "engineering\Microservices.md"                 = "ENG-MSV-001"
    "engineering\MigrationStrategy.md"             = "ENG-MIG-001"
    "engineering\NotificationSystem.md"            = "ENG-NTS-001"
    "engineering\OfflineFirstArchitecture.md"      = "ENG-OFA-001"
    "engineering\performance-benchmarks.md"        = "ENG-BEN-001"
    "engineering\PermissionsAndRoles.md"           = "ENG-PERM-001"
    "engineering\Policies.md"                      = "ENG-POL-001"
    "engineering\QueueArchitecture.md"             = "ENG-QUE-001"
    "engineering\RateLimiting.md"                  = "ENG-RTL-001"
    "engineering\Realtime.md"                      = "ENG-RTE-001"
    "engineering\RealtimeArchitecture.md"          = "ENG-RTA-001"
    "engineering\Repositories.md"                  = "ENG-REP-001"
    "engineering\REST.md"                          = "ENG-RST-001"
    "engineering\RLS.md"                           = "ENG-RLS-001"
    "engineering\Schedulers.md"                    = "ENG-SCH-001"
    "engineering\Schema.md"                        = "ENG-SCM-001"
    "engineering\SearchArchitecture.md"            = "ENG-SRC-001"
    "engineering\ServerActions.md"                 = "ENG-SAC-001"
    "engineering\Services.md"                      = "ENG-SRV-001"
    "engineering\StateManagement.md"               = "ENG-STM-001"
    "engineering\Triggers.md"                      = "ENG-TRG-001"
    "engineering\Validation.md"                    = "ENG-VAL-001"
    "engineering\VectorDatabase.md"                = "ENG-VDB-001"
    "engineering\Versioning.md"                    = "ENG-VER-001"
    "engineering\Views.md"                         = "ENG-VWS-001"
    "engineering\Webhooks.md"                      = "ENG-WHK-001"
    "engineering\WorkflowEngine.md"                = "ENG-WFE-001"

    # engineering / ADR
    "engineering\adr\ADR-001-monorepo-over-multi-repo.md"        = "ENG-ADR01-001"
    "engineering\adr\ADR-002-supabase-over-custom-backend-db.md" = "ENG-ADR02-001"
    "engineering\adr\ADR-003-ollama-primary-claude-fallback.md"  = "ENG-ADR03-001"
    "engineering\adr\ADR-004-in-process-agents-over-microservices.md" = "ENG-ADR04-001"
    "engineering\adr\ADR-005-zustand-over-redux.md"              = "ENG-ADR05-001"
    "engineering\adr\ADR-006-apscheduler-over-celery.md"         = "ENG-ADR06-001"
    "engineering\adr\ADR-007-pwa-over-native-mobile.md"          = "ENG-ADR07-001"
    "engineering\adr\ADR-008-no-event-bus-in-alpha.md"           = "ENG-ADR08-001"
    "engineering\adr\ADR-009-prompt-loader.md"                   = "ENG-ADR09-001"
    "engineering\adr\ADR-010-ai-provider-failover.md"            = "ENG-ADR10-001"
    "engineering\adr\ADR-011-graceful-degradation.md"            = "ENG-ADR11-001"
    "engineering\adr\ADR-012-api-versioning-strategy.md"         = "ENG-ADR12-001"
    "engineering\adr\ADR-013-secret-management.md"               = "ENG-ADR13-001"
    "engineering\adr\ADR-014-testing-philosophy.md"              = "ENG-ADR14-001"
    "engineering\adr\ADR-015-resilience-patterns.md"             = "ENG-ADR15-001"

    # engineering / api
    "engineering\api\openapi-reference.md"          = "ENG-OAR-001"
    "engineering\api\rate-limiting.md"              = "ENG-RLIM-001"
    "engineering\api\changelog.md"                  = "ENG-CHG-001"

    # engineering / modules
    "engineering\modules\ModulesImplementationSpec.md" = "ENG-MIS-001"

    # engineering / integrations
    "engineering\integrations\Claude.md"           = "INT-CLD-001"
    "engineering\integrations\Email.md"            = "INT-EML-001"
    "engineering\integrations\Gemini.md"           = "INT-GEM-001"
    "engineering\integrations\GitHub.md"           = "INT-GIT-001"
    "engineering\integrations\Google.md"           = "INT-GGL-001"
    "engineering\integrations\Notifications.md"    = "INT-NTF-001"
    "engineering\integrations\Ollama.md"           = "INT-OLL-001"
    "engineering\integrations\OpenAI.md"           = "INT-OPN-001"
    "engineering\integrations\Supabase.md"         = "INT-SUP-001"
    "engineering\integrations\YouTube.md"          = "INT-YTB-001"

    # ── Frontend ──
    "frontend\FolderStructure.md"                  = "FE-FS-001"
    "frontend\IMPLEMENTATION_BACKLOG.md"            = "FE-IMPL-001"
    "frontend\RenderingStrategy.md"                 = "FE-RS-001"
    "frontend\SEO.md"                               = "FE-SEO-001"

    # ── Governance ──
    "governance\01_DocumentationStandards.md"       = "GOV-STD-001"
    "governance\02_ChangeManagement.md"             = "GOV-CHG-001"
    "governance\README.md"                          = "GOV-IDX-001"
    "governance\documentation-maturity-model.md"    = "GOV-DMM-001"
    "governance\documentation-ownership.md"         = "GOV-OWN-001"
    "governance\documentation-review-schedule.md"   = "GOV-REV-001"
    "governance\templates\template-architecture.md" = "GOV-TAR-001"
    "governance\templates\template-api-endpoint.md" = "GOV-TAE-001"
    "governance\templates\template-guide.md"        = "GOV-TGD-001"

    # ── Operations ──
    "operations\30_Analytics.md"                    = "OPS-ANL-001"
    "operations\31_Observability.md"                = "OPS-OBS-001"
    "operations\32_Monitoring.md"                   = "OPS-MON-001"
    "operations\33_Roadmap.md"                      = "OPS-RMP-001"
    "operations\34_Backlog.md"                      = "OPS-BKL-001"
    "operations\39_Runbooks.md"                     = "OPS-RUN-001"
    "operations\40_IncidentResponse.md"             = "OPS-IR-001"
    "operations\41_DisasterRecovery.md"             = "OPS-DR-001"
    "operations\42_RiskManagement.md"               = "OPS-RM-001"
    "operations\43_SLA.md"                          = "OPS-SLA-001"
    "operations\44_DeveloperOnboarding.md"          = "OPS-ONB-001"
    "operations\47_CostManagement.md"               = "OPS-CST-001"
    "operations\50_TechnicalDebt.md"                = "OPS-TDB-001"
    "operations\Alerts.md"                          = "OPS-ALR-001"
    "operations\AuditLogs.md"                       = "OPS-AUD-001"
    "operations\Contributing.md"                    = "OPS-CON-001"
    "operations\Dashboards.md"                      = "OPS-DSH-001"
    "operations\DefinitionOfDone.md"                = "OPS-DOD-001"
    "operations\Dependencies.md"                    = "OPS-DEP-001"
    "operations\DependencyManagement.md"            = "OPS-DPM-001"
    "operations\Events.md"                          = "OPS-EVT-001"
    "operations\firefighter-runbooks.md"            = "OPS-FFR-001"
    "operations\Funnels.md"                         = "OPS-FNL-001"
    "operations\GitWorkflow.md"                     = "OPS-GIT-001"
    "operations\IMPLEMENTATION_STATUS.md"           = "OPS-IMPL-001"
    "operations\InnovationRadar.md"                 = "OPS-IR-002"
    "operations\KPIs.md"                            = "OPS-KPI-001"
    "operations\Maintenance.md"                     = "OPS-MNT-001"
    "operations\MaturityModel.md"                   = "OPS-MM-001"
    "operations\monitoring-guide.md"                = "OPS-MNG-001"
    "operations\Playbooks.md"                       = "OPS-PLB-001"
    "operations\PostHog.md"                         = "OPS-PST-001"
    "operations\Reports.md"                         = "OPS-RPT-001"
    "operations\ScalingPlan.md"                     = "OPS-SCL-001"
    "operations\Sentry.md"                          = "OPS-SNT-001"
    "operations\SOC2Readiness.md"                   = "OPS-SOC-001"
    "operations\SprintPlan.md"                      = "OPS-SPR-001"
    "operations\SprintReview.md"                    = "OPS-SRV-001"
    "operations\Support.md"                         = "OPS-SUP-001"
    "operations\TaskBreakdown.md"                   = "OPS-TSK-001"
    "operations\TechnicalDebt.md"                   = "OPS-TDB-002"
    "operations\Tracing.md"                         = "OPS-TRC-001"

    # ── Product ──
    "product\00_ProjectVision.md"                   = "PRD-PVD-001"
    "product\01_CurrentStateAudit.md"               = "PRD-AUD-001"
    "product\02_PRD.md"                             = "PRD-PRD-001"
    "product\03_BRD.md"                             = "PRD-BRD-001"
    "product\03_Features.md"                        = "PRD-FEA-001"
    "product\04_SRS.md"                             = "PRD-SRS-001"
    "product\05_Features.md"                        = "PRD-FEA-002"
    "product\06_UserStories.md"                     = "PRD-US-001"
    "product\07_AcceptanceCriteria.md"              = "PRD-AC-001"
    "product\Assumptions.md"                        = "PRD-ASM-001"
    "product\CompetitiveAnalysis.md"                = "PRD-CA-001"
    "product\Constraints.md"                        = "PRD-CON-001"
    "product\DecisionLog.md"                        = "PRD-DEC-001"
    "product\Glossary.md"                           = "PRD-GLO-001"
    "product\Goals.md"                              = "PRD-GOL-001"
    "product\MarketResearch.md"                     = "PRD-MR-001"
    "product\Mission.md"                            = "PRD-MIS-001"
    "product\Monetization.md"                       = "PRD-MON-001"
    "product\Personas.md"                           = "PRD-PER-001"
    "product\ProductStrategy.md"                    = "PRD-STG-001"
    "product\ProjectScope.md"                       = "PRD-SCO-001"
    "product\RequirementsTraceabilityMatrix.md"     = "PRD-RTM-001"
    "product\Risks.md"                              = "PRD-RIS-001"
    "product\Roadmap.md"                            = "PRD-RMP-001"
    "product\Stakeholders.md"                       = "PRD-SH-001"
    "product\SuccessMetrics.md"                     = "PRD-MET-001"
    "product\UseCases.md"                           = "PRD-UC-001"
    "product\UserFlows.md"                          = "PRD-UF-001"
    "product\ValueProposition.md"                   = "PRD-VP-001"

    # ── QA ──
    "qa\28_Testing.md"                              = "QA-TST-001"
    "qa\AccessibilityTesting.md"                    = "QA-ACC-001"
    "qa\ChaosTesting.md"                            = "QA-CHS-001"
    "qa\E2ETesting.md"                              = "QA-E2E-001"
    "qa\E2ETestPlan.md"                             = "QA-E2P-001"
    "qa\IntegrationTesting.md"                      = "QA-INT-001"
    "qa\LoadTesting.md"                             = "QA-LDT-001"
    "qa\PerformanceTesting.md"                      = "QA-PERF-001"
    "qa\RegressionTesting.md"                       = "QA-RGT-001"
    "qa\SecurityTesting.md"                         = "QA-SCT-001"
    "qa\StressTesting.md"                           = "QA-STR-001"
    "qa\UAT.md"                                     = "QA-UAT-001"

    # ── Security ──
    "security\24_Security.md"                       = "SEC-SEC-001"
    "security\25_Compliance.md"                     = "SEC-COM-001"
    "security\25_DataRetentionPolicy.md"            = "SEC-DRP-001"
    "security\46_DataPrivacy.md"                    = "SEC-DPR-001"
    "security\AuthArchitecture.md"                  = "SEC-AUTH-001"
    "security\Encryption.md"                        = "SEC-ENC-001"
    "security\SecretsManagement.md"                 = "SEC-SCT-001"
    "security\soc2_control_matrix.md"               = "SEC-SOC2-001"
    "security\ThreatModel.md"                       = "SEC-TM-001"
    "security\VulnerabilityInventory.md"            = "SEC-VULN-001"
    "security\policies\data-classification.md"      = "SEC-DC-001"
    "security\policies\incident-response.md"        = "SEC-IR-001"
    "security\policies\vulnerability-management.md" = "SEC-VULM-001"
    "security\reports\penetration-test-report.md"   = "SEC-PENTEST-001"

    # ── Docs root ──
    "DOCUMENTATION_INDEX.md"                        = "OPS-IDX-001"
    "quickstart.md"                                 = "QST-GUIDE-001"

    # ── Root legal ──
    "AGENTS.md"                                     = "LEG-AGR-001"
    "PRIVACY.md"                                    = "LEG-PRIV-001"
    "TERMS.md"                                      = "LEG-TERM-001"
    "COOKIE-POLICY.md"                              = "LEG-COOK-001"
    "SECURITY.md"                                   = "LEG-SEC-001"
    "README.md"                                     = "LEG-README-001"
    "CHANGELOG.md"                                  = "LEG-CHG-001"
    "CODE_OF_CONDUCT.md"                            = "LEG-COC-001"
    "CONTRIBUTING.md"                               = "LEG-CONTRIB-001"
}

# Lookup: try all plausible key forms
function Lookup-KnownId($relPath) {
    $tries = @()
    $tries += $relPath
    $tries += $relPath -replace '^docs\\', ''
    $tries += $relPath -replace '^docs/', ''
    $tries += ($relPath -split '[\\/]' | Select-Object -Skip 1) -join '\'
    $tries += ($relPath -split '[\\/]' | Select-Object -Last 1)
    foreach ($t in $tries) {
        if ($knownIds.ContainsKey($t)) { return $knownIds[$t] }
    }
    return $null
}

# ────────────────────────────────────────────────────────────────────
# 3.  EXTRACT CURRENT DOC ID FROM FILE
# ────────────────────────────────────────────────────────────────────
function Get-CurrentDocId($filePath) {
    $content = Get-Content -Path $filePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $null }

    $lines = $content -split "`r?`n"
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i].Trim()

        # Blockquote: > **Document ID:** XXX
        if ($line -match '^>\s*\*{0,2}Document\s+ID\*{0,2}\s*:\s*(\S+)') {
            return $matches[1]
        }

        # Table: | **Document ID** | XXX |  or  | Document ID | XXX |
        if ($line -match '^\|\s*\*{0,2}Document\s+ID\*{0,2}\s*\|\s*(\S+)') {
            $id = $matches[1]
            if ($id -match '^(Value|Details|Document|Property|Field)$' -or $id.Length -lt 2) {
                continue
            }
            # Strip trailing `|`
            $id = $id -replace '\|\s*$', ''
            return $id.Trim()
        }
    }
    return $null
}

# ────────────────────────────────────────────────────────────────────
# 4.  UPDATE DOCUMENT ID IN FILE
# ────────────────────────────────────────────────────────────────────
function Set-DocumentId($filePath, $newId) {
    $content = Get-Content -Path $filePath -Raw -ErrorAction Stop
    $lines = $content -split "`r?`n"
    $changed = $false

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        # Blockquote: > **Document ID:** XXX
        if ($line -match '^(>\s*\*{0,2}Document\s+ID\*{0,2}\s*:\s*)\S+') {
            $lines[$i] = $line -replace '^(>\s*\*{0,2}Document\s+ID\*{0,2}\s*:\s*)\S+', "`$1$newId"
            $changed = $true
            break
        }

        # Table: | **Document ID** | XXX |
        if ($line -match '^\|\s*\*{0,2}Document\s+ID\*{0,2}\s*\|\s*\S+') {
            $lines[$i] = $line -replace '(^\|\s*\*{0,2}Document\s+ID\*{0,2}\s*\|\s*)\S+', "`$1$newId"
            $changed = $true
            break
        }
    }

    if ($changed) {
        $newContent = $lines -join "`r`n"
        [System.IO.File]::WriteAllText($filePath, $newContent, [System.Text.Encoding]::UTF8)
        return $true
    }
    return $false
}

# ────────────────────────────────────────────────────────────────────
# 5.  ID FORMAT VALIDATION
# ────────────────────────────────────────────────────────────────────
function Test-IsStandardFormat($id) {
    if (-not $id) { return $false }
    return ($id -match '^[A-Z]{2,6}-[A-Z0-9]{1,8}-\d{3}$')
}

function Get-FormatIssue($id) {
    if (-not $id) { return "NO-ID" }
    if ($id -match '^\*\*$') { return "PLACEHOLDER" }
    if ($id -match '^\[.*\]$') { return "PLACEHOLDER" }
    if ($id -match '^SB-') { return "SB-PREFIX" }
    if ($id -match '^[A-Z]{2,5}-\d{1,3}$') { return "NO-TOPIC" }
    if ($id -match '^[A-Z]{2,6}-[A-Z0-9]{1,8}-\d{1,2}$') { return "NUM-SHORT" }
    if ($id -match '^[A-Z]{2,6}-[A-Z0-9]{1,8}-\d{4,}$') { return "NUM-LONG" }
    if (-not ($id -match '^[A-Z]{2,6}-[A-Z0-9]{1,8}-\d{3}$')) { return "MALFORMED" }
    return "OK"
}

# ────────────────────────────────────────────────────────────────────
# 6.  MAIN SCAN
# ────────────────────────────────────────────────────────────────────
$allFiles = @()
Get-ChildItem -Path "$root\docs" -Recurse -Filter "*.md" | ForEach-Object { $allFiles += $_.FullName }
Get-ChildItem -Path "$root" -Filter "*.md" | ForEach-Object { $allFiles += $_.FullName }

$filesScanned = 0
$filesWithId = 0
$migrations = @()

foreach ($f in $allFiles) {
    $relPath = $f.Substring($root.Length + 1)
    $filesScanned++

    $currentId = Get-CurrentDocId $f
    $suggestedId = Lookup-KnownId $relPath

    if ($currentId) {
        $filesWithId++
        $issue = Get-FormatIssue $currentId

        if ($issue -eq "OK") {
            # Valid format - check if it matches the known mapping
            if ($suggestedId -and $currentId -ne $suggestedId) {
                # The format is valid but it doesn't match our mapping
                # Only flag if the ID clearly belongs to a different category
                $currentCat = ($currentId -split '-')[0]
                $suggestedCat = ($suggestedId -split '-')[0]
                if ($currentCat -ne $suggestedCat) {
                    $migrations += [PSCustomObject]@{
                        Path = $relPath; CurrentId = $currentId
                        SuggestedId = $suggestedId; Issue = "WRONG-CATEGORY"
                    }
                }
            }
        } else {
            # Needs migration
            if ($suggestedId) {
                $migrations += [PSCustomObject]@{
                    Path = $relPath; CurrentId = $currentId
                    SuggestedId = $suggestedId; Issue = $issue
                }
            }
        }
    } else {
        # No ID found - only suggest if we have a mapping
        if ($suggestedId) {
            $migrations += [PSCustomObject]@{
                Path = $relPath; CurrentId = "(none)"
                SuggestedId = $suggestedId; Issue = "MISSING"
            }
        }
    }
}

# ────────────────────────────────────────────────────────────────────
# 7.  REPORT
# ────────────────────────────────────────────────────────────────────
function Write-Bar($char = "=", $len = 47) {
    Write-Host ($char * $len)
}

Write-Host ""
Write-Host "  ===============================================" -ForegroundColor Cyan
Write-Host "  DOC ID MIGRATION REPORT - $today" -ForegroundColor Cyan
Write-Host "  ===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host ("  {0,-25} {1}" -f "Files scanned:", $filesScanned) -ForegroundColor Gray
Write-Host ("  {0,-25} {1}" -f "Files with Doc IDs:", $filesWithId) -ForegroundColor Gray
$color = if ($migrations.Count -gt 0) { "Yellow" } else { "Green" }
Write-Host ("  {0,-25} {1}" -f "Files needing action:", $migrations.Count) -ForegroundColor $color
Write-Host ""

if ($migrations.Count -eq 0) {
    Write-Host "  [OK] All document IDs are in standard format!" -ForegroundColor Green
    Write-Host ""
    return
}

$sbGroup  = $migrations | Where-Object { $_.Issue -eq "SB-PREFIX" }
$noTopic  = $migrations | Where-Object { $_.Issue -eq "NO-TOPIC" }
$malformed = $migrations | Where-Object { $_.Issue -in @("MALFORMED","PLACEHOLDER","NUM-SHORT","NUM-LONG") }
$missing  = $migrations | Where-Object { $_.Issue -eq "MISSING" }
$wcGroup  = $migrations | Where-Object { $_.Issue -eq "WRONG-CATEGORY" }

$groups = @()
$groups += @{ Title = "LEGACY SB- PREFIX";   Items = $sbGroup }
$groups += @{ Title = "MISSING TOPIC ABBREVIATION"; Items = $noTopic }
$groups += @{ Title = "MALFORMED / PLACEHOLDER";    Items = $malformed }
$groups += @{ Title = "WRONG CATEGORY";      Items = $wcGroup }
$groups += @{ Title = "MISSING DOCUMENT ID"; Items = $missing }

foreach ($g in $groups) {
    if ($g.Items.Count -gt 0) {
        Write-Host ("  $($g.Title) ($($g.Items.Count) files):") -ForegroundColor Magenta
        Write-Bar "-"
        foreach ($m in $g.Items) {
            Write-Host ("    $($m.Path)") -ForegroundColor Gray
            Write-Host ("      $($m.CurrentId,-25) -> $($m.SuggestedId)") -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

# Footer
Write-Bar "="
if (-not $Apply) {
    $existingCount = ($migrations | Where-Object { $_.Issue -ne "MISSING" }).Count
    Write-Host "  DRY RUN - Use -Apply to apply changes" -ForegroundColor Cyan
    Write-Host "  $existingCount existing IDs would be migrated," -NoNewline
    Write-Host " $($missing.Count) new IDs would be added." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Tip: Review the suggestions above. Some IDs may need manual" -ForegroundColor DarkGray
    Write-Host "  tweaking - check the `$knownIds mapping in this script." -ForegroundColor DarkGray
} else {
    Write-Host "  APPLYING CHANGES..." -ForegroundColor Red
    $applied = 0; $errors = 0
    foreach ($m in $migrations) {
        $fullPath = Join-Path $root $m.Path
        if (Test-Path $fullPath) {
            $ok = Set-DocumentId -filePath $fullPath -newId $m.SuggestedId
            if ($ok) { $applied++ } else { $errors++ }
        }
    }
    Write-Host "  Applied: $applied / Errors: $errors" -ForegroundColor Green
}
Write-Bar "="
Write-Host ""
