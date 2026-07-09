# ARIA OS — Database Migrations Guide

## Overview

Two migration systems are available:

| System | Use Case | Tool |
|--------|----------|------|
| **SQL scripts** (`scripts/migrations/`) | Bootstrap, reference DDL, one-off changes | Run manually via Supabase SQL Editor |
| **Alembic** (`scripts/migrations/alembic/`) | Version-controlled, reversible migrations | `alembic upgrade/downgrade` CLI |

## Prerequisites

```bash
pip install alembic psycopg2-binary
```

Set your database URL:
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/aria_os
```

## Common Commands

```bash
# From scripts/migrations/
cd scripts/migrations

# Check current version
alembic current

# Run all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# View migration history
alembic history

# Create a new migration
alembic revision -m "add_user_preferences_table"

# Generate migration from model changes (auto-detect)
alembic revision --autogenerate -m "detect_changes"
```

## Migration Workflow

1. **Create migration:**
   ```bash
   alembic revision -m "description_of_change"
   ```

2. **Edit the generated file** in `alembic/versions/` — add `upgrade()` and `downgrade()` functions.

3. **Test upgrade:**
   ```bash
   alembic upgrade head
   ```

4. **Test rollback:**
   ```bash
   alembic downgrade -1
   alembic upgrade head  # Back to latest
   ```

5. **Commit both** the migration file and any related schema/model changes.

## Rules

- **Never edit a published migration.** Create a new one to reverse or modify.
- **Always implement both `upgrade()` and `downgrade()`** — every change must be reversible.
- **Test both directions** before merging.
- **Keep migrations small and focused** — one logical change per revision.
- **Use `batch` mode for large tables** with `with op.batch_alter_table()` to avoid locks.

## Reference SQL Scripts

The `scripts/migrations/` directory also contains raw SQL files for reference:

| File | Purpose |
|------|---------|
| `000_skills_complete_ddl.sql` | Full skills schema DDL |
| `001-007_*.sql` | Incremental skills feature migrations |
| `008_agent_activity_log.sql` | Agent activity logging table |
| `009_api_key_tiers.sql` | API key tier plans + migration |

These are maintained alongside Alembic for environments where Alembic is not available (e.g., Supabase SQL Editor).
