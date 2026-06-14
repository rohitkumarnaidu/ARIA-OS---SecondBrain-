# Permissions & Roles — Second Brain OS

## Document Control

| Field | Value |
|---|---|
| **Document ID** | ENG-PERM-001 |
| **Status** | Draft v0.1 |
| **Author** | Architecture Team |
| **Last Updated** | 2026-06-11 |
| **Approved By** | — |

---

## 1. Executive Summary

Second Brain OS currently operates as a single-user system with Row-Level Security (RLS) on all Supabase tables but zero role-based access control. As the platform evolves toward multi-user collaboration (shared projects, team goals, mentor-student workflows), a formal permissions model is required. This document defines a **three-role model** (Admin, User, ReadOnly) with a clear migration path to multi-tenancy, implemented via Supabase RLS + JWT custom claims. Target: no security bypass possible, < 50 ms overhead per authorized request.

---

## 2. Current State

- **Single user model.** Every user is implicitly an admin of their own data.
- **RLS on all tables.** Every policy checks `auth.uid() = user_id`.
- **No role column.** The `users` table has no `role` field.
- **No shared data.** No `shared_resource` or `collaborator` tables.
- **No audit logging.** No record of who accessed what or when.

**Gap:** Adding a second user (collaborator, viewer) currently requires sharing a login. No granularity for read-only access, shared projects, or admin oversight.

---

## 3. Role Model

### 3.1 Roles (v1)

| Role | Description | Scope |
|---|---|---|
| **Admin** | Full system access, user management, billing, audits | All modules |
| **User** | Standard CRUD on own data, access to shared resources | Own modules + shared |
| **ReadOnly** | View-only access to assigned resources | Assigned only |

### 3.2 Roles (v2 — Q4 2026)

| Role | Description |
|---|---|
| **Collaborator** | Full CRUD on shared projects/notes only |
| **Viewer** | View-only on shared projects (no export) |
| **Mentor** | Read + comment on student goals/tasks |

### 3.3 Default Assignment

- On signup: `User` role.
- Admin promotes via admin panel or directly via Supabase.
- ReadOnly assigned per-shared-resource (not globally).

---

## 4. Permission Matrix

### 4.1 Global Permissions (by Role)

| Module | Action | Admin | User | ReadOnly |
|---|---|---|---|---|
| Tasks | Create | ✓ | ✓ | — |
| Tasks | Read (own) | ✓ | ✓ | ✓ |
| Tasks | Read (any) | ✓ | — | — |
| Tasks | Update | ✓ | ✓ | — |
| Tasks | Delete | ✓ | ✓ | — |
| Habits | Create | ✓ | ✓ | — |
| Habits | Read | ✓ | ✓ | ✓ |
| Habits | Update | ✓ | ✓ | — |
| Habits | Delete | ✓ | ✓ | — |
| Goals | Create | ✓ | ✓ | — |
| Goals | Read | ✓ | ✓ | ✓ |
| Goals | Update | ✓ | ✓ | — |
| Goals | Delete | ✓ | ✓ | — |
| Courses | Create | ✓ | ✓ | — |
| Courses | Read | ✓ | ✓ | ✓ |
| Courses | Update | ✓ | ✓ | — |
| Courses | Delete | ✓ | ✓ | — |
| Ideas | CRUD | ✓ | ✓ | — |
| Resources | CRUD | ✓ | ✓ | — |
| Income/Finance | CRUD | ✓ | ✓ | — |
| Analytics | Read | ✓ | ✓ | ✓ |
| **Admin** | Manage Users | ✓ | — | — |
| **Admin** | View Logs | ✓ | — | — |
| **Admin** | Manage Flags | ✓ | — | — |
| **Admin** | Clear Cache | ✓ | — | — |

### 4.2 Resource-Level Permissions (v2)

For shared resources (projects, notes, goal trees):

| Permission | Action | Description |
|---|---|---|
| `owner` | CRUD + manage collaborators | Full control |
| `editor` | CRUD | Full content edit |
| `commenter` | Read + comment | No content changes |
| `viewer` | Read only | No interaction |

---

## 5. Implementation Strategy

### 5.1 Supabase Custom Claims (JWT)

Role is stored as a custom JWT claim, set via Supabase `auth.users` metadata:

```sql
-- Add role to auth.users raw_app_meta_data
UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "user"}'::jsonb
WHERE id = 'user-uuid';

-- Or via Supabase admin API
const { data, error } = await supabase.auth.admin.updateUserById(userId, {
  app_metadata: { role: 'admin' },
})
```

JWT payload after login will include:

```json
{
  "sub": "user-uuid",
  "role": "admin",
  "app_metadata": {
    "role": "admin",
    "provider": "email"
  },
  "user_metadata": {
    "full_name": "Jane Doe"
  }
}
```

