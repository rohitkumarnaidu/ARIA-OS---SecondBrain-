# Chat and AI Guide

## Document Control

| Field | Value |
|---|---|
| Document ID | UG-AI-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public - User Documentation |
| Last Updated | 2026-07-11 |

---

## How to Chat with ARIA

Open the **Chat** page from the sidebar. Type your message in the input box and press **Enter**. ARIA responds in real time with streaming text.

You can ask ARIA about:

- **Tasks** -- "What do I need to do today?" or "Add a task to review DSA notes"
- **Goals** -- "How is my progress on the web dev project?"
- **Habits** -- "Show me my habit streaks"
- **Courses** -- "What courses am I taking right now?"
- **Sleep** -- "How did I sleep last night?"
- **Planning** -- "Plan my study schedule for today"

ARIA also remembers context from your previous conversations and your data across the app.

> If ARIA doesn't understand, it falls back to keyword-based responses so you always get a helpful reply.

## What the AI Can Do

ARIA runs several AI agents behind the scenes:

| Agent | What It Does | When |
|---|---|---|
| **Task Agent** | Breaks down tasks, suggests priorities | On demand |
| **Memory Agent** | Stores preferences and patterns from your chats | Continuous |
| **Learning Agent** | Detects patterns in your productivity | Daily |
| **Sleep Agent** | Generates wind-down routines and sleep analysis | Evenings |
| **Nudge Agent** | Sends reminders for habits and courses | 6 PM daily |
| **Briefing Agent** | Creates your morning summary | 7 AM daily |
| **Review Agent** | Generates weekly performance review | Sunday 8 PM |
| **Opportunity Agent** | Scans for opportunities matching your skills | 6 AM daily |
| **Roadmap Agent** | Optimizes your skill development plan | On demand |

## Daily Briefing (7 AM)

Every morning at 7 AM, ARIA generates a personalized **Daily Briefing** with:

- Your pending tasks sorted by priority
- Last night's sleep score
- Your active habit streaks at a glance
- Any approaching deadlines
- A focus suggestion for the day

You can view previous briefings in the **Briefings** section.

## Weekly Review (Sunday 8 PM)

Every Sunday at 8 PM, ARIA generates a **Weekly Review** covering:

- Tasks completed vs. missed
- Habit consistency for the week
- Sleep trends over 7 days
- Goals progress update
- Suggestions for improvement next week

> The weekly review is a great opportunity to reflect and plan ahead. Read it every Sunday to stay on track.

## Opportunity Radar

The Opportunity agent scans for relevant opportunities (internships, scholarships, hackathons, open-source projects) based on your skills, courses, and goals. Check the **Opportunities** page to see matched opportunities with a relevance score.

## How the AI Learns from You

ARIA uses a **memory agent** that stores:

- Topics you frequently ask about
- Your preferred categories and work styles
- Patterns in your productivity (e.g., you're most productive in the morning)

This memory helps ARIA give you more relevant suggestions over time. You can view or reset your memory in the settings.

## Privacy Note

ARIA OS runs AI in two modes:

- **Local AI (Default)** -- Uses Ollama with Mistral 7B running on your machine. No data leaves your computer. Free and private.
- **Cloud AI (Fallback)** -- If local AI is unavailable, ARIA can optionally use Claude via Anthropic's API. This sends your query to Anthropic's servers but is never used for training.

> Your data is yours. ARIA does not sell, share, or train on your personal information.
