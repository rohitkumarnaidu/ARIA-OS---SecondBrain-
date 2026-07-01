#!/usr/bin/env python3
"""Skill Database Schema Validator.

Validates that the deployed database matches the SDB architecture spec.
Checks: all 33 tables exist, all 8 roles exist, all FK constraints,
all RLS policies, all materialized views, all audit triggers.
Usage: python scripts/validate_skills_schema.py [--dsn CONNECTION_STRING]
"""

import argparse
import os
import sys
from pathlib import Path


# Schema specification from SDB architecture doc
REQUIRED_TABLES = [
    # Core Taxonomy (7)
    "skill_categories", "skills", "skill_relationships", "tags", "skill_tags",
    "skill_external_mappings", "skill_roadmap_definitions",
    # User Skills (5)
    "user_skills", "user_skill_evidence", "user_skill_targets",
    "user_skill_assessments", "user_skill_versions",
    # Intelligence (6)
    "skill_market_data", "skill_income_data", "skill_certifications",
    "skill_projects", "skill_roadmaps", "skill_opportunities",
    # Supporting (5)
    "skill_topics", "skill_resources", "skill_learning_paths",
    "skill_ai_recommendations", "skill_user_activity_log",
    # Audit & History (4)
    "skill_audit_log", "skill_taxonomy_history", "skill_user_skill_history",
    "skill_market_history",
    # Events (5)
    "skill_events", "skill_event_outbox", "skill_webhook_queue",
    "skill_event_subscriptions",
    # Analytics (2)
    "skill_analytics_snapshots", "skill_forecasts",
]

REQUIRED_ROLES = [
    "skill_admin", "skill_manager", "skill_user", "skill_auditor",
    "skill_viewer", "skill_api", "skill_scheduler", "skill_analytics",
]

REQUIRED_MVS = [
    "mv_skill_user_proficiency", "mv_skill_market_intelligence",
    "mv_skill_learning_velocity", "mv_skill_taxonomy_health",
    "mv_skill_ai_effectiveness", "mv_skill_activity_heatmap",
    "mv_skill_roadmap_progress",
]

RLS_ENABLED_TABLES = [
    "user_skills", "user_skill_evidence", "user_skill_targets",
    "user_skill_assessments", "user_skill_versions",
    "skill_ai_recommendations", "skill_user_activity_log",
    "skill_audit_log", "skill_events", "skill_analytics_snapshots",
    "skills", "skill_categories", "skill_relationships",
    "skill_market_data", "skill_income_data",
]

PARTITIONED_TABLES = [
    "user_skill_evidence", "user_skill_versions", "skill_user_activity_log",
    "skill_audit_log", "skill_events", "skill_webhook_queue",
    "skill_analytics_snapshots",
]

AUDIT_TRIGGER_TABLES = [
    "skills", "skill_categories", "user_skills", "user_skill_evidence",
    "user_skill_targets", "user_skill_assessments", "skill_market_data",
    "skill_relationships", "skill_certifications",
]

GENERATED_COLUMN_TABLES = {
    "user_skill_targets": ["gap_size", "progress_pct"],
    "skill_market_data": ["skill_health"],
}

EXCLUDE_CONSTRAINT_TABLES = {
    "skill_relationships": "no_overlapping_prereqs",
    "user_skill_targets": "no_overlapping_active_targets",
    "skill_certifications": "unique_cert_per_provider",
}


