# Firefighter Runbooks

| Field | Value |
|---|---|
| Document ID | OPS-FRB-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Internal — Operations |
| Owner | Developer |
| Last Updated | 2026-07-11 |
| Review Cycle | Monthly |

---

## Scenario 1: AI Provider Down (Ollama + Claude)

**Detection:** Circuit breaker open, `/health/ready` returns `ai_unavailable`, agents return fallback responses.

**Triage:**
```bash
# 1. Check if Mistral model is loaded
ollama ps

# 2. Check if Ollama process is responding
curl -s -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d '{"model":"mistral","prompt":"hi","stream":false}'

# 3. Check circuit breaker state
python -c "from ai.client import llm; print('Ollama:', llm.ollama_circuit.state, '| Claude:', llm.claude_circuit.state)"

# 4. Check health endpoint
curl -s http://localhost:8000/health/ready | python -c "import sys,json; print(json.load(sys.stdin).get('dependencies',{}))"
```

**Mitigation:**
1. If Ollama down: `ollama serve` → `ollama pull mistral:7b`
2. If circuit breaker is OPEN: wait 60s for auto-cooldown or restart API service
3. If both Ollama + Claude down: service runs in degraded mode (algorithmic fallback)
4. Verify: `/health/ready` → ai_provider should show available

**Escalate after:** 15 min if unable to restore

---

## Scenario 2: Database Unreachable

**Detection:** 500 errors across all endpoints, Supabase dashboard shows connection errors, health check fails.

**Triage:**
```bash
# 1. Check health endpoint
curl -s http://localhost:8000/health/ready | python -c "import sys,json; print(json.load(sys.stdin).get('dependencies',{}).get('supabase',{}))"

# 2. Check Supabase dashboard
open https://supabase.com/dashboard/project/<project-id>/database/connections
```

**Mitigation:**
1. Check Supabase status page: https://status.supabase.com
2. If maintenance window: wait for completion, monitor uptime
3. If connection pool exhausted: restart FastAPI app to release connections
4. Check IP allowlist in Supabase dashboard → Authentication → Settings
5. Verify `SUPABASE_URL` and `SUPABASE_KEY` in .env (rotate if compromised)

**Escalate after:** 10 min → Supabase support

---

## Scenario 3: High Error Rate (>5%)

**Detection:** Sentry alert, monitoring dashboard shows error rate spike, user reports of failures.

**Triage:**
```bash
# 1. Check Sentry for top errors
open https://sentry.io/organizations/<org>/issues/

# 2. Check recent deployments
git log --oneline -10

# 3. Check API logs
Get-Content -Path logs/api.log -Tail 100 | Select-String "ERROR"
```

**Mitigation:**
1. If specific endpoint failing: isolate route, check recent changes to that file
2. If AI-related: run Scenario 1 triage
3. Rollback if recent deploy caused it: `railway rollback --service api`
4. File GitHub issue with reproduction steps

**Escalate after:** 30 min → Developer (shared Slack channel)

---

## Scenario 4: Rate Limit Exhausted

**Detection:** 429 responses in logs, users report "Too Many Requests" errors, slow experience.

**Triage:**
```bash
# 1. Check rate limit metrics
python -c "from shared.utils.rate_limiter import rate_limiter; print(rate_limiter.get_stats())"

# 2. Check if traffic is legitimate or abuse
Get-Content -Path logs/api.log -Tail 200 | Select-String "429"
```

**Mitigation:**
1. If abuse detected: block offending IPs via middleware config (see `packages/shared/utils/rate_limiter.py`)
2. If legitimate traffic spike: increase rate limit window/max in `.env` (`RATE_LIMIT_MAX`, `RATE_LIMIT_WINDOW`)
3. Chat endpoint has lower limits (30 req/min) — check if that's the bottleneck
4. Monitor for 15 min after change, verify 429s drop

**Escalate after:** 30 min → Developer

---

## Scenario 5: Scheduler Not Firing

**Detection:** Missed daily briefings, stale data, no weekly review generated, alerts from cron job health checks.

**Triage:**
```bash
# 1. Check scheduler health
curl -s http://localhost:8000/health/ready | python -c "import sys,json; print(json.load(sys.stdin).get('dependencies',{}).get('scheduler',{}))"

# 2. Check scheduler logs
Get-Content -Path logs/scheduler.log -Tail 50

# 3. Check scheduler process
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "scheduler" }
```

**Mitigation:**
1. Restart scheduler: `python services/scheduler/main.py`
2. Verify all 15 cron jobs registered:
   ```bash
   python -c "
   from services.scheduler.main import scheduler
   for job in scheduler.get_jobs():
       print(f'{job.id}: next run at {job.next_run_time}')
   "
   ```
3. Manually trigger missed jobs via automation endpoints:
   - `POST /api/v1/automation/trigger/briefing`
   - `POST /api/v1/automation/trigger/radar`
   - `POST /api/v1/automation/trigger/weekly-review`
4. Add monitoring: ensure scheduler logs contain `JOB_EXECUTED` for every expected run

**Escalate after:** 1 hour → Developer (check Railway if deployed there)

---

## Scenario 6: Security Breach (Suspected)

**Detection:** Unusual access patterns in logs, leaked credentials on GitHub, user report of unauthorized activity, audit log anomalies.

**Triage — STOP AND ROTATE FIRST:**
```bash
# 1. Rotate ALL secrets immediately
# Supabase keys: https://supabase.com/dashboard → Project Settings → API → Regenerate
# JWT secret: update .env, restart API
# Claude API key: https://console.anthropic.com → API Keys → Revoke

# 2. Force re-authentication
# Update auth middleware to invalidate all current tokens
# In Supabase dashboard: Authentication → Users → Revoke all sessions

# 3. Check audit logs
Get-Content -Path logs/audit.log -Tail 200 | Select-String "suspicious|unauthorized|failed"
```

**Mitigation:**
1. Rotate Supabase `SUPABASE_KEY` and `SUPABASE_SERVICE_KEY` immediately
2. Rotate `JWT_SECRET` — all users will need to re-login
3. Rotate `CLAUDE_API_KEY` — update in .env and Railway/Vercel env vars
4. Review GitHub for leaked keys: `gh secret list` — verify no exposed tokens
5. Check git history for committed secrets: `git log --all -p | Select-String "eyJ|sk-|api_key"` (first 10 matches)
6. Check Supabase Audit Logs for unauthorized queries
7. Run `python scripts/attack-scenarios.py` for automated security scan

**Report:**
- If confirmed data access: file incident report in `docs/security/incidents/`
- Post-mortem within 24 hours
- Update SEC-POLICY-IR-001 with lessons learned

**Escalate after:** Immediate — Developer (phone/SMS)

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial firefighter runbooks (6 scenarios) |
