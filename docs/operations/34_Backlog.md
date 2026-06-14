# Product Backlog

## Overview

Prioritized backlog based on the 8-phase build plan (Chapter 12 of the Bible). Items organized by epic, with user stories, estimates, and dependencies. Each item maps to a specific module in the system.

## Priority Levels

- **P0**: Must have for usable product (Phase 1)
- **P1**: Core functionality (Phases 2-4)
- **P2**: Enhanced features (Phases 5-6)
- **P3**: Polish & monitoring (Phases 7-8)
- **P4**: Post-launch roadmap

## Epic: Core Foundation (Phase 1, Weeks 1-2)

### P0 - Authentication & Setup
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-001 | As a user, I can sign in with Google so that my data is private | 2 days | None | Done |
| F-002 | As a new user, I can complete a 5-step onboarding (Profile > Skills > Courses > Goals > Routine) | 3 days | F-001 | Done |
| F-003 | As a user, my profile stores name, college, year, skills, preferences | 1 day | F-001 | Done |

### P0 - Task Manager
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-004 | As a user, I can create a task with title, priority, category, due date | 1 day | F-001 | Done |
| F-005 | As a user, I can view tasks filtered by status (pending/in_progress/completed) | 1 day | F-004 | Done |
| F-006 | As a user, I can edit and delete tasks | 0.5 day | F-004 | Done |
| F-007 | As a user, I can mark a task as complete | 0.5 day | F-004 | Done |
| F-008 | As a user, I can set recurring tasks (daily/weekly/monthly) | 1 day | F-004 | Done |
| F-009 | As a user, overdue tasks auto-reschedule every 15 min | 1 day | F-004 | Done |

### P0 - Course Tracker
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-010 | As a user, I can add a course with mandatory deadline from any platform | 1 day | F-001 | Done |
| F-011 | As a user, I can log video/progress and see completion % | 0.5 day | F-010 | Done |
| F-012 | As a user, I see required daily minutes to meet deadline | 0.5 day | F-010 | Done |
| F-013 | As a user, I get alerted when a course is behind schedule | 0.5 day | F-010 | Done |

### P0 - Dashboard
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-014 | As a user, I see my top 3 prioritized tasks on dashboard | 1 day | F-004 | Done |
| F-015 | As a user, I see a productivity score (0-100) | 0.5 day | F-004, F-011 | Done |
| F-016 | As a user, I see an activity heatmap for last 30 days | 1 day | F-004 | Done |
| F-017 | As a user, I see ARIA's Pick recommendation | 0.5 day | F-004 | Done |

## Epic: Save Everything (Phase 2, Weeks 3-4)

### P1 - YouTube Knowledge Vault
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-018 | As a user, I can save a YouTube video with auto-thumbnail | 1 day | F-001 | Done |
| F-019 | As a user, I can mark videos as watched/pending | 0.5 day | F-018 | Done |
| F-020 | As a user, I receive AI summary of saved videos | 2 days | F-018, AI infra | Not started |
| F-021 | As a user, I can link videos to goals | 0.5 day | F-018, F-034 | Not started |
| F-022 | As a user, unsaved videos expire after 60 days | 0.5 day | F-018 | Not started |

### P1 - Resource Library
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-023 | As a user, I can save articles, books, repos, tools with URL | 1 day | F-001 | Done |
| F-024 | System auto-tags resources based on content | 1 day | F-023, AI infra | Not started |
| F-025 | As a user, I can search resources using natural language | 1 day | F-023 | Not started |
| F-026 | As a user, I can add resources to a reading queue | 0.5 day | F-023 | Not started |

### P1 - Idea Vault
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-027 | As a user, I can instantly capture an idea (title + description) | 1 day | F-001 | Done |
| F-028 | As a user, I can move ideas through pipeline: Raw > Researching > Validating > Building > Archived | 0.5 day | F-027 | Done |
| F-029 | AI runs market check on new ideas automatically | 2 days | F-027, AI infra | Not started |
| F-030 | AI enriches ideas with competitor analysis | 1 day | F-029 | Not started |

### P1 - Browser Extension
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-031 | Extension saves YouTube videos with one click | 2 days | Supabase sync | Not started |
| F-032 | Extension saves articles/resources with auto-tagging | 2 days | F-031 | Not started |
| F-033 | Extension works on Chrome and Firefox | 1 day | F-031 | Not started |

## Epic: ARIA & Memory (Phase 3, Weeks 5-6)

### P1 - ARIA Chat
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-034 | As a user, I can chat with ARIA and get contextual responses | 2 days | Ollama/Claude | Done (rule-based) |
| F-035 | ARIA remembers user preferences, facts, and patterns | 2 days | F-034 | Partial |
| F-036 | As a user, I can create tasks, update goals, save resources via chat | 2 days | F-034 | Partial |
| F-037 | ARIA builds context from profile, courses, goals, recent tasks | 1 day | F-034 | Partial |

