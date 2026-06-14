---
version: 2.0.0
status: active
description: Enterprise email notification templates for ARIA system events — 9 templates with HTML+plain-text specs, A/B testing, tracking, i18n, CAN-SPAM/GDPR compliance, and rendering SLAs
model: none
max_tokens: 0
temperature: 0.0
last_updated: 2026-06-11
approved_by: architecture-review
classification: internal
compliance: can-spam, gdpr, ccpa-ready
delivery_service: resend (primary), sendgrid (fallback)
rate_limit: 100 per user per day
render_time_budget_ms: 150
---

# Email Notification Templates v2.0.0

Complete specification for all system-generated emails. Each template defines purpose, trigger, personalization, subject rules, A/B variants, tracking, compliance, and rendered examples.

---

## 1. Global Delivery Rules

| Rule              | Specification                                                         |
|-------------------|-----------------------------------------------------------------------|
| Rate limit        | 100 emails/user/day (excess queued for next day)                      |
| Suppression       | Check `users.notification_preferences.email_opt_out`                   |
| Quiet hours       | 21:00–07:00 user local — batch non-urgent to morning                  |
| Urgent override   | Password reset, security alerts bypass all suppressions                |
| Bounce handling   | 3 consecutive bounces → suppress 30 days, flag for review             |
| Unsubscribe       | `List-Unsubscribe: <mailto:unsubscribe@secondbrain.com?subject={id}>` + RFC 8058 one-click |

### Trigger & Suppression Matrix

| Template                | Trigger                          | Suppression                          | Max Freq    |
|-------------------------|----------------------------------|--------------------------------------|-------------|
| Weekly Review           | Cron Sun 18:00 local             | Opted out of weekly                  | 1x/week     |
| Daily Briefing          | Cron wake_time - 30min           | Opted out of daily                   | 1x/day      |
| Opportunity Alert       | New match > 75%                  | Job search paused; max 3/week        | 3x/week     |
| Missed Task Escalation  | Daily batch 20:00 local          | <3 overdue; nudges paused            | 1x/day      |
| Goal Milestone          | Progress 25/50/75/100%           | Milestones disabled                  | 4x/goal     |
| Habit Streak Lost       | Streak >=7d broken               | Nudges paused                        | 1x/week     |
| Course Alert            | Behind pace > 20%                | Academic nudges paused; 1x/3d        | 1x/3 days   |
| Sleep Alert             | 3 consecutive nights < 6h        | Health nudges paused                 | 1x/week     |
| Welcome Onboarding      | Registration complete            | Never (one-time)                     | 1x total    |

---

## 2. Template Specifications

### 2.1 Weekly Review
- **Purpose**: Summarize weekly productivity, habits, goals
- **Fields**: `user_name`, `week_range`, `completed_tasks`, `total_tasks`, `consistency_pct`, `avg_sleep_score`, `wins`, `improvements`, `closing_tip`
- **Subject**: "Your ARIA Weekly — {week_range}" (30-60 chars)
- **A/B**: (A) baseline / (B) "{user_name}, here's your weekly" / (C) "📊 Your Second Brain Weekly Review"
- **HTML**: 3-column score card (tasks/habits/sleep), wins list, tip block, cyberpunk dark theme, unsubscribe footer
- **Plain**: `Tasks: {c}/{t} Habits: {p}% Sleep: {s}/100\nWINS: {w}\nFOCUS: {i}\nTip: {t}`
- **Examples**: (1) 18/22 tasks, 85% habits, 78 sleep (2) 10/18 tasks, 62% habits, 65 sleep (3) 5/15 tasks, 30% habits — reset mode

### 2.2 Daily Briefing
- **Purpose**: Morning brief with focus, tasks, health context
- **Fields**: `user_name`, `time_of_day`, `date`, `focus_today`, `top_tasks`, `additional_sections`
- **Subject**: "☀️ Your Briefing — {date}" (40-60 chars)
- **Examples**: (1) 4h deep work, 3 tasks, 7.5h sleep (2) Exam week, DS June 13, request extensions (3) Weekend light day

### 2.3 Opportunity Alert
- **Purpose**: Career opportunity match >= 75%
- **Fields**: `opportunity_title`, `company`, `type`, `match_score`, `deadline`, `matching_skills`, `highlight_skills`, `url`
- **Subject**: "🔍 New {type}: {title}" (max 60 chars) | **Priority**: High (time-sensitive)
- **HTML**: Card with match score badge, skill tags, CTA button
- **Examples**: (1) SDE Intern Google 92%, Jun 25 (2) Backend Engineer Stripe 88%, Jul 1 (3) Amazon walk-in Bangalore 85%, Jun 15

### 2.4 Missed Task Escalation
- **Purpose**: Overdue task alert with recovery suggestions
- **Trigger**: >=3 overdue at daily batch 20:00
- **Fields**: `missed_count`, `task_list`, `suggestions`
- **Subject**: "⚠️ {n} tasks need attention" (max 50 chars)
- **Examples**: (1) 3 overdue — extension for Compiler PA4 (2) 8 overdue crisis — 2 P0, recovery plan (3) 1 overdue — read DDIA commute

