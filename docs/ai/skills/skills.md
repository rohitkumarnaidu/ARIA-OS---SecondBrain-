# Skills System — Enterprise Architecture

---

## Document Control

| Field | Value |
|---|---|
| Document ID | SB-SKILLS-ARCH-001 |
| Version | 1.0.0 |
| Status | Active |
| Last Updated | 2026-06-12 |
| Classification | Internal — Architecture Reference |
| Target Audience | AI Agents, Developers, Product Managers, Architects |

---

## Table of Contents

- [1. Vision](#1-vision)
- [2. Skill Architecture](#2-skill-architecture)
- [3. Skill Taxonomy](#3-skill-taxonomy)
- [4. Skill Categories](#4-skill-categories)
- [5. Skill Levels](#5-skill-levels)
- [6. Skill States](#6-skill-states)
- [7. Current Skills](#7-current-skills)
- [8. Target Skills](#8-target-skills)
- [9. Skill Trees](#9-skill-trees)
- [10. Skill Dependencies](#10-skill-dependencies)
- [11. Skill Evidence Framework](#11-skill-evidence-framework)
- [12. Skill Assessment Framework](#12-skill-assessment-framework)
- [13. Skill Certification Framework](#13-skill-certification-framework)
- [14. Skill Project Mapping](#14-skill-project-mapping)
- [15. Skill Roadmap Mapping](#15-skill-roadmap-mapping)
- [16. Skill Opportunity Mapping](#16-skill-opportunity-mapping)
- [17. Skill Market Intelligence](#17-skill-market-intelligence)
- [18. Skill Income Mapping](#18-skill-income-mapping)
- [19. Skill Analytics](#19-skill-analytics)
- [20. AI Recommendations](#20-ai-recommendations)
- [21. ARIA Agent Capabilities](#21-aria-agent-capabilities)
- [22. Skill Lifecycle Management](#22-skill-lifecycle-management)
- [23. Skill Versioning](#23-skill-versioning)
- [24. Database Mapping](#24-database-mapping)
- [25. API Requirements](#25-api-requirements)
- [26. UI/UX Requirements](#26-uiux-requirements)
- [27. Security Requirements](#27-security-requirements)
- [28. Future Expansion](#28-future-expansion)
- [29. Enterprise Governance & Compliance](#29-enterprise-governance--compliance)
- [30. Enterprise Integration Patterns](#30-enterprise-integration-patterns)
- [31. Multi-Tenant Architecture & Isolation](#31-multi-tenant-architecture--isolation)
- [32. Enterprise SLAs, KPIs & Pricing](#32-enterprise-slas-kpis--pricing)
- [33. Enterprise Change Management & Rollout](#33-enterprise-change-management--rollout)
- [Appendix A: Codebase Mapping](#appendix-a-codebase-mapping)
- [Appendix B: Glossary](#appendix-b-glossary)

---

## 1. Vision

### 1.1 Purpose

The Skills System is the foundational intelligence layer of Second Brain OS (ARIA OS). It transforms raw user activity data into a structured, evolving, and actionable representation of human capability. Skills are not static labels — they are living entities with states, evidence, dependencies, market value, and projected growth trajectories.

This system serves as the single source of truth for everything a user knows, is learning, or needs to learn, across every domain of their professional and personal development. It unifies two fundamental concepts:

- **User Skills** — What the user knows (technical, professional, business competencies)
- **Agent Capabilities** — What ARIA can do (briefing, opportunity matching, task analysis)

Both share the same data model, taxonomy, lifecycle, and governance, enabling consistent intelligence across human and AI capabilities.

### 1.2 Business Value

| Dimension | Value |
|---|---|
| User Retention | Skill progression creates stickiness — users stay to grow their skill trees |
| Monetization | Skill-to-income mapping enables coaching upsells, certification validation, and marketplace fees |
| Competitive Moat | No existing productivity OS has a first-class skill graph with market intelligence |
| Data Network Effects | Aggregated skill data (anonymized) powers market intelligence no competitor can replicate |
| Ecosystem Expansion | Open skill taxonomy enables third-party integrations, plugins, and enterprise deployments |
| Career Intelligence | Transforms passive tracking into active career development guidance |
| Market Intelligence | Unique demand/salary/trend data creates defensible advantage |

### 1.3 User Value

| User Need | How the Skills System Addresses It |
|---|---|
| "What should I learn next?" | AI recommendations based on career targets, market demand, and skill gaps |
| "How good am I at this?" | Multi-signal proficiency scoring (evidence + assessment + project history) |
| "What is my skill worth?" | Income mapping shows earning potential per skill and per combination |
| "Am I on track for my dream job?" | Career readiness scoring with gap analysis and targeted roadmaps |
| "What have I actually accomplished?" | Evidence framework captures every project, cert, and contribution |
| "What skills are becoming obsolete?" | Market intelligence tracks demand trends, salary trends, and future relevance |
| "How fast am I growing?" | Learning velocity tracking across all skills with trend analysis |
| "What opportunities match me?" | Skill-based opportunity matching with personalized fit scores |

### 1.4 Enterprise Goals

1. **Universal Skill Graph**: Every user has a complete, portable, verifiable skill graph that travels with them across roles, industries, and life stages.
2. **Skill-as-Asset**: User skills become measurable, improvable, and monetizable assets with clear ROI tracking.
3. **AI-Native Skill Intelligence**: ARIA continuously monitors, assesses, and recommends skill development without user intervention.
4. **Market-Aligned Growth**: User skill development is aligned with real market demand, not guesswork.
5. **Ecosystem Platform**: Third parties (employers, educators, certifiers) can plug into the skill graph for hiring, validation, and credentialing.
6. **Cross-Domain Intelligence**: Skills from different domains (tech, business, creative) are unified in one graph for holistic career intelligence.
7. **Autonomous Skill Acquisition**: ARIA proactively identifies gaps, recommends resources, and tracks progress without user configuration.

### 1.5 Long-Term Evolution

| Phase | Timeline | Capabilities |
|---|---|---|
| Phase 1 — Foundation | Q3 2026 | Skill CRUD, basic levels, evidence tracking, tree view |
| Phase 2 — Intelligence | Q4 2026 | Market intelligence, income mapping, AI recommendations |
| Phase 3 — Ecosystem | Q1 2027 | Open taxonomy, third-party plugins, employer verification |
| Phase 4 — Autonomous | Q2 2027 | ARIA proactively identifies, recommends, and executes skill acquisition plans |
| Phase 5 — Universal | H2 2027 | Cross-platform skill passport, blockchain verification, DAO-governed taxonomy |

---

## 2. Skill Architecture

### 2.1 What Is a Skill

A **skill** is a structured representation of a user's demonstrated or aspirational capability in a defined domain. Every skill is a first-class entity with:

| Attribute | Description |
|---|---|
| Identity | Unique ID, name, slug, canonical reference |
| Classification | Category, subcategory, tags, custom labels |
| Proficiency | Level (L0-L5), confidence score, evidence score |
| State | Planned, Learning, Practicing, Active, Advanced, Expert, Archived, Deprecated |
| Evidence | Projects, certifications, assessments, contributions, work history |
| Relationships | Parent, child, sibling, prerequisite, related skills |
| Market Data | Demand score, salary data, growth trend, competition level |
| Income Data | Freelance rates, employment salary ranges, product revenue attribution |
| Versioning | Version history, change log, upgrade paths |
| Metadata | Created date, updated date, source, owner |

### 2.2 Unified Skill Model

This system recognizes two fundamental skill types that share the same core data model:

**User Skills** — What the USER knows (e.g., React, Python, Product Management)
- Evidence-backed
- Level-assessed
- Market-mapped
- Income-tracked

**Agent Capabilities** — What ARIA can DO (e.g., briefing, opportunity matching, task breakdown)
- Prompt-defined
- Executable via triggers
- Improvement-tracked
- Performance-monitored

Both types share the same taxonomy, versioning, and lifecycle systems, but differ in how they are assessed and executed. An Agent Capability is essentially a skill that ARIA possesses, with its evidence being execution logs and performance metrics rather than user projects.

### 2.3 Skill Lifecycle

```
                  ┌─────────┐
                  │ Concept │ (not yet created)
                  └────┬────┘
                       │ User/AI creates skill
                       ▼
                  ┌──────────┐
                  │  Active  │ ◄──────────────┐
                  └────┬─────┘                │
                       │                      │
              ┌────────┼─────────┐            │
              ▼        ▼         ▼            │
         ┌────────┐┌────────┐┌────────┐      │
         │Learning││Practic-││Advanced│      │
         │        ││ing     ││        │      │
         └────────┘└────────┘└────────┘      │
              │        │         │            │
              └────────┼─────────┘            │
                       ▼                      │
                  ┌──────────┐                │
                  │  Expert  │                │
                  └────┬─────┘                │
                       │                      │
                       ▼                      │
                  ┌──────────┐                │
                  │ Archived │                │
                  └────┬─────┘                │
                       │                      │
                       ▼                      │
                  ┌────────────┐              │
                  │ Deprecated │──────────────┘
                  └────────────┘  (reactivate)
```

### 2.4 Skill Ownership

| Owner Type | Description | Examples |
|---|---|---|
| User-Owned | Skills the user has added, learned, or claimed | React, Python, UI Design |
| System-Detected | Skills ARIA auto-detects from activity | GitHub repos, course completions |
| Derived | Skills inferred from combinations of evidence | Full-stack (Frontend + Backend), Leadership (Mentoring + Management) |
| Market-Sourced | Skills pulled from market intelligence feeds | Emerging tech skills, trending certifications |
| Organization | Skills defined by company/team requirements | Internal tooling, proprietary frameworks |

### 2.5 Skill Governance

| Governance Layer | Responsibility |
|---|---|
| Taxonomy Committee | Defines canonical categories, level standards, and naming conventions |
| Quality Assurance | Validates evidence, assessments, and proficiency claims |
| Market Intelligence | Curates demand/salary/trend data quality |
| Community Moderation | Reviews user-substituted categories, custom skills, and non-standard evidence |
| AI Governance | Ensures recommendation algorithms are fair, unbiased, and transparent |

### 2.6 Skill Hierarchy

```
Skill Domain (e.g., Engineering)
└── Category (e.g., Frontend Development)
    └── Subcategory (e.g., React Ecosystem)
        └── Skill (e.g., React.js)
            └── Sub-skill (e.g., React Hooks, Context API)
                └── Concept (e.g., useState, useEffect)
```

The hierarchy supports unlimited depth and branching, allowing both high-level domain mastery and granular concept tracking. A skill can belong to multiple categories (cross-listing) — for example, Python is both a Backend skill and a Data Science skill.

---

## 3. Skill Taxonomy

### 3.1 Taxonomy Design Principles

1. **Extensible** — New categories can be added at any level without breaking existing data
2. **Cross-Domain** — A skill can belong to multiple categories (e.g., Python is Backend and Data)
3. **Hierarchical** — Skills form trees with parent-child relationships
4. **Tag-Based** — Every skill supports unlimited tags for non-hierarchical grouping
5. **Versioned** — Taxonomy itself is versioned to support evolution without data loss
6. **Open** — Users can extend any branch with custom skills
7. **Mappable** — Every skill can be mapped to external taxonomies (ESCO, O*NET, Lightcast, etc.)

### 3.2 Full Taxonomy Tree

```
SKILL UNIVERSE
│
├── 1. TECHNICAL SKILLS
│   ├── 1.1 Frontend Development
│   │   ├── 1.1.1 Core Web (HTML, CSS, JavaScript, DOM API)
│   │   ├── 1.1.2 Frameworks (React, Vue, Angular, Svelte, Solid)
│   │   ├── 1.1.3 State Management (Redux, Zustand, Pinia, Jotai)
│   │   ├── 1.1.4 Styling (Tailwind, CSS Modules, Styled Components, Sass)
│   │   ├── 1.1.5 Testing (Jest, Vitest, Cypress, Playwright)
│   │   ├── 1.1.6 Build Tools (Webpack, Vite, Turbopack, esbuild)
│   │   ├── 1.1.7 Performance (Core Web Vitals, Lighthouse, RUM)
│   │   ├── 1.1.8 Accessibility (WCAG, ARIA, Screen Readers)
│   │   ├── 1.1.9 Animation (Framer Motion, GSAP, Lottie, CSS Animations)
│   │   ├── 1.1.10 Mobile Web (PWA, Responsive Design, Touch Events)
│   │   └── 1.1.11 WebGL/3D (Three.js, WebGL, Canvas, D3.js)
│   │
│   ├── 1.2 Backend Development
│   │   ├── 1.2.1 Languages (Python, JavaScript/Node, Go, Rust, Java, C#, PHP)
│   │   ├── 1.2.2 Frameworks (FastAPI, Express, Next.js API, Django, Spring Boot, Laravel)
│   │   ├── 1.2.3 API Design (REST, GraphQL, gRPC, WebSocket, Webhook)
│   │   ├── 1.2.4 Authentication (OAuth, JWT, SAML, SSO, MFA)
│   │   ├── 1.2.5 Authorization (RBAC, ABAC, Policy Engines)
│   │   ├── 1.2.6 Database Access (ORM, Query Builders, Raw SQL)
│   │   ├── 1.2.7 Caching (Redis, Memcached, CDN, HTTP Cache)
│   │   ├── 1.2.8 Queues & Messaging (RabbitMQ, Kafka, Celery, SQS)
│   │   ├── 1.2.9 Search (Elasticsearch, Meilisearch, Algolia, Typesense)
│   │   ├── 1.2.10 File Storage (S3, GCS, MinIO, CDN)
│   │   ├── 1.2.11 Background Jobs (Cron, Celery, Bull, Sidekiq)
│   │   └── 1.2.12 Web Servers (Nginx, Caddy, Traefik, Apache)
│   │
│   ├── 1.3 Mobile Development
│   │   ├── 1.3.1 iOS (Swift, SwiftUI, UIKit, Xcode)
│   │   ├── 1.3.2 Android (Kotlin, Jetpack Compose, XML Layouts)
│   │   ├── 1.3.3 Cross-Platform (React Native, Flutter, Kotlin Multiplatform)
│   │   ├── 1.3.4 Mobile APIs (Camera, Location, Sensors, Biometrics)
│   │   ├── 1.3.5 App Store (Distribution, Review Process, ASO)
│   │   ├── 1.3.6 Push Notifications (FCM, APNs, Local)
│   │   ├── 1.3.7 Offline-First (Sync Engines, Local DB, Conflict Resolution)
│   │   └── 1.3.8 Mobile Performance (Profiling, Memory, Battery, Network)
│   │
│   ├── 1.4 DevOps & Infrastructure
│   │   ├── 1.4.1 CI/CD (GitHub Actions, GitLab CI, Jenkins, ArgoCD)
│   │   ├── 1.4.2 Containerization (Docker, Podman, Container Security)
│   │   ├── 1.4.3 Orchestration (Kubernetes, Nomad, Docker Swarm)
│   │   ├── 1.4.4 Infrastructure as Code (Terraform, Pulumi, Ansible, CloudFormation)
│   │   ├── 1.4.5 Monitoring (Prometheus, Grafana, Datadog, Sentry)
│   │   ├── 1.4.6 Logging (ELK, Loki, Fluentd, OpenTelemetry)
│   │   ├── 1.4.7 Networking (DNS, Load Balancers, Firewalls, VPN, CDN)
│   │   ├── 1.4.8 Linux Administration (Shell, Systemd, Filesystem, Security)
│   │   ├── 1.4.9 SRE (SLIs, SLOs, Error Budgets, Incident Response)
│   │   └── 1.4.10 Chaos Engineering (Litmus, Gremlin, GameDays)
│   │
│   ├── 1.5 Cloud Platforms
│   │   ├── 1.5.1 AWS (EC2, Lambda, S3, RDS, DynamoDB, ECS, EKS, IAM)
│   │   ├── 1.5.2 GCP (Compute Engine, Cloud Functions, GKE, BigQuery, Cloud Run)
│   │   ├── 1.5.3 Azure (VMs, Functions, AKS, Cosmos DB, DevOps)
│   │   ├── 1.5.4 Cloud Architecture (Well-Architected Framework, Cost Optimization)
│   │   ├── 1.5.5 Serverless (Lambda, Cloudflare Workers, Vercel Edge)
│   │   ├── 1.5.6 Multi-Cloud (Cross-cloud Strategy, Migration, Federation)
│   │   └── 1.5.7 Edge Computing (CloudFront, Cloudflare, Fastly, Edge Functions)
│   │
│   ├── 1.6 Data Engineering
│   │   ├── 1.6.1 ETL/ELT (Airbyte, Fivetran, dbt, Airflow)
│   │   ├── 1.6.2 Data Warehousing (Snowflake, BigQuery, Redshift, ClickHouse)
│   │   ├── 1.6.3 Data Lakes (S3/ADLS, Delta Lake, Iceberg, Hudi)
│   │   ├── 1.6.4 Stream Processing (Kafka, Flink, Spark Streaming)
│   │   ├── 1.6.5 Data Modeling (Kimball, Inmon, Data Vault)
│   │   ├── 1.6.6 SQL (PostgreSQL, MySQL, Advanced Queries, Optimization)
│   │   ├── 1.6.7 NoSQL (MongoDB, DynamoDB, Cassandra, Redis)
│   │   ├── 1.6.8 Vector Databases (Pinecone, Qdrant, Weaviate, Chroma)
│   │   └── 1.6.9 Data Governance (Cataloging, Lineage, PII Masking, Compliance)
│   │
│   ├── 1.7 Security Engineering
│   │   ├── 1.7.1 Application Security (OWASP Top 10, SAST, DAST, SCA)
│   │   ├── 1.7.2 Cloud Security (CSPM, CWPP, IAM Policies, Secrets Management)
│   │   ├── 1.7.3 Network Security (Firewalls, IDS/IPS, Zero Trust)
│   │   ├── 1.7.4 Identity & Access (SSO, MFA, Directory Services, Federation)
│   │   ├── 1.7.5 Cryptography (Encryption, Hashing, PKI, TLS)
│   │   ├── 1.7.6 Security Operations (SIEM, SOAR, Threat Hunting, Incident Response)
│   │   ├── 1.7.7 Compliance & Audit (SOC 2, ISO 27001, PCI DSS, HIPAA)
│   │   ├── 1.7.8 Penetration Testing (Web, Mobile, Network, Social Engineering)
│   │   └── 1.7.9 DevSecOps (Shift Left, Pipeline Security, Policy as Code)
│   │
│   ├── 1.8 Artificial Intelligence
│   │   ├── 1.8.1 Machine Learning (Supervised, Unsupervised, Reinforcement)
│   │   ├── 1.8.2 Deep Learning (CNNs, RNNs, Transformers, GANs, Diffusion)
│   │   ├── 1.8.3 NLP (LLMs, Tokenization, Embeddings, RAG, Fine-tuning)
│   │   ├── 1.8.4 Computer Vision (Object Detection, Segmentation, OCR, Video)
│   │   ├── 1.8.5 MLOps (Model Serving, Monitoring, A/B Testing, Feature Stores)
│   │   ├── 1.8.6 Prompt Engineering (Chain-of-Thought, Few-Shot, Structured Outputs)
│   │   ├── 1.8.7 AI Safety (Alignment, Red Teaming, Guardrails, Evaluation)
│   │   ├── 1.8.8 Model Optimization (Quantization, Pruning, Distillation, ONNX)
│   │   ├── 1.8.9 Data Science (Statistics, Experimentation, A/B Testing, Visualization)
│   │   └── 1.8.10 AI Agents (Frameworks, Tools, Memory, Planning, Multi-Agent)
│   │
│   ├── 1.9 Agent Engineering
│   │   ├── 1.9.1 Agent Frameworks (LangChain, CrewAI, AutoGen, Swarms)
│   │   ├── 1.9.2 Tool Building (Function Calling, API Tools, Custom Tools)
│   │   ├── 1.9.3 Memory Systems (Short-term, Long-term, Episodic, Semantic)
│   │   ├── 1.9.4 Agent Orchestration (Planning, Decomposition, Execution, Validation)
│   │   ├── 1.9.5 Multi-Agent Systems (Agent Communication, Consensus, Role Assignment)
│   │   ├── 1.9.6 Agent Observability (Tracing, Logging, Evaluation, Cost Tracking)
│   │   ├── 1.9.7 RAG Systems (Retrieval, Chunking, Re-ranking, Hybrid Search)
│   │   ├── 1.9.8 Prompt Management (Versioning, Testing, Optimization, Registry)
│   │   ├── 1.9.9 Agent Security (Prompt Injection, Data Leakage, Access Control)
│   │   └── 1.9.10 Agent Evaluation (Benchmarks, Human Eval, Automated Scoring)
│   │
│   ├── 1.10 Data Science & Analytics
│   │   ├── 1.10.1 Statistical Analysis (Hypothesis Testing, Regression, Bayesian)
│   │   ├── 1.10.2 Data Visualization (Matplotlib, D3.js, Tableau, Streamlit)
│   │   ├── 1.10.3 Experimentation (A/B Testing, Multi-armed Bandit, Factorial)
│   │   ├── 1.10.4 Time Series (Forecasting, Anomaly Detection, Seasonality)
│   │   ├── 1.10.5 Product Analytics (Funnel, Cohort, Retention, Attribution)
│   │   └── 1.10.6 Business Intelligence (Dashboards, KPIs, Reporting, OLAP)
│   │
│   ├── 1.11 Blockchain & Web3
│   │   ├── 1.11.1 Smart Contracts (Solidity, Rust, Move, Vyper)
│   │   ├── 1.11.2 DApp Development (Ethers.js, Wagmi, Rainbow Kit)
│   │   ├── 1.11.3 DeFi (Lending, DEX, Yield, Liquidity Pools)
│   │   ├── 1.11.4 NFTs (ERC-721, ERC-1155, Metadata, Marketplace)
│   │   ├── 1.11.5 DAOs (Governance, Treasury, Voting, Proposals)
│   │   ├── 1.11.6 Layer 2 (Rollups, Sidechains, State Channels)
│   │   └── 1.11.7 Cryptography (Hashing, Signatures, ZK-Proofs, Merkle Trees)
│   │
│   └── 1.12 Emerging & Cross-Cutting
│       ├── 1.12.1 System Design (Distributed Systems, Scalability, Fault Tolerance)
│       ├── 1.12.2 Software Architecture (Patterns, Microservices, Event-Driven)
│       ├── 1.12.3 API Design & Development
│       ├── 1.12.4 Database Design & Optimization
│       ├── 1.12.5 Testing Strategy (Unit, Integration, E2E, Performance)
│       ├── 1.12.6 Code Review & Quality
│       ├── 1.12.7 Documentation (Technical Writing, API Docs, Architecture)
│       └── 1.12.8 Developer Experience (CLI Tools, Dev Environments, DX Design)
│
├── 2. PROFESSIONAL SKILLS
│   ├── 2.1 Leadership
│   │   ├── 2.1.1 Team Management (1-on-1s, Performance Reviews, Career Growth)
│   │   ├── 2.1.2 Technical Leadership (Architecture Decisions, Mentoring, Code Standards)
│   │   ├── 2.1.3 Strategic Thinking (Roadmapping, OKRs, Vision Setting)
│   │   ├── 2.1.4 Conflict Resolution (Mediation, Difficult Conversations)
│   │   ├── 2.1.5 Decision Making (Data-Driven, Trade-off Analysis, Risk Assessment)
│   │   ├── 2.1.6 Delegation (Task Assignment, Trust Building, Escalation)
│   │   └── 2.1.7 Executive Communication (Board Updates, Investor Relations, Public Speaking)
│   │
│   ├── 2.2 Communication
│   │   ├── 2.2.1 Written Communication (Technical Writing, Proposals, Reports)
│   │   ├── 2.2.2 Verbal Communication (Presentations, Meetings, Facilitation)
│   │   ├── 2.2.3 Cross-Functional Communication (Bridging Teams, Stakeholder Mgmt)
│   │   ├── 2.2.4 Remote Communication (Async, Documentation-First, Video)
│   │   └── 2.2.5 Persuasion & Negotiation (Influence, Stakeholder Alignment)
│   │
│   ├── 2.3 Product Thinking
│   │   ├── 2.3.1 Product Strategy (Vision, Roadmap, Market Fit)
│   │   ├── 2.3.2 User Research (Interviews, Surveys, Usability Testing)
│   │   ├── 2.3.3 Product Discovery (Problem Definition, Solution Validation)
│   │   ├── 2.3.4 Metrics & Analytics (North Stars, Usage Metrics, Retention)
│   │   ├── 2.3.5 Prioritization (RICE, ICE, Opportunity Scoring, Weighted)
│   │   └── 2.3.6 Go-to-Market (Launch Strategy, Positioning, Messaging)
│   │
│   ├── 2.4 Project Management
│   │   ├── 2.4.1 Agile/Scrum (Sprints, Ceremonies, Estimation, Velocity)
│   │   ├── 2.4.2 Kanban (WIP Limits, Flow, Cycle Time, Throughput)
│   │   ├── 2.4.3 Risk Management (Identification, Mitigation, Contingency)
│   │   ├── 2.4.4 Stakeholder Management (Communication, Expectation Setting)
│   │   ├── 2.4.5 Resource Planning (Capacity, Allocation, Hiring)
│   │   └── 2.4.6 Delivery Management (Milestones, Dependencies, Launch)
│   │
│   ├── 2.5 Design
│   │   ├── 2.5.1 UI Design (Visual Design, Typography, Color, Layout)
│   │   ├── 2.5.2 UX Design (Interaction Design, Information Architecture, User Flows)
│   │   ├── 2.5.3 Design Systems (Components, Tokens, Documentation, Governance)
│   │   ├── 2.5.4 Prototyping (Figma, Framer, Interactive Prototypes)
│   │   ├── 2.5.5 Design Research (User Testing, Heatmaps, Analytics)
│   │   └── 2.5.6 Motion Design (Animation, Micro-interactions, Transitions)
│   │
│   └── 2.6 Engineering Management
│       ├── 2.6.1 Hiring (Interviewing, Inclusivity, Onboarding)
│       ├── 2.6.2 Team Building (Culture, Psychological Safety, Growth)
│       ├── 2.6.3 Technical Strategy (Platform Vision, Architecture, Tech Debt)
│       ├── 2.6.4 Process Improvement (Retrospectives, Metrics, Automation)
│       └── 2.6.5 Budget & Planning (Headcount, Tools, Infrastructure)
│
├── 3. BUSINESS SKILLS
│   ├── 3.1 Startup Building
│   │   ├── 3.1.1 Idea Validation (Problem-Solution Fit, Market Research)
│   │   ├── 3.1.2 Lean Methodology (MVP, Build-Measure-Learn, Pivot)
│   │   ├── 3.1.3 Business Modeling (Revenue Models, Unit Economics, Pricing)
│   │   ├── 3.1.4 Fundraising (Pitch Decks, Investor Relations, Cap Table)
│   │   ├── 3.1.5 Legal & IP (Incorporation, Contracts, IP Protection)
│   │   ├── 3.1.6 Growth Hacking (SEO, Viral Loops, Community Building)
│   │   └── 3.1.7 Product-Market Fit (Measurement, Iteration, Scaling)
│   │
│   ├── 3.2 Marketing
│   │   ├── 3.2.1 Digital Marketing (SEO, SEM, Social Media, Email)
│   │   ├── 3.2.2 Content Marketing (Blog, Video, Podcast, Newsletter)
│   │   ├── 3.2.3 Brand Strategy (Positioning, Voice, Identity, Storytelling)
│   │   ├── 3.2.4 Growth Marketing (Acquisition, Activation, Retention, Referral)
│   │   ├── 3.2.5 Analytics & Attribution (Cohorts, LTV, CAC, ROAS)
│   │   └── 3.2.6 Community Building (Forums, Events, Ambassador Programs)
│   │
│   ├── 3.3 Sales
│   │   ├── 3.3.1 B2B Sales (Enterprise Sales, Procurement, Contracts)
│   │   ├── 3.3.2 B2C Sales (Conversion Optimization, Funnel Management)
│   │   ├── 3.3.3 SaaS Sales (Subscription, Upsells, Churn Reduction)
│   │   ├── 3.3.4 Sales Operations (CRM, Pipeline, Forecasting)
│   │   └── 3.3.5 Negotiation (Pricing, Terms, Partnerships)
│   │
│   ├── 3.4 Finance
│   │   ├── 3.4.1 Financial Modeling (Projections, Scenarios, Valuations)
│   │   ├── 3.4.2 Accounting (Bookkeeping, GAAP, Tax, Audit)
│   │   ├── 3.4.3 Budgeting & Forecasting (Annual Planning, Variance)
│   │   ├── 3.4.4 Investment Analysis (ROI, IRR, DCF, Comparables)
│   │   └── 3.4.5 Personal Finance (Investing, Taxes, Retirement, Insurance)
│   │
│   ├── 3.5 Consulting
│   │   ├── 3.5.1 Client Management (Engagement, Scoping, Delivery)
│   │   ├── 3.5.2 Proposal Writing (Solutions, Pricing, Statements of Work)
│   │   ├── 3.5.3 Industry Analysis (Market Sizing, Competitive Research)
│   │   └── 3.5.4 Presentation (Executive Briefings, Deck Design)
│   │
│   └── 3.6 Entrepreneurship
│       ├── 3.6.1 Opportunity Recognition
│       ├── 3.6.2 Resource Acquisition (Team, Capital, Partnerships)
│       ├── 3.6.3 Execution & Operations
│       ├── 3.6.4 Resilience & Adaptability
│       └── 3.6.5 Exit Strategy (Acquisition, IPO, Merger)
│
├── 4. CREATIVE & MEDIA SKILLS
│   ├── 4.1 Content Creation (Writing, Video, Audio, Photography)
│   ├── 4.2 Design (Graphic Design, Brand Identity, Illustration)
│   ├── 4.3 Music Production (Composition, Recording, Mixing, Mastering)
│   ├── 4.4 Game Development (Unity, Unreal, Godot, Game Design)
│   └── 4.5 3D & VFX (Blender, Maya, Houdini, After Effects)
│
└── 5. USER-DEFINED SKILLS (Unlimited Custom Categories)
    ├── 5.1 Custom Technical (Any language, framework, tool not in catalog)
    ├── 5.2 Custom Professional (Any professional capability)
    ├── 5.3 Custom Business (Any business or domain expertise)
    ├── 5.4 Custom Academic (Research, Teaching, Tutoring, Subjects)
    ├── 5.5 Custom Hobby (Gaming, Sports, Cooking, Travel, Fitness)
    ├── 5.6 Custom Language (Human languages with proficiency levels)
    └── 5.7 Custom Domain (Industry-specific: Healthcare, Legal, Education, etc.)
```

### 3.3 Taxonomy Versioning

The taxonomy itself is versioned. Each version tracks:

| Field | Description |
|---|---|
| taxonomy_version | Semantic version (e.g., 1.2.0) |
| released_at | ISO date of release |
| changes | Summary of additions, modifications, deprecations |
| schema | JSON Schema definition of taxonomy structure |
| migration_path | Instructions for migrating from previous version |

Changes to the taxonomy follow semver conventions:
- **Major**: Structural changes (new top-level categories, hierarchy reorganization)
- **Minor**: New subcategories, new standard skills
- **Patch**: Corrections, renames, deprecation marking

### 3.4 External Taxonomy Mapping

| External Taxonomy | Mapping Method | Use Case |
|---|---|---|
| ESCO (EU Skills) | Crosswalk table | EU job market alignment |
| O*NET (US DOL) | Crosswalk table | US job market alignment |
| Lightcast / Emsi | API-based mapping | Labor market analytics |
| LinkedIn Skills | Name + alias matching | Profile import/export |
| roadmap.sh | Direct URL mapping | Roadmap generation |
| Stack Overflow Tags | Tag-to-skill mapping | Developer skill inference |

---

## 4. Skill Categories

### 4.1 Category: Frontend Development

| Field | Value |
|---|---|
| ID | cat:frontend |
| Description | Building user interfaces for web browsers using HTML, CSS, and JavaScript ecosystems |
| Purpose | Enable users to create interactive, responsive, accessible web experiences |
| Typical Use Cases | Building web apps, design systems, component libraries, landing pages, dashboards |
| Related Careers | Frontend Developer, UI Engineer, Web Developer, Full-Stack Developer, Creative Developer |
| Related Projects | Portfolio site, SaaS frontend, Design system, Browser extension, PWA |
| Related Certifications | Meta Frontend Developer, Google UX Design, FreeCodeCamp Responsive Web Design |
| Market Demand | Very High — consistently among top 5 most in-demand technical domains |
| Median Salary Range | $80K-$160K (depending on level and location) |
| Key Libraries | React, Vue, Angular, Next.js, Tailwind, Framer Motion, Three.js |

### 4.2 Category: Backend Development

| Field | Value |
|---|---|
| ID | cat:backend |
| Description | Building server-side logic, APIs, databases, and infrastructure that power applications |
| Purpose | Enable reliable, scalable, secure data processing and service delivery |
| Typical Use Cases | REST/GraphQL APIs, microservices, data processing pipelines, authentication systems |
| Related Careers | Backend Developer, API Engineer, Systems Engineer, Software Architect |
| Related Projects | API service, authentication system, data pipeline, real-time service |
| Related Certifications | AWS Certified Developer, Spring Professional, MongoDB Associate |
| Market Demand | Very High — fundamental to all digital products |
| Median Salary Range | $90K-$180K |
| Key Libraries | FastAPI, Express, Django, Spring Boot, Redis, PostgreSQL, Kafka |

### 4.3 Category: Mobile Development

| Field | Value |
|---|---|
| ID | cat:mobile |
| Description | Building native and cross-platform mobile applications for iOS and Android |
| Purpose | Enable users to deliver mobile-first experiences with native performance |
| Typical Use Cases | Consumer apps, enterprise mobile tools, health/fitness trackers, social platforms |
| Related Careers | iOS Developer, Android Developer, React Native Developer, Mobile Architect |
| Related Projects | Fitness app, social media clone, e-commerce app, utility tool |
| Related Certifications | Meta iOS Developer, Meta Android Developer, Google Associate Android Developer |
| Market Demand | High — stable demand with continued mobile-first growth |
| Median Salary Range | $90K-$170K |
| Key Libraries | SwiftUI, Jetpack Compose, React Native, Flutter, Firebase, Apollo |

### 4.4 Category: DevOps & Infrastructure

| Field | Value |
|---|---|
| ID | cat:devops |
| Description | Automating deployment, infrastructure management, monitoring, and reliability engineering |
| Purpose | Ensure systems are reliable, scalable, secure, and efficiently operated |
| Typical Use Cases | CI/CD pipelines, container orchestration, infrastructure as code, incident response |
| Related Careers | DevOps Engineer, SRE, Platform Engineer, Infrastructure Engineer, Cloud Engineer |
| Related Projects | CI/CD pipeline setup, Kubernetes cluster, monitoring stack, migration automation |
| Related Certifications | AWS DevOps Engineer, CKA/CKAD, Terraform Associate, Docker Certified |
| Market Demand | Very High — critical for all production systems |
| Median Salary Range | $100K-$200K |
| Key Tools | Docker, Kubernetes, Terraform, GitHub Actions, Prometheus, Grafana |

### 4.5 Category: Cloud Platforms

| Field | Value |
|---|---|
| ID | cat:cloud |
| Description | Designing, deploying, and managing applications on cloud infrastructure |
| Purpose | Enable scalable, cost-effective, globally distributed applications |
| Typical Use Cases | Cloud migration, serverless applications, multi-region deployment, cost optimization |
| Related Careers | Cloud Architect, Cloud Engineer, Solutions Architect, Platform Engineer |
| Related Projects | Serverless app, multi-region deployment, cost optimization analysis |
| Related Certifications | AWS Solutions Architect, GCP Professional Architect, Azure Solutions Architect |
| Market Demand | Very High — cloud adoption continues across all industries |
| Median Salary Range | $110K-$200K |
| Key Platforms | AWS, GCP, Azure, Cloudflare, Vercel, Netlify |

### 4.6 Category: Data Engineering

| Field | Value |
|---|---|
| ID | cat:data |
| Description | Building and maintaining data pipelines, warehouses, and infrastructure for analytics and ML |
| Purpose | Enable reliable, efficient data flow from source to insight |
| Typical Use Cases | ETL pipelines, data warehousing, real-time processing, data lake architecture |
| Related Careers | Data Engineer, Analytics Engineer, Data Architect, Database Administrator |
| Related Projects | Data pipeline, warehouse migration, streaming analytics, data catalog |
| Related Certifications | GCP Data Engineer, AWS Data Analytics, dbt Certification, Snowflake Pro |
| Market Demand | Very High — data-driven decision making requires robust data infrastructure |
| Median Salary Range | $100K-$190K |
| Key Tools | Airflow, dbt, Spark, Kafka, Snowflake, BigQuery, Airbyte |

### 4.7 Category: Security Engineering

| Field | Value |
|---|---|
| ID | cat:security |
| Description | Protecting systems, data, and users from security threats and vulnerabilities |
| Purpose | Ensure confidentiality, integrity, and availability of digital systems |
| Typical Use Cases | Security audits, penetration testing, incident response, compliance implementation |
| Related Careers | Security Engineer, Penetration Tester, Security Architect, CISO |
| Related Projects | Security audit, CTF participation, bug bounty, security tool development |
| Related Certifications | CISSP, CEH, OSCP, Security+, AWS Security Specialty |
| Market Demand | Very High — cybersecurity skills gap continues to widen |
| Median Salary Range | $100K-$200K+ |
| Key Domains | AppSec, Cloud Security, Network Security, IAM, Cryptography, Compliance |

### 4.8 Category: Artificial Intelligence

| Field | Value |
|---|---|
| ID | cat:ai |
| Description | Building intelligent systems using machine learning, deep learning, and large language models |
| Purpose | Enable automation, prediction, personalization, and intelligent decision-making |
| Typical Use Cases | Chatbots, recommendation systems, computer vision, NLP applications, predictive models |
| Related Careers | ML Engineer, AI Engineer, Data Scientist, NLP Engineer, Computer Vision Engineer |
| Related Projects | LLM chatbot, image classifier, RAG system, recommendation engine, fine-tuned model |
| Related Certifications | TensorFlow Developer, AWS ML Specialty, GCP ML Engineer, Deep Learning Specialization |
| Market Demand | Extremely High — fastest growing technical domain |
| Median Salary Range | $120K-$250K+ |
| Key Libraries | PyTorch, TensorFlow, LangChain, Hugging Face, vLLM, Weights & Biases |

### 4.9 Category: Agent Engineering

| Field | Value |
|---|---|
| ID | cat:agent_engineering |
| Description | Designing, building, and deploying autonomous AI agents that perceive, reason, and act |
| Purpose | Enable autonomous task execution, multi-agent collaboration, and AI-driven workflows |
| Typical Use Cases | Customer support agents, research assistants, automation workflows, multi-agent systems |
| Related Careers | AI Agent Engineer, LLM Engineer, Prompt Engineer, AI Architect |
| Related Projects | Research agent, customer support bot, automation pipeline, multi-agent system |
| Related Certifications | (Emerging — few exist yet, expect 2-3 by 2027) |
| Market Demand | Very High — rapidly growing as agent frameworks mature |
| Median Salary Range | $130K-$250K+ |
| Key Frameworks | LangChain, CrewAI, AutoGen, Swarms, Semantic Kernel, Haystack |

### 4.10 Category: Data Science & Analytics

| Field | Value |
|---|---|
| ID | cat:data_science |
| Description | Extracting insights and making data-driven decisions through statistical analysis and visualization |
| Purpose | Enable evidence-based decision-making through rigorous data analysis |
| Typical Use Cases | A/B testing, cohort analysis, predictive modeling, dashboard creation, reporting |
| Related Careers | Data Scientist, Data Analyst, BI Engineer, Growth Analyst, Product Analyst |
| Related Projects | Sales forecasting, user segmentation, churn analysis, experimentation platform |
| Related Certifications | Google Data Analytics, IBM Data Science, Microsoft Data Analyst |
| Market Demand | High — every organization needs data insights |
| Median Salary Range | $80K-$160K |
| Key Tools | Python, R, SQL, Tableau, Streamlit, Jupyter, dbt |

### 4.11 Category: Leadership

| Field | Value |
|---|---|
| ID | cat:leadership |
| Description | Guiding teams, making strategic decisions, and fostering growth in people and organizations |
| Purpose | Enable effective team management, organizational growth, and strategic execution |
| Typical Use Cases | Managing engineering teams, setting technical vision, mentoring junior engineers |
| Related Careers | Engineering Manager, Tech Lead, Director of Engineering, CTO |
| Related Projects | Team scaling initiative, mentoring program, technical strategy document |
| Related Certifications | PMP, Certified Manager, Leadership Development Programs |
| Market Demand | High — leadership skills are always in demand at senior levels |
| Median Salary Range | $130K-$250K+ |
| Key Competencies | Team Management, Mentoring, Strategic Planning, Conflict Resolution |

### 4.12 Category: Startup Building

| Field | Value |
|---|---|
| ID | cat:startup |
| Description | Taking an idea from concept to scalable business through validation, building, and growth |
| Purpose | Enable users to create and scale successful ventures |
| Typical Use Cases | Idea validation, MVP development, fundraising, growth strategy |
| Related Careers | Founder, Co-Founder, Product Manager, Growth Lead |
| Related Projects | MVP launch, Y Combinator application, pitch deck, customer discovery |
| Related Certifications | Y Combinator Startup School, Harvard CS50 Business, Startup School by OpenAI |
| Market Demand | Moderate — highly specialized but extremely valuable |
| Income Potential | Unlimited (equity-based) — highest upside of any category |
| Note | Startup skills cross multiple categories: technical building + business strategy + fundraising |

### 4.13 Category: Creative & Media

| Field | Value |
|---|---|
| ID | cat:creative |
| Description | Producing creative content across writing, video, audio, design, and interactive media |
| Purpose | Enable creative expression and media production for personal or commercial use |
| Typical Use Cases | Content creation, graphic design, music production, video editing, game development |
| Related Careers | Content Creator, Graphic Designer, Video Editor, Game Developer, Musician |
| Related Projects | YouTube channel, podcast, mobile game, design portfolio, music album |
| Related Certifications | Adobe Certified Professional, Unity Certified, Pro Tools Certification |
| Market Demand | High — creator economy continues to grow |
| Income Potential | Moderate to High — wide range based on platform and audience |

### 4.14 User-Defined Categories

Users can create unlimited custom categories following this schema:

| Field | Required | Description |
|---|---|---|
| id | Auto | System-generated unique identifier |
| name | Yes | Human-readable category name |
| description | Yes | What this category covers |
| parent_category | No | Link to parent in taxonomy |
| icon | No | Icon or emoji identifier for UI |
| color | No | Hex color for UI display |
| tags | No | Free-form categorization tags |
| is_public | No | Whether category can be shared or discovered by others |
| version | Auto | Category definition version |
| created_at | Auto | Timestamp |
| created_by | Auto | User ID who created it |

Users can submit categories for inclusion in the global taxonomy, which go through governance review.

---

## 5. Skill Levels

### 5.1 Level Framework

The skill level system is a standardized 6-level framework (L0-L5) that provides consistent, cross-domain proficiency assessment. Every skill, regardless of domain, uses this framework.

### 5.2 Level 0 — Unknown

| Dimension | Description |
|---|---|
| Code | L0 / unknown |
| Label | Unknown |
| Knowledge | No knowledge of the skill exists. User has never encountered or used it. |
| Practical | Cannot demonstrate any capability. May not know what the skill is. |
| Evidence | No evidence. Never mentioned, used, or studied. |
| Assessment | Would score 0% on any test. Cannot answer basic "what is" questions. |
| UI Indicator | Gray circle, no fill |
| Score Range | 0 |
| Confidence | N/A — no data to be confident about |

### 5.3 Level 1 — Beginner

| Dimension | Description |
|---|---|
| Code | L1 / beginner |
| Label | Beginner |
| Knowledge | Understands basic concepts and terminology. Knows what the skill is and why it matters. |
| Practical | Can complete simple, guided tasks with significant help or documentation. Cannot work independently. |
| Evidence | Completed an introductory tutorial, read documentation, watched a beginner course. |
| Assessment | Can answer basic conceptual questions. Cannot solve real problems. |
| UI Indicator | 1/5 filled, faint color |
| Score Range | 1-20 |

**Typical Evidence:**
- Completed "Getting Started" tutorial
- Finished an introductory course (beginner level)
- Read official documentation cover-to-cover
- Built a tutorial project (to-do app, hello world, etc.)
- Attended a workshop or bootcamp

### 5.4 Level 2 — Basic

| Dimension | Description |
|---|---|
| Code | L2 / basic |
| Label | Basic |
| Knowledge | Understands core concepts and common patterns. Knows when to use the skill. |
| Practical | Can complete standard tasks with occasional help. Can build simple projects independently. |
| Evidence | Built 1-2 small projects. Completed intermediate courses. Has some practical exposure. |
| Assessment | Can solve straightforward problems. May struggle with complex or nuanced scenarios. |
| UI Indicator | 2/5 filled |
| Score Range | 21-40 |

**Typical Evidence:**
- Built 1-2 small but functional projects
- Completed intermediate-level course or certification
- Contributed minor fixes to an open-source project
- Used the skill in a real (non-tutorial) context
- Can explain concepts to other beginners

### 5.5 Level 3 — Intermediate

| Dimension | Description |
|---|---|
| Code | L3 / intermediate |
| Label | Intermediate |
| Knowledge | Strong understanding of core concepts and common patterns. Knows advanced techniques. Understands trade-offs. |
| Practical | Can work independently on most tasks. Can architect solutions for moderate complexity. Handles common edge cases. |
| Evidence | Multiple real projects. Several months of consistent use. Open-source contributions. Professional experience. |
| Assessment | Can solve complex problems. Can review and critique others work. Can teach basics. |
| UI Indicator | 3/5 filled, medium color intensity |
| Score Range | 41-60 |

**Typical Evidence:**
- 6+ months of consistent practical use
- 3+ significant projects (not tutorials)
- Multiple open-source contributions
- Professional or freelance experience
- Can give a technical talk or workshop
- Mentored junior developers in this skill

### 5.6 Level 4 — Advanced

| Dimension | Description |
|---|---|
| Code | L4 / advanced |
| Label | Advanced |
| Knowledge | Deep, comprehensive knowledge including edge cases, internals, and historical context. Understands ecosystem and alternatives intimately. |
| Practical | Can architect and deliver complex systems independently. Handles performance optimization, security, and scalability. Defines best practices for others. |
| Evidence | Multiple production-scale projects. Years of experience. Published content. Recognized expertise. |
| Assessment | Can solve novel, ambiguous problems. Can design systems from scratch. Can write authoritative content. |
| UI Indicator | 4/5 filled, strong color |
| Score Range | 61-80 |

**Typical Evidence:**
- 2+ years of active professional/commercial use
- Production systems serving real users
- Conference talks or workshops delivered
- Published articles, books, or courses
- Significant open-source maintainership
- Led major technical decisions in this domain

### 5.7 Level 5 — Expert

| Dimension | Description |
|---|---|
| Code | L5 / expert |
| Label | Expert |
| Knowledge | Mastery-level understanding. Contributes to the skill's evolution. Recognized authority. Knows everything including esoteric edge cases. |
| Practical | Can solve any problem in the domain. Creates new patterns, tools, or frameworks. Sets industry direction. |
| Evidence | Industry recognition. Invention or creation of tools/frameworks. Book authorship. Years of leadership. |
| Assessment | Cannot be assessed by standard tests — only peer review and impact assessment. |
| UI Indicator | 5/5 filled, full color with glow effect |
| Score Range | 81-100 |

**Typical Evidence:**
- 5+ years of deep specialization
- Created widely-used tools or frameworks
- Authored definitive books or documentation
- Keynote speaker at major conferences
- Industry awards or fellowships
- Open-source project with thousands of stars
- Patents or groundbreaking contributions

### 5.8 Level Progression Rules

| Transition | Typical Time | Requirements |
|---|---|---|
| L0 to L1 | 1-4 weeks | Complete any introductory resource |
| L1 to L2 | 1-3 months | Build 1-2 real projects, use consistently |
| L2 to L3 | 3-6 months | Build 3+ projects, contribute to OSS, get professional exposure |
| L3 to L4 | 1-2 years | Production experience, mentoring, deep specialization |
| L4 to L5 | 3+ years | Industry recognition, original contributions, thought leadership |

### 5.9 Rapid Level Assessment Matrix

| Signal | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Tutorials completed | 1+ | 3+ | — | — | — |
| Real projects | — | 1-2 | 3+ | 10+ | 20+ |
| Production experience | — | — | Some | Regular | Extensive |
| Can teach others | — | Concepts | Basics | Mentoring | Authoritative |
| Published content | — | — | Tutorial | Articles | Books/Keynotes |
| OSS contributions | — | Minor | Regular | Maintainer | Creator |
| Years of use | <3mo | 3-6mo | 6-18mo | 2-4yr | 5+yr |
| Independence | Guided | Supported | Independent | Architect | Visionary |

### 5.10 Domain-Specific Level Calibration

Different domains may require level calibration. The framework supports optional domain-specific rubrics:

- **Programming Languages**: L2 = can write simple programs; L4 = can design libraries/frameworks
- **Human Languages**: L2 = conversational; L4 = fluent/native-level
- **Leadership**: L2 = can lead small teams; L4 = can lead organizations
- **Physical/Creative**: L3 = can perform reliably; L5 = competition/professional level

The core L0-L5 numeric framework remains consistent for cross-domain comparison, while the domain-specific rubric provides context within each domain.

---

## 6. Skill States

### 6.1 State Definitions

| State | Code | Description | Default? |
|---|---|---|---|
| Planned | planned | User intends to learn this skill. May have a start date and learning resources identified. | No |
| Learning | learning | Actively studying or training. Following a course, curriculum, or self-study plan. | No |
| Practicing | practicing | Applied learning — using the skill in projects, exercises, or real scenarios. | No |
| Active | active | Regularly used skill. User can perform tasks independently. Current in their toolkit. | Yes |
| Advanced | advanced | Deep expertise actively maintained. User can teach, architect, and lead in this skill. | No |
| Expert | expert | Mastery level. User is a recognized authority. Contributes to the skill's evolution. | No |
| Archived | archived | No longer actively used but history preserved. Can be reactivated. | No |
| Deprecated | deprecated | Skill is obsolete or replaced. Kept for historical reference only. | No |

### 6.2 State Transition Rules

```
planned -> learning:        User starts first learning resource
learning -> practicing:     User applies skill in a real project
practicing -> active:       User demonstrates independent capability (passes assessment or completes project)
active -> advanced:         User meets advanced evidence requirements (mentoring, production, depth)
advanced -> expert:         User meets expert evidence requirements (recognition, creation, authority)
active/advanced/expert -> archived:  User marks as no longer active (pause)
archived -> active:         User reactivates (state returns to last active state)
any -> deprecated:          Skill is obsolete (system or user action)
deprecated -> archived:     Historical preservation
learning -> planned:        User stops learning (downgrade)
practicing -> learning:     User identifies need for more structured study
active -> practicing:       User wants to rebuild depth after break
```

### 6.3 Automatic State Transitions

| Trigger | From | To | Condition |
|---|---|---|---|
| Course completion | learning | practicing | User completed a structured course |
| 30d no activity | active/practicing | archived | No evidence logged for 30 days |
| Significant new evidence | practicing | active | New project or cert submitted |
| Skill assessed as obsolete | any | deprecated | Market intelligence flags as declining |
| Re-engagement | archived | active | New evidence logged after archival |
| Project completion | learning/practicing | active | Real-world project delivered |
| Mentoring activity | active | advanced | User mentored others in this skill |
| Certification earned | practicing/active | advanced | Professional certification validated |
| AI assessment score threshold | any | +1 level | AI evaluation exceeds threshold for next level |
| Market deprecation signal | active/advanced | deprecated | Skill demand drops below threshold for 6 months |

### 6.4 State Machine Rules

The state machine enforces these invariants:
1. A skill cannot skip states (e.g., cannot go from learning directly to expert)
2. A skill can only go to archived from active states or deprecated
3. Archived skills retain all evidence and can be reactivated to their previous state
4. Deprecated skills can only transition to archived (not back to active)
5. Transitions are logged in an immutable audit trail
6. Automatic transitions generate user notifications

---

## 7. Current Skills

### 7.1 User Skill Inventory

Every user maintains a personal skill inventory — the complete list of skills they have claimed, demonstrated, or been assigned. Each entry includes:

| Field | Type | Description |
|---|---|---|
| skill_id | UUID | Reference to taxonomy skill or custom skill |
| user_id | UUID | Owner of this skill entry |
| level | enum(L0-L5) | Current proficiency level |
| state | enum(state) | Current lifecycle state |
| confidence_score | float(0-1) | System confidence in this assessment |
| evidence_score | float(0-1) | Aggregate score from all evidence |
| experience_months | int | Total experience in months |
| first_experienced | date | Date first evidence was logged |
| last_active | datetime | Last evidence or usage timestamp |
| hours_invested | int | Estimated total hours invested |
| learning_resources | jsonb | Courses, books, tutorials used (array of {name, type, url}) |
| notes | text | User personal notes on this skill |
| tags | text[] | User-specific tags for filtering and grouping |
| metadata | jsonb | Flexible extension data (future-proof) |
| auto_detected | boolean | Whether ARIA detected this automatically |

### 7.2 Skill Rating

The overall rating for a skill is a composite of multiple signals:

```
Overall Skill Rating = Combine(Level, Confidence, Evidence, Recency, Consistency)
```

Where:
- **Level** (40% weight): The L0-L5 level assigned
- **Confidence Score** (20% weight): How certain the system is about this rating
- **Evidence Score** (25% weight): Quality and quantity of supporting evidence
- **Recency** (10% weight): How recently the skill was used (decay factor)
- **Consistency** (5% weight): How consistently the skill has been maintained over time

### 7.3 Confidence Score

The confidence score represents the system certainty about a user skill level. It is calculated from:

| Signal | Weight | Source |
|---|---|---|
| Evidence Quality | 35% | Number and quality of evidence items |
| Assessment Results | 25% | Test scores, AI evaluations |
| Recency of Activity | 15% | Last evidence timestamp |
| Evidence Diversity | 10% | Different types of evidence (projects, certs, work) |
| Peer Validation | 10% | Endorsements, reviews, verifications |
| Self-Assessment Accuracy | 5% | How well user self-assessment matches evidence |

A Confidence Score below 0.3 triggers ARIA to recommend evidence submission or assessment. A score above 0.8 indicates high certainty and can be used for automated decisions.

### 7.4 Evidence Score

The evidence score reflects the quality, quantity, and recency of evidence:

```
Evidence Score = min(1.0, (Evidence_Quality_Sum / Evidence_Threshold) * Recency_Multiplier)
```

Where:
- Each evidence item has a quality weight (defined in Section 11)
- A single evidence item is capped at 0.7 to require multiple sources
- Recency multiplier decays linearly from 1.0 (today) to 0.5 (365+ days ago)
- Evidence_Threshold is configurable per category (default: 3 items)

### 7.5 Skill Inventory Views

The system supports multiple views into the user skill inventory:

1. **All Skills** — Complete flat list of every skill with state and level
2. **By Category** — Grouped by taxonomy category
3. **By State** — Filtered by lifecycle state
4. **By Level** — Filtered by proficiency level
5. **Active Skills** — subset with state in (active, advanced, expert)
6. **Learning Queue** — Skills in planned or learning state
7. **Archived Skills** — Historical skills no longer active
8. **Derived Skills** — Skills inferred from combinations of evidence
9. **Auto-Detected** — Skills ARIA found automatically
10. **Highest Confidence** — Sorted by confidence score descending

---

## 8. Target Skills

### 8.1 Target Framework

Target skills represent the skills a user needs or wants to develop. They serve as the bridge between current state and future goals. Target skills drive ARIA recommendations, roadmaps, and opportunity matching.

### 8.2 Target Types

| Target Type | Description | Example |
|---|---|---|
| Career Target | Skills needed for a specific job role | Frontend Engineer at Google needs React, TypeScript, System Design |
| Company Target | Skills valued by a specific organization | Stripe values: API Design, Payments, Distributed Systems |
| Startup Target | Skills needed to build a venture | Building a SaaS requires: Full-Stack, DevOps, Marketing, Sales |
| Income Target | Skills to reach a specific income goal | Target $200K/year: Cloud Architecture + AI + Leadership |
| Project Target | Skills required for a specific project | Building an AI chatbot: LangChain, RAG, Vector DBs, LLM APIs |
| Certification Target | Skills covered by a certification exam | AWS SA Pro exam: 14 domains including Compute, Storage, Networking |
| Learning Target | Self-defined growth areas | Get to L3 in Rust this quarter |
| Role Model Target | Skills of an aspirational person | Skills of [person]: what they know at their level |

### 8.3 Target Skills Data Model

| Field | Type | Description |
|---|---|---|
| target_id | UUID | Unique identifier |
| user_id | UUID | Owner |
| skill_id | UUID | Reference to skill |
| type | enum | Target type from above list |
| target_level | enum(L0-L5) | Desired proficiency |
| current_level | enum(L0-L5) | Current proficiency (auto-updated) |
| gap | int | target_level minus current_level |
| priority | enum(high, medium, low) | User-assigned priority |
| deadline | date | Optional target date for achieving target level |
| motivation | text | Why this target matters |
| source | text | How this target was created (user, ai, career, market) |
| created_at | datetime | |
| updated_at | datetime | |

### 8.4 Gap Analysis

For each target skill, the system calculates:

| Metric | Formula | Description |
|---|---|---|
| Skill Gap | target_level - current_level | How many levels to gain |
| Gap Severity | gap * priority_weight | Weighted gap considering user priority |
| Time to Target | estimated months based on learning velocity | How long to reach target |
| Readiness | 1 - (gap / max_possible_gap) (0-1) | How ready user is for target |
| Priority Score | gap_severity * deadline_urgency * motivation_weight | Overall priority for ARIA |

### 8.5 Target Aggregation Example

```
Career Target: "Senior AI Engineer"
    Skills Required:
    ├── Python (current: L3, target: L5, gap: 2)
    ├── Deep Learning (current: L2, target: L4, gap: 2)
    ├── MLOps (current: L1, target: L3, gap: 2)
    ├── System Design (current: L2, target: L4, gap: 2)
    ├── Leadership (current: L2, target: L3, gap: 1)
    └── Communication (current: L3, target: L4, gap: 1)

    Career Readiness: 52% overall
    Priority Skills: Python (HIGH), Deep Learning (HIGH), MLOps (MED)
    Estimated Time to Target: 8 months
    Recommended Next Step: Deep Learning specialization course
```

### 8.6 Target Creation Sources

| Source | Description | Automation |
|---|---|---|
| User-Defined | User manually sets targets | None |
| AI Suggested | ARIA recommends targets based on career goals | Auto-suggested, user approves |
| Career Import | Targets derived from imported job description | Auto-parsed, user reviews |
| Market-Driven | Targets from trending/in-demand skills | Auto-suggested by market intelligence |
| Certification | Targets from certification exam requirements | Auto-generated when cert is added |
| Role Model | Targets derived from analyzing a role model skill set | Auto-generated, user reviews |
| Gap-Driven | Targets created from opportunity match gaps | Auto-suggested when match < 60% |

---

## 9. Skill Trees

### 9.1 Tree Architecture

Skill trees are hierarchical representations of skill relationships. They enable visual navigation of skill domains, path planning for skill acquisition, dependency understanding, cluster identification, and learning pathway generation.

| Component | Description | Example |
|---|---|---|
| Root Node | Top-level domain | Frontend Development |
| Category Node | Major subdomain | React Ecosystem |
| Skill Node | Individual skill | React.js |
| Sub-skill Node | Granular capability | React Hooks |
| Leaf Node | Specific concept | useState |
| Edge | Relationship between nodes | React.js requires JavaScript |

### 9.2 Tree Types

| Tree Type | Description | Use Case |
|---|---|---|
| Taxonomy Tree | Canonical category hierarchy | Browsing all available skills |
| Dependency Tree | Prerequisite relationships | What to learn before X |
| Pathway Tree | Recommended learning sequence | Roadmap to become X |
| Cluster Tree | Related skills grouped together | Skills that complement each other |
| User Skill Tree | User personal skill graph | What I know and how it connects |
| Career Tree | Skills for a specific role | What a Frontend Engineer needs |
| Market Tree | Skills grouped by market demand | Skills trending together |

### 9.3 Example: Frontend Skill Tree

```
Frontend Development
│
├── Foundation
│   ├── HTML5 (Semantic HTML, Accessibility, SEO)
│   ├── CSS3 (Flexbox, Grid, Animations, Preprocessors)
│   └── JavaScript (ES6+, DOM API, Async, Modules)
│
├── Framework (pick one primary)
│   ├── React.js
│   │   ├── Components (Class, Functional, Hooks)
│   │   ├── State (useState, useReducer, Context, Redux)
│   │   ├── Side Effects (useEffect, useLayoutEffect, Custom Hooks)
│   │   ├── Performance (memo, useMemo, useCallback, Suspense)
│   │   ├── Routing (React Router, TanStack Router)
│   │   └── Testing (Jest, React Testing Library, Cypress)
│   │
│   ├── Vue.js (Composition API, Pinia, Vue Router, Vitest)
│   │
│   └── Angular (Components, Services, RxJS, Jasmine)
│
├── Build & Deploy
│   ├── Build Tools (Vite, Webpack, esbuild, Turbopack)
│   ├── Linting & Formatting (ESLint, Prettier)
│   ├── TypeScript (Types, Generics, Advanced Patterns)
│   └── Deployment (Vercel, Netlify, Cloudflare Pages)
│
├── Performance
│   ├── Core Web Vitals (LCP, FID, CLS)
│   ├── Bundle Optimization (Code Splitting, Tree Shaking)
│   ├── Rendering (CSR, SSR, SSG, ISR, Streaming)
│   └── Monitoring (Lighthouse, RUM, Web Vitals API)
│
├── Accessibility (WCAG, ARIA, Keyboard Navigation, Screen Readers)
│
├── Design Integration
│   ├── Design Systems (Components, Tokens, Documentation)
│   ├── Figma/Design Handoff
│   ├── Responsive Design
│   └── Animation (Framer Motion, GSAP, CSS Animations)
│
└── Advanced
    ├── WebGL/Three.js
    ├── Web Workers & Offloading
    ├── WebAssembly
    ├── PWA (Service Workers, Cache, Offline)
    └── Micro Frontends (Module Federation, Isolation)
```

### 9.4 Example: AI/ML Skill Tree

```
Artificial Intelligence
│
├── Mathematics Foundation
│   ├── Linear Algebra (Vectors, Matrices, Eigenvalues)
│   ├── Calculus (Derivatives, Gradients, Optimization)
│   ├── Probability (Distributions, Bayes, Statistical Tests)
│   └── Statistics (Hypothesis Testing, Regression, ANOVA)
│
├── Programming Foundation
│   ├── Python (NumPy, Pandas, Scikit-learn)
│   ├── R (Statistical Computing, ggplot2)
│   ├── SQL (Data Querying, Window Functions)
│   └── CUDA (GPU Programming, Optimization)
│
├── Machine Learning
│   ├── Supervised Learning (Regression, SVM, Random Forest, XGBoost)
│   ├── Unsupervised Learning (K-Means, PCA, t-SNE, DBSCAN)
│   ├── Feature Engineering (Selection, Extraction, Encoding)
│   ├── Model Evaluation (Cross-Validation, Metrics, Bias-Variance)
│   └── Hyperparameter Tuning (Grid Search, Bayesian, Optuna)
│
├── Deep Learning
│   ├── Neural Networks (Architectures, Activation, Backprop)
│   ├── CNNs (Image Classification, Object Detection, Segmentation)
│   ├── RNNs/LSTMs (Sequence Modeling, Time Series)
│   ├── Transformers (Attention, BERT, GPT, ViT)
│   ├── GANs (Generation, Style Transfer, Super Resolution)
│   └── Diffusion Models (Image Generation, Denoising)
│
├── NLP & LLMs
│   ├── Text Processing (Tokenization, Embeddings, Vectorization)
│   ├── Language Models (Pre-training, Fine-tuning, RLHF)
│   ├── RAG (Retrieval, Chunking, Re-ranking, Generation)
│   ├── Prompt Engineering (Chain-of-Thought, Few-Shot, Structured)
│   ├── Model Serving (vLLM, TGI, Triton, ONNX)
│   └── Evaluation (BLEU, ROUGE, HELM, Human Eval)
│
├── MLOps
│   ├── Experiment Tracking (MLflow, Weights & Biases, Neptune)
│   ├── Model Registry (Versioning, Staging, Production)
│   ├── CI/CD for ML (Data Validation, Model Testing, Deployment)
│   ├── Monitoring (Drift Detection, Performance Alerts)
│   └── Feature Store (Feast, Tecton, SageMaker Feature Store)
│
└── AI Agents
    ├── Agent Frameworks (LangChain, CrewAI, AutoGen, Swarms)
    ├── Tool Use (Function Calling, API Integration, Custom Tools)
    ├── Memory (Short-term, Long-term, Episodic, Vector Memory)
    ├── Planning (ReAct, Plan-and-Execute, Tree-of-Thought)
    ├── Multi-Agent (Communication, Delegation, Consensus)
    ├── Evaluation (Benchmarks, Traces, Scoring)
    └── Safety (Guardrails, Red Teaming, Alignment)
```

### 9.5 Example: Agent Engineering Skill Tree

```
Agent Engineering
│
├── Foundation
│   ├── LLM Fundamentals (Architecture, Training, Inference)
│   ├── Prompt Engineering (Zero-Shot, Few-Shot, Chain-of-Thought)
│   ├── Function Calling (Tool Definitions, JSON Mode, Structured Output)
│   └── Embeddings & Vector Search (Text Embeddings, Similarity Search)
│
├── Agent Frameworks
│   ├── LangChain (LCEL, Tools, Memory, Callbacks)
│   ├── CrewAI (Roles, Tasks, Processes, Delegation)
│   ├── AutoGen (Agent Chat, Multi-Agent, Code Execution)
│   ├── Swarms (Swarm Intelligence, Hierarchical Agents)
│   └── Custom Framework (Building from scratch)
│
├── Agent Capabilities
│   ├── Tool Building (API Tools, File Tools, Code Tools, Custom)
│   ├── Memory Systems (Short-term, Long-term, Episodic, Semantic)
│   ├── Planning (ReAct, Plan-and-Execute, Reflexion, Tree-of-Thought)
│   ├── Reasoning (Chain-of-Thought, Self-Consistency, Verification)
│   └── Learning (In-Context, Fine-tuning, RAG, Interactive)
│
├── Multi-Agent Systems
│   ├── Agent Communication (Message Passing, Shared Memory)
│   ├── Coordination (Orchestrator, Hierarchical, Peer-to-Peer)
│   ├── Role Assignment (Specialist, Generalist, Manager)
│   ├── Consensus & Voting (Majority, Weighted, Debate)
│   └── Error Recovery (Retry, Delegation, Human-in-the-Loop)
│
├── RAG Architecture
│   ├── Ingestion (Chunking, Embedding, Indexing, Metadata)
│   ├── Retrieval (Semantic, Hybrid, Multi-Vector, Re-ranking)
│   ├── Generation (Context Assembly, Citation, Hallucination Guard)
│   └── Evaluation (Hit Rate, MRR, NDCG, Faithfulness)
│
├── Observability
│   ├── Tracing (LangSmith, LangFuse, OpenAI Trace)
│   ├── Logging (Token Usage, Latency, Error Rates)
│   ├── Evaluation (Benchmarks, Human Eval, Automated Scoring)
│   └── Cost Tracking (Per-Agent, Per-Tool, Per-Run)
│
└── Safety & Security
    ├── Prompt Injection (Detection, Prevention, Mitigation)
    ├── Data Leakage (PII Redaction, Output Filtering)
    ├── Access Control (Tool Permissions, Rate Limiting)
    └── Alignment (Guardrails, Content Filtering, Ethical Constraints)
```

### 9.6 Example: Startup Building Skill Tree

```
Startup Building
│
├── Ideation & Validation
│   ├── Problem Discovery (Customer Interviews, Pain Points)
│   ├── Market Research (TAM, SAM, SOM, Competitive Analysis)
│   ├── Solution Validation (MVP, Prototype, Smoke Tests)
│   └── Business Modeling (Revenue Models, Unit Economics)
│
├── Building
│   ├── Technical (Full-Stack Development, DevOps, Architecture)
│   ├── Design (UI/UX, Brand Identity, Design System)
│   ├── Product (Roadmap, Prioritization, Metrics)
│   └── Data (Analytics, Dashboards, Experimentation)
│
├── Growth
│   ├── Marketing (Content, SEO, Social, Email, Paid)
│   ├── Sales (B2B, B2C, SaaS, Enterprise)
│   ├── Community Building (Forums, Events, Ambassador Programs)
│   └── Partnerships (Strategic, Channel, Integration)
│
├── Fundraising
│   ├── Pitch Deck (Story, Metrics, Vision, Ask)
│   ├── Investor Relations (Network, Updates, Meetings)
│   ├── Cap Table Management (Equity, Dilution, Vesting)
│   └── Due Diligence (Legal, Financial, Technical)
│
├── Operations
│   ├── Legal (Incorporation, Contracts, IP, Compliance)
│   ├── Finance (Accounting, Budgeting, Forecasting)
│   ├── Hiring (Culture, Interviewing, Onboarding)
│   └── Processes (OKRs, Reviews, Communication)
│
└── Scaling
    ├── Team Building (Leadership, Culture, Organization)
    ├── Product-Market Fit (Measurement, Iteration)
    ├── System Architecture (Scaling, Reliability, Cost)
    └── Exit Strategy (Acquisition, IPO, Merger)
```

### 9.7 Tree Storage & Query

Trees are stored as directed acyclic graphs (DAGs) in the database, with each edge having a relationship type. The system supports:

| Operation | Description |
|---|---|
| Get Children | All direct children of a skill node |
| Get Ancestors | Full path from root to this skill |
| Get Dependencies | Prerequisites and recommended dependencies |
| Shortest Path | Optimal learning path between two skills |
| Subtree | All nodes connected to a root |
| Common Ancestors | Shared prerequisites between two skills |
| Skill Clusters | Automatically detected groups of related skills |
| Skill Pathways | Curated learning sequences to reach a target |

---

## 10. Skill Dependencies

### 10.1 Dependency Framework

Skills have explicit relationships that define prerequisites, recommendations, and connections. The dependency framework enables intelligent learning path generation, gap analysis, and curriculum design.

### 10.2 Dependency Types

| Type | Code | Description | Example |
|---|---|---|---|
| Hard Dependency | hard | Must be learned before the target skill | JavaScript before React |
| Soft Dependency | soft | Should be learned before but not strictly required | HTML before React |
| Recommended | recommended | Helpful for context but not necessary | TypeScript before React |
| Complementary | complementary | Often used together | React + TypeScript |
| Alternative | alternative | Can substitute for each other | Vue instead of React |
| Builds On | builds_on | Target skill extends this prerequisite | React builds on JavaScript |
| Parallel | parallel | Can be learned concurrently | HTML + CSS |
| Version-Dependent | version | Specific version required | React 18+ for Server Components |

### 10.3 Dependency Examples

#### Frontend Dependencies

| Skill | Hard Dependencies | Soft Dependencies | Recommended |
|---|---|---|---|
| React.js | JavaScript | HTML, CSS | TypeScript |
| Next.js | React.js, JavaScript | Node.js | TypeScript, CSS |
| TypeScript | JavaScript | — | — |
| Redux | React.js | JavaScript | TypeScript |
| Tailwind CSS | CSS | HTML | — |
| Vue.js | JavaScript | HTML, CSS | TypeScript |
| Angular | TypeScript, JavaScript | HTML, CSS | RxJS |
| Svelte | JavaScript | HTML, CSS | TypeScript |

#### Backend Dependencies

| Skill | Hard Dependencies | Soft Dependencies | Recommended |
|---|---|---|---|
| FastAPI | Python | SQL | Pydantic |
| Django | Python | SQL | HTML, CSS |
| GraphQL | Any Backend Language | REST APIs | — |
| PostgreSQL | SQL | — | Database Design |
| Redis | Backend Experience | — | Caching Concepts |
| Kafka | Backend Experience | Message Queues | — |

#### AI/ML Dependencies

| Skill | Hard Dependencies | Soft Dependencies | Recommended |
|---|---|---|---|
| PyTorch | Python | Linear Algebra, Calculus | NumPy |
| LangChain | Python | LLM Concepts | Prompt Engineering |
| RAG | LangChain or Similar | Embeddings, Vector DBs | Prompt Engineering |
| Fine-tuning | Deep Learning | PyTorch/Hugging Face | MLOps |
| MLOps | ML Workflow | DevOps, Docker | — |

#### Agent Engineering Dependencies

| Skill | Hard Dependencies | Soft Dependencies | Recommended |
|---|---|---|---|
| LangChain | Python | LLM APIs | Prompt Engineering |
| CrewAI | LangChain | Agent Concepts | Tool Building |
| Multi-Agent | Single Agent | Communication Patterns | — |
| RAG Systems | Vector DBs | Embeddings | LangChain |
| Agent Evaluation | Agent Building | Testing | Observability |

### 10.4 Dependency Graph

The dependency framework enables:

```
1. Learning Path Generation
   Input: Target skill (e.g., Next.js)
   Output: Ordered list of prerequisites to learn first
   └── JavaScript -> React -> Next.js

2. Gap Analysis
   Input: Current skills + target skills
   Output: Missing prerequisites sorted by priority
   └── Missing: TypeScript (recommended before React)

3. Curriculum Design
   Input: Set of target skills
   Output: Optimal learning sequence minimizing dependencies
   └── Learn: JavaScript -> TypeScript -> React -> Next.js

4. Skill Validation
   Input: Claimed skill level
   Output: Check if prerequisites are at adequate levels
   └── React L4 requires JavaScript at least L3
```

---

## 11. Skill Evidence Framework

### 11.1 Evidence Types

Evidence is the foundation of the skill system. Every proficiency claim must be backed by verifiable evidence. The framework defines 12 evidence types:

| # | Evidence Type | Code | Description | Verification Method |
|---|---|---|---|---|
| 1 | Project | project | Completed software, design, or business project | URL, repo, screenshots, description |
| 2 | GitHub Contribution | github | Code commits, PRs, issues, reviews | GitHub API verification |
| 3 | Certification | certification | Professional certification or exam | Credential ID, badge URL |
| 4 | Course Completion | course | Completed online or in-person course | Certificate, transcript |
| 5 | Employment | employment | Professional work experience | LinkedIn, offer letter, portfolio |
| 6 | Freelance Work | freelance | Paid client work | Contract, invoice, client reference |
| 7 | Open Source | opensource | Contributions to public repositories | GitHub profile, merged PRs |
| 8 | Assessment | assessment | Platform assessment or test score | Score report, test ID |
| 9 | Publication | publication | Articles, books, talks, research papers | URL, DOI, conference link |
| 10 | Hackathon | hackathon | Competition participation or win | Devpost, certificate, project |
| 11 | Mentorship | mentorship | Teaching, mentoring, or training others | Testimonials, mentee count |
| 12 | AI Evaluation | ai_eval | AI-conducted skill evaluation | Evaluation report, score |

### 11.2 Evidence Quality Scoring

Each evidence item is scored on quality:

| Quality Level | Score | Criteria | Examples |
|---|---|---|---|
| Gold | 1.0 | Verifiable, significant, externally recognized | Major OSS project, FAANG employment, published book |
| Silver | 0.8 | Verifiable, substantial | Freelance project, course completion, hackathon win |
| Bronze | 0.5 | Verifiable, moderate | Small project, minor OSS contribution, internal assessment |
| Basic | 0.3 | Claimed but lightly verifiable | Self-reported skill use, tutorial completion |
| Unverified | 0.1 | Claimed only, no verification | User added without evidence |

### 11.3 Evidence Scoring Model

```
Evidence Score = Sum of (Evidence Item Quality) / Evidence Threshold

Where:
- Evidence_Threshold = 2.0 (configurable per category)
- Single evidence item max contribution = 0.7 (requires multiple sources)
- Max score = 1.0

Recency Multiplier:
- < 30 days: 1.0
- 30-180 days: 0.9
- 180-365 days: 0.7
- > 365 days: 0.5
- > 730 days: 0.3

Final Evidence Score = Raw Score * Recency Multiplier
```

### 11.4 Evidence Requirements Per Level

| Level | Minimum Evidence | Minimum Quality |
|---|---|---|
| L1 | 1 item (Bronze+) | 0.3 |
| L2 | 2 items (Bronze+) | 0.6 |
| L3 | 3 items (Silver+) | 2.0 |
| L4 | 5 items (Silver+, 1 Gold) | 4.0 |
| L5 | 8 items (Gold preferred) | 7.0 |

### 11.5 Evidence Submission & Verification

| Step | Description | Automation |
|---|---|---|
| Submit | User submits evidence with type, URL, description | Manual or API import |
| Parse | System extracts metadata (repo stats, dates, etc.) | Automatic |
| Verify | System attempts verification (API call, link check) | Automatic |
| Score | Evidence quality score calculated | Automatic |
| Accept | Evidence added to skill profile | Automatic after verification |
| Flag | If verification fails, evidence is flagged for review | Manual review required |
| Challenge | Other users can challenge evidence validity | Community governance |

---

## 12. Skill Assessment Framework

### 12.1 Assessment Types

| Assessment Type | Code | Description | Best For | AI Involvement |
|---|---|---|---|---|
| Multiple Choice | mcq | Standardized knowledge test | L1-L2 verification | Auto-graded |
| Coding Challenge | coding | Write real code to solve problems | L2-L4 verification | Auto-graded + AI review |
| Portfolio Review | portfolio | Review of user projects and work | L3-L5 verification | AI-assisted review |
| Project Review | project_review | Deep dive into a specific project | L3-L5 verification | AI-assisted with human review |
| Interview Simulation | interview | Simulated technical or behavioral interview | L3-L5 verification | AI-conducted |
| AI Evaluation | ai_eval | LLM evaluates skill through conversation | All levels | AI-conducted |
| Peer Review | peer | Review by other users with same skill | L4-L5 | Community |
| Practical Exercise | practical | Complete a real-world task with constraints | L2-L4 | AI-graded |
| Knowledge Graph | knowledge_graph | User explains relationships between concepts | L3-L5 | AI-analyzed |

### 12.2 Assessment Scoring

Each assessment produces multiple scores:

| Score | Description | Range |
|---|---|---|
| Raw Score | Percentage of questions/tasks correct | 0-100% |
| Adjusted Score | Normalized for difficulty | 0-100% |
| Confidence Score | System confidence in the assessment result | 0-1 |
| Domain Coverage | What percentage of the skill domain was tested | 0-100% |
| Time Efficiency | Score relative to time taken | 0-100% |

### 12.3 Readiness Score

The readiness score determines if a user is ready for a given level:

```
Readiness = (Current_Evidence_Score * 0.4) + (Assessment_Score * 0.4) + (Recency_Factor * 0.2)

If Readiness >= Level_Threshold: User is ready for level transition
Where Level_Threshold for L3 = 0.6, L4 = 0.75, L5 = 0.85
```

### 12.4 AI Evaluation Protocol

For AI-conducted evaluations:

1. ARIA selects the evaluation scope based on target level
2. ARIA generates adaptive questions (increasing difficulty based on responses)
3. For practical skills: ARIA observes user reasoning, not just output
4. ARIA scores against the level rubric (Section 5)
5. ARIA generates a detailed feedback report with strengths, gaps, and recommendations
6. AI evaluation scores are weighted at 50% of the confidence score (vs 25% for other signals)

### 12.5 Assessment Triggers

| Trigger | Assessment Type | Frequency |
|---|---|---|
| User requests level advancement | Portfolio or Project Review | On-demand |
| 90 days since last activity | Quick MCQ | Quarterly |
| New evidence submitted | Optional auto-assessment | On evidence |
| Career target readiness check | Full AI Evaluation | Monthly |
| Course completion | Post-course assessment | Per course |
| Opportunity application | Targeted skill assessment | Per application |

---

## 13. Skill Certification Framework

### 13.1 Certification Providers

The system maps certifications from major providers:

| Provider | Certifications Tracked | Verification Method |
|---|---|---|
| AWS | Solutions Architect, DevOps, ML Specialty, Security | Credential ID + API |
| Google Cloud | Professional Architect, Data Engineer, ML Engineer | Credential ID + API |
| Microsoft Azure | AZ-104, AZ-305, AI-102, DP-203 | Credential ID + API |
| Meta | Frontend Developer, Backend Developer, iOS, Android | Badge URL |
| Google | UX Design, Data Analytics, Project Management | Badge URL |
| CompTIA | Security+, Network+, A+ | Credential ID |
| ISC2 | CISSP, SSCP, CC | Credential ID |
| (ISC)2 | Certified Ethical Hacker (CEH) | Credential ID |
| Linux Foundation | CKA, CKAD, CKS | Credential ID |
| HashiCorp | Terraform Associate, Vault Associate | Badge URL |
| MongoDB | Associate, Developer | Badge URL |
| Snowflake | SnowPro Core, Advanced | Credential ID |
| dbt | dbt Developer, Analytics Engineer | Badge URL |
| TensorFlow | Developer Certificate | Badge URL |
| OpenAI | (Coming — expected certifications) | Pending |

### 13.2 Certification Mapping

Each certification maps to skills and levels:

| Certification | Skill | Level Equivalent |
|---|---|---|
| AWS Solutions Architect Associate | AWS Architecture | L3 |
| AWS Solutions Architect Professional | AWS Architecture | L4 |
| AWS DevOps Engineer Professional | DevOps | L4 |
| AWS ML Specialty | AI/ML | L3 |
| CKA (Kubernetes Admin) | Kubernetes | L3 |
| CKAD (Kubernetes App Dev) | Kubernetes | L3 |
| CISSP | Security | L4 |
| OSCP | Penetration Testing | L4 |
| Terraform Associate | IaC | L2 |
| Terraform Advanced | IaC | L3 |
| Google Data Engineer | Data Engineering | L3 |
| SnowPro Core | Data Warehousing | L2 |
| Meta Frontend Developer | Frontend | L2 |

### 13.3 Certification Validation

| Step | Method | Time |
|---|---|---|
| Submit credential ID | User input | Instant |
| API verification | System calls provider API | 1-5 seconds |
| Badge URL check | Scrape badge metadata | 1-3 seconds |
| Expiry check | Check credential expiration date | Instant |
| Skills extraction | Map cert to skills using certification-skill mapping | 1-2 seconds |
| Level assignment | Apply cert-to-level mapping | Instant |

### 13.4 Certification Expiry Tracking

| Certification | Typical Validity | Renewal Method |
|---|---|---|
| CISSP | 3 years | CPE credits |
| AWS Certifications | 3 years | Recertification exam |
| CompTIA Security+ | 3 years | CE credits |
| CKA/CKAD | 2 years | Recertification exam |
| OSCP | No expiry | — |
| PMP | 3 years | PDUs |

The system tracks expiry dates and sends renewal reminders 90/60/30 days before expiration.

---

## 14. Skill Project Mapping

### 14.1 Bidirectional Mapping

Skills and projects have a bidirectional relationship:

```
Skills -> Projects: Skills enable project completion
Projects -> Skills: Projects demonstrate and develop skills
```

### 14.2 Skill-to-Project Mapping

For each skill, the system catalogs example projects that develop or demonstrate it:

| Skill | Example Projects | Complexity | Skill Coverage |
|---|---|---|---|
| React.js | Portfolio website, Dashboard, E-commerce frontend | L1-L3 | useState, Props, Routing |
| React.js | Design system component library | L3-L4 | Hooks, Performance, Accessibility |
| React.js | Real-time collaborative editor | L4-L5 | WebSocket, CRDT, Optimization |
| Python | Data analysis script | L1-L2 | Pandas, Matplotlib |
| Python | REST API with FastAPI | L2-L3 | FastAPI, Pydantic, PostgreSQL |
| Python | ML pipeline with MLOps | L4-L5 | MLflow, Docker, CI/CD |
| Kubernetes | Single service deployment | L1-L2 | Pods, Services, ConfigMaps |
| Kubernetes | Multi-service mesh deployment | L3-L4 | Istio, Cert-manager, Helm |
| Kubernetes | Platform engineering with operators | L4-L5 | Operators, CRDs, Admission Webhooks |

### 14.3 Project-to-Skill Mapping

For each project, the system identifies required and developed skills:

| Project Type | Required Skills | Skills Developed | Complexity |
|---|---|---|---|
| Full-Stack SaaS | React, Node.js, PostgreSQL, DevOps | System Design, DevOps, Full-Stack | L3-L4 |
| ML Model Deployment | Python, ML, Docker, Cloud | MLOps, Model Serving, Monitoring | L3-L4 |
| Mobile App | React Native, Firebase, API Design | Mobile Dev, Push Notifications | L2-L3 |
| Open Source Library | Advanced Language, Testing, Documentation | OSS Maintenance, Community | L3-L5 |
| Data Pipeline | Python, SQL, Kafka, Airflow | Data Engineering, Streaming | L3-L4 |
| Startup (Full Product) | Full-Stack, DevOps, Product, Design | Startup Building, Leadership | L3-L5 |

### 14.4 Project Complexity Framework

| Complexity | Level Range | Description | Example |
|---|---|---|---|
| Beginner | L1-L2 | Tutorial-level, single concept | CRUD API, static site |
| Intermediate | L2-L3 | Multiple concepts, some integration | Full-stack app with auth |
| Advanced | L3-L4 | Production-ready, multiple systems | SaaS platform, microservices |
| Expert | L4-L5 | Large-scale, distributed, optimized | Multi-region platform, real-time system |
| Master | L5+ | Industry-leading, novel | Framework, database, distributed system |

---

## 15. Skill Roadmap Mapping

### 15.1 Roadmap Types

| Type | Source | Description |
|---|---|---|
| roadmap.sh | Standard | Curated learning paths for software roles |
| Custom | User-created | User-designed learning paths |
| AI Generated | ARIA | Personalized roadmaps based on user profile |
| Company | Employer | Internal career progression paths |
| Certification | Cert body | Exam preparation roadmaps |
| Career | Industry | Standard career progression (e.g., Junior to Senior) |
| Market | Intelligence | Trending skill pathways |

### 15.2 Roadmap-to-Skill Mapping

Each roadmap milestone maps to one or more skills:

```
Roadmap: "Frontend Developer" (roadmap.sh)
├── Month 1-2: HTML & CSS (L1-L2)
│   ├── HTML5 (Semantic HTML, Forms, SEO)
│   └── CSS3 (Flexbox, Grid, Responsive, Animations)
├── Month 3-4: JavaScript (L2-L3)
│   ├── JavaScript (ES6+, DOM, Async, Modules)
│   └── TypeScript (Types, Interfaces, Generics)
├── Month 5-8: Framework (L2-L3)
│   ├── React.js (Components, State, Effects, Routing)
│   ├── Next.js (SSR, SSG, API Routes, ISR)
│   └── State Management (Context, Redux, Zustand)
├── Month 9-10: Testing & Performance (L2-L3)
│   ├── Testing (Jest, RTL, Cypress, Playwright)
│   └── Performance (CWV, Bundle, Lighthouse, Monitoring)
└── Month 11-12: Advanced (L3-L4)
    ├── Accessibility (WCAG, ARIA, Screen Readers)
    ├── Animation (Framer Motion, GSAP)
    └── Architecture (Design Systems, Micro Frontends)
```

### 15.3 Readiness Requirements

For each roadmap, the system checks if the user has adequate prerequisites before recommending it:

| Roadmap | Prerequisite Skills | Min Level | Stale After |
|---|---|---|---|
| Frontend Developer | HTML, CSS, JavaScript | L2 | 6 months |
| Backend Developer | Any Language, SQL | L2 | 6 months |
| DevOps Engineer | Linux, Any Language, Networking | L2 | 6 months |
| AI Engineer | Python, Math Fundamentals | L2 | 6 months |
| Agent Engineer | Python, LLM Concepts | L2 | 3 months |
| Full-Stack Developer | Frontend + Backend fundamentals | L2 each | 6 months |
| Cloud Architect | At least one cloud platform | L3 | 6 months |

### 15.4 Roadmap Progress Tracking

| Metric | Description |
|---|---|
| Completion % | Percentage of milestones completed |
| Skills Acquired | Number of skills moved from L0 to L2+ |
| Time vs Estimate | Actual time vs roadmap estimate |
| Readiness Progression | Career readiness score over time |
| Skill Coverage | Percentage of required skills at target level |

---

## 16. Skill Opportunity Mapping

### 16.1 Opportunity Types

| Type | Code | Description | Skills Role |
|---|---|---|---|
| Job | job | Full-time employment | Required + preferred skills |
| Internship | internship | Student/work experience | Required skills (lower level) |
| Hackathon | hackathon | Competition events | Skills you want to demonstrate |
| Fellowship | fellowship | Structured development program | Prerequisite skills |
| Freelance | freelance | Paid project work | Skills client needs |
| Open Source | opensource | OSS project contribution | Skills project uses |
| Competition | competition | Coding/design contests | Skills being tested |
| Startup Program | startup | Accelerator, incubator | Founder/team skills |
| Contract | contract | Short-term paid engagement | Required skills |
| Grant | grant | Research/innovation funding | Technical expertise |

### 16.2 Skill Matching Framework

```
Match Score = 0.40 * Skill_Alignment + 0.25 * Level_Match + 0.15 * Growth_Potential + 0.10 * Interest_Alignment + 0.10 * Deadline_Urgency

Where:
- Skill_Alignment: % of required skills user has (weighted by skill importance)
- Level_Match: How well user levels match required levels
- Growth_Potential: Skills user would develop through this opportunity
- Interest_Alignment: Match with user interest categories
- Deadline_Urgency: Sooner deadlines score higher (if user wants)

Threshold: Match Score >= 40% to surface to user
```

### 16.3 Skill Gap for Opportunities

For each opportunity, the system identifies:

| Component | Description |
|---|---|
| Required Skills | Skills you MUST have to qualify |
| Preferred Skills | Skills that improve your candidacy |
| Skills You Have | Your current matching skills |
| Skills You Lack | Missing required skills |
| Growth Skills | Skills this opportunity would develop |
| Gap Score | Percentage of required skills missing |
| Readiness Time | Estimated time to fill gaps |

### 16.4 Opportunity Match Example

```
Opportunity: "AI Research Intern at DeepMind"
├── Required Skills:
│   ├── Python [L3]          ✅ You have L4
│   ├── Deep Learning [L3]   ✅ You have L3
│   ├── PyTorch [L2]         ✅ You have L3
│   └── Research [L2]        ❌ You lack this
│
├── Preferred Skills:
│   ├── NLP [L2]             ✅ You have L2
│   ├── Transformers [L2]    ✅ You have L2
│   └── Publications [L1]    ❌ You have 0 publications
│
├── Match Score: 78%
├── Skills You Have: Python, Deep Learning, PyTorch, NLP, Transformers
├── Skills You Lack: Research Experience, Publications
├── Growth Skills: Research Methodology, Academic Writing
└── Recommendations: Start a research blog, apply to smaller research internships first
```

---

## 17. Skill Market Intelligence

### 17.1 Intelligence Scores

The market intelligence system tracks five core scores for each skill:

| Score | Code | Description | Range |
|---|---|---|---|
| Demand Score | demand | Current market demand for this skill | 0-100 |
| Growth Score | growth | Year-over-year demand growth rate | -100 to +100 |
| Salary Score | salary | Average compensation for this skill | 0-100 (normalized) |
| Competition Score | competition | Supply-side competition (how many people have this skill) | 0-100 (lower = better) |
| Future Relevance Score | future | Predicted relevance in 3-5 years | 0-100 |

### 17.2 Score Calculation Methodology

#### Demand Score

```
Demand = f(Job_Postings, Search_Volume, Freelance_Projects, Course_Enrollments)

Where:
- Job_Postings (40%): Number of unique job postings requiring this skill
- Search_Volume (25%): Relative search frequency on job platforms
- Freelance_Projects (20%): Number of freelance/contract projects
- Course_Enrollments (15%): Enrollment in related courses (inverse signal)

Score normalized to 0-100 using percentile rank across all tracked skills
```

#### Growth Score

```
Growth = ((Current_Period_Demand - Prior_Period_Demand) / Prior_Period_Demand) * 100

Where:
- Period = 12 months rolling
- Score capped at -100 to +100
- Positive = growing demand
- Negative = declining demand
```

#### Salary Score

```
Salary = Normalize(Average_Expected_Compensation) across skill tiers

Where:
- Compensation includes: base salary + bonus + equity (annualized)
- Data sources: user-reported, public datasets, market research
- Normalized to 0-100 (100 = top 5% of all skills)
```

#### Competition Score

```
Competition = f(LinkedIn_Profiles, GitHub_Contributors, Course_Graduates)

Where:
- Lower score = less competition (better for job seekers)
- Higher score = more competition (saturated market)
- Score normalized to 0-100
```

#### Future Relevance Score

```
Future = 0.35 * Growth_Trend + 0.25 * Industry_Adoption + 0.20 * Tech_Innovation + 0.20 * Ecosystem_Health

Where:
- Growth_Trend: Sustained growth over 3+ years
- Industry_Adoption: How many industries use this skill
- Tech_Innovation: Rate of new tools/frameworks being built
- Ecosystem_Health: OSS activity, community size, corporate backing
```

### 17.3 Skill Health Indicator

Combined health metric for quick decision-making:

```
Skill Health = (Demand * 0.30) + (Growth * 0.20) + (Salary * 0.25) + ((100 - Competition) * 0.10) + (Future * 0.15)
```

| Health Range | Label | Recommendation |
|---|---|---|
| 80-100 | Excellent | High priority for development |
| 60-79 | Good | Continue development |
| 40-59 | Fair | Consider if aligned with interests |
| 20-39 | Weak | Low priority, may be declining |
| 0-19 | Poor | Avoid unless specific need |

### 17.4 Market Data Sources

| Source | Data Provided | Update Frequency |
|---|---|---|
| Job Boards (LinkedIn, Indeed, Glassdoor) | Job posting counts, salary ranges | Weekly |
| Freelance Platforms (Upwork, Fiverr, Toptal) | Project counts, rates | Weekly |
| Search Trends (Google Trends) | Search volume trends | Daily |
| Course Platforms (Udemy, Coursera) | Enrollment data | Monthly |
| GitHub API | Repository activity, language stats | Daily |
| Stack Overflow | Tag question volume, trends | Weekly |
| Industry Reports (Gartner, Forrester) | Technology adoption cycles | Quarterly |
| O*NET / Lightcast | Labor market statistics | Monthly |
| User Aggregated Data (Anonymized) | Skill distribution, salary reports | Weekly |

---

## 18. Skill Income Mapping

### 18.1 Income Sources

Skills can generate income through multiple channels:

| Source | Code | Description | Skill Intensity |
|---|---|---|---|
| Employment | employment | Full-time or part-time job salary | High (core skills required) |
| Freelancing | freelance | Per-project or hourly client work | High (skills directly sold) |
| Consulting | consulting | Expert advisory at premium rates | Very High (expertise premium) |
| Content Creation | content | Monetized knowledge sharing | Medium (skills taught/demonstrated) |
| SaaS/Product | product | Building and selling software | Medium-High (build + business) |
| Agency | agency | Service-based business | High (team of skills) |
| Teaching/Training | teaching | Courses, workshops, coaching | Medium (skills taught) |
| Open Source | opensource | Donations, sponsorships, support | Low (indirect) |
| Digital Products | digital | Templates, themes, code libraries | Medium (productized skills) |
| Affiliate Marketing | affiliate | Promoting skill-related products | Low (peripheral) |

### 18.2 Income Scoring Framework

Each skill has an income potential score:

```
Income Potential = f(Employment_Median, Freelance_Rate, Consulting_Premium, Content_Monetization)

Where:
- Employment_Median: Median salary for roles requiring this skill
- Freelance_Rate: Average hourly/project rate on freelance platforms
- Consulting_Premium: Expert rate multiplier (typically 2-5x freelance rate)
- Content_Monetization: Revenue potential from teaching/creating content about this skill

Normalized: 0-100 scale
```

### 18.3 Income Data Model

| Field | Type | Description |
|---|---|---|
| skill_id | UUID | Reference to skill |
| source | enum | Employment, Freelance, Consulting, Product, etc. |
| level | enum(L0-L5) | Level at which this income data applies |
| p10 | int | 10th percentile income |
| p25 | int | 25th percentile income |
| p50 | int | Median income |
| p75 | int | 75th percentile income |
| p90 | int | 90th percentile income |
| currency | text | ISO currency code |
| location | text | Geographic region (if applicable) |
| source_data | jsonb | Data sources and confidence |
| updated_at | datetime | Last updated |

### 18.4 Income by Skill Level Example

```
Skill: "Cloud Architecture (AWS)"
├── L2 (Basic):
│   ├── Employment: $80K-$110K
│   ├── Freelance: $50-80/hr
│   └── Consulting: N/A
├── L3 (Intermediate):
│   ├── Employment: $110K-$150K
│   ├── Freelance: $80-130/hr
│   └── Consulting: $150-200/hr
├── L4 (Advanced):
│   ├── Employment: $150K-$200K
│   ├── Freelance: $130-200/hr
│   └── Consulting: $200-350/hr
└── L5 (Expert):
    ├── Employment: $200K-$350K+
    ├── Freelance: $200-350/hr
    └── Consulting: $350-600/hr
```

### 18.5 Income Portfolio

Users can view their total income portfolio across all skills:

```
Income Portfolio
├── Primary Skill: Cloud Architecture
│   ├── Employment: $165,000
│   └── Skill ROI: +$12,500 per level
│
├── Secondary Skill: DevOps
│   ├── Employment: +$15,000 (premium)
│   └── Skill ROI: +$4,000 per level
│
├── Freelance Skills: React, Node.js
│   ├── Annual Freelance: $24,000
│   └── Effective Rate: $95/hr
│
├── Content Skills: Python, AI
│   ├── Course Revenue: $8,000/year
│   └── Content ROI: $0.50 per hour invested
│
└── Total Skills Income: $212,000/year
    └── Income Diversification Score: 72/100
```

### 18.6 Income Diversification Score

```
Diversification Score = 0.40 * Source_Count_Bonus + 0.30 * Income_Balance + 0.20 * Skill_Diversity + 0.10 * Stability_Factor

Where:
- Source_Count_Bonus: More income sources = higher score (max at 5+ sources)
- Income_Balance: Even distribution across sources (not 90% from one)
- Skill_Diversity: Different skill categories contributing
- Stability_Factor: Employment + retainer income > project-based only
```

---

## 19. Skill Analytics

### 19.1 Analytics Architecture

The skill analytics system provides real-time and historical insights across all skill dimensions. It powers dashboards, reports, recommendations, and automated alerts.

### 19.2 Core Analytics Dimensions

| Dimension | Metrics | Update Frequency |
|---|---|---|
| Growth | Skill count, level changes, new skills added | Daily |
| Velocity | Learning rate per skill, hours invested, milestones achieved | Weekly |
| Readiness | Career readiness %, target completion %, gap closure rate | Weekly |
| Health | Active vs archived ratio, stale skills, confidence trends | Daily |
| Market | Demand alignment, salary potential changes, emerging skill alerts | Weekly |
| Income | Income per skill, ROI per learning hour, diversification | Monthly |
| Engagement | Assessment completion, evidence submission, skill tree interaction | Daily |

### 19.3 Skill Growth Dashboard

The dashboard displays key growth metrics:

```
Skill Growth Dashboard
├── Skills Overview
│   ├── Total Skills: 24 (Active: 18, Learning: 4, Archived: 2)
│   ├── Avg Level: L2.7
│   ├── Skills Added This Month: 2
│   └── Skills Deprecated: 1
│
├── Level Distribution
│   ├── L0 (Unknown): 12 (skills in taxonomy, not yet started)
│   ├── L1 (Beginner): 3
│   ├── L2 (Basic): 7
│   ├── L3 (Intermediate): 8
│   ├── L4 (Advanced): 4
│   └── L5 (Expert): 2
│
├── Recent Progress
│   ├── React.js: L2 -> L3 (completed e-commerce project)
│   ├── TypeScript: L1 -> L2 (completed course)
│   └── Docker: L2 -> L3 (deployed production app)
│
├── Learning Velocity
│   ├── This Month: +0.3 avg level gain
│   ├── This Quarter: +0.8 avg level gain
│   └── Trend: Steady improvement (up 12% from last quarter)
│
└── Alerts
    ├── Python has no evidence for 60 days (stale)
    ├── GraphQL demand up 25% this quarter (consider adding)
    └── Next.js target gap = 2 levels (behind schedule)
```

### 19.4 Learning Velocity

```
Learning Velocity = Average level gain per month across all active skills

Standard Velocity: 0.2-0.3 levels/month (active learning)
Fast Velocity: 0.4-0.6 levels/month (focused learning)
Exceptional: 0.7+ levels/month (immersion)

Velocity by Category:
├── Technical Skills: 0.25 levels/month
├── Professional Skills: 0.15 levels/month
├── Business Skills: 0.10 levels/month
└── Overall: 0.22 levels/month
```

### 19.5 Career Readiness Score

```
Career Readiness = Average(Target_Skill_Readiness) across all career targets

Where each target skill readiness = min(1.0, current_level / target_level)

Overall Readiness: 62% (Fair)
├── Career Target "Senior AI Engineer": 52% (Need improvement)
├── Career Target "Full-Stack Developer": 78% (Good)
└── Career Target "Tech Lead": 45% (Need significant improvement)
```

### 19.6 Opportunity Match Score

```
Opportunity Match = Average match score across all surfaced opportunities

Current: 68% average match
├── High Match (80%+): 3 opportunities
├── Medium Match (60-79%): 8 opportunities
└── Low Match (40-59%): 5 opportunities
```

### 19.7 Income Potential Score

```
Income Potential = Normalized sum of income forecasts across all monetizable skills

Current: 72/100
├── Employment Potential: $165,000/yr (primary skills)
├── Freelance Potential: $24,000/yr (secondary skills)
├── Content Potential: $8,000/yr (teachable skills)
└── Product Potential: $12,000/yr (buildable skills)
```

### 19.8 Analytics Data Sources

| Source | Data | Integration |
|---|---|---|
| Skill Inventory | Counts, levels, states, evidence | Internal |
| Activity Log | Evidence submissions, assessments | Internal |
| Market Intelligence | Demand, growth, salary | External feeds |
| Income Data | Earnings per skill, rates | User-reported + market |
| Opportunities | Match scores, applications | Internal |
| Roadmaps | Progress, completion | Internal |
| Assessments | Scores, completion, frequency | Internal |

---

## 20. AI Recommendations

### 20.1 Recommendation Framework

ARIA provides AI-generated recommendations across five dimensions using the skill graph, market intelligence, and user profile data.

### 20.2 Skills to Learn

```
Recommendation: Learn TypeScript
├── Reasoning:
│   ├── Required for target: React (L3 -> L4 requires TypeScript)
│   ├── Market demand: Very High (Demand Score: 92/100)
│   ├── Income impact: +$8,000-12,000/yr at current level
│   └─┬ Time to L3: 2-3 months (based on your learning velocity)
│
├── Recommended Resources:
│   ├── TypeScript Handbook (free, 2 weeks)
│   └── TypeScript Course on Frontend Masters (paid, 4 weeks)
│
└── Success Criteria: Build a TypeScript React project (L3 evidence)
```

### 20.3 Skills to Improve

```
Recommendation: Improve Python from L3 to L4
├── Reasoning:
│   ├── Career impact: Senior AI Engineer target requires L4
│   ├── Income impact: +$15,000/yr (L3 -> L4 premium)
│   ├── Evidence gap: You have 4 items but all are projects (no certs)
│   └─┬ Time to L4: 4-6 months
│
├── Improvement Plan:
│   ├── Month 1-2: Advanced Python concepts (concurrency, metaprogramming)
│   ├── Month 3-4: Build a production Python service
│   └── Month 5-6: Contribute to a Python OSS project
│
└── Evidence Needed: 2 more quality items (certification + OSS)
```

### 20.4 Skills to Drop

```
Recommendation: Consider dropping Angular
├── Reasoning:
│   ├── No evidence for 8 months (stale)
│   ├── Not aligned with any current career target
│   ├── Market: Growth Score = -5 (stable but not growing)
│   └── Opportunity cost: Time could be spent on React (higher ROI)
│
├── Options:
│   ├── Archive: Keep history, free up mental space
│   └── Deprecate: Only if you will never use it again
│
└── Recommendation: Archive (can reactivate if needed)
```

### 20.5 Emerging Skills

```
Recommendation: Watch these emerging skills
├── High Priority:
│   ├── Agent Engineering (+35% demand growth this year)
│   │   └── Relevance: Directly related to your AI Engineer target
│   │
│   └── RAG Systems (+40% demand growth this year)
│       └── Relevance: Complements your existing LangChain skill
│
├── Medium Priority:
│   ├── WebAssembly (+20% demand growth)
│   └── Edge Computing (+25% demand growth)
│
└── Low Priority:
    └── Quantum Computing (too early for your current career stage)
```

### 20.6 Opportunity Readiness

```
Recommendation: You are ready for these opportunities now
├── Best Match: AI Intern at [Company]
│   ├── Match: 82%
│   ├── Skills Match: 7/8 required skills at target level
│   └── Gap: Research methodology (can learn in 2 weeks)
│
├── Coming Soon (1 month prep):
│   └── ML Engineer at [Company]
│       ├── Current Match: 65%
│       └── Prep: Complete MLOps course, build deployment pipeline
│
└── Future Goal (6 months prep):
    └── Senior AI Engineer
        ├── Current Match: 52%
        └── Roadmap: Python L4, Deep Learning L4, MLOps L3
```

### 20.7 Recommendation Triggers

| Trigger | Recommendation Type | Frequency |
|---|---|---|
| New skill added | Suggested resources and pathway | On creation |
| Skill goes stale (30d no activity) | Re-engagement reminder | Daily check |
| Target gap detected | Improvement plan | On gap identification |
| Market shift detected | Emerging skill alert | Weekly |
| Opportunity match found | Readiness assessment | Per opportunity |
| Career target added | Full skill roadmap | On target creation |
| Level transition ready | Certification/assessment suggestion | On readiness threshold |
| Quarterly review | Comprehensive skill audit | Quarterly |

### 20.8 Recommendation Sources

| Source | Description | Weight in Recommendation |
|---|---|---|
| Career Targets | User-defined career goals | 35% |
| Market Intelligence | Real-time demand and growth data | 25% |
| Skill Graph | Current skills, gaps, dependencies | 20% |
| User History | Past learning patterns and preferences | 10% |
| Peer Patterns | Anonymized patterns from similar users | 10% |

---

## 21. ARIA Agent Capabilities

### 21.1 Agent Skill Architecture

ARIA possesses its own set of skills — agent capabilities that combine data access, prompt templates, AI models, and decision logic. These share the same taxonomy, versioning, and lifecycle as user skills but are assessed through execution logs and performance metrics rather than evidence.

Each agent capability is defined by:

| Component | Description |
|---|---|
| Skill ID | Canonical identifier (e.g., skill:briefing) |
| Agent Module | Python module that implements the skill (e.g., briefing_agent) |
| Trigger | How the skill is invoked (cron, user message, API call) |
| Input Schema | Structured data requirements |
| Output Schema | Structured output format |
| LLM Dependency | Whether skill requires LLM or uses algorithmic fallback |
| Prompt File | Path to prompt template in prompts/ directory |
| Performance Metrics | Success rate, execution time, user engagement |

### 21.2 Agent Capability Catalog

The following agent capabilities are currently defined:

#### 21.2.1 Daily Briefing Generation

| Property | Value |
|---|---|
| Skill ID | skill:briefing |
| Agent | Briefing Agent (A09) |
| Trigger | 7 AM cron or user greeting |
| Input | Tasks, goals, courses, sleep, habits, opportunities |
| Output | Structured morning briefing JSON |
| LLM Required | Yes |
| Prompt File | prompts/agents/briefing_agent.md (957 lines) |
| Complexity | Medium |
| Status | Active |

**Skill Steps:**
1. Query Supabase for today state (tasks, goals, courses, sleep, habits)
2. Calculate productivity score (task completion x sleep factor x streak factor)
3. Calculate course target minutes (remaining progress / days until deadline)
4. Rank pending tasks by priority and urgency
5. Call LLM with briefing prompt template
6. Parse structured output and insert into daily_briefings table
7. Return formatted briefing dictionary

**Improvement Signals:**
- Briefing read-rate (did user open within 30 min?)
- Which recommendations user acts on
- Preferred briefing length over time

#### 21.2.2 Task Breakdown

| Property | Value |
|---|---|
| Skill ID | skill:task_breakdown |
| Agent | Task Agent (A01) |
| Trigger | User says "Break this task down" or task created with description |
| Input | Task title + description |
| Output | 2-5 subtasks inserted into tasks table |
| LLM Required | No (keyword-based algorithmic) |
| Complexity | Low |
| Status | Active |

**Skill Steps:**
1. Parse task description for keywords (research, write, build, code, design, test)
2. Map keywords to subtask templates
3. Create subtasks in Supabase with parent_task_id
4. Apply original task priority and category to subtasks

#### 21.2.3 Opportunity Matching

| Property | Value |
|---|---|
| Skill ID | skill:opportunity_match |
| Agent | Opportunity Agent (A06) |
| Trigger | 6 AM daily cron |
| Input | User skills, interests, opportunity history |
| Output | Scored opportunities inserted into opportunities table |
| LLM Required | Yes |
| Prompt File | prompts/agents/opportunity_radar_agent.md (822 lines) |
| Complexity | High |
| Status | Active |

**Skill Steps:**
1. Fetch user profile (skills, interests, past applications)
2. For each category (internships, hackathons, open source):
3. Parse opportunity details and calculate match score
4. Apply deadline urgency bonus and history penalty
5. Filter scores below 40, sort descending, insert top 20

#### 21.2.4 Roadmap Building

| Property | Value |
|---|---|
| Skill ID | skill:roadmap_build |
| Agent | Orchestrator (calls LLM) |
| Trigger | User says "Build me a roadmap for..." |
| Input | Goal description, hours/day, days/week, deadline, experience |
| Output | JSON roadmap with milestones |
| LLM Required | Yes |
| Complexity | High |
| Status | Active (design) |

#### 21.2.5 Weekly Review Generation

| Property | Value |
|---|---|
| Skill ID | skill:weekly_review |
| Agent | Weekly Review Agent (A10) |
| Trigger | Sunday 8 PM cron |
| Input | Full week data from 6+ tables |
| Output | Narrative review (email + app) |
| LLM Required | Yes |
| Prompt File | prompts/agents/weekly_review_agent.md (1264 lines) |
| Complexity | High |
| Status | Active |

#### 21.2.6 Idea Validation

| Property | Value |
|---|---|
| Skill ID | skill:idea_validation |
| Agent | Orchestrator |
| Trigger | User captures idea or says "Validate this idea" |
| Input | Idea title + description |
| Output | Market check report |
| LLM Required | Yes |
| Complexity | Medium |
| Status | Design |

#### 21.2.7 Task Prioritization

| Property | Value |
|---|---|
| Skill ID | skill:task_prioritize |
| Agent | Task Agent (A01) |
| Trigger | User says "Prioritize my tasks" or daily briefing |
| Input | All pending tasks + sleep score + goal links |
| Output | Reordered task list with priority assignments |
| LLM Required | No (algorithmic) |
| Complexity | Low |
| Status | Active |

#### 21.2.8 Course Catch-Up Plan

| Property | Value |
|---|---|
| Skill ID | skill:course_plan |
| Agent | Learning Agent (A03) |
| Trigger | User says "Help me catch up on [course]" |
| Input | Course progress, deadline, daily availability |
| Output | Daily study plan until deadline |
| LLM Required | Yes |
| Complexity | Medium |
| Status | Design |

#### 21.2.9 Knowledge Graph Insight

| Property | Value |
|---|---|
| Skill ID | skill:graph_insight |
| Agent | Orchestrator |
| Trigger | User asks "What connects X and Y?" or weekly analysis |
| Input | Users full knowledge graph |
| Output | Natural language insight about entity relationships |
| LLM Required | Yes |
| Complexity | High |
| Status | Design |

#### 21.2.10 Sleep-Aware Schedule Adjustment

| Property | Value |
|---|---|
| Skill ID | skill:sleep_adjust |
| Agent | Sleep Agent (A13) |
| Trigger | New sleep log entry (morning) |
| Input | Sleep score + today task list |
| Output | Adjusted task schedule |
| LLM Required | No (algorithmic) |
| Complexity | Low |
| Status | Active |

#### 21.2.11 Habit Streak Protection

| Property | Value |
|---|---|
| Skill ID | skill:habit_protect |
| Agent | (Habit Agent - A12) |
| Trigger | Midnight cron |
| Input | Habit logs, streak data |
| Output | Notification + streak preservation |
| LLM Required | No |
| Complexity | Low |
| Status | Active |

#### 21.2.12 Browser Extension Capture

| Property | Value |
|---|---|
| Skill ID | skill:capture |
| Agent | Orchestrator (receives from browser extension) |
| Trigger | User saves item via browser extension |
| Input | URL, title, selected text, category |
| Output | Enriched saved item (summary, tags, goal links) |
| LLM Required | Yes (for enrichment) |
| Complexity | Medium |
| Status | Design |

### 21.3 Agent Capability Invocation Matrix

| Skill | User Chat | Cron | API Call | Browser Ext |
|---|---|---|---|---|
| Briefing | Yes | Yes | — | — |
| Task Breakdown | Yes | — | Yes | — |
| Opportunity Match | — | Yes | — | — |
| Roadmap Build | Yes | — | — | — |
| Weekly Review | — | Yes | — | — |
| Idea Validation | Yes | — | — | Yes |
| Task Prioritization | Yes | Yes | Yes | — |
| Course Plan | Yes | — | — | — |
| Graph Insight | Yes | — | — | — |
| Sleep Adjust | — | Yes | Yes | — |
| Habit Protect | — | Yes | — | — |
| Capture | — | — | — | Yes |

### 21.4 Agent Capability Improvement Loop

Each agent capability improves over time through a feedback loop:

```
Skill Executes
    │
    ▼
User responds (or doesn't)
    │
    ▼
Outcome measured:
  - Was recommendation followed?
  - Was output accurate?
  - Did user engage?
    │
    ▼
Parameters adjusted:
  - Prompt weights (if LLM-based)
  - Scoring thresholds
  - Algorithmic parameters
    │
    ▼
Next execution improved
```

### 21.5 Per-Agent Learning Signals

| Skill | Success Signal | Failure Signal | Adaptation |
|---|---|---|---|
| Briefing | User completes top task | User ignores briefing | Change format/tone |
| Task Breakdown | Subtasks completed | Subtasks abandoned | Smaller subtasks |
| Opportunity Match | User applies | User never clicks | Adjust scoring weights |
| Roadmap Build | User follows milestones | Milestones missed | Adjust time estimates |
| Weekly Review | User reads full review | User skips | Shorten length |
| Idea Validation | User starts building | User archives | Improve market analysis |
| Task Prioritization | User completes top tasks | User rearranges | Learn user priorities |
| Course Plan | User sticks to plan | User abandons | Reduce daily target |
| Graph Insight | User acts on insight | User ignores | Improve query relevance |

---

## 22. Skill Lifecycle Management

### 22.1 Lifecycle Stages

The skill lifecycle covers the complete journey from creation through archival or deprecation:

| Stage | Description | Actors |
|---|---|---|
| Creation | Skill is added to the system | User, AI detection, taxonomy import |
| Active Use | Skill is being learned or practiced | User |
| Review | Periodic assessment of skill relevance and accuracy | User, AI |
| Update | Skill definition or metadata is modified | User, Taxonomy |
| Archival | Skill paused but history preserved | User, System (auto) |
| Deprecation | Skill marked as obsolete | User, System (market) |
| Deletion | Skill permanently removed (rare) | Admin only |

### 22.2 Creation

Skills can be created through:

1. **User Manual**: User adds skill with name, category, level, and optional evidence
2. **AI Detection**: ARIA detects skill usage from projects, courses, repos, and suggests addition
3. **Taxonomy Import**: System creates skills from taxonomy import or updates
4. **Course Mapping**: Skills auto-created when course completion is mapped to skills
5. **Integration Import**: Skills imported from external platforms (GitHub, LinkedIn)
6. **Certification**: Skills created when certification is submitted and mapped
7. **Opportunity**: Skills extracted from opportunity requirements and suggested to user

### 22.3 Updates

Skill updates include:

| Update Type | Description | Logged? |
|---|---|---|
| Level Change | User level increased or decreased | Yes |
| State Change | State transition (e.g., learning to active) | Yes |
| Evidence Added | New evidence submitted or detected | Yes |
| Metadata Change | Tags, notes, custom fields | Yes |
| Category Change | Taxonomy category updated | Yes |
| Dependency Update | Prerequisites or relationships modified | Yes |

### 22.4 Reviews

| Review Type | Frequency | Trigger | Actions |
|---|---|---|---|
| User Self-Review | Quarterly | Calendar reminder | Level recalibration, evidence check |
| AI Review | Monthly | System scheduled | Evidence gap detection, state suggestions |
| Skill Accuracy Check | Per evidence | Evidence submitted | Verify level matches evidence |
| Stale Skill Check | Daily | 30d inactivity | Archive suggestion |
| Market Relevance | Weekly | Market data update | Deprecation warnings, growth alerts |
| Taxonomy Review | Per version | Taxonomy update | Re-categorization, merge, split |

### 22.5 Deprecation

Skills are deprecated when:

1. **Manual**: User marks skill as no longer relevant
2. **Market Signal**: Skill demand drops below threshold for 6+ months
3. **Technology Shift**: Framework/library declared end-of-life
4. **Replacements**: Newer skill supersedes this skill
5. **No Activity**: No evidence for 12+ months and user confirms

Deprecated skills:
- Are hidden from default views
- Cannot accept new evidence
- Can be viewed in archive mode
- Can be reactivated only by removing deprecated status

### 22.6 Archival

Archive vs Deprecation:

| Aspect | Archive | Deprecation |
|---|---|---|
| Can be reactivated | Yes (one click) | Yes (but deliberate) |
| Accepts new evidence | No | No |
| Shows in active views | No | No |
| Shows in history | Yes | Yes |
| Counts toward totals | No | No |
| Market data tracked | No | Stopped |
| Skill graph connections | Preserved | Preserved but flagged |

---

## 23. Skill Versioning

### 23.1 Versioning Architecture

Every skill entity maintains a version history to track changes over time. This enables audit trails, rollbacks, and analysis of skill progression.

### 23.2 What Is Versioned

| Entity | Versioned? | Granularity | Retention |
|---|---|---|---|
| Skill Definition | Yes | Per change | Indefinite |
| User Skill Entry | Yes | Per state/level change | Indefinite |
| Taxonomy | Yes | Per release | 10 years |
| Evidence | No (immutable by nature) | — | — |
| Assessment | Yes | Per assessment | 5 years |
| Certification Mapping | Yes | Per change | Indefinite |

### 23.3 Version History

Each version entry contains:

| Field | Description |
|---|---|
| version_id | Unique version identifier |
| entity_id | ID of the entity being versioned |
| version_number | Sequential version number |
| timestamp | When the change occurred |
| changed_by | User ID or system that made the change |
| change_type | Created, Updated, State_Changed, Level_Changed, Archived, Deprecated |
| previous_state | Snapshot of previous state (JSON) |
| new_state | Snapshot of new state (JSON) |
| diff | Computed difference between states |
| reason | Why the change was made |
| metadata | Additional context (source, assessment ID, etc.) |

### 23.4 Change Log

The change log provides a human-readable history:

```
Change Log: React.js (skill:react)
├── 2026-06-01: Level L2 -> L3 (Evidence: Completed e-commerce project)
├── 2026-05-15: State Learning -> Practicing (Evidence: Started building)
├── 2026-04-01: Skill added (Source: User manual)
│
├── 2026-03-10: Taxonomy update: moved to Frontend > Frameworks (v1.2.0)
├── 2026-02-01: Evidence added: Meta Frontend Certification (Quality: 0.8)
└── 2026-01-15: Evidence added: Portfolio website (Quality: 0.5)
```

### 23.5 Upgrade Paths

When the taxonomy changes (e.g., skills are renamed, merged, or split), the system supports:

| Change Type | Migration Action | User Impact |
|---|---|---|
| Skill Renamed | Auto-update skill references | None |
| Skill Merged | Merge skills, combine evidence | Notification |
| Skill Split | Duplicate skill, user chooses which applies | User prompt |
| Category Changed | Re-assign category | None |
| Skill Deprecated | Flag skill, suggest replacement | Notification + suggestion |
| Level Recalibrated | Adjust user level if rubric changed | Notification |

### 23.6 Version API

```
GET /api/skills/{id}/versions       -> List all versions
GET /api/skills/{id}/versions/{v}   -> Get specific version
GET /api/skills/{id}/diff?v1=X&v2=Y -> Compare two versions
GET /api/skills/{id}/changelog      -> Human-readable change log
```

---

## 24. Database Mapping

### 24.1 Architecture Principles

The database schema follows these principles:

1. **Normalized Core**: Skill definitions, categories, and taxonomy are relational
2. **Flexible Extensions**: User-specific data uses JSONB for customization
3. **Immutable Audit**: All state changes are logged in append-only audit tables
4. **Time-Variant**: Historical states preserved via versioning and effective dating
5. **Relationship-Rich**: Skill relationships stored as explicit edges in a graph structure

### 24.2 Core Tables

| Table | Purpose | Key Relationships |
|---|---|---|
| skills | Canonical skill definitions (taxonomy) | belongs to category, has many user_skills |
| skill_categories | Category hierarchy | self-referential (parent_category) |
| skill_relationships | Dependency edges between skills | references skills (from, to) |
| skill_tags | Tag definitions for taxonomy filtering | belongs to many skills |
| skill_external_mappings | External taxonomy crosswalks | references skill |

### 24.3 User Tables

| Table | Purpose | Key Relationships |
|---|---|---|
| user_skills | User skill inventory with levels and states | references skill, belongs to user |
| user_skill_evidence | Evidence items for user skills | references user_skill |
| user_skill_targets | Target skills and goals | references skill, belongs to user |
| user_skill_assessments | Assessment results | references user_skill |
| user_skill_versions | Version history of user_skills | references user_skill |

### 24.4 Intelligence Tables

| Table | Purpose | Key Relationships |
|---|---|---|
| skill_market_data | Demand, growth, salary, competition scores | references skill |
| skill_income_data | Income ranges per skill per level per source | references skill |
| skill_certifications | Certification definitions with level mapping | references skill, category |
| skill_projects | Project definitions with skill requirements | references skills (many-to-many) |
| skill_roadmaps | Roadmap definitions with skill milestones | references skills (many-to-many) |
| skill_opportunities | Opportunity definitions with skill requirements | references skills (many-to-many) |

### 24.5 Audit & History Tables

| Table | Purpose | Retention |
|---|---|---|
| skill_audit_log | All state changes, evidence additions, assessments | Indefinite |
| skill_taxonomy_history | Taxonomy version history | Indefinite |
| skill_user_skill_history | User skill level/state change history | Indefinite |
| skill_market_history | Market intelligence score history | 5 years |

### 24.6 Key Relationship Constraints

| Constraint | Description |
|---|---|
| Skill Uniqueness | Skill name + category must be unique (within taxonomy) |
| Level Bounds | Level must be 0-5 |
| State Machine | State transitions must follow defined rules |
| Evidence Types | Must be from defined evidence type enum |
| Rating Bounds | All scores 0.0-1.0 |
| Cascade Delete | Deleting a skill cascades to user_skills (with confirmation) |
| Soft Delete | Skill deletion is logical, not physical (retains history) |

### 24.7 Supporting Tables

| Table | Purpose |
|---|---|
| skill_topics | Granular topics/concepts within a skill |
| skill_resources | Learning resources (courses, books, tutorials) mapped to skills |
| skill_learning_paths | Curated learning sequences |
| skill_ai_recommendations | Cached AI recommendations with reasoning |
| skill_user_activity_log | Daily/weekly activity tracking for velocity calculation |

---

## 25. API Requirements

### 25.1 API Architecture

The Skills API follows the existing RESTful pattern established in the codebase (FastAPI routers with Supabase backend). All endpoints require authentication via JWT and filter by user_id.

### 25.2 Core CRUD Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills | List skills (with filters: category, search, level, state, tags) |
| GET | /api/skills/{id} | Get skill details |
| POST | /api/skills | Create skill (user adds to their inventory) |
| PUT | /api/skills/{id} | Update skill (level, state, metadata) |
| DELETE | /api/skills/{id} | Remove skill from inventory (soft delete) |
| POST | /api/skills/bulk | Bulk import skills |

### 25.3 Taxonomy Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/taxonomy | Get full taxonomy tree |
| GET | /api/skills/taxonomy/{category_id} | Get subtree for a category |
| GET | /api/skills/taxonomy/versions | List taxonomy versions |
| GET | /api/skills/categories | List categories with metadata |
| POST | /api/skills/categories | Create custom category |

### 25.4 Evidence Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/skills/{id}/evidence | Add evidence to a skill |
| GET | /api/skills/{id}/evidence | List evidence for a skill |
| PUT | /api/skills/evidence/{evidence_id} | Update evidence |
| DELETE | /api/skills/evidence/{evidence_id} | Remove evidence |
| POST | /api/skills/evidence/verify | Verify evidence (trigger API check) |

### 25.5 Assessment Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/skills/{id}/assessments | Start or submit assessment |
| GET | /api/skills/{id}/assessments | List assessment history |
| GET | /api/skills/assessments/{assessment_id} | Get assessment details |
| GET | /api/skills/{id}/readiness | Get readiness score for level up |

### 25.6 Target Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/targets | List target skills |
| POST | /api/skills/targets | Create target skill |
| PUT | /api/skills/targets/{id} | Update target |
| DELETE | /api/skills/targets/{id} | Remove target |
| GET | /api/skills/targets/gap-analysis | Get comprehensive gap analysis |
| GET | /api/skills/targets/career-readiness | Get career readiness score |

### 25.7 Intelligence Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/{id}/market | Get market intelligence for a skill |
| GET | /api/skills/{id}/income | Get income data for a skill |
| GET | /api/skills/market/trending | Get trending skills |
| GET | /api/skills/market/emerging | Get emerging skills |
| GET | /api/skills/{id}/income-portfolio | Get user income portfolio |
| GET | /api/skills/market/by-demand | Skills sorted by demand |
| GET | /api/skills/market/by-growth | Skills sorted by growth |

### 25.8 Recommendation Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/recommendations/learn | Skills recommended to learn |
| GET | /api/skills/recommendations/improve | Skills recommended to improve |
| GET | /api/skills/recommendations/emerging | Emerging skills to watch |
| GET | /api/skills/recommendations/drop | Skills to consider dropping |
| POST | /api/skills/recommendations/generate | Force-regenerate recommendations |

### 25.9 Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/analytics/dashboard | Full analytics dashboard data |
| GET | /api/skills/analytics/velocity | Learning velocity metrics |
| GET | /api/skills/analytics/distribution | Level distribution |
| GET | /api/skills/analytics/trends | Skill growth trends over time |

### 25.10 Tree & Graph Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/tree/{skill_id} | Get skill subtree |
| GET | /api/skills/tree/user | Get user skill tree |
| GET | /api/skills/{id}/dependencies | Get skill dependencies |
| GET | /api/skills/{id}/pathways | Get learning pathways to this skill |
| GET | /api/skills/path?from={id}&to={id} | Get learning path between two skills |

### 25.11 Versioning Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/skills/{id}/versions | List skill version history |
| GET | /api/skills/{id}/versions/{version_id} | Get specific version |
| GET | /api/skills/{id}/changelog | Get human-readable change log |

---

## 26. UI/UX Requirements

### 26.1 Design Principles

The skills interface must be:

1. **Visual**: Skill trees, graphs, and distributions should be immediately understandable
2. **Actionable**: Every view should lead to a next action (add evidence, start learning, etc.)
3. **Personalized**: Each user sees their unique skill landscape
4. **Progressive**: From simple (flat list) to complex (graph views) based on user sophistication
5. **Responsive**: Full functionality on mobile, tablet, and desktop
6. **Consistent**: Follows the cyberpunk design system (tailwind.config.js tokens)

### 26.2 View Requirements

#### 26.2.1 Skill Dashboard (Primary View)

| Component | Description | Priority |
|---|---|---|
| Overview Cards | Total skills, active skills, avg level, career readiness | P0 |
| Level Distribution | Horizontal bar chart of L0-L5 distribution | P0 |
| Recent Progress | Timeline of recent level changes and evidence | P0 |
| Learning Velocity | Trend chart showing level gain over time | P1 |
| Top Recommendations | 3 AI recommendations displayed as cards | P0 |
| Quick Actions | Add skill, add evidence, start assessment buttons | P0 |

#### 26.2.2 Skill List View

| Feature | Description | Priority |
|---|---|---|
| Flat List | All skills displayed as rows with level, state, last active | P0 |
| Filtering | By category, level, state, tags, search text | P0 |
| Sorting | By level, name, last active, confidence | P0 |
| Grouping | By category, level, state | P0 |
| Bulk Actions | Select multiple for archive, delete, tag | P1 |
| Column Customization | Show/hide columns | P2 |

#### 26.2.3 Skill Detail View

| Feature | Description | Priority |
|---|---|---|
| Skill Header | Name, level badge, state badge, category, tags | P0 |
| Level Indicator | Visual L0-L5 progress bar with score | P0 |
| Evidence Section | List of evidence with quality badges, add button | P0 |
| Assessment History | Past assessments with scores | P1 |
| Market Intelligence | Demand, growth, salary cards | P1 |
| Income Data | Income ranges per level, source breakdown | P2 |
| Relationships | Prerequisites, dependencies, related skills | P1 |
| Version History | Change log timeline | P2 |
| AI Recommendations | Personalized recommendations for this skill | P1 |
| Notes | User notes section | P1 |

#### 26.2.4 Skill Graph View

| Feature | Description | Priority |
|---|---|---|
| Interactive Graph | Force-directed or hierarchical layout | P1 |
| Node Detail | Click node to see skill details | P1 |
| Relationship Lines | Dependencies shown as connecting lines | P1 |
| Zoom/Pan | Navigation across large skill trees | P1 |
| Search | Highlight matching nodes | P1 |
| Filter | Show/hide categories, states | P1 |
| Path Highlight | Show learning path between two selected skills | P2 |

#### 26.2.5 Skill Tree View

| Feature | Description | Priority |
|---|---|---|
| Vertical Tree | Expandable/collapsible skill tree | P0 |
| Progress Indicators | Color-coded nodes by level or state | P0 |
| Breadcrumb | Current position in taxonomy | P0 |
| Quick Add | Add skill to inventory from tree | P1 |
| Custom Trees | User-designed skill trees | P2 |

#### 26.2.6 Assessment View

| Feature | Description | Priority |
|---|---|---|
| Assessment Card | Skill name, current level, readiness score, start button | P0 |
| MCQ Interface | Question display, timer, progress bar | P1 |
| Coding Interface | Code editor with test runner | P2 |
| Portfolio Upload | File upload with metadata form | P1 |
| AI Evaluation | Chat interface for AI-conducted evaluation | P2 |
| Results View | Score breakdown, strengths, gaps, recommendations | P0 |

#### 26.2.7 Market Intelligence View

| Feature | Description | Priority |
|---|---|---|
| Skill Health Cards | Visual radar or gauge for each score | P1 |
| Trending Skills | Demand growth chart over time | P1 |
| Salary Comparison | Salary ranges by skill (bar chart) | P2 |
| Competition Analysis | Supply-demand visualization | P2 |
| Emerging Alerts | Notifications for rising skills | P1 |

#### 26.2.8 Analytics View

| Feature | Description | Priority |
|---|---|---|
| Growth Charts | Level changes over time (line chart) | P1 |
| Velocity Metrics | Learning rate by month (bar chart) | P1 |
| Career Readiness | Radar chart by target readiness | P1 |
| Income Portfolio | Income by source (pie/donut chart) | P2 |
| Skill Distribution | Treemap by category and level | P2 |

### 26.3 Responsive Design

| Breakpoint | Layout | Changes |
|---|---|---|
| Mobile (<768px) | Single column, stacked cards | Graph view simplified to list, trees collapsed |
| Tablet (768-1024px) | 2-column grid | Graph/tree visible but simplified |
| Desktop (1024-1440px) | 3-column grid | Full graph/tree with sidebar |
| Wide (>1440px) | 4-column with sidebar | All views available, side-by-side |

### 26.4 States

| State | Handling |
|---|---|
| Loading | Skeleton screens for all card/table components |
| Empty | Illustration + CTA: Add your first skill, Import from GitHub, Browse taxonomy |
| Error | Error card with retry button, fallback to cached data |
| Offline | Show cached skill data, queue evidence for sync |
| Large Dataset | Pagination (list view), virtualized rendering (tree view), clustered nodes (graph view) |

### 26.5 UX Flows

| Flow | Steps |
|---|---|
| Add Skill | Dashboard -> Add Skill -> Search/Browse -> Select -> Set Level -> Add Evidence -> Done |
| Add Evidence | Skill Detail -> Add Evidence -> Select Type -> Fill Details -> Submit -> Verify -> Score |
| Take Assessment | Skill Detail -> Start Assessment -> Complete Questions/Code -> Submit -> View Results |
| View Recommendations | Dashboard -> View Recommendations -> Accept/Dismiss -> Action Taken |
| Career Target | Dashboard -> Add Target -> Select Role -> Skills Auto-Loaded -> Set Priority -> Gap Analysis |
| Market Research | Skill Detail -> View Market Tab -> Demand/Growth/Salary Data -> Compare Skills |

---

## 27. Security Requirements

### 27.1 Ownership

| Principle | Implementation |
|---|---|
| User Ownership | Every skill entry is owned by exactly one user |
| System Ownership | Taxonomy, market data, and certification mappings are system-owned |
| Shared Skills | Users can optionally share skills for collaboration (opt-in) |
| Data Portability | Users can export all their skill data at any time |

### 27.2 Privacy

| Data Classification | Examples | Access Level |
|---|---|---|
| Public (user opt-in) | Skill name, level, public profile | Anyone |
| Private (default) | Full skill inventory, evidence details | User only |
| Sensitive | Salary data, assessment raw scores, personal notes | User only |
| Aggregated (anonymized) | Market intelligence, anonymized analytics | System only |

### 27.3 Access Control

| Role | Permissions |
|---|---|
| User (self) | CRUD own skills, view own data, take assessments |
| User (other) | View public skills only |
| AI (ARIA) | Read user skills for recommendations, write assessments |
| System | Read/write taxonomy, market data, anonymized analytics |
| Admin | Manage taxonomy, certifications, moderation |
| Enterprise Admin | View org skills (aggregated), manage org taxonomy |

### 27.4 Audit Logging

| Event | Logged | Retention |
|---|---|---|
| Skill created | User ID, timestamp, skill details | Indefinite |
| Skill updated | User ID, timestamp, before/after state | Indefinite |
| Skill deleted | User ID, timestamp, soft-delete marker | Indefinite |
| Evidence added | User ID, timestamp, evidence metadata | Indefinite |
| Assessment completed | User ID, timestamp, score summary | 5 years |
| Level changed | User ID, timestamp, before/after level | Indefinite |
| Data export | User ID, timestamp, export scope | 1 year |
| Data access (other user) | Requester ID, target ID, timestamp | 2 years |

### 27.5 Data Retention

| Data | Retention | Deletion Policy |
|---|---|---|
| Skill inventory | Until user account deletion | Hard delete with account |
| Evidence | Until user account deletion | Hard delete with account |
| Assessment results | 5 years after last activity | Anonymized after 5 years |
| Market data | 5 years | Aggregated only after 5 years |
| Audit logs | Indefinite | Never deleted (append-only) |
| Taxanomy history | Indefinite | Never deleted (append-only) |
| AI recommendations | 90 days | Auto-purged after 90 days |

### 27.6 Rate Limiting

| Endpoint Group | Limit | Window |
|---|---|---|
| Skill CRUD | 100 requests | 1 minute |
| Evidence submission | 30 requests | 1 minute |
| Assessment start | 10 requests | 1 hour |
| AI recommendations | 20 requests | 1 minute |
| Analytics queries | 60 requests | 1 minute |
| Market data queries | 100 requests | 1 minute |

---

## 28. Future Expansion

### 28.1 AI-Native Skills

As AI evolves, the skills system must accommodate entirely new categories of skills:

| Emerging Category | Description | Timeline |
|---|---|---|
| Multi-Agent Orchestration | Coordinating multiple AI agents for complex workflows | 2026-2027 |
| AI Safety Engineering | Red teaming, alignment, guardrail development | 2026-2027 |
| Prompt Systems Design | Engineering prompt hierarchies and chains at scale | 2026-2027 |
| LLMOps | Operations for large language model deployment at scale | 2026-2027 |
| Human-AI Collaboration | Designing workflows that optimally combine human and AI | 2027+ |
| AI Governance | Policy, regulation, and ethical framework development | 2027+ |
| Synthetic Data Engineering | Generating and validating training data | 2027+ |

### 28.2 Agent Engineering Skills

Agent engineering is expected to become a major skill category. The taxonomy and dependency framework should evolve to include:

- Agent Architecture Patterns
- Multi-Agent Communication Protocols
- Tool-Use Optimization
- Agent Memory Design
- Agent Evaluation Methodologies
- Agent Safety & Alignment
- Agent Economics (cost optimization, resource allocation)

### 28.3 Future Framework Support

The taxonomy must be able to accommodate frameworks and tools that do not yet exist. Principles:

1. **Generative Naming**: Users can name any skill freely
2. **Template-Based Taxonomy**: New frameworks can inherit structure from known categories
3. **Community Detection**: System detects clusters of related custom skills and suggests taxonomy updates
4. **Automatic Categorization**: AI suggests category placement for new/unknown skills

### 28.4 User-Generated Ecosystems

Future phases will enable:

| Feature | Description | Phase |
|---|---|---|
| Skill Packs | Curated skill collections (e.g., AI Engineer Starter Pack) | Phase 3 |
| Skill Markets | Users sell skill assessment services or coaching | Phase 3 |
| Skill Challenges | Community-defined skill challenges with verification | Phase 3 |
| Team Skill Graphs | Organizational skill mapping for teams | Phase 3 |
| Skill Endorsements | Peer-verified skill claims | Phase 4 |
| Skill-Based Hiring | Employers search by verified skill graphs | Phase 4 |
| DAO-Governed Taxonomy | Community votes on taxonomy changes | Phase 5 |

### 28.5 Marketplace Integrations

| Integration | Description | Phase |
|---|---|---|
| Course Platforms | Auto-suggest courses for skill gaps | Phase 2 |
| Certification Providers | Direct cert verification API connections | Phase 2 |
| Job Platforms | Auto-match skills to job listings | Phase 3 |
| Freelance Platforms | Import/export skill profiles to Upwork, Toptal | Phase 3 |
| Learning Platforms | Sync progress from Coursera, Udemy, Pluralsight | Phase 3 |
| HR Platforms | Integration with Workday, Lever, Greenhouse | Phase 4 |
| Blockchain Verification | Immutable skill credential storage | Phase 5 |

### 28.6 Cross-Platform Skill Passport

The ultimate evolution: a portable skill graph that users carry across platforms:

| Component | Description |
|---|---|
| User Skill Profile | Complete portable JSON export of all skills |
| Verification Chain | Cryptographic proof of evidence validity |
| Platform Bridges | Read/write connectors to major platforms |
| Universal ID | Single identity linking skills across platforms |
| Privacy Controls | Granular sharing permissions per skill |
| Analytics | Cross-platform usage and growth tracking |

---

## 29. Enterprise Governance & Compliance

### 29.1 Enterprise Governance Framework

The Skills System operates under a multi-tier governance model designed for organizational deployments with hundreds to thousands of users.

| Governance Tier | Role | Authority | Meeting Cadence |
|---|---|---|---|
| Strategic Steering Committee | CTO, CPO, Head of L&D | Taxanomy strategy, budget, roadmap | Quarterly |
| Taxanomy Working Group | SME representatives, Data Stewards | Taxanomy changes, category approval | Monthly |
| Data Governance Council | CDO, Data Stewards, Compliance | Data quality, privacy, retention | Monthly |
| AI Ethics Board | Legal, Ethics, Engineering | Recommendation fairness, bias audits | Quarterly |
| User Advisory Board | Power users from each org unit | Feature feedback, usability | Bi-monthly |

### 29.2 Decision Rights Matrix

| Decision | Owner | Approver | Consulted | Informed |
|---|---|---|---|---|
| Add new taxonomy category | Taxanomy Working Group | Steering Committee | SMEs | All users |
| Deprecate a skill | Taxanomy Working Group | Steering Committee | Market analysts | Affected users |
| Modify level rubric | Taxanomy Working Group | Data Governance Council | QA team | All users |
| Add new assessment type | Product Team | Steering Committee | AI Ethics Board | Users |
| Change scoring algorithm | AI/Data Team | AI Ethics Board | Data Governance Council | Users |
| Add new integration | Engineering | Steering Committee | Security | IT admin |
| Modify data retention policy | Data Governance Council | Legal | Security | All users |
| Approve new certification mapping | Taxanomy Working Group | Data Governance Council | SMEs | Users |
| Override AI recommendation threshold | User (personal) | None | — | — |
| Enterprise-wide setting change | Org Admin | Steering Committee | IT, Security | All org users |

### 29.3 Enterprise Compliance Mapping

| Framework | Requirements | Skills System Controls |
|---|---|---|
| SOC 2 (Type II) | Security, Availability, Processing Integrity, Confidentiality, Privacy | Encryption at rest/transit, access controls, audit logging, uptime monitoring, data classification |
| ISO 27001 | ISMS, risk assessment, access control, cryptography | RBAC, audit trails, encryption, incident response plan, regular risk assessments |
| GDPR | Data minimization, right to erasure, data portability, consent | PII classification, delete API, export API, consent management, data retention policies |
| CCPA / CPRA | Consumer data rights, opt-out, disclosure | Privacy dashboard, data deletion, disclosure reports, opt-out mechanisms |
| HIPAA (if applicable) | PHI protection, BAAs, access controls | Enhanced encryption, minimum necessary access, audit logging, BAA support |
| FedRAMP (if applicable) | NIST 800-53 controls, third-party assessment | Enhanced security controls, continuous monitoring, third-party audit support |
| EEOC / OFCCP (US Employment) | Non-discriminatory hiring practices | Bias audit trails for skill assessments, fairness monitoring, adverse impact analysis |

### 29.4 Data Quality Framework

| Dimension | Definition | Target | Measurement |
|---|---|---|---|
| Completeness | All required fields populated | >99% | Fields with nulls / total fields |
| Accuracy | Skill levels reflect true capability | >90% (post-verification) | Audit sample verification rate |
| Consistency | Same skill has same meaning across org | >95% | Cross-org taxonomy compliance |
| Timeliness | Evidence is current | <30 day lag | Last evidence date distribution |
| Uniqueness | No duplicate skill entries | <1% duplicates | Duplicate detection rate |
| Validity | Data conforms to schema | >99.5% | Schema validation pass rate |
| Integrity | Relationships are intact | >99% | Orphaned reference count |

### 29.5 Data Stewardship

| Role | Responsibilities | Per |
|---|---|---|
| Enterprise Data Steward | Taxonomy governance, quality monitoring, escalation handling | Organization |
| Domain Data Steward | Category accuracy, SME review, user support | Domain (e.g., Engineering) |
| User Data Owner | Personal skill data accuracy, evidence submission | Individual user |
| System Steward | Automated quality checks, anomaly detection | System |

### 29.6 Enterprise Audit Requirements

| Audit Type | Frequency | Scope | Performed By |
|---|---|---|---|
| Internal Data Quality | Monthly | Random 5% sample of skill records | Data Stewards |
| Access Control Review | Quarterly | All role assignments, permission changes | Security Team |
| Compliance Audit | Annual | Full framework compliance | External Auditor |
| AI Fairness Audit | Quarterly | Recommendation bias analysis | AI Ethics Board |
| Privacy Impact Assessment | Per major feature | Data collection, processing, retention | Legal/Privacy |
| Skill Inflation Audit | Quarterly | Level vs evidence verification | QA Team |

### 29.7 Skill Inflation Detection

The system actively monitors and flags skill inflation (users claiming higher levels than evidence supports):

| Signal | Detection | Action |
|---|---|---|
| Level vs Evidence Gap | User level 2+ above evidence score | Flag for review, suggest assessment |
| Rapid Level Inflation | Multiple level increases in 30 days | Flag, require evidence verification |
| Category Concentration | All skills at L4+ with minimal evidence | Review sample, suggest peer assessment |
| Org-Level Inflation | Average levels significantly above market | Org-level report to steering committee |
| AI Score Deviation | AI assessment score significantly below claimed level | Auto-reduce confidence, suggest reassessment |

---

## 30. Enterprise Integration Patterns

### 30.1 Integration Architecture

The Skills System must integrate with existing enterprise tooling to be viable in organizational deployments.

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTERPRISE ECOSYSTEM                       │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │  HRIS   │  │   LMS   │  │   ATS   │  │   SSO   │         │
│  │(Workday)│  │(Corner- │  │(Green-  │  │(Okta,   │         │
│  │ BambooHR│  │ stone,  │  │ house,  │  │ Azure   │         │
│  │ Rippling│  │Docebo)  │  │ Lever)  │  │ AD, One)│         │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘         │
│       │            │            │            │              │
│       └────────────┼────────────┼────────────┘              │
│                    ▼            ▼                           │
│  ┌─────────────────────────────────────────────┐           │
│  │           SKILLS SYSTEM API GATEWAY          │           │
│  │  (SCIM v2, REST, Webhook, Event Bus)        │           │
│  └───────────────┬─────────────────────────────┘           │
│                  │                                         │
│  ┌───────────────▼─────────────────────────────┐           │
│  │           SKILLS ENGINE                      │           │
│  │  Taxonomy | Inventory | Assessment | Market   │           │
│  │  Recommendations | Analytics | Graph         │           │
│  └─────────────────────────────────────────────┘           │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │  IDP    │  │  Slack  │  │ Email   │  │ Mobile  │         │
│  │(Portal) │  │ Notifs  │  │(Resend) │  │ (React  │         │
│  │         │  │         │  │         │  │ Native) │         │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 30.2 HRIS Integration (Workday, BambooHR, Rippling)

| Integration | Direction | Data | Protocol | Frequency |
|---|---|---|---|---|
| Employee Import | HRIS -> Skills | User profile, job title, department, manager | SCIM v2 | Real-time + daily sync |
| Role Sync | HRIS -> Skills | Job descriptions, role requirements, career ladders | SCIM v2 | Weekly |
| Skills Export | Skills -> HRIS | Verified skills, levels, certifications | REST API | Daily |
| Reporting | Skills -> HRIS | Org skill heatmap, gap analysis, readiness | REST API | On-demand |

### 30.3 LMS Integration (Cornerstone, Docebo, Moodle)

| Integration | Direction | Data | Protocol | Frequency |
|---|---|---|---|---|
| Course Catalog | LMS -> Skills | Available courses, mapped skills | REST API | Daily |
| Course Completion | LMS -> Skills | Completed courses, scores, dates | Webhook + REST | Real-time |
| Skill Recommendations | Skills -> LMS | Recommended courses for skill gaps | REST API | Weekly |
| Learning Path Sync | Skills <-> LMS | Skill-based learning paths | REST API | On change |
| Progress Tracking | LMS -> Skills | Course progress, time spent | REST API | Daily |

### 30.4 ATS Integration (Greenhouse, Lever, Workable)

| Integration | Direction | Data | Protocol | Frequency |
|---|---|---|---|---|
| Job Requirements | ATS -> Skills | Required skills, levels, preferences | REST API | Per job posting |
| Candidate Match | Skills -> ATS | Candidate skill match scores | REST API | On application |
| Skill Verification | Skills -> ATS | Verified skill claims, assessments | REST API | On request |
| Hiring Analytics | Skills -> ATS | Org skill gaps vs hiring needs | REST API | Weekly |

### 30.5 Identity & SSO Integration

| Protocol | Usage | Implementation |
|---|---|---|
| SAML 2.0 | Enterprise SSO for web app | Identity provider-initiated SSO |
| OIDC / OAuth 2.0 | SSO + API authentication | Authorization code flow with PKCE |
| SCIM v2 | User provisioning and deprovisioning | Create, update, deactivate users |
| Just-In-Time (JIT) Provisioning | Auto-create accounts on first SSO | SAML attribute mapping |
| Directory Sync (LDAP/AD) | Group-based access control | Group membership sync |

### 30.6 Webhook & Event Integration

| Event | Trigger | Payload | Consumers |
|---|---|---|---|
| skill.level.changed | User level changes | user_id, skill_id, old_level, new_level | LMS, HRIS, Slack |
| skill.evidence.added | New evidence submitted | user_id, skill_id, evidence_type, score | HRIS, Reporting |
| skill.certification.verified | Certification validated | user_id, cert_id, skill_id, level | HRIS, ATS |
| skill.target.reached | Target level achieved | user_id, target_id, skill_id | Slack, Email |
| skill.assessment.completed | Assessment finished | user_id, skill_id, score, level | HRIS, LMS |
| skill.recommendation.generated | New AI recommendation | user_id, recommendation_type, skills | Email, Mobile |

### 30.7 Integration SLA Requirements

| Integration Type | Uptime SLA | Max Latency | Data Freshness |
|---|---|---|---|
| Real-time (Webhook) | 99.9% | <30 seconds | Real-time |
| Synchronous API | 99.95% | <2 seconds | Real-time |
| Batch Sync | 99.5% | <4 hours | <24 hours |
| Bulk Export | 99.0% | <1 hour | <24 hours |

---

## 31. Multi-Tenant Architecture & Isolation

### 31.1 Tenant Model

The Skills System supports multiple deployment models for enterprise:

| Model | Description | Best For | Isolation Level |
|---|---|---|---|
| Single-Tenant Dedicated | Each org has isolated infrastructure | Large enterprises, regulated industries | Physical |
| Multi-Tenant Pooled | Multiple orgs share infrastructure | Mid-market, SMB | Logical (Row-level) |
| Hybrid | Dedicated core + shared services | Enterprise with subsidiaries | Mixed |
| Self-Hosted | Org deploys on own infrastructure | Government, defense, finance | Physical + Network |

### 31.2 Tenant Isolation Strategies

| Layer | Single-Tenant | Multi-Tenant (Pooled) | Governance |
|---|---|---|---|
| Database | Dedicated instance | Row-level security (tenant_id) | RLS policies per table |
| Cache | Dedicated Redis instance | Key prefix per tenant (tenant:{id}:) | Namespace isolation |
| File Storage | Dedicated bucket | Prefix-based isolation | IAM bucket policies |
| Compute | Dedicated containers | Shared with rate limits | Resource quotas |
| AI Models | Fine-tuned per tenant | Shared with context isolation | Prompt injection protection |
| API Rate Limits | Per-tenant allocation | Per-tenant + shared pool | Configurable thresholds |

### 31.3 Enterprise Admin Console

| Feature | Description | Priority |
|---|---|---|
| Org Dashboard | User count, skill distribution, top skills, growth trends | P0 |
| User Management | Invite, suspend, deactivate, role assignment | P0 |
| Taxanomy Management | Custom categories, skill enable/disable, rename | P0 |
| Policy Configuration | Level requirements, evidence rules, assessment defaults | P1 |
| Integration Settings | API keys, webhook URLs, SCIM config | P1 |
| Compliance Reports | Audit logs, data export, compliance status | P1 |
| Billing & Usage | Seat count, API usage, storage, AI credits | P1 |
| White-Labeling | Custom domain, logo, brand colors | P2 |

### 31.4 Enterprise Roles & Permissions

| Role | Scope | Permissions |
|---|---|---|
| Super Admin | Entire org | All settings, all user data, billing, integrations |
| Org Admin | Entire org | User management, taxonomy, policy, reporting |
| Department Admin | Department | User management within department, department taxonomy |
| Manager | Direct reports | View team skills, recommend targets, approve evidence |
| User | Self | Manage personal skills, evidence, assessments, targets |
| Auditor | Read-only org-wide | View all data, export reports, audit logs |
| Integration | API operations | API access with scoped permissions |
| Data Steward | Taxonomy | Modify taxonomy, review evidence, manage certifications |

### 31.5 Enterprise Scalability Targets

| Metric | Target | Design Notes |
|---|---|---|
| Max tenants | 10,000+ | Partitioned by region, sharded by tenant ID |
| Users per tenant | 100,000+ | Horizontally scalable read replicas |
| Skills per user | 1,000+ | Efficient pagination, lazy loading |
| API throughput | 10,000+ req/s | Caching layers, CDN for static data |
| AI requests/day | 1,000,000+ | Queue-based processing, batchable |
| Evidence storage | 100M+ items | Time-partitioned tables, archival |
| Audit log retention | 10+ years | Append-only, cold storage for older data |
| Uptime SLA | 99.95% (99.99% single-tenant) | Multi-region, auto-failover |

---

## 32. Enterprise SLAs, KPIs & Pricing

### 32.1 Service Level Agreements

| Metric | Standard | Enterprise | Premium |
|---|---|---|---|
| Uptime | 99.5% | 99.9% | 99.99% |
| API Response Time (P95) | <500ms | <200ms | <100ms |
| AI Recommendation Latency | <5s | <2s | <1s |
| Support Response Time | 4 hours | 1 hour | 15 minutes |
| Support Availability | Business hours | 24/5 | 24/7 |
| Dedicated Support Engineer | No | Yes | Yes (named) |
| SLA Credit | 5% per 0.5% below | 10% per 0.5% below | Negotiated |
| Max Monthly Downtime | 3.6 hours | 43 minutes | 4 minutes |

### 32.2 Enterprise KPIs

| KPI | Definition | Target | Measurement |
|---|---|---|---|
| User Adoption | Active users / total licensed users | >80% | Monthly active users |
| Skill Coverage | % of users with >5 skills at L2+ | >60% | Quarterly |
| Skill Accuracy | % of skill levels matching evidence | >85% | Audit sample |
| Evidence Submission Rate | % of skills with evidence | >70% | Quarterly |
| Assessment Completion Rate | Started vs completed assessments | >75% | Monthly |
| Recommendation Acceptance | Actions taken / recommendations shown | >30% | Weekly |
| Time to Value | Days from onboarding to first skill added | <7 days | Per cohort |
| User Satisfaction | NPS survey score | >50 | Quarterly |
| Learning Velocity Improvement | Avg level gain per user per quarter | +0.3 levels | Quarterly |
| Org Readiness Score | % of org meeting career readiness targets | >60% | Quarterly |
| Data Completeness | % of required fields populated | >95% | Monthly |
| Integration Uptime | % of time integrations are functional | >99.5% | Monthly |

### 32.3 Enterprise Pricing Tiers

| Feature | Essentials | Business | Enterprise | Premium |
|---|---|---|---|---|
| **Users** | Up to 50 | Up to 500 | 500-5,000 | 5,000+ |
| **Skills** | Core taxonomy | Full taxonomy | Full + custom | Full + custom + dedicated |
| **Evidence** | 3 types | 6 types | All 12 types | All + custom evidence types |
| **Assessments** | Self-assess only | Self + MCQ | Full assessment suite | Assessment + AI evaluation |
| **Market Intelligence** | Basic (scores only) | Standard (scores + trends) | Advanced (forecasts + alerts) | API access + custom feeds |
| **Income Mapping** | Not available | Employment only | All sources | Custom income models |
| **AI Recommendations** | Weekly | Daily | Real-time | Custom models |
| **Integrations** | SSO only | SSO + 1 integration | SSO + 5 integrations | Unlimited + custom |
| **API Rate Limit** | 1,000/day | 10,000/day | 100,000/day | Unlimited |
| **Support** | Email (4h) | Chat + email (1h) | 24/5 + dedicated | 24/7 + named engineer |
| **SLA** | 99.5% | 99.9% | 99.95% | 99.99% |
| **Self-Hosted Option** | No | No | Yes (add-on) | Yes (included) |
| **White Label** | No | No | Yes | Yes |
| **Custom Taxanomy** | No | Limited | Full | Full + dedicated steward |
| **Data Export** | CSV | CSV + JSON | Full API | Real-time streaming |
| **Audit Logs** | 30 days | 90 days | 1 year | 10 years |
| **Price (per user/month)** | $5 | $12 | $25 | Custom |

### 32.4 ROI Model

| Stakeholder | Cost Saved / Value Generated | Measurement |
|---|---|---|
| Hiring Manager | 40% reduction in screening time | Skill-based matching vs resume screening |
| L&D Director | 30% higher course completion | Targeted recommendations vs blanket training |
| Employee | +15% salary growth per year | Skill-based career progression |
| Organization | 25% faster time-to-productivity | Skill-gap-driven onboarding |
| HR | 50% reduction in skills inventory admin | Automated detection vs manual surveys |
| Leadership | Org skill heatmap in real-time | Strategic workforce planning accuracy |

### 32.5 Enterprise Contract Terms

| Term | Standard | Enterprise |
|---|---|---|
| Contract Length | Monthly / Annual | 1-3 year commitment |
| Payment Terms | Net 30 | Net 60-90 |
| Data Processing Agreement | Standard | Custom (by legal) |
| Business Associate Agreement | Not available | Available (HIPAA) |
| Security Questionnaire | Standard | Custom (by security team) |
| Right to Audit | Not included | Included (annual) |
| Termination for Cause | 30 days | Negotiated |
| Data Return | CSV export | Full API access + SQL dump |
| Non-Disclosure Agreement | Optional | Required |
| Enterprise License Agreement | Not required | Custom negotiation |

---

## 33. Enterprise Change Management & Rollout

### 33.1 Organizational Change Management Framework

Enterprise skill system adoption requires deliberate change management. The framework follows the ADKAR model:

| Phase | Objective | Activities | Success Metric |
|---|---|---|---|
| Awareness | Why skills matter | Executive briefing, town halls, email campaign | >80% aware |
| Desire | Individual motivation | Personalized benefit emails, manager 1-on-1s | >60% opted in |
| Knowledge | How to use the system | Training sessions, documentation, videos | >90% trained |
| Ability | Effective daily use | Hands-on workshops, cheat sheets, support | >70% weekly active |
| Reinforcement | Long-term adoption | NPS surveys, success stories, gamification | >80% retention at 6 months |

### 33.2 Enterprise Rollout Phases

```
Phase 1: Pilot (4 weeks)
├── Select: 1-2 departments, 20-50 users
├── Activities: Executive sponsor identified, pilot team trained
├── Success Criteria: >70% adoption, >3 skills added per user
└── Decision Gate: Go/No-go for Phase 2 based on pilot results

Phase 2: Department Rollout (8 weeks)
├── Scale: 3-5 departments, 100-500 users
├── Activities: Department-level training, integration setup, feedback loops
├── Success Criteria: >60% adoption across departments, <5% support tickets
└── Decision Gate: Process adjustments based on departmental feedback

Phase 3: Organization-Wide (12 weeks)
├── Scale: All departments, all users
├── Activities: Full training program, integration rollout, communications
├── Success Criteria: >80% adoption, measurable skill growth
└── Decision Gate: Full deployment validated

Phase 4: Optimization (Ongoing)
├── Scale: Continuous improvement
├── Activities: Quarterly reviews, feature updates, advanced training
├── Success Criteria: Continuous KPI improvement
└── Decision Gate: Annual strategic review
```

### 33.3 Executive Sponsorship Requirements

| Role | Responsibilities | Time Commitment |
|---|---|---|
| Executive Sponsor | Vision setting, resource allocation, removing blockers | 2 hours/month |
| Program Champion | Day-to-day leadership, escalation handling | 8 hours/week |
| Department Leads | Department rollout, user support, feedback | 4 hours/week |
| Technical Lead | Integration, data migration, technical support | 8 hours/week |
| Change Management Lead | Communications, training, adoption tracking | Full-time during rollout |
| Data Stewards | Data quality, taxonomy, user support | 4 hours/week |

### 33.4 Enterprise Training Program

| Training Module | Audience | Format | Duration | Frequency |
|---|---|---|---|---|
| Skills System Overview | All users | Video + doc | 15 min | Onboarding |
| Adding & Managing Skills | All users | Workshop (live) | 30 min | Onboarding |
| Evidence Submission | All users | Tutorial (interactive) | 20 min | Onboarding |
| Assessments & Evaluations | All users | Workshop (live) | 45 min | Monthly |
| Manager Dashboard & Team View | Managers | Workshop (live) | 30 min | Monthly |
| Administrative Console | Admins | Hands-on training | 2 hours | Quarterly |
| Integration Configuration | IT/Tech | Technical workshop | 4 hours | Per deployment |
| Data Stewardship | Data stewards | Certification program | 8 hours | Quarterly |
| Advanced Analytics | Power users | Workshop (live) | 1 hour | Monthly |

### 33.5 Enterprise Communication Plan

| Communication | Audience | Channel | Frequency |
|---|---|---|---|
| Launch Announcement | All | Email, Slack, Intranet | Once |
| Weekly Tips | All | Slack, Email | Weekly (first 8 weeks) |
| Monthly Progress Report | Org-wide | Email, Dashboard | Monthly |
| Quarterly Business Review | Executive | Presentation | Quarterly |
| Success Stories | All | Slack, Newsletter | Monthly |
| Product Updates | All | In-app, Email | Per release |
| Training Reminders | New users | Email, In-app | Onboarding |
| Feedback Surveys | All | In-app | Quarterly |

### 33.6 Enterprise Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Low user adoption | Medium | High | Executive sponsorship, manager incentives, success stories |
| Skill inflation | High | Medium | Evidence verification, AI auditing, level calibration |
| Data quality degradation | Medium | High | Data stewardship program, automated quality checks |
| Integration failures | Low | High | Robust testing, fallback procedures, monitoring |
| Privacy/compliance breach | Low | Critical | Regular audits, encryption, access controls |
| AI recommendation bias | Medium | Medium | Ethics board, regular bias audits, transparency |
| User resistance to change | Medium | Medium | Change management program, early adopters, feedback loops |
| Taxonomy not matching org needs | Medium | Medium | Custom taxonomy support, governance flexibility |
| Vendor lock-in concern | Low | Medium | Data export, self-hosted option, open standards |
| Cost overrun | Medium | Medium | Phased rollout, clear success criteria, budget governance |

### 33.7 Enterprise Customer Success Metrics

| Phase | Success Metric | Target | Measurement |
|---|---|---|---|
| Day 7 | Onboarding completion | >80% | % completed setup wizard |
| Day 30 | First skill added | >90% | % with 1+ skills |
| Day 60 | Evidence submitted | >60% | % with evidence on 50%+ skills |
| Day 90 | Assessment taken | >40% | % with 1+ assessment |
| Quarter 1 | Regular engagement | >70% | Weekly active users |
| Quarter 2 | Career target set | >50% | % with 1+ career target |
| Quarter 3 | Income mapping used | >30% | % viewing income data |
| Quarter 4 | Organizational readiness | +20% improvement | Readiness score delta |
| Year 1 | ROI demonstrated | >3x | Value generated / cost |
| Year 2 | Platform stickiness | >90% retention | Renewal rate |

### 33.8 Enterprise Rollback Plan

| Scenario | Trigger | Response | Timeframe |
|---|---|---|---|
| Critical bug | P0 incident affecting data integrity | Rollback to last stable version, restore from backup | <4 hours |
| Integration failure | HRIS/LMS sync breaking downstream systems | Disable integration, manual sync fallback, notify IT | <2 hours |
| Performance degradation | API latency >2s for 5+ minutes | Scale resources, enable caching, throttle non-critical | <30 minutes |
| Security incident | Breach or unauthorized access | Isolate tenant, revoke tokens, forensics, notify | <15 minutes |
| User backlash | NPS < 0 or >15% support tickets | Pause rollout, gather feedback, adjust approach | <1 week |

## Appendix A: Codebase Mapping

This section maps the Skills System architecture to the existing Second Brain OS codebase conventions and components.

### A.1 AGENTS.md Alignment

| AGENTS.md Convention | Skills System Implementation |
|---|---|
| PromptLoader for all prompts | Skills use prompts/skills/ directory with YAML frontmatter |
| Graceful degradation | Every skill has algorithmic fallback if prompt unavailable |
| In-process agents | Skills execute as async functions within FastAPI |
| Supabase as source of truth | All skill data stored in Supabase with RLS |
| Filter by user_id | Every skill query filtered by auth.uid() |
| Pre-commit validation | scripts/validate_skills.py validates skill configurations |

### A.2 PromptLoader Integration

The existing PromptLoader (packages/ai/prompt_loader.py) will be extended:

| Current | Extension |
|---|---|
| System prompts (prompts/system/) | Skills prompts (prompts/skills/) |
| Agent prompts (prompts/agents/) | Per-skill prompt files |
| Template prompts (prompts/templates/) | Assessment templates, recommendation templates |
| get_system(), get_agent(), get_template() | New: get_skill(skill_name) method |
| PromptEntry: system_prompt, agent_prompt | New: skill_prompt, assessment_prompt, recommendation_prompt |

### A.3 Agent Integration

| Existing Agent | Skills System Role |
|---|---|
| Briefing Agent (A09) | Includes skill progress in daily briefings |
| Memory Agent (A02) | Stores skill acquisitions as memory entries |
| Learning Agent (A03) | Suggests courses based on skill gaps |
| Opportunity Agent (A06) | Uses skill match scoring (already implemented) |
| Weekly Review Agent (A10) | Reports skill progress in weekly reviews |
| Sleep Agent (A13) | Sleep-aware skill scheduling (heavy vs light skill tasks) |
| Nudge Agent (A14) | Course progress nudges linked to skill targets |

### A.4 New Agents Required

| Agent | Purpose |
|---|---|
| Skill Intelligence Agent | Market intelligence, trend analysis, demand scoring |
| Skill Recommendation Agent | AI recommendations for skill development |
| Skill Assessment Agent | Automated skill evaluation and scoring |
| Career Intelligence Agent | Career readiness, gap analysis, roadmap generation |

### A.5 Database Schema Evolution

| Current | Evolved |
|---|---|
| users_profile.skills (JSONB array) | user_skills (normalized table) |
| No skill evidence table | user_skill_evidence (dedicated table) |
| No skill market data | skill_market_data (dedicated table) |
| opportunities.skills_required (TEXT[]) | skill_opportunities (junction table) |
| No skill versioning | skill_audit_log (append-only) |

### A.6 Prompt Files (Required New)

| Prompt File | Purpose | Location |
|---|---|---|
| skill_assessment.md | AI skill evaluation prompts | prompts/skills/ |
| skill_recommendation.md | Skill recommendation generation | prompts/skills/ |
| skill_market_analysis.md | Market intelligence analysis | prompts/skills/ |
| career_readiness.md | Career readiness assessment | prompts/skills/ |

### A.7 API Router

New router file: apps/api/app/api/skills.py
Registration: app.include_router(skills_router, prefix="/api/skills", tags=["skills"])

### A.8 Test Files (Required New)

| Test File | Purpose |
|---|---|
| tests/test_skills_api.py | API endpoint testing |
| tests/test_skill_assessment.py | Assessment logic testing |
| tests/test_skill_market.py | Market intelligence testing |
| tests/test_skill_recommendations.py | Recommendation logic testing |

### A.9 Migration Path

```
Phase 1: Create normalized tables + API CRUD endpoints + basic UI list view
         Keep legacy users_profile.skills JSONB synced during migration

Phase 2: Add evidence framework + assessment system + market intelligence
         New prompt files + agent modules

Phase 3: Full recommendation engine + career intelligence + income mapping
         Tree/graph views + analytics dashboards

Phase 4: Ecosystem integrations + team features + marketplace
         Open taxonomy + third-party connections
```

---

## Appendix B: Glossary

| Term | Definition |
|---|---|
| Skill | A structured representation of demonstrated or aspirational capability in a defined domain |
| Skill Taxonomy | The hierarchical classification system for all skills |
| Skill Level | Proficiency rating from L0 (Unknown) to L5 (Expert) |
| Skill State | Current lifecycle stage (planned, learning, practicing, active, etc.) |
| Skill Evidence | Verifiable proof of skill capability (project, cert, work, etc.) |
| Skill Assessment | Formal evaluation of skill proficiency |
| Skill Tree | Hierarchical view of skill relationships and dependencies |
| Skill Graph | Full network of user skills with all relationships |
| Skill Cluster | Automatically detected group of related skills |
| Skill Pathway | Curated learning sequence to reach a target skill |
| Skill Dependency | Prerequisite relationship between skills |
| Skill Gap | Difference between current and target proficiency |
| Confidence Score | System certainty about skill level assessment (0-1) |
| Evidence Score | Aggregate quality of all evidence (0-1) |
| Market Intelligence | Data about skill demand, growth, salary, and competition |
| Career Readiness | Overall preparedness for a specific career target |
| Learning Velocity | Rate of skill level gain over time |
| Income Potential | Projected earnings from a skill across income sources |
| Agent Capability | A skill that ARIA (the AI assistant) possesses |
| Skill Passport | Portable, verifiable export of a user complete skill graph |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-06-12 | AI Agent | Initial enterprise architecture document (28 sections) |
| 2.0.0 | 2026-06-12 | AI Agent | Added enterprise depth: Governance & Compliance (Sec 29), Integration Patterns (Sec 30), Multi-Tenant Architecture (Sec 31), SLAs/KPIs/Pricing (Sec 32), Change Management & Rollout (Sec 33) |

*End of Document*