### P1 - Daily Briefing
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-038 | System generates daily briefing at 7 AM with top tasks, sleep, weather | 2 days | F-014, F-046 | Done (agent exists) |
| F-039 | Briefing delivered as push notification + email + in-app banner | 1 day | F-038 | Partial |

### P2 - Weekly Review
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-040 | System generates weekly narrative review every Sunday 8 PM | 2 days | All trackers | Done (agent exists) |
| F-041 | Review emailed to user with insights and recommendations | 0.5 day | F-040 | Partial |

## Epic: Opportunity Radar (Phase 4, Weeks 7-9)

### P1 - Opportunity Discovery
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-042 | Radar scans 6+ categories at 6 AM daily (internships, hackathons, fellowships, etc.) | 2 days | Brave API | Done (mock data) |
| F-043 | Opportunities matched to user skills (40% min threshold) | 1 day | F-042 | Done |
| F-044 | Critical deadline alerts for opportunities closing within 48h | 1 day | F-042 | Not started |

### P1 - Opportunity Dashboard
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-045 | As a user, I can browse opportunities by type, skill match, deadline | 1 day | F-042 | Done |
| F-046 | As a user, I can track application status (saved/applied/accepted/rejected) | 0.5 day | F-045 | Done |

## Epic: Roadmap Engine (Phase 5, Weeks 10-11)

### P2 - Visual Roadmap Builder
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-047 | As a user, I can create roadmaps with 8 node types on React Flow canvas | 3 days | F-001 | Done |
| F-048 | As a user, I can paste text and AI builds the roadmap | 2 days | F-047, AI infra | Not started |
| F-049 | As a user, I can upload PDF/image and extract roadmap plan | 2 days | F-047, OCR | Not started |
| F-050 | As a user, I can adjust timing sliders (hours/day, days/week, intensity) | 1 day | F-047 | Done |

### P2 - Roadmap Intelligence
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-051 | Weekly AI update check - verifies roadmap items still current | 1 day | F-047 | Not started |
| F-052 | Hard deadline mode - works backwards from exam date | 1 day | F-047 | Not started |
| F-053 | Missed milestone auto-reschedule with downstream impact | 1 day | F-047 | Not started |
| F-054 | Scenario planning (what-if slider changes) | 1 day | F-047 | Not started |

## Epic: Full Student Tracking (Phase 6, Weeks 12-13)

### P2 - Income Tracker
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-055 | As a user, I can log income with amount, platform, date, hours | 1 day | F-001 | Done |
| F-056 | As a user, I see effective hourly rate, monthly totals, trends | 1 day | F-055 | Partial |
| F-057 | Weekly ROI report comparing income vs time invested | 1 day | F-055 | Not started |

### P2 - Project Tracker
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-058 | As a user, I can track projects through 6 phases (Planning > Maintain) | 1 day | F-001 | Done |
| F-059 | As a user, I can log blockers and resolve them | 0.5 day | F-058 | Done |
| F-060 | GitHub integration: commit activity on linked repos | 2 days | GitHub API | Not started |

### P2 - Academic Planner
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-061 | As a user, I can add subjects with credits and semester | 1 day | F-001 | Done |
| F-062 | As a user, I can log marks (assignment/midterm/final/practical) | 1 day | F-061 | Done |
| F-063 | CGPA calculator with projected CGPA | 1 day | F-062 | Done |
| F-064 | At-risk alerts for subjects below 40% | 0.5 day | F-062 | Done |
| F-065 | Exam countdown for upcoming exams | 0.5 day | F-061 | Done |

### P2 - Habit Engine
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-066 | As a user, I can create custom habits with frequency and time target | 1 day | F-001 | Done |
| F-067 | System tracks streak (current/best) and consistency % | 0.5 day | F-066 | Done |
| F-068 | Miss nudge - notification when habit skipped | 0.5 day | F-066 | Not started |
| F-069 | 30-day consistency report with trend | 1 day | F-066 | Not started |

## Epic: Monitoring System (Phase 7, Weeks 14-15)

### P2 - Sleep Monitor
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-070 | As a user, I can log bedtime/wake with one tap | 1 day | F-001 | Done |
| F-071 | System calculates sleep score and debt | 0.5 day | F-070 | Done |
| F-072 | Task adjustment based on poor sleep | 1 day | F-070, F-004 | Not started |
| F-073 | Bedtime reminder at configured time | 1 day | F-070 | Not started |
| F-074 | Google Fit integration for auto sleep detection | 2 days | Google Fit API | Not started |

