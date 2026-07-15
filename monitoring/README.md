# Monitoring & Uptime

This directory contains configuration and tooling for external uptime monitoring of ARIA OS.

## UptimeRobot Setup

[UptimeRobot](https://uptimerobot.com) is the primary uptime monitor. The free tier supports 5 monitors checking every 5 minutes.

### 1. Create an Account

1. Go to [uptimerobot.com](https://uptimerobot.com) and sign up for a free account
2. Navigate to **My Settings** → **API Settings**
3. Generate a **Main API Key** (read-write)

### 2. Set Environment Variable

Add to your `.env.local` or production environment:

```env
UPTIMEROBOT_API_KEY=ur123456-7890abcdef1234567890abcdef
```

### 3. Add Monitors

The monitors are defined in `monitoring/uptimerobot-config.json`. To add them via the API:

```bash
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=$UPTIMEROBOT_API_KEY&format=json&type=1&url=https://api.secondbrain-os.com/health&friendly_name=ARIA%20OS%20-%20API%20Health&interval=300"
```

Repeat for each monitor in the config file. You can also use the UptimeRobot dashboard to add them manually.

### 4. Configure Alert Contacts

Alert contacts are defined in `uptimerobot-config.json` under `alert_contacts`. Supported types:

- Email (`notification_email`)
- SMS (paid tier)
- Slack/Teams webhooks (paid tier via integrations)

To add an email alert contact via API:

```bash
curl -X POST "https://api.uptimerobot.com/v2/newAlertContact" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=$UPTIMEROBOT_API_KEY&format=json&type=2&value=developer@secondbrain-os.com"
```

In the UptimeRobot dashboard, you can also configure Slack, Discord, or PagerDuty integrations under **Alert Contacts** → **Add Integration**.

---

## Health Check Script

As a fallback, `scripts/health-check.py` provides standalone Python-based health monitoring.

### Usage

```bash
# Basic single check
python scripts/health-check.py

# JSON output (for CI/CD integration)
python scripts/health-check.py --format json

# Prometheus metrics output (for Grafana)
python scripts/health-check.py --prometheus

# Send Slack notification on failure
python scripts/health-check.py --slack-webhook https://hooks.slack.com/services/xxx/yyy/zzz

# Run in a loop every 5 minutes
python scripts/health-check.py --repeat 5

# With custom timeout
python scripts/health-check.py --timeout 15
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0    | All endpoints UP |
| 1    | One or more endpoints DOWN |
| 2    | One or more endpoints DEGRADED (HTTP error, non-2xx/3xx) |

### CI/CD Integration

Add to your CI pipeline to gate deployments on health:

```yaml
- name: Health check
  run: python scripts/health-check.py --format json
```

### Cron Job (Linux/Mac)

```cron
*/5 * * * * cd /path/to/project && python scripts/health-check.py --slack-webhook $SLACK_WEBHOOK >> /var/log/health-check.log 2>&1
```

### Windows Task Scheduler

Create a scheduled task that runs every 5 minutes:

```
Program: python
Arguments: scripts/health-check.py --slack-webhook https://hooks.slack.com/services/xxx
Start in: C:\PROJECTS\My SecondBrain\ARIA OS - SecondBrain
```

### Prometheus + Grafana

Run the script with `--prometheus` and scrape the output:

```bash
# Run once and redirect to a file that Prometheus node_exporter can serve
python scripts/health-check.py --prometheus > /var/lib/prometheus/textfile/aria-health.prom
```

Or pipe to Prometheus Pushgateway if configured.

---

## Monitored Endpoints

| Friendly Name | URL | Expected |
|---|---|---|
| ARIA OS - API Health | `https://api.secondbrain-os.com/health` | 200 |
| ARIA OS - API Ready | `https://api.secondbrain-os.com/health/ready` | 200 |
| ARIA OS - Frontend | `https://secondbrain-os.vercel.app` | 200 |
| ARIA OS - Scheduler | `https://scheduler.secondbrain-os.com/health` | 200 |

---

## Alerting Strategy

| Severity | Condition | Notification |
|---|---|---|
| P0 (Critical) | Any endpoint DOWN for 5+ min | Email + Slack |
| P1 (High) | Degraded response for 2 consecutive checks | Email |
| P2 (Warning) | Intermittent timeout | Slack only |

---

## Grafana Dashboard

A pre-built Grafana dashboard is available at `monitoring/grafana-dashboard.json`. Import it into your Grafana instance and configure a Prometheus datasource to visualize:

- Request rate, error rate, and duration (RED metrics)
- Endpoint health status
- Uptime percentage per endpoint