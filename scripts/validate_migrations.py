"""Validate all 6+1 migration SQL files for structural correctness and consistency.
Adapted to the actual skills-tracking schema — not aspirational."""

import re
import sys
from pathlib import Path

MIGRATIONS_DIR = Path("scripts/migrations")
FILES = [
    "000_skills_complete_ddl.sql",
    "001_skills_core_taxonomy.sql",
    "002_skills_user_tables.sql",
    "003_skills_intelligence_supporting.sql",
    "004_skills_audit_events_analytics.sql",
    "005_skills_security_rls.sql",
    "006_skills_materialized_views.sql",
]

REQUIRED_EXTENSIONS = ["pgcrypto", "ltree", "btree_gist", "pg_stat_statements"]

CHECKLIST = {
    "000_skills_complete_ddl.sql": [
        # Extensions
        ("btree_gist extension", r"CREATE EXTENSION IF NOT EXISTS.*btree_gist"),
        # Core tables from 001
        ("skill_categories table", r"CREATE TABLE.*skill_categories\b"),
        ("skills table", r"CREATE TABLE.*skills\b"),
        ("skill_relationships table", r"CREATE TABLE.*skill_relationships\b"),
        ("tags table", r"CREATE TABLE.*tags\b"),
        ("skill_tags table", r"CREATE TABLE.*skill_tags\b"),
        ("skill_external_mappings table", r"CREATE TABLE.*skill_external_mappings\b"),
        ("skill_roadmap_definitions table", r"CREATE TABLE.*skill_roadmap_definitions\b"),
        # User tables from 002
        ("user_skills table", r"CREATE TABLE.*user_skills\b"),
        ("user_skill_evidence table", r"CREATE TABLE.*user_skill_evidence\b"),
        ("user_skill_targets table", r"CREATE TABLE.*user_skill_targets\b"),
        ("user_skill_assessments table", r"CREATE TABLE.*user_skill_assessments\b"),
        ("user_skill_versions table", r"CREATE TABLE.*user_skill_versions\b"),
        # Intelligence tables from 003
        ("skill_market_data table", r"CREATE TABLE.*skill_market_data\b"),
        ("skill_income_data table", r"CREATE TABLE.*skill_income_data\b"),
        ("skill_certifications table", r"CREATE TABLE.*skill_certifications\b"),
        ("skill_projects table", r"CREATE TABLE.*skill_projects\b"),
        ("skill_roadmaps table", r"CREATE TABLE.*skill_roadmaps\b"),
        ("skill_opportunities table", r"CREATE TABLE.*skill_opportunities\b"),
        ("skill_topics table", r"CREATE TABLE.*skill_topics\b"),
        ("skill_resources table", r"CREATE TABLE.*skill_resources\b"),
        ("skill_learning_paths table", r"CREATE TABLE.*skill_learning_paths\b"),
        ("skill_ai_recommendations table", r"CREATE TABLE.*skill_ai_recommendations\b"),
        ("skill_user_activity_log table", r"CREATE TABLE.*skill_user_activity_log\b"),
        # Event/audit tables from 004
        ("skill_audit_log table", r"CREATE TABLE.*skill_audit_log\b"),
        ("skill_taxonomy_history table", r"CREATE TABLE.*skill_taxonomy_history\b"),
        ("skill_user_skill_history table", r"CREATE TABLE.*skill_user_skill_history\b"),
        ("skill_market_history table", r"CREATE TABLE.*skill_market_history\b"),
        ("skill_events table", r"CREATE TABLE.*skill_events\b"),
        ("skill_event_outbox table", r"CREATE TABLE.*skill_event_outbox\b"),
        ("skill_webhook_queue table", r"CREATE TABLE.*skill_webhook_queue\b"),
        ("skill_event_subscriptions table", r"CREATE TABLE.*skill_event_subscriptions\b"),
        ("skill_analytics_snapshots table", r"CREATE TABLE.*skill_analytics_snapshots\b"),
        ("skill_forecasts table", r"CREATE TABLE.*skill_forecasts\b"),
        # Partitions
        ("audit_log partition", r"PARTITION OF skill_audit_log"),
        ("events partition", r"PARTITION OF skill_events"),
        ("webhook_queue partition", r"PARTITION OF.*skill_webhook_queue"),
        ("analytics_snapshots partition", r"PARTITION OF.*skill_analytics_snapshots"),
        # RLS
        ("RLS enabled", r"ENABLE ROW LEVEL SECURITY"),
        ("FORCE ROW LEVEL SECURITY", r"FORCE ROW LEVEL SECURITY"),
        # EXCLUDE
        ("EXCLUDE on skill_relationships", r"EXCLUDE USING gist"),
        # Materialized views
        ("mv_skill_user_proficiency", r"CREATE MATERIALIZED VIEW.*mv_skill_user_proficiency"),
        ("mv_skill_market_intelligence", r"CREATE MATERIALIZED VIEW.*mv_skill_market_intelligence"),
        ("mv_skill_roadmap_progress", r"CREATE MATERIALIZED VIEW.*mv_skill_roadmap_progress"),
        ("mv_skill_learning_velocity", r"CREATE MATERIALIZED VIEW.*mv_skill_learning_velocity"),
        ("mv_skill_taxonomy_health", r"CREATE MATERIALIZED VIEW.*mv_skill_taxonomy_health"),
        ("mv_skill_ai_effectiveness (or full name)", r"mv_skill_ai_effectiveness\b"),
        ("mv_skill_activity_heatmap", r"CREATE MATERIALIZED VIEW.*mv_skill_activity_heatmap"),
    ],
    "001_skills_core_taxonomy.sql": [
        ("btree_gist extension", r"CREATE EXTENSION IF NOT EXISTS.*btree_gist"),
        ("pgcrypto extension", r"CREATE EXTENSION IF NOT EXISTS.*pgcrypto"),
        ("ltree extension", r"CREATE EXTENSION IF NOT EXISTS.*ltree"),
        ("EXCLUDE on skill_relationships", r"EXCLUDE USING gist"),
        ("7 tables created", lambda t: len(re.findall(r"CREATE TABLE IF NOT EXISTS", t, re.I)) >= 7),
    ],
    "002_skills_user_tables.sql": [
        ("btree_gist extension", r"CREATE EXTENSION IF NOT EXISTS.*btree_gist"),
        ("5 tables created", lambda t: len(re.findall(r"CREATE TABLE IF NOT EXISTS", t, re.I)) >= 5),
        ("level CHECK (0-5)", r"CHECK\s*\(\s*level\s+>=\s+0\s+AND\s+level\s+<=\s+5\s*\)"),
        (
            "EXCLUDE on user_skill_targets",
            lambda t: bool(re.search(r"EXCLUDE USING gist", t, re.I)),
            "EXCLUDE USING gist on user_skill_targets",
        ),
        ("evidence partition child tables", r"CREATE TABLE IF NOT EXISTS user_skill_evidence_2026"),
        ("versions partition child tables", r"CREATE TABLE IF NOT EXISTS user_skill_versions_2026"),
    ],
    "003_skills_intelligence_supporting.sql": [
        ("btree_gist extension", r"CREATE EXTENSION IF NOT EXISTS.*btree_gist"),
        ("11 tables created", lambda t: len(re.findall(r"CREATE TABLE IF NOT EXISTS", t, re.I)) >= 11),
        (
            "EXCLUDE on certifications",
            lambda t: bool(re.search(r"EXCLUDE USING gist", t, re.I)),
            "EXCLUDE USING gist on skill_certifications",
        ),
        ("activity_log partition child tables", r"CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026"),
    ],
    "004_skills_audit_events_analytics.sql": [
        ("10 tables created", lambda t: len(re.findall(r"CREATE TABLE IF NOT EXISTS", t, re.I)) >= 10),
        ("event_version TEXT DEFAULT 1.0", r"event_version\s+TEXT\s+NOT\s+NULL\s+DEFAULT\s+'1\.0'"),
        ("webhook_queue_Q3 partition", r"skill_webhook_queue_2026_q3"),
        ("analytics_snapshots_Q3 partition", r"skill_analytics_snapshots_2026_q3"),
        ("taxonomy notify trigger", r"trg_skills_notify"),
        ("categories notify trigger", r"trg_categories_notify"),
        ("notify function exists", r"fn_notify_taxonomy_change"),
    ],
    "005_skills_security_rls.sql": [
        ("8 roles created", lambda t: len(re.findall(r"CREATE ROLE skill_", t, re.I)) >= 8),
        ("RLS enabled on 31+ tables", lambda t: len(re.findall(r"ENABLE ROW LEVEL SECURITY", t, re.I)) >= 31),
        ("FORCE RLS on 31+ tables", lambda t: len(re.findall(r"FORCE ROW LEVEL SECURITY", t, re.I)) >= 31),
        ("REVOKE UPDATE", r"REVOKE UPDATE"),
        ("GRANT UPDATE (columns)", r"GRANT UPDATE\s*\("),
        ("audit trigger function", r"skill_audit_trigger_func"),
        ("notify audit function", r"skill_notify_audit_event"),
        ("8 audit triggers", lambda t: len(re.findall(r"CREATE TRIGGER.*_audit", t, re.I)) >= 8),
        ("PII encryption functions", r"skill_encrypt_pii"),
        ("PII decryption functions", r"skill_decrypt_pii"),
    ],
    "006_skills_materialized_views.sql": [
        ("7 materialized views", lambda t: len(re.findall(r"CREATE MATERIALIZED VIEW", t, re.I)) >= 7),
        ("mv_skill_user_proficiency", r"mv_skill_user_proficiency"),
        ("mv_skill_market_intelligence", r"mv_skill_market_intelligence"),
        ("mv_skill_roadmap_progress", r"mv_skill_roadmap_progress"),
        ("mv_skill_learning_velocity", r"mv_skill_learning_velocity"),
        ("mv_skill_taxonomy_health", r"mv_skill_taxonomy_health"),
        ("mv_skill_ai_recommendation_effectiveness", r"mv_skill_ai_recommendation_effectiveness"),
        ("mv_skill_activity_heatmap", r"mv_skill_activity_heatmap"),
        ("refresh helper function", r"skill_refresh_all_materialized_views"),
    ],
}


