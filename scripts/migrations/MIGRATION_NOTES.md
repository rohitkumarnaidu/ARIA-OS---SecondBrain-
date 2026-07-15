# Migration Notes — Known Issues & Conflicts

## 1. Table Name Collision: `skill_categories`

**Conflict:** `skill_categories` is defined in two different migration files with incompatible schemas:

| File | Schema Purpose | Key Columns |
|---|---|---|
| `000_skills_complete_ddl.sql` (line 25) | Full skills taxonomy DDL with ltree hierarchy, RLS, triggers, 7 indexes | `category_id`, `parent_category_id`, `name`, `slug`, `path` (ltree), `sort_order`, `tenant_id`, etc. |
| `014_core_app_seed.sql` (line 48) | Simple reference lookup for user profile skill categories | `id`, `name`, `slug`, `icon`, `description`, `sort_order` |

Since both use `CREATE TABLE IF NOT EXISTS`, whichever runs first wins. If `000_skills_complete_ddl.sql` runs first, `014_core_app_seed.sql` will silently skip creating its simpler version, and its `INSERT` statements may conflict with the different column structure.

**Recommendation:** Rename one of the tables. Options:
- Rename `014_core_app_seed.sql`'s table to `profile_skill_categories` or `user_skill_categories`
- Or remove the `skill_categories` DDL from `014_core_app_seed.sql` and reference the one from `000_skills_complete_ddl.sql` (if that migration is guaranteed to run first)

## 2. Table Name Drift

The following tables were renamed in `010_core_app_schema.sql` but old names still appear in `generate-test-data.sql` (now fixed) and potentially in other files:

| Old Name | New Name | Defined In |
|---|---|---|
| `time_entries` | `time_logs` | `010_core_app_schema.sql:442` |
| `income_entries` | `income_logs` | `010_core_app_schema.sql:326` |
| `memory` | `aria_memory` | `010_core_app_schema.sql:478` |
| `users` | `users_profile` | `010_core_app_schema.sql:19` |

**Recommendation:** Audit all API route files, agent modules, and cron jobs for references to the old table names. Files most likely affected:
- `apps/api/app/api/` — all route handlers referencing these tables
- `services/scheduler/crons/` — cron job SQL queries
- `packages/ai/agents/` — agent modules that query these tables
- Any remaining test data or seed files

## 3. Column Structure Mismatches

After the above renames, the new tables have different column schemas. `generate-test-data.sql` was updated in July 2026 to match, but other files may still reference old columns.

| Table | Removed/Changed Columns | New Columns |
|---|---|---|
| `users_profile` | no `full_name`, `avatar_url`, `preferences` | `user_id`, `name`, `college`, `year`, `branch`, `skills` (JSONB) |
| `income_logs` | no `source_type`, `hourly_rate`, `hours_worked`, `updated_at` | `source_id` (FK), `hours_spent` |
| `time_logs` | no `start_time`, `end_time`, `duration_minutes`, `activity_type` | `task_id` (FK), `started_at`, `ended_at`, `duration_seconds`, `is_pomodoro`, `is_deep_work`, `energy_level` |
| `aria_memory` | no `key`, `value`, `updated_at` | `memory_type` (enum), `content`, `confidence`, `last_referenced_at` |
