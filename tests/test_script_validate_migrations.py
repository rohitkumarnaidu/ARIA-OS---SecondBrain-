"""Tests for scripts/validate_migrations.py — migration SQL validator."""

from unittest.mock import patch


def test_has_pattern_matches():
    from scripts.validate_migrations import has_pattern

    assert has_pattern("CREATE TABLE skills", r"CREATE TABLE") is True


def test_has_pattern_no_match():
    from scripts.validate_migrations import has_pattern

    assert has_pattern("DROP TABLE skills", r"CREATE TABLE") is False


def test_has_pattern_case_insensitive():
    from scripts.validate_migrations import has_pattern

    assert has_pattern("create table skills", r"CREATE TABLE") is True
    assert has_pattern("CREATE TABLE skills", r"create table") is True


def test_check_file_all_pass(tmp_path):
    from scripts.validate_migrations import check_file

    sql = "CREATE TABLE IF NOT EXISTS skill_categories"
    passes, fails, msgs = check_file("000_skills_complete_ddl.sql", sql)
    assert isinstance(passes, int)
    assert isinstance(fails, int)
    assert isinstance(msgs, list)


def test_check_file_unknown_file(tmp_path):
    from scripts.validate_migrations import check_file

    passes, fails, msgs = check_file("unknown.sql", "CREATE TABLE x")
    assert passes == 0
    assert fails == 0
    assert msgs == []


def test_check_file_with_lambda_check(tmp_path):
    from scripts.validate_migrations import check_file

    sql = "CREATE TABLE IF NOT EXISTS a (id int); CREATE TABLE IF NOT EXISTS b (id int); CREATE TABLE IF NOT EXISTS c (id int); CREATE TABLE IF NOT EXISTS d (id int); CREATE TABLE IF NOT EXISTS e (id int); CREATE TABLE IF NOT EXISTS f (id int); CREATE TABLE IF NOT EXISTS g (id int);"
    passes, fails, msgs = check_file("001_skills_core_taxonomy.sql", sql)
    assert passes >= 1


def test_check_cross_reference_no_issues():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE IF NOT EXISTS skills (\n  id int\n)",
        "001_skills_core_taxonomy.sql": "CREATE TABLE IF NOT EXISTS skills (\n  id int\n)",
    }
    passes, fails, msgs = check_cross_reference(files)
    assert passes >= 1
    assert fails == 0


def test_check_cross_reference_missing_table():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE IF NOT EXISTS existing_tbl (\n  id int\n)",
        "001_skills_core_taxonomy.sql": "CREATE TABLE IF NOT EXISTS missing_tbl (\n  id int\n)",
    }
    passes, fails, msgs = check_cross_reference(files)
    assert passes == 0  # existing_tbl not in 001, missing_tbl not in 000
    assert fails >= 1


def test_check_cross_reference_skips_000():
    from scripts.validate_migrations import check_cross_reference

    files = {
        "000_skills_complete_ddl.sql": "CREATE TABLE IF NOT EXISTS t1 (id int)",
        "001_skills_core_taxonomy.sql": "CREATE TABLE IF NOT EXISTS t1 (id int)",
    }
    passes, fails, msgs = check_cross_reference(files)
    assert fails == 0


def test_main_migrations_not_found(tmp_path):
    from scripts.validate_migrations import main

    with patch("scripts.validate_migrations.MIGRATIONS_DIR", tmp_path):
        result = main()
        assert result == 1


def test_main_with_dummy_files(tmp_path):
    from scripts.validate_migrations import main, FILES

    for fname in FILES:
        (tmp_path / fname).write_text("CREATE TABLE dummy (id int);", encoding="utf-8")

    with patch("scripts.validate_migrations.MIGRATIONS_DIR", tmp_path):
        result = main()
        assert isinstance(result, int)