### 5.2 Database Schema

```sql
-- Users table extension
ALTER TABLE public.users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
  CHECK (role IN ('admin', 'user', 'readonly'));

-- Shared resources table (v2)
CREATE TABLE shared_resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_type TEXT NOT NULL,          -- 'project' | 'note' | 'goal_tree'
  resource_id UUID NOT NULL,           -- FK to the actual resource
  owner_id UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Collaborators junction table (v2)
CREATE TABLE resource_collaborators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_type TEXT NOT NULL,
  resource_id UUID NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id),
  permission TEXT NOT NULL DEFAULT 'viewer'
    CHECK (permission IN ('owner', 'editor', 'commenter', 'viewer')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(resource_type, resource_id, user_id)
);
```

---

## 6. RLS Policy Patterns

### 6.1 Helper Function

```sql
-- Get current user's role from JWT custom claim
CREATE OR REPLACE FUNCTION public.current_user_role()
RETURNS TEXT
LANGUAGE SQL STABLE
AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claims', true)::jsonb
      -> 'app_metadata'
      ->> 'role',
    'user'
  );
$$;
```

### 6.2 Per-Role Policies

```sql
-- Tasks table policies

-- Admin: full access
CREATE POLICY "admin_all_tasks"
  ON tasks
  FOR ALL
  USING (public.current_user_role() = 'admin')
  WITH CHECK (public.current_user_role() = 'admin');

-- User: own tasks only
CREATE POLICY "user_own_tasks"
  ON tasks
  FOR ALL
  USING (
    auth.uid() = user_id
    AND public.current_user_role() = 'user'
  )
  WITH CHECK (
    auth.uid() = user_id
    AND public.current_user_role() = 'user'
  );

-- ReadOnly: select only, own tasks
CREATE POLICY "readonly_view_tasks"
  ON tasks
  FOR SELECT
  USING (
    auth.uid() = user_id
    AND public.current_user_role() = 'readonly'
  );

-- Enable RLS (already enabled)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
```

### 6.3 Admin Bypass Policy

Admins bypass all user-level restrictions. They can read/update/delete any row. This is achieved by the `admin_all_tasks` policy above — PostgreSQL merges policies with OR, so if either `admin_all_tasks` or `user_own_tasks` passes, the row is accessible.

### 6.4 Row-Level vs Column-Level Security

| Approach | When to Use | Example |
|---|---|---|
| Row-level (RLS) | Entire row access control | User cannot see another user's tasks |
| Column-level | Sensitive fields | ReadOnly cannot see `goal_notes.private_reflection` |

For v1, row-level is sufficient. Column-level is added in v2 for private fields:

```sql
-- Column-level: hide private_reflection from readers
CREATE POLICY "hide_private_reflection"
  ON goal_notes
  FOR SELECT
  USING (
    auth.uid() = user_id
    OR public.current_user_role() = 'admin'
  );
```

---

## 7. API Authorization

### 7.1 Middleware

`apps/api/app/core/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from typing import List

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not permitted. Required: {self.allowed_roles}"
            )
        return user

# Usage
allow_admin = RoleChecker(["admin"])
allow_admin_or_user = RoleChecker(["admin", "user"])

@router.get("/admin/users")
async def list_users(admin: User = Depends(allow_admin)):
    result = await supabase.from_("users").select("*").execute()
    return result.data

@router.post("/tasks")
async def create_task(
    task: TaskCreate,
    user: User = Depends(allow_admin_or_user),
):
    result = await supabase.from_("tasks").insert(task.dict()).execute()
    return result.data
```

### 7.2 Resource-Level Authorization (v2)

```python
# apps/api/app/core/permissions.py
async def require_resource_access(
    resource_type: str,
    resource_id: str,
    required_permission: str,
    user: User,
):
    """Check if user has the required permission on a shared resource."""
    if user.role == "admin":
        return True  # Admin bypass

    # Check ownership
    owner = await supabase.from_("shared_resources") \
        .select("owner_id") \
        .eq("id", resource_id) \
        .single() \
        .execute()

    if owner.data and owner.data["owner_id"] == user.id:
        return True

    # Check collaborator permissions
    collab = await supabase.from_("resource_collaborators") \
        .select("permission") \
        .eq("resource_type", resource_type) \
        .eq("resource_id", resource_id) \
        .eq("user_id", user.id) \
        .single() \
        .execute()

    if not collab.data:
        raise HTTPException(403, "No access to this resource")

    perm_levels = {"owner": 4, "editor": 3, "commenter": 2, "viewer": 1}
    required_level = perm_levels.get(required_permission, 0)
    actual_level = perm_levels.get(collab.data["permission"], 0)

    if actual_level < required_level:
        raise HTTPException(403, f"Insufficient permissions. Need {required_permission}, have {collab.data['permission']}")

    return True
```