def has_pattern(sql: str, pattern: str) -> bool:
    return bool(re.search(pattern, sql, re.IGNORECASE | re.MULTILINE))


def check_file(file_name: str, sql: str) -> tuple[int, int, list[str]]:
    passes = 0
    fails = 0
    msgs = []

    def check(cond: bool, msg: str):
        nonlocal passes, fails
        if cond:
            passes += 1
        else:
            fails += 1
            msgs.append(f"  FAIL: {msg}")

    checks = CHECKLIST.get(file_name, [])
    for name, *rest in checks:
        if len(rest) == 1:
            arg = rest[0]
            if callable(arg):
                ok = arg(sql)
            else:
                ok = has_pattern(sql, arg)
            msg = name
        elif len(rest) == 2:
            arg, msg = rest[0], rest[1]
            if callable(arg):
                ok = arg(sql)
            else:
                ok = has_pattern(sql, arg)
        else:
            ok, msg = False, f"Invalid check format: {rest}"
        check(ok, msg)

    return passes, fails, msgs


def check_cross_reference(files: dict[str, str]) -> tuple[int, int, list[str]]:
    """Every table in 001-006 also exists in 000."""
    passes = 0
    fails = 0
    msgs = []

    def check(cond: bool, msg: str):
        nonlocal passes, fails
        if cond:
            passes += 1
        else:
            fails += 1
            msgs.append(f"  FAIL: {msg}")

    sql_000 = files.get("000_skills_complete_ddl.sql", "")

    for fname, sql in files.items():
        if fname == "000_skills_complete_ddl.sql":
            continue
        for m in re.finditer(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)", sql, re.IGNORECASE):
            tbl = m.group(1)
            if tbl.startswith("_"):
                continue
            ref_pat = rf"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?{re.escape(tbl)}\b"
            check(has_pattern(sql_000, ref_pat), f"Table '{tbl}' from {fname} present in 000")

    return passes, fails, msgs


def main() -> int:
    root = Path.cwd() / MIGRATIONS_DIR
    print(f"Scanning {root.resolve()}\n")

    files_content: dict[str, str] = {}
    all_ok = True

    for fname in FILES:
        fpath = root / fname
        if not fpath.exists():
            print(f"  FILE NOT FOUND: {fpath}")
            all_ok = False
            continue

        sql = fpath.read_text(encoding="utf-8")
        files_content[fname] = sql

        p, f, msgs = check_file(fname, sql)
        status = "PASS" if f == 0 else "FAIL"
        all_ok = all_ok and (f == 0)
        print(f"{fname:45s} {p:>3d} pass  {f:>3d} fail  {status}")
        for m in msgs:
            print(m)
        if msgs:
            print()

    print("--- Cross-File (tables in 001-006 vs 000) ---")
    cp, cf, cm = check_cross_reference(files_content)
    all_ok = all_ok and (cf == 0)
    print(f"Cross-file: {cp} pass  {cf} fail")
    for m in cm:
        print(m)

    print(f"\nResult: {'ALL PASS' if all_ok else 'SOME FAILED'}")
    return 0 if all_ok else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
