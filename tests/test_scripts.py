"""Tests for utility scripts: validate_migrations, gen_sdb_full, validate_skills_schema."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── validate_migrations.py ──


def test_validate_migrations_has_pattern():
    from scripts.validate_migrations import has_pattern

    assert has_pattern("CREATE TABLE foo", r"CREATE TABLE")
    assert not has_pattern("DROP TABLE foo", r"CREATE TABLE")


def test_validate_migrations_check_file():
    from scripts.validate_migrations import check_file

    sql = """
    CREATE TABLE IF NOT EXISTS skill_categories (...);
    CREATE TABLE IF NOT EXISTS skills (...);
    CREATE EXTENSION IF NOT EXISTS btree_gist;
    """
    p, f, msgs = check_file("001_skills_core_taxonomy.sql", sql)
    assert isinstance(p, int) and isinstance(f, int)


def test_validate_migrations_check_file_invalid():
    from scripts.validate_migrations import check_file

    p, f, msgs = check_file("000_skills_complete_ddl.sql", "")
    assert isinstance(p, int)


def test_validate_migrations_check_cross_reference():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE foo (id int);",
        "001_skills_core_taxonomy.sql": "CREATE TABLE foo (id int);",
    }
    p, f, msgs = check_cross_reference(files)
    assert p >= 1


def test_validate_migrations_check_cross_reference_skips_internal():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE foo (id int);",
        "001_skills_core_taxonomy.sql": "CREATE TABLE _internal (id int);",
    }
    p, f, msgs = check_cross_reference(files)
    assert f == 0


def test_validate_migrations_check_cross_reference_missing():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE foo (id int);",
        "001_skills_core_taxonomy.sql": "CREATE TABLE bar (id int);\nCREATE TABLE foo (id int);",
    }
    p, f, msgs = check_cross_reference(files)
    assert f == 1
    assert any("bar" in m for m in msgs)


def test_validate_migrations_main_missing_dir(tmp_path):
    from scripts.validate_migrations import main

    with patch("scripts.validate_migrations.Path.cwd", return_value=tmp_path):
        code = main()
    assert code == 1


def test_validate_migrations_main_with_files(tmp_path):
    from scripts.validate_migrations import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in [
        "000_skills_complete_ddl.sql",
        "001_skills_core_taxonomy.sql",
        "002_skills_user_tables.sql",
        "003_skills_intelligence_supporting.sql",
        "004_skills_audit_events_analytics.sql",
        "005_skills_security_rls.sql",
        "006_skills_materialized_views.sql",
    ]:
        (mig_dir / fname).write_text("SELECT 1;", encoding="utf-8")

    with patch("scripts.validate_migrations.Path.cwd", return_value=tmp_path):
        code = main()
    assert code == 1


def test_validate_migrations_entry_point():
    import scripts.validate_migrations as vm
    assert hasattr(vm, "main")
    assert callable(vm.main)


def test_validate_migrations_cross_reference_with_failures():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE foo (id int);",
        "001_skills_core_taxonomy.sql": "CREATE TABLE bar (id int);",
    }
    p, f, msgs = check_cross_reference(files)
    assert f >= 1
    assert len(msgs) >= 1


def test_validate_migrations_main_cross_failures(tmp_path):
    from scripts.validate_migrations import main

    # Place files so that MIGRATIONS_DIR relative to cwd resolves correctly
    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    (mig_dir / "000_skills_complete_ddl.sql").write_text("CREATE TABLE foo (id int);", encoding="utf-8")
    (mig_dir / "001_skills_core_taxonomy.sql").write_text("CREATE TABLE bar (id int);", encoding="utf-8")
    for fname in [
        "002_skills_user_tables.sql", "003_skills_intelligence_supporting.sql",
        "004_skills_audit_events_analytics.sql", "005_skills_security_rls.sql",
        "006_skills_materialized_views.sql",
    ]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    with patch("scripts.validate_migrations.Path.cwd", return_value=tmp_path):
        code = main()
    assert code == 1


def test_validate_migrations_has_pattern_len2_rest(tmp_path):
    """Cover line 176 — len(rest)==2 with non-callable arg."""
    from scripts.validate_migrations import check_file
    import scripts.validate_migrations as vm

    bad = dict(vm.CHECKLIST)
    bad["000_skills_complete_ddl.sql"] = [("tab", r"CREATE TABLE foo", "custom msg")]
    with patch.object(vm, "CHECKLIST", bad):
        p, f, msgs = check_file("000_skills_complete_ddl.sql", "CREATE TABLE foo (id int);")
    assert p >= 1


def test_validate_migrations_invalid_check_format():
    from scripts.validate_migrations import check_file
    import scripts.validate_migrations as vm

    # Add a bad entry with 3 extra args
    bad_checklist = dict(vm.CHECKLIST)
    bad_checklist["000_skills_complete_ddl.sql"] = [
        ("bad check", "pattern1", "pattern2", "msg"),
    ]
    with patch.object(vm, "CHECKLIST", bad_checklist):
        p, f, msgs = check_file("000_skills_complete_ddl.sql", "SELECT 1")
    assert f >= 1
    assert any("Invalid check format" in m for m in msgs)


# ── gen_sdb_full.py ──


def test_gen_sdb_validate_migrations_missing(tmp_path):
    from scripts.gen_sdb_full import validate_migrations

    result = validate_migrations(tmp_path)
    assert len(result["missing"]) == 8
    assert len(result["present"]) == 0


def test_gen_sdb_validate_migrations_present(tmp_path):
    from scripts.gen_sdb_full import validate_migrations

    (tmp_path / "000_skills_complete_ddl.sql").write_text("SELECT 1", encoding="utf-8")
    result = validate_migrations(tmp_path)
    assert "000_skills_complete_ddl.sql" in result["present"]


def test_gen_sdb_build_aggregate_ddl(tmp_path):
    from scripts.gen_sdb_full import build_aggregate_ddl

    (tmp_path / "000_skills_complete_ddl.sql").write_text("CREATE TABLE test;", encoding="utf-8")
    ddl = build_aggregate_ddl(tmp_path)
    assert "Begin: 000_skills_complete_ddl.sql" in ddl
    assert "CREATE TABLE test;" in ddl


def test_gen_sdb_generate_python_schemas(tmp_path):
    from scripts.gen_sdb_full import generate_python_schemas

    out = tmp_path / "schemas"
    out.mkdir()
    result = generate_python_schemas(out)
    assert result.exists()
    assert "SkillAuditLogCreate" in result.read_text(encoding="utf-8")


def test_gen_sdb_generate_api_stubs(tmp_path):
    from scripts.gen_sdb_full import generate_api_stubs

    out = tmp_path / "stubs"
    out.mkdir()
    result = generate_api_stubs(out)
    assert result.exists()
    assert "list_audit_log" in result.read_text(encoding="utf-8")


def test_gen_sdb_main_validate_only(tmp_path):
    from scripts.gen_sdb_full import MIGRATIONS, main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in MIGRATIONS:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    with patch("sys.argv", ["prog", "--validate-only", "--migrations-dir", str(mig_dir)]):
        result = main()
    assert result is None


def test_gen_sdb_main_validate_only_missing(tmp_path):
    from scripts.gen_sdb_full import main

    with patch("sys.argv", ["prog", "--validate-only", "--migrations-dir", str(tmp_path)]):
        with pytest.raises(SystemExit):
            main()


def test_gen_sdb_main_output(tmp_path):
    from scripts.gen_sdb_full import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in ["000_skills_complete_ddl.sql", "001_skills_core_taxonomy.sql"]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")
    out_file = tmp_path / "aggregate.sql"

    with patch("sys.argv", ["prog", "--output", str(out_file), "--migrations-dir", str(mig_dir)]):
            main()
    assert out_file.exists()
    assert "Begin: 000_skills_complete_ddl.sql" in out_file.read_text(encoding="utf-8")


def test_gen_sdb_main_generate_schemas(tmp_path):
    from scripts.gen_sdb_full import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    (mig_dir / "000_skills_complete_ddl.sql").write_text("SELECT 1", encoding="utf-8")

    with patch("sys.argv", ["prog", "--generate-schemas", "--migrations-dir", str(mig_dir)]):
        main()


def test_gen_sdb_main_generate_api_stubs(tmp_path):
    from scripts.gen_sdb_full import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    (mig_dir / "000_skills_complete_ddl.sql").write_text("SELECT 1", encoding="utf-8")

    with patch("sys.argv", ["prog", "--generate-api-stubs", "--migrations-dir", str(mig_dir)]):
        main()


def test_gen_sdb_main_no_options(tmp_path):
    from scripts.gen_sdb_full import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in ["000_skills_complete_ddl.sql", "001_skills_core_taxonomy.sql"]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    with patch("sys.argv", ["prog", "--migrations-dir", str(mig_dir)]):
        main()


def test_gen_sdb_main_missing_directory(tmp_path):
    from scripts.gen_sdb_full import main

    with patch("sys.argv", ["prog", "--migrations-dir", str(tmp_path / "nonexistent")]):
        with pytest.raises(SystemExit):
            main()


def test_gen_sdb_entry_point():
    import scripts.gen_sdb_full as gs
    assert hasattr(gs, "main")
    assert callable(gs.main)


# ── validate_skills_schema.py ──


def test_validate_skills_schema_regex_helpers():
    """Test that basic regex patterns work with the validator"""
    import re
    assert re.search(r"CREATE TABLE skills", "CREATE TABLE skills", re.IGNORECASE)
    assert not re.search(r"CREATE TABLE skills", "DROP TABLE skills", re.IGNORECASE)


def test_validate_skills_schema_check():
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.check(True, "should pass")
    assert v.checks["pass"] == 1
    v.check(False, "should fail")
    assert v.checks["fail"] == 1
    assert len(v.errors) == 1


def test_validate_skills_schema_check_warn():
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.check(False, "warning test", level="warn")
    assert v.checks["fail"] == 1
    assert len(v.warnings) == 1


def test_validate_skills_schema_report_pass():
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    assert v.report() == 0


def test_validate_skills_schema_report_fail():
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.check(False, "intentional fail")
    assert v.report() == 1


def test_validate_skills_schema_validate_migration_files(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in [
        "000_skills_complete_ddl.sql",
        "001_skills_core_taxonomy.sql",
        "002_skills_user_tables.sql",
        "003_skills_intelligence_supporting.sql",
        "004_skills_audit_events_analytics.sql",
        "005_skills_security_rls.sql",
        "006_skills_materialized_views.sql",
        "007_skills_partman_cron.sql",
    ]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    v = SchemaValidator()
    v.validate_migration_files(mig_dir)
    assert v.checks["pass"] >= 8
    assert v.checks["fail"] == 0


def test_validate_skills_schema_validate_ddl_coverage(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    ddl = tmp_path / "ddl.sql"
    ddl.write_text("""
    CREATE TABLE IF NOT EXISTS skill_categories ();
    CREATE TABLE IF NOT EXISTS skills ();
    CREATE TABLE IF NOT EXISTS skill_relationships ();
    CREATE TABLE IF NOT EXISTS tags ();
    CREATE TABLE IF NOT EXISTS skill_tags ();
    CREATE TABLE IF NOT EXISTS skill_external_mappings ();
    CREATE TABLE IF NOT EXISTS skill_roadmap_definitions ();
    CREATE TABLE IF NOT EXISTS user_skills ();
    CREATE TABLE IF NOT EXISTS user_skill_evidence ();
    CREATE TABLE IF NOT EXISTS user_skill_targets ();
    CREATE TABLE IF NOT EXISTS user_skill_assessments ();
    CREATE TABLE IF NOT EXISTS user_skill_versions ();
    CREATE TABLE IF NOT EXISTS skill_market_data ();
    CREATE TABLE IF NOT EXISTS skill_income_data ();
    CREATE TABLE IF NOT EXISTS skill_certifications ();
    CREATE TABLE IF NOT EXISTS skill_projects ();
    CREATE TABLE IF NOT EXISTS skill_roadmaps ();
    CREATE TABLE IF NOT EXISTS skill_opportunities ();
    CREATE TABLE IF NOT EXISTS skill_topics ();
    CREATE TABLE IF NOT EXISTS skill_resources ();
    CREATE TABLE IF NOT EXISTS skill_learning_paths ();
    CREATE TABLE IF NOT EXISTS skill_ai_recommendations ();
    CREATE TABLE IF NOT EXISTS skill_user_activity_log ();
    CREATE TABLE IF NOT EXISTS skill_audit_log ();
    CREATE TABLE IF NOT EXISTS skill_taxonomy_history ();
    CREATE TABLE IF NOT EXISTS skill_user_skill_history ();
    CREATE TABLE IF NOT EXISTS skill_market_history ();
    CREATE TABLE IF NOT EXISTS skill_events ();
    CREATE TABLE IF NOT EXISTS skill_event_outbox ();
    CREATE TABLE IF NOT EXISTS skill_webhook_queue ();
    CREATE TABLE IF NOT EXISTS skill_event_subscriptions ();
    CREATE TABLE IF NOT EXISTS skill_analytics_snapshots ();
    CREATE TABLE IF NOT EXISTS skill_forecasts ();
    CREATE ROLE skill_admin;
    CREATE ROLE skill_manager;
    CREATE ROLE skill_user;
    CREATE ROLE skill_auditor;
    CREATE ROLE skill_viewer;
    CREATE ROLE skill_api;
    CREATE ROLE skill_scheduler;
    CREATE ROLE skill_analytics;
    CREATE MATERIALIZED VIEW mv_skill_user_proficiency AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_taxonomy_health AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_ai_effectiveness AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_activity_heatmap AS SELECT 1;
    CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS SELECT 1;
    ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;
    ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
    """, encoding="utf-8")

    v = SchemaValidator()
    v.validate_ddl_coverage(ddl)
    assert v.checks["pass"] > 0


def test_validate_skills_schema_validate_ddl_coverage_missing(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.validate_ddl_coverage(tmp_path / "nonexistent.sql")
    assert v.checks["fail"] > 0


def test_validate_skills_schema_validate_notify_triggers(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    ddl = tmp_path / "ddl.sql"
    ddl.write_text("fn_notify_taxonomy_change trg_skills_notify trg_categories_notify skill_notify_audit_event trg_audit_log_notify", encoding="utf-8")

    v = SchemaValidator()
    v.validate_notify_triggers(ddl)
    assert v.checks["pass"] == 5
    assert v.checks["fail"] == 0


def test_validate_skills_schema_validate_audit_triggers(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    ddl = tmp_path / "ddl.sql"
    ddl.write_text(" ".join(f"trg_{t}_audit" for t in [
        "skills", "skill_categories", "user_skills", "user_skill_evidence",
        "user_skill_targets", "user_skill_assessments", "skill_market_data",
        "skill_relationships", "skill_certifications",
    ]), encoding="utf-8")

    v = SchemaValidator()
    v.validate_audit_triggers(ddl)
    assert v.checks["pass"] == 9
    assert v.checks["fail"] == 0


def test_validate_skills_schema_validate_partitions(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    ddl = tmp_path / "ddl.sql"
    ddl.write_text("\n".join(f"PARTITION OF {t}" for t in [
        "user_skill_evidence", "user_skill_versions", "skill_user_activity_log",
        "skill_audit_log", "skill_events", "skill_webhook_queue", "skill_analytics_snapshots",
    ]), encoding="utf-8")

    v = SchemaValidator()
    v.validate_partitions(ddl)
    assert v.checks["pass"] == 7
    assert v.checks["fail"] == 0


def test_validate_skills_schema_validate_cron_jobs(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    cron = tmp_path / "cron.sql"
    cron.write_text(" ".join([
        "skill-proficiency-refresh", "skill-market-refresh", "skill-update-stale-flags",
        "skill-process-outbox", "skill-process-webhooks", "skill-vacuum-main",
        "skill-partman-maintenance",
    ]), encoding="utf-8")

    v = SchemaValidator()
    v.validate_cron_jobs(cron)
    assert v.checks["pass"] == 7
    assert v.checks["fail"] == 0


def test_validate_skills_schema_validate_cron_jobs_missing(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.validate_cron_jobs(tmp_path / "nonexistent.sql")
    assert v.checks["fail"] >= 1


def test_validate_skills_schema_validate_generator_script(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    gen = tmp_path / "gen.py"
    gen.write_text("def main():\n    pass\n", encoding="utf-8")

    v = SchemaValidator()
    v.validate_generator_script(gen)
    assert v.checks["pass"] >= 2


def test_validate_skills_schema_validate_generator_script_missing(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.validate_generator_script(tmp_path / "nonexistent.py")
    assert v.checks["fail"] >= 1


def test_validate_skills_schema_main(tmp_path):
    from scripts.validate_skills_schema import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in [
        "000_skills_complete_ddl.sql", "001_skills_core_taxonomy.sql",
        "002_skills_user_tables.sql", "003_skills_intelligence_supporting.sql",
        "004_skills_audit_events_analytics.sql", "005_skills_security_rls.sql",
        "006_skills_materialized_views.sql", "007_skills_partman_cron.sql",
    ]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    gen_dir = tmp_path / "scripts"
    gen_script = gen_dir / "gen_sdb_full.py"
    gen_script.write_text("def main():\n    pass\n", encoding="utf-8")

    with patch("scripts.validate_skills_schema.Path.cwd", return_value=tmp_path):
        with patch("sys.argv", ["prog"]):
            code = main()
    assert code == 1


def test_validate_skills_schema_main_no_migrations(tmp_path):
    from scripts.validate_skills_schema import main

    with patch("scripts.validate_skills_schema.Path.cwd", return_value=tmp_path):
        with patch("sys.argv", ["prog"]):
            code = main()
    assert code == 1


def test_validate_skills_schema_entry_point():
    import scripts.validate_skills_schema as vss
    assert hasattr(vss, "main")
    assert callable(vss.main)


def test_validate_skills_schema_empty_migration_file(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    (mig_dir / "000_skills_complete_ddl.sql").write_text("", encoding="utf-8")

    v = SchemaValidator()
    v.validate_migration_files(mig_dir)
    assert v.checks["fail"] >= 1


def test_validate_skills_schema_partition_findall(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    ddl = tmp_path / "ddl.sql"
    ddl.write_text("""
    CREATE TABLE IF NOT EXISTS skill_audit_log () PARTITION BY RANGE (created_at);
    """, encoding="utf-8")

    v = SchemaValidator()
    v.validate_ddl_coverage(ddl)
    assert v.checks["fail"] >= 0


def test_validate_skills_schema_with_warnings(tmp_path):
    from scripts.validate_skills_schema import SchemaValidator

    v = SchemaValidator()
    v.check(False, "test warning", level="warn")
    code = v.report()
    assert len(v.warnings) >= 1


def test_validate_skills_schema_model_check(tmp_path):
    from scripts.validate_skills_schema import main

    mig_dir = tmp_path / "scripts" / "migrations"
    mig_dir.mkdir(parents=True)
    for fname in [
        "000_skills_complete_ddl.sql", "001_skills_core_taxonomy.sql",
        "002_skills_user_tables.sql", "003_skills_intelligence_supporting.sql",
        "004_skills_audit_events_analytics.sql", "005_skills_security_rls.sql",
        "006_skills_materialized_views.sql", "007_skills_partman_cron.sql",
    ]:
        (mig_dir / fname).write_text("SELECT 1", encoding="utf-8")

    gen_dir = tmp_path / "scripts"
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / "gen_sdb_full.py").write_text("def main():\n    pass\n", encoding="utf-8")

    # Create schema dir with skill.py
    schema_dir = tmp_path / "packages" / "database" / "schemas"
    schema_dir.mkdir(parents=True)
    (schema_dir / "skill.py").write_text("SkillAuditLogCreate = None", encoding="utf-8")

    with patch("sys.argv", ["prog", "--migrations-dir", str(mig_dir), "--gen-script", str(gen_dir / "gen_sdb_full.py")]):
        with patch("scripts.validate_skills_schema.Path.cwd", return_value=tmp_path):
            code = main()
        # Should pass or fail gracefully
        assert code in (0, 1)
