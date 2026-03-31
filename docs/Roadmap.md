# Build Roadmap

## Overview

17-week build plan divided into 8 phases.

---

## Phase 1: Core Foundation (Week 1-2)

**Goal:** Working app you can log into and use from Day 1

### Tasks
- [ ] Set up Next.js 14 + Tailwind + Supabase
- [ ] Create all 21 tables with RLS
- [ ] Implement Google Auth
- [ ] Deploy to Vercel
- [ ] Build User Profile with skills list
- [ ] Build 5-step onboarding wizard
- [ ] Create Task Manager (CRUD, priority, category)
- [ ] Create Course Tracker (add, progress, deadline)
- [ ] Build Dashboard with task overview
- [ ] Set up basic auto-reschedule cron (15 min)

### Deliverable
Working app with login, tasks, courses, dashboard

---

## Phase 2: Save Everything (Week 3-4)

**Goal:** YouTube vault, resource library, idea vault, browser extension

### Tasks
- [ ] Build YouTube Knowledge Vault
  - Save videos, AI summary, goal linking
  - Watch scheduling, 60-day expiry
- [ ] Build Resource Library
  - Save articles, books, GitHub repos
  - Auto-tagging, natural language search
- [ ] Build Idea Vault
  - Capture ideas, status pipeline
  - AI market check on new ideas
- [ ] Build Browser Extension (WXT)
  - One-click save from any page
  - Works on Chrome/Firefox
- [ ] Integrate Claude API for summaries
- [ ] Build Resurface Engine
  - Surface relevant items when working on topic

### Deliverable
All save modules working, extension deployed

---

## Phase 3: ARIA & Memory (Week 5-6)

**Goal:** ARIA chat works, knows you, can take actions

### Tasks
- [ ] Build ARIA chat panel
- [ ] Set up Ollama with Llama 3.1
- [ ] Implement context builder
  - Serialize profile, goals, courses into prompt
- [ ] Create aria_memory table
  - Store preferences, facts, patterns
- [ ] Implement chat-triggered actions
  - Add task, update goal, save resource via chat
- [ ] Build Daily Briefing Edge Function
  - Runs 7 AM, generates briefing
  - Push + email + in-app
- [ ] Build Weekly Review Edge Function
  - Runs Sunday 8 PM
  - Narrative review via Claude

### Deliverable
Working AI assistant with memory

---

## Phase 4: Opportunity Radar (Week 7-9)

**Goal:** Every morning, relevant opportunities are waiting

### Tasks
- [ ] Set up Brave Search API
- [ ] Build Opportunity Radar Edge Function
  - Runs 6 AM daily
  - Scans 6 categories
- [ ] Implement matching algorithm
  - Skill match score
  - Deadline urgency
  - History personalization
- [ ] Build Opportunities Dashboard
  - Filters, apply tracking, countdowns
- [ ] Add Critical Deadline Alerts
  - Push notification for < 48 hours
- [ ] Build Opportunity Profile Editor
  - Fine-tune what radar searches

### Deliverable
Automated opportunity discovery

---

## Phase 5: Roadmap Engine (Week 10-11)

**Goal:** Every goal has a visual, smart, auto-updating plan

### Tasks
- [ ] Integrate React Flow canvas
- [ ] Build visual drag-and-drop builder
- [ ] Create 8 node types
- [ ] Implement text-to-roadmap parser
  - Paste text, AI builds roadmap
- [ ] Add PDF/image upload
  - Extract syllabus/plan using Claude Vision
- [ ] Build template library
  - 8 pre-built roadmap types
- [ ] Implement timing sliders
  - Real-time recalculation
- [ ] Add Hard Deadline Mode
  - Work backwards from exam date
- [ ] Build Weekly AI Update Checker
  - Verify roadmap items still current

### Deliverable
Visual roadmap builder for all goals

---

## Phase 6: Income, Projects, Academics (Week 12-13)

**Goal:** Full student life tracking

### Tasks
- [ ] Build Income Sources Dashboard
  - Log entries, monthly summary
  - Effective hourly rate calculation
- [ ] Build Project Tracker
  - Phase tracking (Kanban)
  - Next action rule
  - Blocker logging
- [ ] Integrate GitHub API
  - Link repos to projects
  - Weekly commit check
  - Skill profile auto-update
- [ ] Build LinkedIn Post Generator
  - Draft posts on milestones
- [ ] Build Academic Planner
  - Subjects, marks, CGPA calculator
  - At-risk alerts
- [ ] Build Habit Engine
  - Custom habits, streaks
  - Goal linking, consistency reports

### Deliverable
Complete life tracking

---

## Phase 7: Reminders, Sleep, Time (Week 14-15)

**Goal:** System watches you even when not looking

### Tasks
- [ ] Build full reminder system
  - Push notifications
  - Email via Resend
  - SMS via Twilio (escalation)
- [ ] Build Sleep Monitor
  - Bedtime/wake logging
  - Quality rating, score
  - Task adjustment based on sleep
  - Google Fit integration (optional)
- [ ] Build Time Tracker
  - Start/stop timer per task
  - Pomodoro mode
  - Deep work detection
  - Focus hour analysis
- [ ] Build Habit Reminders
  - Miss detection, streak alerts
- [ ] Integrate Google Calendar
  - Two-way sync

### Deliverable
Complete monitoring system

---

## Phase 8: Polish & PWA (Week 16-17)

**Goal:** Fast, offline-capable, voice-enabled

### Tasks
- [ ] Build PWA with next-pwa
  - Service worker
  - IndexedDB offline storage
  - Background sync
- [ ] Add Voice Input
  - Web Speech API for ARIA
- [ ] Implement ARIA Pattern Detection
  - After 3 months data
  - Deep behavioral insights
- [ ] Mobile Optimization
  - Lighthouse score > 90
  - Works on low-end Android
- [ ] Add Data Export
  - JSON/CSV export in Settings
- [ ] Security Audit
  - Verify RLS on all tables
  - No API keys in client
  - Rate limiting

### Deliverable
Production-ready PWA

---

## Priority Order

If running short on time, build in this order:

1. **Phase 1** - Core foundation (non-negotiable)
2. **Phase 3** - ARIA (makes system intelligent)
3. **Phase 2** - Save modules (changes behavior)
4. **Phase 4** - Opportunity radar (biggest advantage)
5. **Phase 5** - Roadmap engine (visual planning)
6. **Phase 6** - Income/Projects (real builder features)
7. **Phase 7** - Monitoring (staying on track)
8. **Phase 8** - Polish (production quality)

---

## Quick Start

### Week 1-2: Phase 1
- Set up Next.js + Supabase
- Login + Tasks + Courses + Dashboard
- Deploy to Vercel

### Week 3-4: Phase 2
- YouTube Vault + Resources + Ideas
- Browser Extension

### Week 5-6: Phase 3
- ARIA Chat + Memory
- Daily Briefing

### Week 7+: Continue with phases

---

## Milestones

| Week | Milestone |
|------|-----------|
| 2 | Working task manager you actually use |
| 4 | Save everything through extension |
| 6 | ARIA knows you and chats |
| 9 | Opportunities found automatically |
| 11 | Visual roadmaps for all goals |
| 13 | Track money, projects, marks |
| 15 | Sleep and time fully tracked |
| 17 | Production PWA ready |

---

## Tips

1. **Start using Phase 1 from Day 1** - Don't wait to finish building
2. **Use Ollama** - Keep costs at zero
3. **Mobile-first** - Most usage will be on phone
4. **Focus on daily briefing** - This is the main value
5. **Enable RLS from Day 1** - Security first
