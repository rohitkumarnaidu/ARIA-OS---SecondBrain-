# Database Documentation Index

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-DB-001 |
| **Version** | 2.0.0 |
| **Status** | Active |
| **Date** | 2026-07-11 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Review Cycle** | Monthly |

---

## Purpose

This file was formerly the monolithic **Database Schema** reference (1,168 lines, v1). It has been split into 12 focused guides covering every database concern. This index page serves as the entry point for navigating all database documentation.

The original v1 content is preserved in git history (`git log --follow docs/engineering/15_Database.md`).

---

## Canonical Docs

| # | Document | Document ID | Description |
|---|----------|-------------|-------------|
| 1 | [Schema.md](Schema.md) | ENG-SCH-001 | Complete column-level schema for all 27 tables |
| 2 | [ERD.md](ERD.md) | ENG-ERD-001 | Entity-relationship diagram with cardinalities |
| 3 | [Indexes.md](Indexes.md) | ENG-IDX-002 | Index strategy, partial indexes, GIN/FTS indexes |
| 4 | [Constraints.md](Constraints.md) | ENG-CON-003 | CHECK, UNIQUE, NOT NULL, FK constraint catalog |
| 5 | [Views.md](Views.md) | ENG-VWS-004 | Database views for reporting and aggregation |
| 6 | [MaterializedViews.md](MaterializedViews.md) | ENG-MVW-005 | Materialized view refresh strategy and usage |
| 7 | [Triggers.md](Triggers.md) | ENG-TRG-006 | Trigger functions for audit, timestamps, validation |
| 8 | [Functions.md](Functions.md) | ENG-FNC-007 | PL/pgSQL functions for business logic |
| 9 | [Policies.md](Policies.md) | ENG-POL-008 | RLS policy catalog for all tables |
| 10 | [RLS.md](RLS.md) | ENG-RLS-009 | RLS deep dive: policies, performance, edge cases |
| 11 | [BackupStrategy.md](BackupStrategy.md) | ENG-BAK-010 | Backup schedule, point-in-time recovery, restore playbook |
| 12 | [MigrationStrategy.md](MigrationStrategy.md) | ENG-MIG-011 | Migration workflow, naming conventions, rollback process |

---

## Quick Reference

- **Tables**: 27 tables across 15 modules, all with RLS enabled
- **Database**: Supabase PostgreSQL with Realtime + pg_cron
- **Auth**: All tables filtered by `auth.uid() = user_id` (enforced at DB, API, and service layers)
- **Related**: [Architecture](12_Architecture.md) Â§ Component Responsibilities â†’ Database, [AGENTS.md Â§7](/AGENTS.md) â†’ Schema overview
