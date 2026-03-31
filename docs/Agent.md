# Agent Guide

## Purpose

This document explains how the AI agents work in Second Brain OS. Any agent (AI or developer) should understand the complete application after reading this and examining the code.

---

## What is Second Brain OS?

A personal AI productivity system for BTech CSE students who want to become builders - not just collect degrees.

**Core Problem:** Students have too many things to track (courses, ideas, opportunities, projects) and lose track of everything.

**Solution:** An AI system that:
- Remembers everything
- Tells you what to do each morning
- Finds opportunities for you
- Connects learning → building → income

---

## Architecture Overview

```
User → Frontend (Next.js) → Backend (FastAPI) → Supabase (DB)
                                           ↓
                                      Ollama/Claude (AI)
```

### Technology Stack
- **Frontend:** Next.js 14, React, Tailwind, Zustand, React Flow
- **Backend:** FastAPI, Python
- **Database:** Supabase (PostgreSQL + Auth + Realtime)
- **AI:** Ollama (local) → Claude API (fallback)
- **Hosting:** Vercel (frontend) + Render (backend)

---

## The 15 Modules

| # | Module | Purpose |
|---|--------|---------|
| 1 | Dashboard | Morning briefing, productivity score, quick capture |
| 2 | Task Manager | Smart tasks with AI priority, auto-reschedule |
| 3 | Course Tracker | Track Udemy/Coursera/NPTEL with deadlines |
| 4 | YouTube Vault | Save videos with AI summaries, watch scheduling |
| 5 | Resource Library | Save articles, books, repos with auto-tagging |
| 6 | Idea Vault | Capture startup ideas with market validation |
| 7 | Goals & Roadmap | Visual roadmap builder with 8 types |
| 8 | Opportunity Radar | Daily scan for internships, hackathons, fellowships |
| 9 | Income Tracker | Log earnings, calculate hourly rate |
| 10 | Project Tracker | Kanban board, GitHub integration, LinkedIn posts |
| 11 | Academic Planner | Subjects, marks, CGPA calculator |
| 12 | Habit Engine | Custom habits with streaks |
| 13 | Sleep Monitor | Track sleep, adjust tasks based on rest |
| 14 | Time Tracker | Pomodoro, deep work detection |
| 15 | Weekly Review | AI-generated narrative review |

---

## Database Schema (21 Tables)

All tables follow: `auth.uid() = user_id` (Row Level Security)

1. **users** - Profile, skills, preferences
2. **tasks** - Task items with priority, category, status
3. **subtasks** - Breakdown of complex tasks
4. **task_dependencies** - Task relationships
5. **courses** - Course tracking with deadline
6. **videos** - YouTube saves with AI summary
7. **resources** - Articles, books, tools saved
8. **ideas** - Startup/business ideas
9. **goals** - Goals with roadmap nodes JSON
10. **opportunities** - Internships, hackathons found
11. **income_entries** - Income logging
12. **projects** - Project phases and status
13. **subjects** - Academic subjects
14. **marks** - Exam marks
15. **habits** - Habit definitions
16. **habit_logs** - Daily habit completion
17. **sleep_logs** - Sleep tracking
18. **time_entries** - Time tracking sessions
19. **chat_messages** - ARIA conversation history
20. **aria_memory** - Long-term memory about user
21. **daily_logs** - Evening reflection entries

---

## ARIA - Your AI Assistant

### What ARIA Knows About User
- All enrolled courses and progress
- All skills (have, learning, gaps)
- Active goals and progress
- Every project phase
- Income sources and trends
- Task completion rate
- Sleep patterns
- Every idea captured
- Every opportunity shown

### What ARIA Does
1. **Chat** - Answer questions about their data
2. **Suggest** - What to focus on today
3. **Break Down** - Complex tasks into subtasks
4. **Generate** - Daily briefings and weekly reviews
5. **Take Actions** - Create tasks, update goals via chat

### ARIA Sub-Agents (Automated)

| Agent | Schedule | Function |
|-------|----------|----------|
| Daily Briefing | 7 AM daily | Compile morning report |
| Missed Task Checker | Every 15 min | Find & reschedule overdue |
| Opportunity Radar | 6 AM daily | Scan for opportunities |
| Roadmap Update | Sunday 9 AM | Verify roadmap still current |
| Weekly Review | Sunday 8 PM | Generate narrative review |
| Sleep Reminder | 9:30 PM | Send bedtime notification |
| Habit Checker | Midnight | Check streak status |
| Course Nudge | 6 PM daily | Remind about courses |