### 2.5 Goal Milestone
- **Purpose**: Celebrate 25/50/75/100% progress
- **Subject**: "🎯 {pct}% — {goal}" (max 50 chars) | **Priority**: Low
- **Examples**: (1) 50% capstone — ERD done, Raft in progress (2) 100% 12 tech books in 5.5 months (3) 25% 5K — pace improving

### 2.6 Habit Streak Lost
- **Purpose**: Supportive nudge when streak >=7d breaks
- **Subject**: "🔥 Streak broken: {habit}" (max 50 chars) | **Priority**: Low
- **Examples**: (1) 14d run — 3rd reset, just 10 min today (2) 30d journaling — write 1 line restart (3) 7d LeetCode — weekend easy problem

### 2.7 Course Alert
- **Purpose**: Course behind pace > 20%
- **Subject**: "📚 {course} — falling behind" (max 50 chars) | **Priority**: Medium
- **Examples**: (1) DS 35% behind, deadline Jun 13, 2h/day (2) Compiler 50% behind critical, extend (3) ML 5% behind, extra 30min

### 2.8 Sleep Alert
- **Purpose**: 3 consecutive nights < 6h
- **Subject**: "😴 Sleep: {avg}h avg — {n} nights" (max 50 chars) | **Priority**: Medium
- **Examples**: (1) 5.1h avg, score 82→68→55, cognitive -20% (2) 4.8h 5 nights critical, memory -40% (3) Recovery: 6.5h improving

### 2.9 Welcome Onboarding
- **Purpose**: New user first steps (one-time, 1 min delivery)
- **Subject**: "Welcome to ARIA — set up your Second Brain" (max 45 chars)
- **Examples**: (1) 3-step: profile 30s, goal 1m, task 1m (2) Welcome back: 47 tasks preserved, 5 goals (3) CSE orientation: courses, goals, insights

---

## 3. A/B Testing

| Property        | Specification                                                    |
|-----------------|------------------------------------------------------------------|
| Assignment      | Random at first send, sticks per template type, resets every 90d |
| Metrics         | open_rate, click_rate                                            |
| Min sample      | 500 per variant                                                  |
| Winner          | 95% confidence after 7 days → auto-promoted, losers archived     |

---

## 4. Tracking & Compliance

### 4.1 Tracking
- **Open**: 1x1 pixel `https://track.secondbrain.com/o/{email_id}.png` (conditional on `analytics_consent`)
- **Links**: Wrapped `https://track.secondbrain.com/c/{id}?url={target}` (exclude unsubscribe/privacy)
- **Data**: `email_id`, `user_id`, `template`, `opened_at`, `clicked_at`, `user_agent`, `ip_country`

### 4.2 Compliance

| Standard   | Requirement                 | Implementation                          |
|------------|-----------------------------|------------------------------------------|
| CAN-SPAM   | Physical address            | "123 Tech Lane, San Francisco, CA 94105" |
| CAN-SPAM   | Honest subjects             | Template-enforced, no deception          |
| CAN-SPAM   | Opt-out honored 10 days     | Immediate (exceeds requirement)          |
| GDPR       | Unsubscribe link            | Footer link + List-Unsubscribe header    |
| GDPR       | Tracking consent            | Pixel conditional on user flag           |
| GDPR       | Right to erasure            | Unsubscribe includes data deletion opt   |
| Universal  | Auth headers                | SPF/DKIM/DMARC on `secondbrain.com`      |
| Universal  | Email headers               | `Precedence: bulk`, `X-Entity-Ref-ID`    |

**Footer (all emails):**
```
ARIA OS — Your Second Brain | 123 Tech Lane, San Francisco, CA 94105
Unsubscribe · Settings · Privacy Policy
```

---

## 5. Internationalization

| Property        | Specification                                                 |
|-----------------|---------------------------------------------------------------|
| Encoding        | UTF-8, `<meta charset="utf-8">`                               |
| Date formats    | en-US: "June 11, 2026" / en-IN: "11 June 2026"               |
| Number formats  | en-US: "1,234.56" / en-IN: "1,234.56"                        |
| Currency        | en-US: "$1,234" / en-IN: "₹1,235"                            |
| Source          | `packages/shared/utils/i18n/email_{locale}.json`              |

---

## 6. Rendering & Fallback

| Phase                | Budget  | Engine                    |
|----------------------|---------|---------------------------|
| HTML render          | 50ms    | Mustache.js / pystache    |
| Plain-text render    | 30ms    | Same engine               |
| Footer + tracking    | 20ms    | Template partial + inject |
| Queue delivery       | 50ms    | Resend API                |
| **Total**            |**150ms**|                           |

**Missing field fallback**: Replace with `""` (never null). Numerical → `0`/`N/A`. Critical fields (`user_name`, `unsubscribe_url`) → abort send, log ERROR.

---

## 7. Version History

| Version | Date       | Author             | Changes                                      |
|---------|------------|--------------------|----------------------------------------------|
| 2.0.0   | 2026-06-11 | Architecture Team  | 9 templates, A/B configs, tracking, i18n, compliance, rendering SLA |
| 1.0.0   | 2026-01-15 | Initial            | 4 plain-text templates                       |
