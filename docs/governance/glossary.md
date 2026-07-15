# Project Glossary

## Document Control

| Field | Value |
|---|---|
| Document ID | GOV-GLO-001 |
| Version | 1.0.0 |
| Status | Active |
| Date | 2026-07-12 |
| Classification | Internal |
| Owner | Developer |

---

## A-C

| Term | Definition |
|---|---|
| ADR | Architecture Decision Record — documents a significant architectural choice with context, decision, and consequences |
| ARIA | AI Reasoning & Intelligent Assistant — the orchestrator agent that routes user requests to sub-agents |
| C4 Model | Context, Container, Component, Code — hierarchical approach to software architecture diagrams |
| CORS | Cross-Origin Resource Sharing — browser security mechanism for controlling cross-origin requests |
| CSP | Content Security Policy — HTTP header that prevents XSS and data injection attacks |
| CSRF | Cross-Site Request Forgery — attack that tricks authenticated users into performing unintended actions |

## D-H

| Term | Definition |
|---|---|
| DAST | Dynamic Application Security Testing — detects vulnerabilities by probing a running application |
| DPIA | Data Protection Impact Assessment — GDPR-mandated risk assessment for high-risk data processing |
| DREAD | Damage, Reproducibility, Exploitability, Affected Users, Discoverability — threat risk rating model |
| GDPR | General Data Protection Regulation — EU regulation for data protection and privacy |
| HSTS | HTTP Strict Transport Security — enforces HTTPS connections to prevent downgrade attacks |

## J-M

| Term | Definition |
|---|---|
| JWT | JSON Web Token — compact URL-safe token format used for authentication |
| LLM | Large Language Model — AI model powering ARIA and all sub-agents |
| MCP | Model Context Protocol — protocol for LLMs to interact with external tools and services |

## P-R

| Term | Definition |
|---|---|
| P0-P4 | Severity levels: P0=Critical, P1=High, P2=Medium, P3=Low, P4=Wishlist |
| PITR | Point-in-Time Recovery — database restoration to any point within a retention window |
| PWA | Progressive Web App — web application with native app-like capabilities |
| RAG | Retrieval-Augmented Generation — combining LLM generation with retrieved context |
| RED Metrics | Rate, Errors, Duration — the three key pillars of service monitoring |
| RLS | Row-Level Security — Supabase feature that restricts row access per user |
| RPO | Recovery Point Objective — maximum acceptable data loss in a disaster |
| RTO | Recovery Time Objective — maximum acceptable downtime in a disaster |

## S-Z

| Term | Definition |
|---|---|
| SAST | Static Application Security Testing — analyzes source code for vulnerabilities without execution |
| SBOM | Software Bill of Materials — inventory of all software components and dependencies |
| SDL | Security Development Lifecycle — security practices integrated into the development process |
| SLI | Service Level Indicator — quantitative measure of a service property (e.g., latency, error rate) |
| SLO | Service Level Objective — target value for an SLI over a measurement window |
| SOC 2 | Service Organization Control 2 — auditing standard for service providers' data security controls |
| STRIDE | Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege — threat classification model |
| XSS | Cross-Site Scripting — injection attack that executes malicious scripts in a user's browser |

---

## Related Documents

| Document | Purpose |
|---|---|
| [AGENTS.md](../../AGENTS.md) | Master project reference — complete system documentation |
| [Security Architecture](../security/24_Security.md) | Enterprise security architecture with security glossary (Appendix D) |
| [SDL](../security/sdl.md) | Secure Development Lifecycle — security methodology reference |
| [KPI Dashboard](../product/KPI-dashboard.md) | Project health metrics and documentation maturity tracking |
| [Error Budget](../operations/error-budget.md) | SLO definitions and service level terminology |

> **Duplicate note:** A product-level glossary exists at [`docs/product/Glossary.md`](../product/Glossary.md) covering product, feature, and domain-specific terms (e.g., module names, agent IDs, ARIA-specific concepts). This governance glossary focuses on project management, operations, compliance, and technical infrastructure terms. Cross-reference for a complete terminology mapping.
