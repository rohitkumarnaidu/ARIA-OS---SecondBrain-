# Canary Deployments & A/B Testing

## Overview
ARIA OS uses **feature-flag-gated canary deployments** — new features deploy behind a flag, then ramp percentage gradually. Zero code rollback: just set `enabled=false`.

## Architecture

```
                     ┌─────────────────────┐
                     │  Feature Flag Admin  │
                     │  API + Supabase DB   │
                     └────────┬────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Control     │    │  Canary 5%   │    │  Canary 50%  │
│  (v1)        │    │  (v2 flag)   │    │  (v2 flag)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Feature Flag System

### Server-Side (`packages/shared/utils/feature_flags.py`)
- In-memory store with periodic DB refresh (60s TTL)
- Env-var override via `FF_` prefix (e.g., `FF_NEW_DASHBOARD=true`)
- User segmentation by user ID list
- Percentage rollout via hash bucket (`sha256(user_id:key) % 100`)

### Admin API (`apps/api/app/api/feature_flags.py`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/feature-flags/` | List all flags |
| GET | `/{key}` | Get flag details |
| GET | `/{key}/evaluate` | Evaluate flag for user |
| POST | `/` | Create flag |
| PUT | `/{key}` | Update flag |
| DELETE | `/{key}` | Delete flag |

### Client-Side (`apps/web/lib/utils/feature-flags.ts`)
- `featureFlags.isEnabled(key, userId)` — boolean check
- `featureFlags.getVariant(key, userId)` — 'control' | 'treatment'
- `featureFlags.evaluate(key, userId)` — API-backed evaluation with cache
- Auto-refresh every 60s

## Canary Workflow

### 1. Create flag
```bash
curl -X POST /api/v1/feature-flags/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"key": "new.dashboard", "enabled": true, "rollout_percentage": 5}'
```

### 2. Deploy behind flag
```python
from shared.utils.feature_flags import flags

if flags.get("new.dashboard", user_id=user_id):
    return await new_dashboard_response(user_id)
else:
    return await old_dashboard_response(user_id)
```

### 3. Monitor
```bash
# Track error rates and latency
k6 run tests/performance/load-test-crud.js

# Check flag split
curl /api/v1/analytics/feature-flag?key=new.dashboard
```

### 4. Ramp
```bash
# 5% → 25% → 50% → 100%
curl -X PUT /api/v1/feature-flags/new.dashboard \
  -d '{"rollout_percentage": 25}'
```

### 5. Finalize
```bash
# At 100% for 24h+ with no issues:
curl -X PUT /api/v1/feature-flags/new.dashboard \
  -d '{"rollout_percentage": 100}'
# Then remove dead code in next release
```

## Rollback (Instant)
```bash
# Kill switch — zero code change
curl -X PUT /api/v1/feature-flags/new.dashboard \
  -d '{"enabled": false}'
# Traffic immediately reverts to control.
```

## Docker Compose

### Production (stable)
```yaml
# docker-compose.yml — always the current stable release
services:
  api:
    image: ghcr.io/org/aria-api:latest
```

### Canary override
```yaml
# infrastructure/canary/docker-compose.canary.yml
services:
  api-canary:
    image: ghcr.io/org/aria-api:canary
    ports: ["8001:8000"]
    labels:
      "traffic.weight": "5"
      "feature.flag": "canary.api-v2"
```

## CI/CD

### Canary workflow (`.github/workflows/canary.yml`)
1. Build `canary` Docker tag from feature branch
2. Deploy to canary environment
3. Run smoke tests (30s)
4. If smoke tests pass → set `rollout_percentage=5`
5. Monitor for 15min
6. On success → auto-promote to stable
7. On failure → auto-rollback flag to `enabled=false`

## A/B Testing

### Define an experiment
```python
variant = flags.get_variant("checkout.button-color", user_id)
# variant = "control" (blue) or "treatment" (green)
```

### Measure
```python
@router.post("/api/v1/analytics/experiment")
async def log_experiment(user_id: str, experiment: str, variant: str, metric: str, value: float):
    # Store in analytics table
```

### Analyze
```sql
SELECT variant, AVG(conversion_rate) FROM experiment_results
WHERE experiment = 'checkout.button-color'
GROUP BY variant;
```

## Security
- All flag changes are audited via `audit.py`
- Flag evaluation is idempotent per user (hash bucket is stable)
- Env var overrides cannot exceed 100% rollout