---

## 8. Frontend Authorization

### 8.1 Auth Context with Role

```typescript
// apps/web/lib/auth/AuthContext.tsx
interface AuthState {
  user: User | null
  role: 'admin' | 'user' | 'readonly'
  isLoading: boolean
}

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    role: 'user',
    isLoading: true,
  })

  useEffect(() => {
    supabase.auth.onAuthStateChange((event, session) => {
      const role = session?.user?.app_metadata?.role || 'user'
      setState({
        user: session?.user ?? null,
        role,
        isLoading: false,
      })
    })
  }, [])

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>
}
```

### 8.2 Role-Based Conditional Rendering

```typescript
// apps/web/components/auth/Can.tsx
import { useAuth } from '@/hooks/useAuth'

interface CanProps {
  roles: Array<'admin' | 'user' | 'readonly'>
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function Can({ roles, children, fallback = null }: CanProps) {
  const { role } = useAuth()
  return roles.includes(role) ? <>{children}</> : <>{fallback}</>
}

// Usage
<Can roles={['admin']} fallback={<p>Contact admin for access</p>}>
  <AdminPanel />
</Can>

<Can roles={['admin', 'user']}>
  <button onClick={handleCreateTask}>New Task</button>
</Can>
```

### 8.3 Route Guards

```typescript
// apps/web/lib/auth/ProtectedRoute.tsx
'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

interface ProtectedRouteProps {
  roles?: Array<'admin' | 'user' | 'readonly'>
  children: React.ReactNode
}

export function ProtectedRoute({ roles, children }: ProtectedRouteProps) {
  const { user, role, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isLoading) return
    if (!user) {
      router.push('/login')
      return
    }
    if (roles && !roles.includes(role)) {
      router.push('/403')
    }
  }, [user, role, isLoading, roles, router])

  if (isLoading) return <FullPageSpinner />
  if (!user) return null
  if (roles && !roles.includes(role)) return null

  return <>{children}</>
}

// Usage in layout/page
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute roles={['admin']}>
      {children}
    </ProtectedRoute>
  )
}
```

### 8.4 Hiding UI Elements

```typescript
// apps/web/hooks/useCan.ts
import { useAuth } from '@/hooks/useAuth'

export function useCan(requiredRole: 'admin' | 'user' | 'readonly'): boolean {
  const { role } = useAuth()
  const hierarchy = { admin: 3, user: 2, readonly: 1 }
  return hierarchy[role] >= hierarchy[requiredRole]
}

// Usage
function TaskItem({ task }: { task: Task }) {
  const canEdit = useCan('user')
  const canDelete = useCan('admin')

  return (
    <div>
      <span>{task.title}</span>
      {canEdit && <TaskEditButton task={task} />}
      {canDelete && <TaskDeleteButton task={task} />}
    </div>
  )
}
```

---

## 9. Multi-Tenancy

### 9.1 User Isolation via RLS

Every table already filters by `user_id`. Global RLS policy ensures no cross-tenant data leakage:

```sql
CREATE POLICY "universal_user_isolation"
  ON tasks
  FOR ALL
  USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM resource_collaborators rc
      WHERE rc.resource_type = 'tasks'
        AND rc.resource_id = tasks.id
        AND rc.user_id = auth.uid()
    )
    OR public.current_user_role() = 'admin'
  );
```

### 9.2 Data Sharing via `shared_resource` + `resource_collaborators`

```typescript
// apps/web/lib/sharing/share-resource.ts
export async function shareResource(
  resourceType: string,
  resourceId: string,
  collaboratorEmail: string,
  permission: 'editor' | 'commenter' | 'viewer',
): Promise<void> {
  // 1. Find user by email
  const { data: user } = await supabase
    .from('users')
    .select('id')
    .eq('email', collaboratorEmail)
    .single()

  if (!user) throw new Error('User not found')

  // 2. Find or create shared resource entry
  const { data: shared } = await supabase
    .from('shared_resources')
    .upsert({ resource_type: resourceType, resource_id: resourceId, owner_id: currentUserId })
    .select()
    .single()

  // 3. Add collaborator
  await supabase
    .from('resource_collaborators')
    .upsert({
      resource_type: resourceType,
      resource_id: resourceId,
      user_id: user.id,
      permission,
    })
}
```

### 9.3 Shared Resource UI

Share dialog at `/resource/share/[type]/[id]`:

```
┌────────────────────────────────────────┐
│  Share "Q3 Goals"                      │
│                                        │
│  Collaborators:                        │
│  ┌──────────┬──────────┬──────────┐   │
│  │ User    │ Role     │ Actions  │   │
│  ├──────────┼──────────┼──────────┤   │
│  │ Jane    │ Editor   │ [Remove] │   │
│  │ Bob     │ Viewer   │ [Remove] │   │
│  └──────────┴──────────┴──────────┘   │
│                                        │
│  Add: [email@example.com] [Add]       │
│  Permission: [Editor ▼]               │
└────────────────────────────────────────┘
```

