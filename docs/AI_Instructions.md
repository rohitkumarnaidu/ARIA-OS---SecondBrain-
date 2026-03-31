# AI Instructions

## Overview

This document explains how AI is used in Second Brain OS and how to configure it.

---

## AI Architecture

### Dual Mode System

```
┌─────────────────────────────────────────────┐
│              AI Request                     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         ┌───────────────┐
         │ USE_LOCAL_AI  │──────── Yes ────▶ ┌─────────┐
         │ env variable  │                  │ Ollama  │
         └───────────────┘                  │ (Local) │
                  │                          └────┬────┘
                  │ No                          │
                  └────────────────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ Claude API      │
                                    │ (Cloud Fallback)│
                                    └─────────────────┘
```

---

## Configuration

### Environment Variables

```env
# Backend .env
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
CLAUDE_API_KEY=sk-ant-...  # Only if using Claude
```

### How It Works

1. If `USE_LOCAL_AI=true`, requests go to Ollama
2. If Ollama is unavailable or `USE_LOCAL_AI=false`, fallback to Claude API
3. Claude API uses free $5 monthly credits

---

## AI Use Cases

### 1. Task Smart Creation
When user creates a task, AI assigns:
- Priority (low/medium/high/urgent)
- Category (study/project/habit/personal/income)
- Estimated time

### 2. Course Summary
AI generates 3-sentence summary of what user will learn from a YouTube video or course.

### 3. Resource Tagging
Auto-tags resources with:
- Topics
- Skills
- Related goals

### 4. Idea Market Check
When user captures an idea, AI:
- Searches online for competitors
- Estimates market size
- Suggests validation steps

### 5. Daily Briefing Generation
Every morning, AI compiles:
- Top 3 tasks
- Opportunity highlights
- Progress summary
- Best recommendation (ARIA's pick)

### 6. Weekly Review
Sunday 8 PM, AI generates narrative review:
- What completed vs planned
- Patterns noticed
- Recommendations for next week

### 7. Roadmap Generation
User can describe a goal verbally, AI builds visual roadmap with:
- Milestones
- Time estimates
- Resource suggestions

### 8. Chat Responses
User chats with ARIA, AI:
- Knows all user data
- Provides personalized advice
- Can take actions

---

## Prompt Engineering

### ARIA System Prompt

```
You are ARIA (Adaptive Reasoning and Intelligence Assistant), a personal AI assistant for a BTech CSE student.

You know:
- All their tasks, goals, courses
- Their sleep patterns and productivity data
- Their projects and income sources
- Every idea they've ever captured

Guidelines:
- Be direct and practical, not overly polite
- Focus on action and progress
- Connect their daily tasks to long-term goals
- Use their first name when you know it
- Keep responses concise
- When suggesting tasks, consider their energy level and schedule
- Be honest about missed deadlines or skipped habits
- Help them build things, not just consume content
```

### Context Building

Before any AI call, build context:
```python
context = {
    "user_name": user.name,
    "tasks_today": tasks.filter(today),
    "goals_active": goals.filter(active),
    "courses_progress": courses.progress(),
    "sleep_last_night": sleep.latest(),
    "productive_hours": time_stats.peak_hours(),
    "recent_opportunities": opportunities.recent(5),
    "streaks": habits.streaks()
}
```

---

## Custom Prompts Library

### Daily Planning
- "What should I focus on first this morning?"
- "I have 2 hours free, what's best use?"
- "My sleep score is low, adjust my plan"
- "Give me top 3 must-do items"

### Learning
- "Which course am I most behind on?"
- "Quiz me on my last DSA study session"
- "Create 4-week plan to complete my Node.js course"

### Career
- "What skills for internship in next 6 weeks?"
- "Generate LinkedIn post about my project"
- "What do startups actually look for?"

### Goals
- "Build me a 6-month full-stack roadmap"
- "I'm 3 weeks behind, how to adjust?"
- "Is AngularJS still relevant in 2026?"

### Weekly Review
- "Full review of my week"
- "What patterns do you notice?"
- "Build plan for next week"

---

## Cost Optimization

### Ollama (Primary - Free)
Use for:
- Chat conversations
- Simple summaries
- Quick suggestions

### Claude API (Fallback - $5/month)
Use for:
- Weekly reviews (long generation)
- Opportunity parsing (complex)
- Roadmap generation (complex)

### Tips
1. Always set `USE_LOCAL_AI=true`
2. Only use Claude for complex/long tasks
3. Cache responses where possible
4. Use smaller models for simple tasks

---

## Model Selection

### Ollama Models
| Model | Size | Use Case |
|-------|------|----------|
| llama3.1 | 4.7GB | Best overall |
| mistral | 4GB | Fast, good quality |
| codellama | 3.8GB | Code-related tasks |

### Recommendation
Use Llama 3.1 for best quality:
```bash
ollama pull llama3.1
```

---

## Troubleshooting

### Ollama Not Running
```
Error: Connection refused to localhost:11434
```
Solution: Run `ollama serve`

### Model Not Found
```
Error: model not found
```
Solution: Run `ollama pull llama3.1`

### Claude Credits Exhausted
```
Error: insufficient credits
```
Solution: Check billing or switch to Ollama

---

## Future Enhancements

- Fine-tuned model on user's data
- Voice input with Whisper
- Image understanding for whiteboard roadmaps
- Predictive suggestions based on patterns
