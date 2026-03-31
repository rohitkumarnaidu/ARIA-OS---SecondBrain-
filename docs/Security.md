# Security

## Authentication

### Supabase Auth
- Google OAuth for one-click login
- No password storage needed
- JWT tokens with 7-day expiry
- Token refresh handled automatically

### Setup
```python
# In Supabase Dashboard:
# 1. Authentication > Providers > Google
# 2. Enable Google provider
# 3. Add your Google Cloud OAuth credentials
```

---

## Authorization

### Row Level Security (RLS)

Every table has RLS enabled:

```sql
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see own tasks" ON tasks
  FOR ALL
  USING (auth.uid() = user_id);
```

**Standard Policy for All Tables:**
```sql
CREATE POLICY "Users can only see own data" ON table_name
  FOR ALL
  USING (auth.uid() = user_id);
```

### Tables Requiring RLS
- [x] users
- [x] tasks
- [x] subtasks
- [x] task_dependencies
- [x] courses
- [x] videos
- [x] resources
- [x] ideas
- [x] goals
- [x] opportunities
- [x] income_entries
- [x] projects
- [x] subjects
- [x] marks
- [x] habits
- [x] habit_logs
- [x] sleep_logs
- [x] time_entries
- [x] chat_messages
- [x] aria_memory
- [x] daily_logs

---

## API Security

### Token Validation
All API routes validate the JWT token:
```python
from app.core.auth import get_current_user

@router.get("/tasks")
async def get_tasks(current_user = Depends(get_current_user)):
    # Only authenticated users can access
    return tasks
```

### Environment Variables
Never commit sensitive data:
```
# .gitignore
.env
.env.local
.env.*.local
```

---

## Rate Limiting

### Supabase Limits
- Free tier: 60 requests/minute
- Pro tier: 300 requests/minute

### Implementation
```python
# In Supabase Dashboard:
# 1. Go to API Settings
# 2. Enable Rate Limiting
# 3. Set limits per endpoint
```

---

## Data Protection

### Encryption
- All data encrypted at rest (Supabase)
- All data encrypted in transit (TLS/HTTPS)

### Backup
- Supabase provides daily automatic backups
- Point-in-time recovery available on Pro tier

### Export
- Users can export all data as JSON/CSV
- Available in Settings page

---

## Web Security Headers

### Next.js Configuration
```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },
};
```

---

## PWA Security

### Service Worker
- Only cache same-origin resources
- No cross-origin caching
- Clear cache on logout

### Manifest
```json
{
  "name": "Second Brain OS",
  "short_name": "SecondBrain",
  "display": "standalone",
  "same_origin": true
}
```

---

## Vulnerability Prevention

| Issue | Prevention |
|-------|------------|
| SQL Injection | ORM (SQLAlchemy) handles escaping |
| XSS | React auto-escapes content |
| CSRF | Supabase handles automatically |
| Token Theft | Short expiry + refresh tokens |
| Data Leakage | RLS on every table |

---

## Audit Checklist

Before deployment, verify:
- [ ] RLS enabled on all 21 tables
- [ ] No API keys in client code
- [ ] HTTPS enforced
- [ ] Environment variables in .gitignore
- [ ] Rate limiting configured
- [ ] Security headers added
- [ ] Data export works
- [ ] Logout clears all data

---

## Incident Response

If security breach occurs:
1. **Immediate:** Rotate all API keys
2. **Investigate:** Check logs for unauthorized access
3. **Notify:** Alert affected users
4. **Fix:** Patch vulnerability
5. **Review:** Update security measures
