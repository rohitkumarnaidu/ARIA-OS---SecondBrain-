# Row Level Security Policies — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-POL-008 |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Date** | 2026-07-10 |
| **Classification** | Internal |
| **Owner** | Developer |
| **Related Docs** | [RLS.md](RLS.md), [Schema.md](Schema.md), [Constraints.md](Constraints.md) |

---

## 1. Executive Summary

Row Level Security (RLS) is the primary data isolation mechanism in Second Brain OS. Every user-owned table has RLS enabled with policies that restrict access to rows where `user_id = auth.uid()`. Child tables (subtasks, task_dependencies, marks) inherit access through parent table relationships. The service role bypasses all RLS for administrative operations and cron jobs.

---

## 2. Policy Naming Convention

```
policy_{table}_{operation}    -- Standard format
```

Examples:
- `policy_tasks_select` — SELECT policy on tasks
- `policy_tasks_all` — ALL operations on tasks

---

## 3. Standard User Ownership Policy

Every user-owned table has this policy applied:

```sql
CREATE POLICY "users_own_data" ON table_name
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

---

## 4. Complete Policy Catalog

### 4.1 Primary User-Owned Tables

| Table | Policy Name | Type | Expression | Purpose |
|---|---|---|---|---|
| users_profile | users_own_data | ALL | auth.uid() = user_id | Users see only their own profile |
| tasks | users_own_data | ALL | auth.uid() = user_id | Task isolation |
| courses | users_own_data | ALL | auth.uid() = user_id | Course isolation |
| youtube_saves | users_own_data | ALL | auth.uid() = user_id | Video isolation |
| resources | users_own_data | ALL | auth.uid() = user_id | Resource isolation |
| ideas | users_own_data | ALL | auth.uid() = user_id | Idea isolation |
| goals | users_own_data | ALL | auth.uid() = user_id | Goal isolation |
| roadmaps | users_own_data | ALL | auth.uid() = user_id | Roadmap isolation |
| roadmap_updates | users_own_data | ALL | auth.uid() = user_id | Update isolation |
| opportunities | users_own_data | ALL | auth.uid() = user_id | Opportunity isolation |
| income_sources | users_own_data | ALL | auth.uid() = user_id | Income isolation |
| income_logs | users_own_data | ALL | auth.uid() = user_id | Income log isolation |
| projects | users_own_data | ALL | auth.uid() = user_id | Project isolation |
| academic_subjects | users_own_data | ALL | auth.uid() = user_id | Academic isolation |
| habits | users_own_data | ALL | auth.uid() = user_id | Habit isolation |
| habit_logs | users_own_data | ALL | auth.uid() = user_id | Habit log isolation |
| sleep_logs | users_own_data | ALL | auth.uid() = user_id | Sleep log isolation |
| time_logs | users_own_data | ALL | auth.uid() = user_id | Time log isolation |
| chat_messages | users_own_data | ALL | auth.uid() = user_id | Chat isolation |
| aria_memory | users_own_data | ALL | auth.uid() = user_id | Memory isolation |
| daily_briefings | users_own_data | ALL | auth.uid() = user_id | Briefing isolation |
| weekly_reviews | users_own_data | ALL | auth.uid() = user_id | Review isolation |
| study_sessions | users_own_data | ALL | auth.uid() = user_id | Study isolation |
| daily_logs | users_own_data | ALL | auth.uid() = user_id | Journal isolation |

### 4.2 Child Tables (Inherited Access)

These tables do NOT have `user_id` columns. Access is inherited through parent table RLS:

| Table | Parent | Access Method |
|---|---|---|
| subtasks | tasks(task_id) | Application filters by parent task's user_id |
| task_dependencies | tasks(task_id) | Application filters by parent task's user_id |
| marks | academic_subjects(subject_id) | Application filters by parent subject's user_id |

**Policy for child tables (example):**

```sql
CREATE POLICY "subtasks_via_task" ON subtasks
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM tasks
      WHERE tasks.id = subtasks.task_id
        AND tasks.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM tasks
      WHERE tasks.id = subtasks.task_id
        AND tasks.user_id = auth.uid()
    )
  );
```

---

## 5. Policy Template

```sql
-- Generic template for creating policies on any user-owned table
DO $$
DECLARE
  table_name TEXT := 'tasks';  -- Replace with target table
BEGIN
  EXECUTE format(
    'ALTER TABLE %I ENABLE ROW LEVEL SECURITY;
     CREATE POLICY "users_own_data" ON %I
       FOR ALL USING (auth.uid() = user_id)
       WITH CHECK (auth.uid() = user_id);',
    table_name, table_name
  );
END $$;
```

---

## 6. Service Role Bypass

Supabase service role (`service_role`) bypasses ALL RLS policies:

```python
# Server-side operations use service role
supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# This bypasses RLS — for cron jobs and admin operations
data = supabase_service.table("opportunities").select("*").execute()
```

**Security rules for service role usage:**
- Never expose service key to client
- Use only in server-side cron jobs and admin endpoints
- Always add explicit `user_id` filters even with service role
- Service role endpoints must have separate auth (API key)

---

## 7. RLS Testing Queries

```sql
-- Test as specific user
SELECT auth.uid();  -- Must return the authenticated user's ID

-- Verify RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Test policy behavior (run as anon or specific user)
-- Should return 0 rows if not authenticated
SELECT * FROM tasks LIMIT 1;
```

---

## 8. Policy Audit Checklist

- [ ] Every user-owned table has RLS enabled
- [ ] Every user-owned table has a `user_id` column
- [ ] Every policy uses `auth.uid()` for user identification
- [ ] Child tables have policies that check parent table ownership
- [ ] Service role usage is documented and audited
- [ ] No table has RLS enabled without at least one policy
- [ ] Policies use `FOR ALL` unless specific operations are restricted

---

## 9. Related Documents

| Document | Description |
|---|---|
| [RLS.md](RLS.md) | RLS deep dive with architecture |
| [Schema.md](Schema.md) | Column-level schema |
| [Functions.md](Functions.md) | RLS helper functions |
