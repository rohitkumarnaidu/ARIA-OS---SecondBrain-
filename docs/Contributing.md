# Contributing Guide

## Team Workflow

### Before Starting
1. Pull latest changes: `git pull origin main`
2. Create new branch: `git checkout -b feature/your-feature-name`

### Code Standards

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small (< 50 lines)

#### TypeScript/React (Frontend)
- Use TypeScript for everything
- Follow existing component patterns
- Use Tailwind CSS (no custom CSS)
- Keep components small
- Use proper naming: `PascalCase` for components, `camelCase` for functions

### File Structure

```
backend/
├── api/          # API endpoints
├── core/         # Config, auth, db
├── models/       # Database models
├── schemas/      # Pydantic schemas
├── services/     # Business logic
├── crons/        # Scheduled tasks
├── agents/       # AI agents
└── utils/        # Helpers

frontend/
├── app/          # Next.js pages
├── components/  # Reusable UI
├── lib/          # Supabase, stores
├── hooks/       # Custom hooks
├── types/        # TS types
└── styles/      # Global CSS
```

### Git Commit Messages

Use clear, concise messages:
- `feat: add task priority selection`
- `fix: resolve task reschedule bug`
- `docs: update API documentation`
- `refactor: simplify task service`

### Pull Request Process

1. **Create Branch:** `feature/task-manager`
2. **Make Changes:** Write code
3. **Test:** Run locally
4. **Commit:** Clear message
5. **Push:** `git push origin feature/task-manager`
6. **Create PR:** Describe changes
7. **Review:** Get team approval
8. **Merge:** Squash and merge

---

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- Git
- VS Code (recommended)

### Quick Start

```bash
# Clone repo
git clone https://github.com/your-repo/second-brain-os.git
cd second-brain-os

# Backend setup
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
# Create .env file

# Frontend setup
cd ../frontend
npm install
# Create .env.local file

# Run both
# Terminal 1: cd backend && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

### Environment Variables

See `docs/Deployment.md` for full list.

---

## Code Review Checklist

Before submitting PR, verify:

- [ ] Code follows style guide
- [ ] No console.logs or debug code
- [ ] No sensitive data in code
- [ ] TypeScript types correct
- [ ] API routes have proper auth
- [ ] Database queries have RLS
- [ ] Tested locally
- [ ] Commit message clear

---

## Communication

### Daily Standup
- What you did yesterday
- What you're doing today
- Any blockers

### Issues
- Use GitHub Issues
- Label appropriately
- Assign to yourself

### Discussions
- Use GitHub Discussions
- Ask questions there, not in DMs

---

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Supabase Docs](https://supabase.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Ollama](https://github.com/ollama/ollama)

---

## Questions?

Ask in team chat or create GitHub discussion.
