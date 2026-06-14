# Tech Stack

## Overview

26 free tools, Rs. 0 forever. Every tool listed here has a free tier sufficient for personal use.

## Backend

### Framework
- **FastAPI** (Python 3.10+)
  - Modern, fast Python web framework
  - Built-in async support
  - Automatic API documentation

### Server
- **Uvicorn**
  - ASGI server
  - Runs FastAPI applications
  - Hot reload in development

### Database
- **Supabase**
  - PostgreSQL database
  - Built-in authentication (Google OAuth)
  - Row Level Security (RLS)
  - Realtime subscriptions
  - Edge Functions
  - Free tier: 500MB database, 1GB file storage, 2GB bandwidth

### AI/ML

#### Primary (Free, Local)
- **Ollama**
  - Local LLM running on your machine
  - Models: Llama 3.1, Mistral, etc.
  - No API costs
  - Privacy preserved

#### Fallback (Paid, Cloud)
- **Anthropic Claude API**
  - For complex tasks: weekly reports, opportunity parsing
  - $5 free credits/month
  - Pay only for heavy usage

### Scheduled Tasks
- **Supabase pg_cron**
  - Built-in PostgreSQL cron
  - Runs background jobs
  - No external service needed

### External APIs (Free Tiers)
- **Brave Search API** - For opportunity radar
- **GitHub API** - For project tracking
- **Google Fit API** - For sleep data (optional)

### Email
- **Resend**
  - Transactional emails
  - 3,000 emails/month free
  - Weekly reviews, reminders

### SMS (Optional)
- **Twilio**
  - For critical alerts escalation
  - Pay as you go

---

## Frontend

### Framework
- **Next.js 14** (App Router)
  - React full-stack framework
  - Server-side rendering
  - API routes

### UI Library
- **React 18**
  - Component-based UI
  - Hooks for state management

### Styling
- **Tailwind CSS**
  - Utility-first CSS
  - Dark mode built-in
  - Rapid development

### State Management
- **Zustand**
  - Simple, lightweight
  - No boilerplate
  - Persist middleware for offline

### Data Fetching
- **TanStack Query** (React Query)
  - Caching, background updates
  - Optimistic updates

### Forms
- **React Hook Form**
  - Performant forms
  - Easy validation with Zod

### Visualization
- **React Flow** - Roadmap builder
- **Recharts** - Charts and graphs
- **Framer Motion** - Animations

### Drag & Drop
- **@dnd-kit**
  - Accessible drag and drop
  - For kanban boards

### Icons
- **Lucide React**
  - Clean, consistent icons
  - Tree-shakable

### Notifications
- **React Hot Toast**
  - Toast notifications

### Offline
- **next-pwa**
  - Service worker for PWA
  - Workbox integration

### Build Tools
- **TypeScript** - Type safety
- **ESLint** - Code linting
- **PostCSS** - CSS processing
- **Autoprefixer** - Vendor prefixes

---

## Browser Extension

### Framework
- **WXT**
  - Web Extension Tools
  - React-based
  - Works on Chrome and Firefox
  - Free and open source

---

## Development Tools

### Code Editor
- **VS Code**
  - Free, powerful
  - Extensions for everything

### Version Control
- **Git**
  - Version control
  - GitHub for hosting

### Deployment
- **Vercel**
  - Frontend hosting
  - Automatic deployments
  - Free tier: 100GB bandwidth

---

## Cost Breakdown

| Service | Free Tier | Cost |
|---------|-----------|------|
| Supabase | 500MB DB, 1GB Storage | Rs. 0 |
| Ollama | Local | Rs. 0 |
| Claude API | $5/month credit | Rs. 0-400 |
| Vercel | 100GB bandwidth | Rs. 0 |
| Resend | 3,000 emails/month | Rs. 0 |
| Brave Search | 2,000 searches/month | Rs. 0 |
| WXT | Open source | Rs. 0 |
| GitHub | Unlimited repos | Rs. 0 |
| Google Fit | Free | Rs. 0 |

**Total: Rs. 0 per month** (or Rs. 0-400 with Claude API)

---

## Environment Variables

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
JWT_SECRET=your_jwt_secret
CLAUDE_API_KEY=your_claude_api_key
OLLAMA_BASE_URL=http://localhost:11434
USE_LOCAL_AI=true
BRAVE_API_KEY=your_brave_api_key
RESEND_API_KEY=your_resend_api_key
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=your_twilio_phone
```

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

## Tech Stack Summary

```
┌─────────────────────────────────────────┐
│              Frontend                   │
│  Next.js 14 + React 18 + Tailwind     │
│  Zustand + React Query + React Flow    │
│  TypeScript + PWA                      │
└──────────────────┬──────────────────────┘
                   │
                   │ API
                   ▼
┌─────────────────────────────────────────┐
│              Backend                    │
│  FastAPI + Python + Uvicorn            │
│  Supabase (DB + Auth + Edge Functions) │
└──────────────────┬──────────────────────┘
                   │
                   │ AI
                   ▼
┌─────────────────────────────────────────┐
│              AI Layer                   │
│  Ollama (Local) → Claude API (Fallback)│
│  Brave Search for Opportunities        │
└─────────────────────────────────────────┘
```