---

## Key Features Explained

### Zero Miss Policy
- Cron job runs every 15 minutes
- Finds overdue tasks
- Auto-reschedules to next available slot
- Sends escalation: push → email → SMS

### Auto-Reschedule
- When task missed, moves to tomorrow
- Adjusts all downstream tasks
- Notifies user of changes

### Sleep-Aware Priority
- Morning briefing checks sleep score
- Low sleep = lighter tasks prioritized
- Heavy cognitive tasks moved to tomorrow

### Opportunity Matching
- Skills stored in user profile
- Radar scans with Brave Search API
- Calculates skill match percentage
- Filters below 40% match

### Visual Roadmap
- React Flow canvas
- 8 node types (Goal, Milestone, Task, etc.)
- Drag-and-drop builder
- AI generates from text/image/PDF

### PWA Offline
- Service worker caches app
- IndexedDB stores data locally
- Background sync when online
- Works without internet

---

## Data Flow Examples

### Creating a Task
1. User submits task form
2. Frontend sends POST to /api/tasks
3. Backend creates in Supabase
4. AI assigns priority/category/time
5. Realtime pushes to all clients

### Chat with ARIA
1. User sends message
2. Backend builds context (all user data)
3. Calls Ollama with context + prompt
4. Returns response
5. Saves message to chat_messages
6. If action requested, performs it

### Morning Briefing
1. Cron triggers at 7 AM
2. Loads all user data
3. Calls Claude API
4. Generates briefing
5. Stores + sends notification

---

## Environment Variables

### Backend Required
```
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_KEY
JWT_SECRET
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=true
```

### Backend Optional
```
CLAUDE_API_KEY
BRAVE_API_KEY
RESEND_API_KEY
TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE
```

### Frontend Required
```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
```

---

## Common Patterns

### API Route Pattern
```python
@router.get("/tasks")
async def get_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return service.get_tasks(current_user.id)
```

### Service Pattern
```python
class TaskService:
    def __init__(self, db):
        self.db = db
    
    def get_tasks(self, user_id):
        return self.db.query(Task).filter(Task.user_id == user_id).all()
```

### Frontend State
```javascript
// Zustand store
const useTaskStore = create((set) => ({
  tasks: [],
  fetchTasks: async () => {
    const { data } = await supabase.from('tasks').select('*')
    set({ tasks: data })
  }
}))
```

---

## How to Extend

### Adding New Feature
1. Create table in Supabase (with RLS)
2. Add schema in backend/schemas
3. Add service in backend/services
4. Add API route in backend/api
5. Add frontend page in frontend/app
6. Add component in frontend/components
7. Add store in frontend/lib

### Modifying AI Behavior
1. Edit prompt in backend/services/aria_service.py
2. Or create new prompt in AI_Instructions.md

### Adding New Agent
1. Create function in backend/agents/
2. Set up cron in Supabase pg_cron
3. Add to Agent.md documentation

---

## Testing Checklist

- [ ] User can sign up/login with Google
- [ ] Tasks CRUD works
- [ ] Courses show progress
- [ ] Goals create roadmaps
- [ ] Chat responds with context
- [ ] Morning briefing generates
- [ ] Weekly review sends email
- [ ] Opportunity radar finds items
- [ ] Time tracker starts/stops
- [ ] PWA works offline
- [ ] Data exports correctly

---

## Key Files Location

| File | Location |
|------|----------|
| Main app | backend/app/main.py |
| Config | backend/app/core/config.py |
| Schemas | backend/app/schemas/*.py |
| Services | backend/app/services/*.py |
| API Routes | backend/app/api/*.py |
| Frontend App | frontend/app/**/*.tsx |
| Components | frontend/components/**/*.tsx |
| Stores | frontend/lib/**/*.ts |
| Styles | frontend/styles/globals.css |

---

## Support

- **Documentation:** docs/ folder
- **Database:** Database.md
- **API:** API.md
- **AI:** AI_Instructions.md
- **Deployment:** Deployment.md
