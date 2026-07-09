# App

A personal AI productivity system for BTech CSE students that acts as your memory, advisor, opportunity scanner, and daily planner. Built to help you become a builder - not just collect degrees.

## Features

- **Dashboard & Morning Briefing** - Daily AI-generated briefing with top tasks, opportunities, and progress updates
- **Task Manager** - Smart task creation with AI-priority, auto-reschedule, and zero-miss policy
- **Course Tracker** - Track Udemy, Coursera, NPTEL, YouTube playlists all in one place
- **YouTube Knowledge Vault** - One-tap save, AI summaries, and watch scheduling
- **Resource Library** - Save articles, books, GitHub repos with auto-tagging and natural language search
- **Idea Vault** - Capture startup ideas with AI market validation
- **Goal & Roadmap System** - Visual drag-and-drop roadmap builder with 8 types
- **Opportunity Radar** - Daily automated scanning for internships, hackathons, fellowships
- **Income Sources Tracker** - Track all income streams with hourly rate analysis
- **Project Tracker** - Kanban board with GitHub integration and LinkedIn post generator
- **Academic Planner** - Semester subjects, marks logging, CGPA calculator
- **Habit Engine** - Custom habits with streak tracking and goal linking
- **Sleep Monitor** - Sleep quality tracking with task adjustment based on rest
- **Time Tracker** - Pomodoro mode, deep work detection, focus hour analysis
- **Weekly Review** - AI-generated narrative review of your week

## Tech Stack

### Backend
- FastAPI (Python)
- Supabase (Database, Auth, Realtime)
- Ollama (Local AI)
- Claude API (AI Fallback)
- PostgreSQL with RLS

### Frontend
- Next.js 14
- React 18
- Tailwind CSS
- Zustand (State Management)
- React Flow (Roadmap Builder)
- Recharts (Analytics)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Supabase Account
- Claude API Key (optional, for advanced AI)

### Backend Setup (Agent Orchestrator)

1. Navigate to the backend directory:
```bash
cd apps/api
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\Activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp ../../.env.example .env
# Edit .env with your Supabase credentials
```

6. Run the backend server:
```bash
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd apps/web
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
Create a `.env.local` file in `apps/web/`:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
├── apps/
│   ├── api/             FastAPI backend (app/api/)
│   └── web/             Next.js 14 frontend
├── packages/
│   ├── ai/              AI agent modules + PromptLoader + LLM client
│   ├── config/core/     FastAPI config, auth, supabase
│   ├── database/schemas/ Pydantic models
│   ├── shared/utils/    Logging, cache, rate limiter, security, audit
│   ├── types/           Shared TypeScript types
│   └── ui/              Shared React components
├── services/
│   └── scheduler/       APScheduler + 7 cron jobs
├── prompts/             AI prompt templates (YAML frontmatter)
│   ├── system/          System prompts (aria_system, guardrails)
│   ├── agents/          Agent prompts (briefing, memory, sleep, etc.)
│   └── templates/       Context assembly, email templates
├── docs/                ~185 files (product, design, engineering, AI, security, devops, qa, operations)
├── infrastructure/      Helm, K8s, Docker, Terraform, nginx, canary
├── tests/               2411 Python tests
├── scripts/             Security, SOC 2, release, bundle audit
├── security/            SOC 2 reports, pen test reports
├── monitoring/          Grafana dashboards
```

## Documentation

See the `docs/` folder for detailed documentation:
- Product: PRD, Features, Roadmap
- Design: UIUX
- Engineering: Architecture, API, Database
- AI: Agents, AI Instructions
- Security
- DevOps: Deployment
- Operations: Implementation Status, TechStack

## License

MIT License