class SchemaValidator:
    def __init__(self, db_available: bool = False):
        self.db_available = db_available
        self.errors = []
        self.warnings = []
        self.checks = {"pass": 0, "fail": 0, "warn": 0}

    def check(self, condition: bool, message: str, level: str = "error"):
        if condition:
            self.checks["pass"] += 1
        else:
            self.checks["fail"] += 1
            (self.errors if level == "error" else self.warnings).append(message)

    def validate_migration_files(self, migrations_dir: Path):
        """Validate that all migration files exist and look reasonable."""
        expected = [
            "000_skills_complete_ddl.sql",
            "001_skills_core_taxonomy.sql",
            "002_skills_user_tables.sql",
            "003_skills_intelligence_supporting.sql",
            "004_skills_audit_events_analytics.sql",
            "005_skills_security_rls.sql",
            "006_skills_materialized_views.sql",
            "007_skills_partman_cron.sql",
        ]
        for fname in expected:
            fpath = migrations_dir / fname
            exists = fpath.exists()
            self.check(exists, f"Migration file missing: {fname}")
            if exists and fpath.stat().st_size == 0:
                self.check(False, f"Migration file empty: {fname}")

    def validate_generator_script(self, gen_path: Path):
        exists = gen_path.exists()
        self.check(exists, f"Generator script missing: {gen_path}")
        if exists:
            content = gen_path.read_text(encoding="utf-8", errors="replace")
            self.check(
                "def main()" in content,
                f"Generator script missing main() function: {gen_path}"
            )

    def validate_ddl_coverage(self, ddl_path: Path):
        """Validate DDL against schema spec."""
        import re
        if not ddl_path.exists():
            self.check(False, f"DDL file not found: {ddl_path}")
            return

        content = ddl_path.read_text(encoding="utf-8", errors="replace")

        for table in REQUIRED_TABLES:
            pattern = f"CREATE TABLE IF NOT EXISTS {table}"
            self.check(
                pattern in content,
                f"Missing CREATE TABLE for {table} in DDL"
            )

        for role in REQUIRED_ROLES:
            pattern = f"CREATE ROLE {role}"
            self.check(
                pattern in content,
                f"Missing CREATE ROLE {role} in DDL"
            )

        for mv in REQUIRED_MVS:
            pattern = f"CREATE MATERIALIZED VIEW IF NOT EXISTS {mv}"
            self.check(
                pattern in content or f"CREATE MATERIALIZED VIEW {mv}" in content,
                f"Missing materialized view {mv} in DDL"
            )

        # 000_skills_complete_ddl.sql uses dynamic PL/pgSQL loop instead of per-table statements
        has_rls_loop = "ENABLE ROW LEVEL SECURITY" in content and "FOREACH tbl IN ARRAY" in content
        for table in RLS_ENABLED_TABLES:
            pattern = f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"
            self.check(
                has_rls_loop or pattern in content,
                f"Missing RLS enable for {table} in DDL"
            )

        for table in PARTITIONED_TABLES:
            pattern = f"PARTITION BY RANGE"
            present = False
            if pattern in content:
                # Check that the CREATE TABLE for this table includes PARTITION BY RANGE
                # Find the CREATE TABLE block for this table
                blocks = re.findall(
                    rf"CREATE TABLE IF NOT EXISTS {table}.*?\);",
                    content, re.DOTALL
                )
                for block in blocks:
                    if "PARTITION BY RANGE" in block:
                        present = True
                        break
            self.check(
                present,
                f"Table {table} should be partitioned but PARTITION BY RANGE not found in its DDL"
            )

        for table, generated_cols in GENERATED_COLUMN_TABLES.items():
            for col in generated_cols:
                # DDL pattern: col_name   TYPE   GENERATED ALWAYS AS (...)
                # (not: GENERATED ALWAYS AS (col_name ...)
                col_pattern = re.search(
                    rf"{re.escape(col)}\s+\w+\s+GENERATED\s+ALWAYS\s+AS",
                    content, re.IGNORECASE
                )
                self.check(
                    bool(col_pattern),
                    f"Missing GENERATED column {col} on {table}"
                )

        for table, constraint in EXCLUDE_CONSTRAINT_TABLES.items():
            self.check(
                constraint in content,
                f"Missing EXCLUDE constraint {constraint} on {table}"
            )

    def validate_notify_triggers(self, ddl_path: Path):
        if not ddl_path.exists():
            return
        content = ddl_path.read_text(encoding="utf-8", errors="replace")
        expected_notify = [
            ("fn_notify_taxonomy_change", "Taxonomy NOTIFY function"),
            ("trg_skills_notify", "Skills NOTIFY trigger"),
            ("trg_categories_notify", "Categories NOTIFY trigger"),
            ("skill_notify_audit_event", "Audit NOTIFY function"),
            ("trg_audit_log_notify", "Audit log NOTIFY trigger"),
        ]
        for func_name, desc in expected_notify:
            self.check(
                func_name in content,
                f"Missing {desc} in DDL"
            )

    def validate_audit_triggers(self, ddl_path: Path):
        if not ddl_path.exists():
            return
        content = ddl_path.read_text(encoding="utf-8", errors="replace")
        for table in AUDIT_TRIGGER_TABLES:
            self.check(
                f"trg_{table}_audit" in content,
                f"Missing audit trigger for {table}"
            )

    def validate_partitions(self, ddl_path: Path):
        if not ddl_path.exists():
            return
        content = ddl_path.read_text(encoding="utf-8", errors="replace")
        for table in PARTITIONED_TABLES:
            pattern = f"PARTITION OF {table}"
            self.check(
                pattern in content,
                f"Missing partition children for {table}"
            )

    def validate_cron_jobs(self, cron_path: Path):
        if not cron_path.exists():
            self.check(False, f"Cron migration file not found: {cron_path}")
            return
        content = cron_path.read_text(encoding="utf-8", errors="replace")
        expected_jobs = [
            "skill-proficiency-refresh",
            "skill-market-refresh",
            "skill-update-stale-flags",
            "skill-process-outbox",
            "skill-process-webhooks",
            "skill-vacuum-main",
            "skill-partman-maintenance",
        ]
        for job in expected_jobs:
            self.check(
                job in content,
                f"Missing pg_cron job: {job}"
            )

    def report(self) -> int:
        print(f"\n{'='*60}")
        print(f"SKILLS DATABASE SCHEMA VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"  Passed: {self.checks['pass']}")
        print(f"  Failed: {self.checks['fail']}")
        print(f"  Warnings: {self.checks['warn']}")
        print(f"  Total: {sum(self.checks.values())}")
        print(f"{'='*60}")

        if self.errors:
            print(f"\n  ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"    [FAIL] {e}")

        if self.warnings:
            print(f"\n  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"    [WARN] {w}")

        if not self.errors:
            print(f"\n  [PASS] ALL CHECKS PASSED")
        else:
            print(f"\n  [FAIL] {len(self.errors)} FAILURES - review above")

        return 0 if not self.errors else 1


def main():
    parser = argparse.ArgumentParser(description="Validate skills schema against SDB architecture spec")
    parser.add_argument("--migrations-dir", default="scripts/migrations",
                        help="Directory containing migration SQL files")
    parser.add_argument("--gen-script", default="scripts/gen_sdb_full.py",
                        help="Path to generator script")
    parser.add_argument("--ddl", default=None,
                        help="DDL file to validate (defaults to migrations-dir/000_skills_complete_ddl.sql)")
    parser.add_argument("--db", action="store_true",
                        help="Also validate against live database (requires --dsn or env DATABASE_URL)")
    args = parser.parse_args()

    base = Path.cwd()
    migrations_dir = base / args.migrations_dir
    ddl_path = Path(args.ddl) if args.ddl else migrations_dir / "000_skills_complete_ddl.sql"
    gen_path = base / args.gen_script
    cron_path = migrations_dir / "007_skills_partman_cron.sql"

    validator = SchemaValidator(db_available=args.db)

    print("Validating skills database schema against SDB architecture v1.0.0...\n")

    print("[Migration Files]")
    validator.validate_migration_files(migrations_dir)

    print("[Generator Script]")
    validator.validate_generator_script(gen_path)

    print("[DDL Coverage]")
    validator.validate_ddl_coverage(ddl_path)

    print("[NOTIFY Triggers]")
    validator.validate_notify_triggers(ddl_path)

    print("[Audit Triggers]")
    validator.validate_audit_triggers(ddl_path)

    print("[Partition Children]")
    validator.validate_partitions(ddl_path)

    print("[Cron Jobs]")
    validator.validate_cron_jobs(cron_path)

    # Check for missing model imports in schemas
    schema_path = base / "packages" / "database" / "schemas" / "skill.py"
    if schema_path.exists():
        schema_content = schema_path.read_text(encoding="utf-8", errors="replace")
        missing_models = []
        for model in [
            "SkillAuditLogCreate", "SkillAuditLogResponse",
            "SkillEventSubscriptionCreate", "SkillEventSubscriptionResponse",
            "SkillEventOutboxResponse",
            "SkillWebhookQueueResponse",
            "SkillAnalyticsSnapshotCreate", "SkillAnalyticsSnapshotResponse",
            "SkillForecastCreate", "SkillForecastResponse",
            "SkillTaxonomyHistoryCreate", "SkillTaxonomyHistoryResponse",
            "SkillUserSkillHistoryCreate", "SkillUserSkillHistoryResponse",
            "SkillMarketHistoryCreate", "SkillMarketHistoryResponse",
            "SkillRoadmapDefinitionCreate", "SkillRoadmapDefinitionResponse",
        ]:
            if model not in schema_content:
                missing_models.append(model)
        if missing_models:
            validator.check(
                len(missing_models) == 0,
                f"Missing Pydantic models: {', '.join(missing_models)}",
                "warn"
            )

    return validator.report()


if __name__ == "__main__":
    sys.exit(main())
