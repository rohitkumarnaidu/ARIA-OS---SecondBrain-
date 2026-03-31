# Product Requirements Document (PRD)

## Project Overview

**Project Name:** Second Brain OS  
**Project Type:** Personal AI Productivity System  
**Core Functionality:** A personal AI system that acts as memory, advisor, opportunity scanner, and daily planner for BTech CSE students who want to become builders.  
**Target Users:** BTech CSE students who want to build real things, earn money, and gain experience while in college.

## Problem Statement

BTech CSE students face:
- Too many courses registered and forgotten
- YouTube videos saved and never watched
- Startup ideas at 2 AM that disappear by morning
- Internship deadlines missed
- Skills meant to learn 6 months ago but never started
- Everything stays separate instead of compounding

## Solution

Second Brain OS is a personal AI system that:
- Acts as your memory - remembers everything you forget
- Acts as your advisor - tells you what to do each morning
- Acts as opportunity scanner - watches internet for matching opportunities
- Connects learning to building to income - everything compounds

## Core Design Principles

1. **Owned Entirely By You** - No subscription, data stays yours
2. **Zero Miss Policy** - Every task either gets done, rescheduled, or explicitly dropped
3. **Active Intelligence** - System pushes info to you, not just passive storage
4. **Build First** - Everything connects to building real things
5. **Honest About Status** - No false progress, real tracking
6. **Offline First** - Works without internet
7. **Privacy by Default** - Your data never训练的AI共享

## User Personas

### Primary Persona
- **Name:** BTech CSE Student
- **Age:** 18-22 years
- **Goals:** Build real projects, earn money, get internships at startups
- **Pain Points:** Too many things to track, ideas lost, deadlines missed

## Functional Requirements

### Module 1: Dashboard & Morning Briefing
- Daily AI briefing at 7 AM with top 3 tasks
- Productivity score (0-100)
- Activity heatmap (GitHub-style)
- Quick capture button
- Today's schedule view

### Module 2: Task Manager
- Smart task creation with AI priority assignment
- Auto-reschedule every 15 minutes
- Subtask AI breakdown
- Task dependencies
- Recurring tasks
- Sleep-aware priority adjustment

### Module 3: Course Tracker
- Universal tracking (Udemy, Coursera, NPTEL, YouTube, College)
- Mandatory deadline requirement
- Auto-generate daily study tasks
- Spaced repetition
- Behind-schedule alerts

### Module 4: YouTube Knowledge Vault
- One-tap save via browser extension
- AI summary generation
- Goal linking
- Watch scheduling
- 60-day expiry for unwatched
- Spaced resurfacing

### Module 5: Resource Library
- Save articles, books, GitHub repos, tools
- Auto-tagging by AI
- Natural language search
- Reading queue
- Annotation and notes
- Resurface engine

### Module 6: Idea Vault
- Instant capture
- AI market check
- Status pipeline (Raw → Researching → Validating → Building → Archived)
- Validation plan generator
- Pattern detection after 6 months

### Module 7: Goal & Roadmap System
- Visual drag-and-drop roadmap builder (React Flow)
- 5 input methods (visual, text, image, PDF, third-party)
- 8 roadmap types
- AI timing estimates
- Auto-reschedule on missed milestones
- Hard deadline mode for exams
- Task generation from roadmap

### Module 8: Opportunity Radar
- Runs daily at 6 AM
- Scans: Internships, Hackathons, Open Source, Fellowships, Freelance
- Skill match scoring
- Critical deadline alerts (48 hours)
- Learns from your behavior

### Module 9: Income Sources Tracker
- Log all income streams
- Effective hourly rate calculation
- Income milestones tracking
- Skill-to-income mapping
- Weekly ROI report

### Module 10: Project Tracker
- Phase tracking (Planning → Launch → Maintain)
- Next action rule
- Blocker logging
- GitHub integration
- LinkedIn post draft generator

### Module 11: Academic Planner
- Semester subjects and credits
- Marks logging
- CGPA calculator
- At-risk alerts
- Exam countdown

### Module 12: Habit Engine
- Custom habits
- Streak tracking
- Goal linking
- Miss notifications
- 30-day consistency report

### Module 13: Sleep Monitor
- One-tap logging
- Sleep score calculation
- Task adjustment based on sleep
- Sleep debt tracking
- Bedtime reminders

### Module 14: Time Tracker
- Start/stop timer per task
- Pomodoro mode
- Idle auto-stop
- Deep work detection
- Focus hour analysis

### Module 15: Weekly Review
- Sunday 8 PM generation
- Tasks, courses, income, opportunities, roadmap progress
- Pattern insight
- Email delivery

## Non-Functional Requirements

- **Performance:** Lighthouse score > 90 on low-end Android
- **Offline:** Full PWA with IndexedDB
- **Security:** RLS on all tables, HTTPS enforced
- **Privacy:** No data sharing, export available anytime
- **Cost:** Rs. 0 per month forever

## Success Metrics

1. User logs in daily
2. Morning briefing read every day
3. Tasks auto-rescheduled correctly
4. Opportunity radar finds relevant opportunities
5. Weekly review generated and delivered
6. CGPA tracked accurately
7. Income streams logged

## Out of Scope

- Social features
- Team collaboration
- Public profiles
- Marketplace features
