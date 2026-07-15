"""Tests for scripts/gen_sdb_full.py — SDB full generator."""

import sys
from unittest.mock import patch
import pytest


def test_validate_migrations_all_present(tmp_path):
    from scripts.gen_sdb_full import validate_migrations, MIGRATIONS

    for fname in MIGRATIONS:
        (tmp_path / fname).write_text("-- test sql", encoding="utf-8")

    result = validate_migrations(tmp_path)
    assert len(result["present"]) == len(MIGRATIONS)
    assert result["missing"] == []
    assert all(fname in result["sizes"] for fname in MIGRATIONS)


def test_validate_migrations_some_missing(tmp_path):
    from scripts.gen_sdb_full import validate_migrations, MIGRATIONS

    (tmp_path / MIGRATIONS[0]).write_text("-- test", encoding="utf-8")

    result = validate_migrations(tmp_path)
    assert len(result["present"]) == 1
    assert len(result["missing"]) == len(MIGRATIONS) - 1


def test_validate_migrations_empty_dir(tmp_path):
    from scripts.gen_sdb_full import validate_migrations, MIGRATIONS

    result = validate_migrations(tmp_path)
    assert result["present"] == []
    assert len(result["missing"]) == len(MIGRATIONS)


def test_build_aggregate_ddl(tmp_path):
    from scripts.gen_sdb_full import build_aggregate_ddl, MIGRATIONS

    for fname in MIGRATIONS:
        (tmp_path / fname).write_text(f"-- content of {fname}", encoding="utf-8")

    ddl = build_aggregate_ddl(tmp_path)
    assert "-- SKILLS DATABASE" in ddl
    assert "Begin:" in ddl
    assert "End:" in ddl
    for fname in MIGRATIONS:
        assert f"content of {fname}" in ddl


def test_generate_python_schemas(tmp_path):
    from scripts.gen_sdb_full import generate_python_schemas

    result = generate_python_schemas(tmp_path)
    assert result.exists()
    assert result.name == "schemas_generated.py"
    content = result.read_text(encoding="utf-8")
    assert "class AuditAction" in content
    assert "class SkillAuditLogCreate" in content
    assert "class SkillEventSubscriptionCreate" in content
    assert "class SkillForecastCreate" in content


def test_generate_api_stubs(tmp_path):
    from scripts.gen_sdb_full import generate_api_stubs

    result = generate_api_stubs(tmp_path)
    assert result.exists()
    assert result.name == "api_stubs_generated.py"
    content = result.read_text(encoding="utf-8")
    assert "list_audit_log" in content
    assert "list_event_subscriptions" in content
    assert "list_analytics_snapshots" in content
    assert "list_forecasts" in content


def test_main_validate_only(tmp_path):
    from scripts.gen_sdb_full import main

    test_args = ["prog", "--migrations-dir", str(tmp_path), "--validate-only"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


def test_main_validate_only_all_present(tmp_path):
    from scripts.gen_sdb_full import main, MIGRATIONS

    for fname in MIGRATIONS:
        (tmp_path / fname).write_text("-- sql", encoding="utf-8")

    test_args = ["prog", "--migrations-dir", str(tmp_path), "--validate-only"]
    with patch.object(sys, "argv", test_args):
        result = main()  # returns None on success; no sys.exit
        assert result is None


def test_main_migrations_dir_not_found(tmp_path):
    from scripts.gen_sdb_full import main

    test_args = ["prog", "--migrations-dir", str(tmp_path / "nonexistent")]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


def test_main_generate_schemas(tmp_path):
    from scripts.gen_sdb_full import main, MIGRATIONS

    for fname in MIGRATIONS:
        (tmp_path / fname).write_text("-- sql", encoding="utf-8")

    test_args = ["prog", "--migrations-dir", str(tmp_path), "--generate-schemas"]
    with patch.object(sys, "argv", test_args):
        with patch("scripts.gen_sdb_full.generate_python_schemas") as mock_gen:
            main()
            mock_gen.assert_called_once()


def test_main_generate_api_stubs(tmp_path):
    from scripts.gen_sdb_full import main, MIGRATIONS

    for fname in MIGRATIONS:
        (tmp_path / fname).write_text("-- sql", encoding="utf-8")

    test_args = ["prog", "--migrations-dir", str(tmp_path), "--generate-api-stubs"]
    with patch.object(sys, "argv", test_args):
        with patch("scripts.gen_sdb_full.generate_api_stubs") as mock_stubs:
            main()
            mock_stubs.assert_called_once()