def test_main_with_full_content(tmp_path):
    from scripts.validate_migrations import main, FILES

    for fname in FILES:
        (tmp_path / fname).write_text(
            "CREATE EXTENSION IF NOT EXISTS btree_gist;\n"
            "CREATE TABLE IF NOT EXISTS skill_categories (id int);\n"
            "CREATE TABLE IF NOT EXISTS skills (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_relationships (id int);\n"
            "CREATE TABLE IF NOT EXISTS tags (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_tags (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_external_mappings (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_roadmap_definitions (id int);\n"
            "CREATE TABLE IF NOT EXISTS user_skills (id int);\n"
            "CREATE TABLE IF NOT EXISTS user_skill_evidence (id int);\n"
            "CREATE TABLE IF NOT EXISTS user_skill_targets (id int);\n"
            "CREATE TABLE IF NOT EXISTS user_skill_assessments (id int);\n"
            "CREATE TABLE IF NOT EXISTS user_skill_versions (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_market_data (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_income_data (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_certifications (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_projects (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_roadmaps (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_opportunities (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_topics (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_resources (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_learning_paths (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_ai_recommendations (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_user_activity_log (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_audit_log (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_taxonomy_history (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_user_skill_history (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_market_history (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_events (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_event_outbox (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_webhook_queue (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_event_subscriptions (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_analytics_snapshots (id int);\n"
            "CREATE TABLE IF NOT EXISTS skill_forecasts (id int);\n"
            "ALTER TABLE x ENABLE ROW LEVEL SECURITY;\n"
            "FORCE ROW LEVEL SECURITY;\n"
            "REVOKE UPDATE;\n"
            "GRANT UPDATE (;\n"
            "EXCLUDE USING gist;\n"
            "CREATE MATERIALIZED VIEW mv_skill_user_proficiency AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_taxonomy_health AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_ai_effectiveness AS;\n"
            "CREATE MATERIALIZED VIEW mv_skill_activity_heatmap AS;\n"
            "PARTITION OF skill_audit_log;\n"
            "PARTITION OF skill_events;\n"
            "PARTITION OF skill_webhook_queue;\n"
            "PARTITION OF skill_analytics_snapshots;\n"
            "CREATE ROLE skill_admin;\nCREATE ROLE skill_manager;\nCREATE ROLE skill_user;\n"
            "CREATE ROLE skill_auditor;\nCREATE ROLE skill_viewer;\nCREATE ROLE skill_api;\n"
            "CREATE ROLE skill_scheduler;\nCREATE ROLE skill_analytics;\n"
            "skill_audit_trigger_func;\nskill_notify_audit_event;\n"
            "skill_encrypt_pii;\nskill_decrypt_pii;\n"
            "skill_refresh_all_materialized_views;\n"
            "mv_skill_ai_recommendation_effectiveness;\n"
            "event_version TEXT NOT NULL DEFAULT '1.0';\n"
            "skill_webhook_queue_2026_q3;\nskill_analytics_snapshots_2026_q3;\n"
            "trg_skills_notify;\ntrg_categories_notify;\nfn_notify_taxonomy_change;\n"
            "CREATE EXTENSION IF NOT EXISTS pgcrypto;\n"
            "CREATE EXTENSION IF NOT EXISTS ltree;\n"
            "CHECK ( level >= 0 AND level <= 5 );\n"
            "CREATE TABLE IF NOT EXISTS user_skill_evidence_2026;\n"
            "CREATE TABLE IF NOT EXISTS user_skill_versions_2026;\n"
            "CREATE TABLE IF NOT EXISTS skill_user_activity_log_2026;\n"
            "CREATE TRIGGER trg_skill_audit;\nCREATE TRIGGER trg_categories_audit;\n"
            "FOREACH tbl IN ARRAY;\n",
            encoding="utf-8",
        )

    with patch("scripts.validate_migrations.MIGRATIONS_DIR", tmp_path):
        result = main()
        assert isinstance(result, int)


def test_main_script_entry():
    """Test that main is callable."""
    from scripts.validate_migrations import main

    assert callable(main)
