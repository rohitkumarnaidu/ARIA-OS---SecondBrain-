# Quick-Start Guide â€” Second Brain OS (ARIA OS)

Get the full stack running in under 10 minutes.

## Document Control

| Field | Value |
|---|---|
| Document ID | QST-GUIDE-001 |
| Version | 1.0.0 |
| Status | Active |
| Classification | Public â€” Developer Guide |
| Owner | Principal Product Manager |
| Last Updated | 2026-07-10 |
| Next Review | 2026-10-10 |

---

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Python | 3.10+ | FastAPI backend + AI agents |
| Node.js | 18+ | Next.js 14 frontend |
| Git | Any | Clone the repo |
| Ollama | Latest | Local AI (Mistral 7B) â€” `ollama pull mistral:7b` |
| Supabase | Free account | Database + Auth â€” sign up at [supabase.com](https://supabase.com) |
| VS Code | Any | Recommended editor |

---

## Setup (3 commands)

```bash
# 1. Clone
git clone <repo-url>
cd "ARIA OS - SecondBrain"

# 2. Install everything (Python deps + Node deps + dev tools)
make install

# 3. Validate
make validate-prompts
make test
```

---

## Environment

```bash
cp .env.example .env.local   # Edit with your keys
```

**Essential variables you MUST configure:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJ...
SUPABASE_SERVICE_KEY=eyJhbGciOiJ...
JWT_SECRET=your-jwt-secret
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJ...
USE_LOCAL_AI=True
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
```

---

## Start Services (3 terminals)

```bash
# Terminal 1: Backend API
make dev-api              # â†’ http://localhost:8000 (docs at /docs)

# Terminal 2: Frontend
make dev-web              # â†’ http://localhost:3000

# Terminal 3: Scheduler (optional â€” cron jobs)
make dev-scheduler
```

---

## Verify

```bash
# Run tests
make test                  # All 2,795+ Python tests
make test-coverage         # With coverage report (open htmlcov/index.html)

# Frontend tests
cd apps/web && npm run test:ci && npm run test

# Lint & validate
make lint                  # Python lint + TS lint + prompt validation
```

---

## Common Commands

| Task | Command |
|---|---|
| Start backend | `make dev-api` |
| Start frontend | `make dev-web` |
| Start scheduler | `make dev-scheduler` |
| Run all tests | `make test` |
| Run tests with coverage | `make test-coverage` |
| Run API tests | `make test-api` |
| Run prompt tests | `make test-prompts` |
| Run E2E tests | `make test-e2e` |
| Validate prompts | `make validate-prompts` |
| Lint all code | `make lint` |
| Format Python | `make format` |
| Type-check TS | `make type-check` |
| Pre-commit check | `make pre-commit` |
| Docker up | `make docker-up` |
| Docker build | `make docker-build` |
| Full install | `make install` |
| Clean artifacts | `make clean` |

---

## Where to Find Help

| Resource | Location |
|---|---|
| **Full developer onboarding** | `docs/operations/44_DeveloperOnboarding.md` |
| **Master reference (AGENTS.md)** | `AGENTS.md` (root) |
| **API docs (Swagger)** | `http://localhost:8000/docs` |
| **API docs (ReDoc)** | `http://localhost:8000/redoc` |
| **Project vision** | `docs/product/00_ProjectVision.md` |
| **Documentation index** | `docs/DOCUMENTATION_INDEX.md` |
| **Makefile targets** | `make help` |
| **GitHub issues** | github.com/your-org/second-brain-os/issues |

---

## Troubleshooting

| Issue | Check |
|---|---|
| `pip install` fails | Activate venv: `.\venv\Scripts\Activate` (Windows) |
| Ollama not responding | `ollama serve` in separate terminal; `ollama pull mistral:7b` |
| Supabase connection error | Verify URL + key in `.env.local` |
| Port 3000/8000 in use | `npx kill-port 3000 8000` |
| Prompts not loading | `make validate-prompts` â€” check YAML syntax |
| Tests fail with import error | `make install` â€” missing dependencies |
| CORS errors in browser | Add origin to `CORS_ORIGINS` in `.env.local` |
