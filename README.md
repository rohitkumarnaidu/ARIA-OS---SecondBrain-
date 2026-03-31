# Second Brain OS

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

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the backend directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
CLAUDE_API_KEY=your_claude_api_key
OLLAMA_BASE_URL=http://localhost:11434
JWT_SECRET=your_jwt_secret
```

6. Run the backend server:
```bash
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
Create a `.env.local` file in the frontend directory:
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
second-brain-os/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes/endpoints
│   │   ├── core/         # Core configurations
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── crons/        # Scheduled tasks
│   │   ├── agents/       # AI agents
│   │   └── utils/        # Utility functions
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/              # Next.js app router
│   │   ├── components/   # Reusable components
│   │   ├── lib/         # Library configurations
│   │   ├── hooks/       # Custom React hooks
│   │   ├── styles/      # Global styles
│   │   └── types/       # TypeScript types
│   ├── public/          # Static assets
│   └── package.json
├── docs/                # Documentation
├── README.md
├── .gitignore
└── package.json
```

## Documentation

See the `docs/` folder for detailed documentation:
- PRD.md - Product Requirements Document
- Features.md - Feature specifications
- TechStack.md - Technology stack details
- Database.md - Database schema
- API.md - API documentation
- Architecture.md - System architecture
- Security.md - Security considerations
- Deployment.md - Deployment guide

## License

MIT License