### P2 - Time Tracker
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-075 | As a user, I can start/stop timer for any task | 1 day | F-001 | Done |
| F-076 | As a user, I can use Pomodoro mode (25/5) | 1 day | F-075 | Done |
| F-077 | Auto-stop timer after 15 min idle | 0.5 day | F-075 | Done |
| F-078 | Deep work detection (sessions >= 90 min) | 0.5 day | F-075 | Done |
| F-079 | Focus hour analysis - when are you most productive | 0.5 day | F-075 | Done |
| F-080 | Estimate accuracy tracking | 1 day | F-075 | Not started |

### P3 - Notification System
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-081 | Push notifications via browser/PWA | 2 days | PWA setup | Not started |
| F-082 | Email notifications via Resend (daily briefing, weekly review) | 1 day | Resend API | Partial |
| F-083 | SMS escalation for critical alerts via Twilio | 1 day | Twilio API | Not started |
| F-084 | Google Calendar two-way sync | 3 days | Google Calendar API | Not started |

## Epic: Polish & PWA (Phase 8, Weeks 16-17)

### P3 - PWA
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-085 | Service worker caches core app shell for offline use | 2 days | next-pwa | Not started |
| F-086 | IndexedDB stores user data for offline access | 2 days | F-085 | Not started |
| F-087 | Background sync on reconnect | 1 day | F-085 | Not started |

### P3 - Voice & Pattern Detection
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-088 | Voice input to ARIA via Web Speech API | 2 days | F-034 | Not started |
| F-089 | After 3 months data, ARIA surfaces behavioral insights | 3 days | F-034 | Not started |

### P3 - Production Readiness
| ID | Story | Estimate | Dependencies | Status |
|----|-------|----------|--------------|--------|
| F-090 | Lighthouse performance score > 90 on low-end Android | 2 days | All features | Not started |
| F-091 | Data export (JSON/CSV) from Settings | 1 day | None | Not started |
| F-092 | Security audit: RLS on all 21 tables | 1 day | F-001 | Not started |
| F-093 | Rate limiting on all API routes | 1 day | None | Done |

## Epic: Post-Launch (V2, Future)

### P4 - Intelligence Phase
| ID | Story | Estimate |
|----|-------|----------|
| F-094 | ARIA learns from 3+ months of user patterns | 5 days |
| F-095 | ML model predicts task completion likelihood | 5 days |
| F-096 | Auto-scheduling from parsed syllabus PDFs | 3 days |
| F-097 | Opportunity outcome analysis - what works | 3 days |
| F-098 | Weekly blind spots report | 2 days |

### P4 - Ecosystem Phase
| ID | Story | Estimate |
|----|-------|----------|
| F-099 | React Native mobile app | 4 weeks |
| F-100 | Google Calendar two-way sync | 3 days |
| F-101 | Notion import/export | 2 days |
| F-102 | Public REST API | 1 week |
| F-103 | Shared roadmaps and collaboration | 2 weeks |

### P4 - Community Phase
| ID | Story | Estimate |
|----|-------|----------|
| F-104 | Template marketplace | 2 weeks |
| F-105 | Anonymous productivity benchmarking | 1 week |
| F-106 | Public streak leaderboard | 3 days |
| F-107 | Plugin system | 3 weeks |

### P4 - Monetization Phase
| ID | Story | Estimate |
|----|-------|----------|
| F-108 | Freemium tier implementation | 1 week |
| F-109 | Team plans for college clubs | 2 weeks |
| F-110 | Placement preparation module | 3 weeks |
| F-111 | Resume builder from project data | 1 week |
| F-112 | LinkedIn auto-posting | 2 days |

## Backlog Summary

| Priority | Count | Total Est. (Days) |
|----------|-------|-------------------|
| P0 (Core) | 17 | 18.5 |
| P1 (Save + ARIA + Radar) | 24 | 30.5 |
| P2 (Roadmap + Tracking + Monitoring) | 29 | 34 |
| P3 (PWA + Polish) | 9 | 14 |
| P4 (V2 Future) | 15 | - |
| **Total** | **94** | **~97** |

## Dependencies Map

```
F-001 (Auth) ─┬─ F-002 (Onboarding)
              ├─ F-004 (Tasks) ── F-014 (Dashboard)
              ├─ F-010 (Courses)
              ├─ F-018 (YouTube)
              ├─ F-023 (Resources)
              ├─ F-027 (Ideas)
              ├─ F-034 (ARIA) ── F-038 (Briefing) ── F-039 (Push)
              ├─ F-042 (Radar) ── F-045 (Dashboard)
              ├─ F-047 (Roadmap)
              ├─ F-055 (Income)
              ├─ F-058 (Projects)
              ├─ F-061 (Academics)
              ├─ F-066 (Habits)
              ├─ F-070 (Sleep)
              └─ F-075 (Timer)
```

## Backlog Maintenance

- Backlog reviewed weekly after daily briefing cron run
- Items moved to "Current Sprint" in project board
- Done items archived with actual time spent
- Estimates refined based on actual velocity
- New feature requests added as P4 and prioritized quarterly