---

## 10. Audit & Compliance

### 10.1 Audit Log Table

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  action TEXT NOT NULL,         -- 'role_change' | 'permission_check' | 'access_denied'
  target_type TEXT,             -- 'user' | 'task' | 'goal'
  target_id UUID,
  details JSONB DEFAULT '{}'::jsonb,
  ip_address INET,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);
```

### 10.2 Key Audit Events

| Event | Trigger | Audit Entry |
|---|---|---|
| Role change | Admin updates user role | `{action: "role_change", details: {from: "user", to: "admin"}}` |
| Permission denied | API 403 response | `{action: "access_denied", details: {resource: "/admin/users"}}` |
| Resource shared | Share dialog submitted | `{action: "resource_shared", details: {type: "project", permission: "editor"}}` |
| Data export | Admin exports user data | `{action: "data_export", details: {format: "json", count: 150}}` |

### 10.3 Audit Endpoint

```python
@router.get("/admin/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    admin: User = Depends(allow_admin),
):
    query = supabase.from_("audit_logs").select("*").order("created_at", ascending=False).limit(limit)
    if user_id:
        query = query.eq("user_id", user_id)
    if action:
        query = query.eq("action", action)
    result = await query.execute()
    return result.data
```

### 10.4 Permission Review Schedule

| Frequency | Activity | Who |
|---|---|---|
| Monthly | Review all admin users | Lead Engineer |
| Quarterly | Audit role changes in past quarter | Security Lead |
| Per Release | Verify new modules have RLS policies | Developer |

---

## 11. Appendices

### 11.1 SQL for RLS Policies — Full Set

```sql
-- ============================================
-- RLS Policies: Tasks
-- ============================================
CREATE POLICY "admin_all_tasks" ON tasks FOR ALL
  USING (public.current_user_role() = 'admin')
  WITH CHECK (public.current_user_role() = 'admin');

CREATE POLICY "user_own_tasks" ON tasks FOR ALL
  USING (auth.uid() = user_id AND public.current_user_role() = 'user')
  WITH CHECK (auth.uid() = user_id AND public.current_user_role() = 'user');

CREATE POLICY "readonly_view_tasks" ON tasks FOR SELECT
  USING (auth.uid() = user_id AND public.current_user_role() = 'readonly');

CREATE POLICY "collaborator_tasks" ON tasks FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM resource_collaborators rc
    WHERE rc.resource_type = 'tasks'
      AND rc.resource_id = tasks.id
      AND rc.user_id = auth.uid()
  ));

-- ============================================
-- RLS Policies: Goals (same pattern)
-- ============================================
CREATE POLICY "admin_all_goals" ON goals FOR ALL
  USING (public.current_user_role() = 'admin')
  WITH CHECK (public.current_user_role() = 'admin');

CREATE POLICY "user_own_goals" ON goals FOR ALL
  USING (auth.uid() = user_id AND public.current_user_role() = 'user')
  WITH CHECK (auth.uid() = user_id AND public.current_user_role() = 'user');

CREATE POLICY "readonly_view_goals" ON goals FOR SELECT
  USING (auth.uid() = user_id AND public.current_user_role() = 'readonly');

-- ============================================
-- RLS Policies: Habits, Courses, Ideas, Resources
--   → Same pattern as Tasks (replace table name)
-- ============================================

-- ============================================
-- Helper function (create once, use everywhere)
-- ============================================
CREATE OR REPLACE FUNCTION public.current_user_role()
RETURNS TEXT
LANGUAGE SQL STABLE
AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claims', true)::jsonb
      -> 'app_metadata'
      ->> 'role',
    'user'
  );
$$;
```

### 11.2 Role Migration Script

```typescript
// scripts/migrate-roles.ts
import { createClient } from '@supabase/supabase-js'

async function migrateRoles() {
  const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_KEY!)

  // Get all users
  const { data: users, error } = await supabase.auth.admin.listUsers()
  if (error) throw error

  for (const user of users.users) {
    const role = user.app_metadata?.role || 'user'

    // 1. Set JWT custom claim
    await supabase.auth.admin.updateUserById(user.id, {
      app_metadata: { ...user.app_metadata, role },
    })

    // 2. Sync to public.users table
    await supabase
      .from('users')
      .upsert({ id: user.id, email: user.email, role })
  }

  console.log(`Migrated ${users.users.length} users`)
}

migrateRoles().catch(console.error)
```

### 11.3 Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-06-11 | Architecture Team | Initial draft |
| — | — | — | — |

---

*End of Document — ENG-PERM-001*
