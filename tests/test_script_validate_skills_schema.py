"""Tests for scripts/validate_skills_schema.py — schema validator."""



class TestSchemaValidator:
    def test_initialization(self):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator(db_available=False)
        assert v.db_available is False
        assert v.errors == []
        assert v.warnings == []
        assert v.checks == {"pass": 0, "fail": 0, "warn": 0}

    def test_check_pass(self):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(True, "should pass")
        assert v.checks["pass"] == 1
        assert v.checks["fail"] == 0

    def test_check_fail(self):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(False, "should fail")
        assert v.checks["pass"] == 0
        assert v.checks["fail"] == 1
        assert len(v.errors) == 1
        assert "should fail" in v.errors

    def test_check_warn(self):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(False, "should warn", level="warn")
        assert v.checks["fail"] == 1
        assert len(v.warnings) == 1
        assert "should warn" in v.warnings

    def test_check_multiple(self):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(True, "pass a")
        v.check(False, "fail b")
        v.check(True, "pass c")
        v.check(True, "pass d")
        v.check(False, "fail e")
        assert v.checks["pass"] == 3
        assert v.checks["fail"] == 2
        assert len(v.errors) == 2

    def test_validate_migration_files_all_present(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

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
            (tmp_path / fname).write_text("-- test content", encoding="utf-8")

        v = SchemaValidator()
        v.validate_migration_files(tmp_path)
        assert v.checks["fail"] == 0

    def test_validate_migration_files_some_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        (tmp_path / "000_skills_complete_ddl.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "001_skills_core_taxonomy.sql").write_text("-- content", encoding="utf-8")

        v = SchemaValidator()
        v.validate_migration_files(tmp_path)
        assert v.checks["fail"] == 6  # 6 missing out of 8

    def test_validate_migration_files_all_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_migration_files(tmp_path)
        assert v.checks["fail"] == 8

    def test_validate_migration_files_empty_file(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        (tmp_path / "000_skills_complete_ddl.sql").write_text("", encoding="utf-8")
        (tmp_path / "001_skills_core_taxonomy.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "002_skills_user_tables.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "003_skills_intelligence_supporting.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "004_skills_audit_events_analytics.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "005_skills_security_rls.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "006_skills_materialized_views.sql").write_text("-- content", encoding="utf-8")
        (tmp_path / "007_skills_partman_cron.sql").write_text("-- content", encoding="utf-8")

        v = SchemaValidator()
        v.validate_migration_files(tmp_path)
        # exists but empty = 1 fail for 000, + 7 present = 1 fail, 7 pass
        assert v.checks["fail"] == 1

    def test_validate_generator_script_exists(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        gen_path = tmp_path / "gen_sdb_full.py"
        gen_path.write_text("def main():\n    pass", encoding="utf-8")

        v = SchemaValidator()
        v.validate_generator_script(gen_path)
        assert v.checks["fail"] == 0

    def test_validate_generator_script_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_generator_script(tmp_path / "nonexistent.py")
        assert v.checks["fail"] == 1

    def test_validate_generator_script_no_main(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        gen_path = tmp_path / "gen_sdb_full.py"
        gen_path.write_text("x = 1", encoding="utf-8")

        v = SchemaValidator()
        v.validate_generator_script(gen_path)
        assert v.checks["fail"] == 1
        assert v.checks["pass"] == 1  # exists=True passes, but main() check fails

    def test_validate_ddl_coverage_not_found(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_ddl_coverage(tmp_path / "nonexistent.sql")
        assert v.checks["fail"] == 1

    def test_validate_ddl_coverage_basic(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "000_skills_complete_ddl.sql"
        ddl_content = "CREATE TABLE IF NOT EXISTS skill_categories (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skills (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_relationships (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS tags (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_tags (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_external_mappings (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_roadmap_definitions (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skills (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skill_evidence (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skill_targets (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skill_assessments (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skill_versions (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_market_data (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_income_data (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_certifications (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_projects (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_roadmaps (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_opportunities (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_topics (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_resources (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_learning_paths (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_ai_recommendations (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_user_activity_log (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_audit_log (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_taxonomy_history (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_user_skill_history (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_market_history (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_events (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_event_outbox (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_webhook_queue (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_event_subscriptions (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_analytics_snapshots (\n  id int\n)\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS skill_forecasts (\n  id int\n)\n"
        ddl_content += "CREATE ROLE skill_admin;\n"
        ddl_content += "CREATE ROLE skill_manager;\n"
        ddl_content += "CREATE ROLE skill_user;\n"
        ddl_content += "CREATE ROLE skill_auditor;\n"
        ddl_content += "CREATE ROLE skill_viewer;\n"
        ddl_content += "CREATE ROLE skill_api;\n"
        ddl_content += "CREATE ROLE skill_scheduler;\n"
        ddl_content += "CREATE ROLE skill_analytics;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_user_proficiency AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_market_intelligence AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_learning_velocity AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_taxonomy_health AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_ai_effectiveness AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_activity_heatmap AS SELECT 1;\n"
        ddl_content += "CREATE MATERIALIZED VIEW mv_skill_roadmap_progress AS SELECT 1;\n"
        ddl_content += "ALTER TABLE user_skills ENABLE ROW LEVEL SECURITY;\n"
        ddl_content += "ALTER TABLE skills ENABLE ROW LEVEL SECURITY;\n"
        ddl_content += "PARTITION BY RANGE;\n"
        ddl_content += "CREATE TABLE IF NOT EXISTS user_skill_evidence (\n  gap_size int GENERATED ALWAYS AS (1) STORED\n);\n"
        ddl_content += "no_overlapping_prereqs;\n"
        ddl_content += "PARTITION OF skill_events;\n"
        ddl_content += "PARTITION OF skill_webhook_queue;\n"
        ddl_content += "PARTITION OF skill_analytics_snapshots;\n"
        ddl_content += "PARTITION OF user_skill_evidence;\n"
        ddl_content += "PARTITION OF user_skill_versions;\n"
        ddl_content += "PARTITION OF skill_user_activity_log;\n"
        ddl_content += "PARTITION OF skill_audit_log;\n"
        ddl_path.write_text(ddl_content, encoding="utf-8")

        v = SchemaValidator()
        v.validate_ddl_coverage(ddl_path)
        passes = v.checks["pass"]
        fails = v.checks["fail"]
        assert passes > 0

    def test_validate_notify_triggers(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text(
            "fn_notify_taxonomy_change\n"
            "trg_skills_notify\n"
            "trg_categories_notify\n"
            "skill_notify_audit_event\n"
            "trg_audit_log_notify\n",
            encoding="utf-8",
        )

        v = SchemaValidator()
        v.validate_notify_triggers(ddl_path)
        assert v.checks["fail"] == 0
        assert v.checks["pass"] == 5

    def test_validate_notify_triggers_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text("nothing here", encoding="utf-8")

        v = SchemaValidator()
        v.validate_notify_triggers(ddl_path)
        assert v.checks["fail"] == 5
        assert len(v.errors) == 5

    def test_validate_notify_triggers_no_file(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_notify_triggers(tmp_path / "nonexistent.sql")
        assert v.checks["fail"] == 0

    def test_validate_audit_triggers(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text(
            "trg_skills_audit trg_skill_categories_audit "
            "trg_user_skills_audit trg_user_skill_evidence_audit "
            "trg_user_skill_targets_audit trg_user_skill_assessments_audit "
            "trg_skill_market_data_audit trg_skill_relationships_audit "
            "trg_skill_certifications_audit",
            encoding="utf-8",
        )

        v = SchemaValidator()
        v.validate_audit_triggers(ddl_path)
        assert v.checks["fail"] == 0
        assert v.checks["pass"] == 9

    def test_validate_audit_triggers_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text("nothing here", encoding="utf-8")

        v = SchemaValidator()
        v.validate_audit_triggers(ddl_path)
        assert v.checks["fail"] == 9

    def test_validate_audit_triggers_no_file(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_audit_triggers(tmp_path / "nonexistent.sql")
        assert v.checks["fail"] == 0

    def test_validate_partitions(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text(
            "PARTITION OF skill_audit_log\n"
            "PARTITION OF skill_events\n"
            "PARTITION OF skill_webhook_queue\n"
            "PARTITION OF skill_analytics_snapshots\n"
            "PARTITION OF user_skill_evidence\n"
            "PARTITION OF user_skill_versions\n"
            "PARTITION OF skill_user_activity_log\n",
            encoding="utf-8",
        )

        v = SchemaValidator()
        v.validate_partitions(ddl_path)
        assert v.checks["fail"] == 0
        assert v.checks["pass"] == 7

    def test_validate_partitions_missing(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        ddl_path = tmp_path / "ddl.sql"
        ddl_path.write_text("nothing here", encoding="utf-8")

        v = SchemaValidator()
        v.validate_partitions(ddl_path)
        assert v.checks["fail"] == 7

    def test_validate_partitions_no_file(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_partitions(tmp_path / "nonexistent.sql")
        assert v.checks["fail"] == 0

    def test_validate_cron_jobs(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        cron_path = tmp_path / "cron.sql"
        cron_path.write_text(
            "skill-proficiency-refresh\n"
            "skill-market-refresh\n"
            "skill-update-stale-flags\n"
            "skill-process-outbox\n"
            "skill-process-webhooks\n"
            "skill-vacuum-main\n"
            "skill-partman-maintenance\n",
            encoding="utf-8",
        )

        v = SchemaValidator()
        v.validate_cron_jobs(cron_path)
        assert v.checks["fail"] == 0
        assert v.checks["pass"] == 7

    def test_validate_cron_jobs_not_found(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.validate_cron_jobs(tmp_path / "nonexistent.sql")
        assert v.checks["fail"] == 1

    def test_validate_cron_jobs_missing_jobs(self, tmp_path):
        from scripts.validate_skills_schema import SchemaValidator

        cron_path = tmp_path / "cron.sql"
        cron_path.write_text("skill-proficiency-refresh", encoding="utf-8")

        v = SchemaValidator()
        v.validate_cron_jobs(cron_path)
        assert v.checks["fail"] == 6  # 1 found, 6 missing

    def test_report_no_errors(self, capsys):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        result = v.report()
        assert result == 0
        captured = capsys.readouterr()
        assert "ALL CHECKS PASSED" in captured.out

    def test_report_with_errors(self, capsys):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(False, "something failed")
        result = v.report()
        assert result == 1
        captured = capsys.readouterr()
        assert "FAILURES" in captured.out

    def test_report_with_warnings(self, capsys):
        from scripts.validate_skills_schema import SchemaValidator

        v = SchemaValidator()
        v.check(False, "warning message", level="warn")
        result = v.report()
        assert result == 0  # warnings only, no errors
        captured = capsys.readouterr()
        assert "WARNINGS" in captured.out
        assert "warning message" in captured.out
