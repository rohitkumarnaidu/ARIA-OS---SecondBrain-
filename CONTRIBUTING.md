# Contributing to Second Brain OS

Welcome to Second Brain OS (ARIA OS) — a personal AI productivity system for BTech CSE students that integrates 15 modules across task management, course tracking, opportunity scanning, and AI-driven planning. Built with Next.js 14, FastAPI, Supabase, and a local-first AI agent architecture, this project aims to help students become builders, not just degree collectors. We welcome contributions from developers, designers, and technical writers who share this vision.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Issue Reporting](#issue-reporting)
- [Documentation Contributions](#documentation-contributions)
- [Community & Support](#community--support)

---

## Code of Conduct

This project is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold its standards. Report unacceptable behavior via GitHub Issues.

---

## Getting Started

### Prerequisites

- **Node.js** 18+ (LTS recommended)
- **Python** 3.10+
- **Git** 2.30+
- **Supabase** account (free tier)
- **Ollama** (optional, for local AI inference)
- **Claude API key** (optional, for advanced AI features)

### Repository Setup

```bash
# Clone the repository
git clone https://github.com/your-org/second-brain-os.git
cd second-brain-os

# Install root-level Python dependencies
pip install -r requirements.txt
```

### Backend Setup (FastAPI)

```bash
cd apps/api
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Edit .env with your Supabase credentials and API keys

# Start the development server
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`.

### Frontend Setup (Next.js)

```bash
cd apps/web
npm install

# Create .env.local from example
cp .env.example .env.local
# Edit with your Supabase public keys

# Start the development server
npm run dev
```

The frontend is available at `http://localhost:3000`.

### Scheduler Setup

```bash
cd services/scheduler
pip install -r requirements.txt
python main.py
```

### Verify Your Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend check — open http://localhost:3000 in a browser

# Run the test suite
pytest
```

---

## Development Workflow

### Branch Strategy

We follow a simplified Git Flow with the following branch conventions:

| Branch | Purpose |
|---|---|
| `main` | Production-ready code. Protected — no direct pushes. |
| `develop` | Integration branch for features. Default target for PRs. |
| `feature/<name>` | New features. Branch from `develop`, merge back to `develop`. |
| `fix/<name>` | Bug fixes. Branch from `develop`, merge back to `develop`. |
| `docs/<name>` | Documentation changes. Branch from `develop`. |
| `release/<version>` | Release preparation. Branch from `develop`, merge to `main` and `develop`. |

Branch names should use kebab-case and be descriptive: `feature/task-priority-drag-drop`, `fix/auth-session-timeout`.

### Before You Start

1. Ensure `develop` is up to date: `git checkout develop && git pull origin develop`
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Make focused, atomic commits (see commit convention below)
4. Push your branch: `git push origin feature/your-feature-name`
5. Open a pull request against `develop`

### Keeping Your Branch Updated

```bash
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop
git push --force-with-lease
```

---

## Commit Message Convention

All commits **must** follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This produces a readable git history and enables automated changelog generation.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Usage |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies, tooling |
| `ci` | CI/CD configuration changes |
| `style` | Formatting, missing semicolons (no production code change) |
| `perf` | Performance improvement |
| `revert` | Reverting a previous commit |

### Scopes

Optional but recommended. Common scopes: `api`, `web`, `scheduler`, `agents`, `auth`, `tasks`, `docs`, `deps`.

### Examples

```
feat(tasks): add AI-priority ranking to task creation
fix(auth): resolve session expiry not redirecting to login
docs: update API endpoint documentation for opportunity radar
refactor(api): extract task validation into shared middleware
test(tasks): add unit tests for priority ranking algorithm
chore(deps): upgrade next.js to 14.2.0
ci: add markdown linting to pull request workflow
```

### Breaking Changes

Append `!` after the type/scope to indicate a breaking change:

```
feat(api)!: redesign task endpoint response schema
```

---

## Pull Request Process

1. **Create a Draft PR early** — open a draft pull request as soon as you start working. This signals your intent and allows early feedback.

2. **Complete the PR template** — fill out the pull request template with a description of changes, related issues, and testing notes.

3. **Keep PRs focused** — each pull request should address a single concern. If you find yourself fixing unrelated issues, create a separate PR. Aim for PRs under 400 lines changed.

4. **Pass all CI checks** — ensure the following pass before requesting review:
   - Linting (ESLint for frontend, Ruff for backend)
   - Type checking (`npm run type-check`)
   - Tests (`pytest` — all tests green)
   - Build (`npm run build` for frontend)

5. **Request review** — assign at least one maintainer as reviewer. Address all feedback with additional commits. Avoid force-pushing after a review has started, so reviewers can track changes incrementally.

6. **Pre-merge checklist**:
   - [ ] Code follows project coding standards
   - [ ] All CI checks pass
   - [ ] At least one approving review from a maintainer
   - [ ] Branch is up to date with `develop` (rebase if behind)
   - [ ] Commit history is clean (squash fixup commits if needed)
   - [ ] Documentation updated if introducing new features or changing behavior
   - [ ] No debug code, console.logs, or secrets committed

7. **Merge** — a maintainer will squash-merge your PR into `develop`. The commit message should follow the Conventional Commits format. After merge, delete the feature branch.

---

## Coding Standards

### TypeScript / React (Frontend)

- **Imports** — Order: external libraries → internal modules → relative imports
- **Naming** — Components: `PascalCase` (`TaskCard`). Hooks: `camelCase` with `use` prefix (`useAuth`). Files: `kebab-case` (`task-card.tsx`). Types: `PascalCase` (`Task`, `User`).
- **Types** — Never use `any`. Define interfaces for all data structures. Use Zod schemas where input validation is needed.
- **State** — Use Zustand stores in `apps/web/lib/` for global state. Local state with `useState`/`useReducer` is preferred for component-local concerns.
- **Styling** — Use Tailwind CSS exclusively. Design tokens from `tailwind.config.js`: `text-text-primary`, `bg-background-card`. Utility classes: `.btn`, `.card`, `.input`, `.text-gradient`. No custom CSS files unless absolutely necessary.
- **Error Handling** — Use try/catch for async operations. Display user-friendly error messages. Handle Supabase errors explicitly.
- **Linting** — Run `npm run lint` and `npm run type-check` before committing.
- **UI/UX** — Follow the cyberpunk design system: dark base (`#0A0B0F`), accent-primary (`#6366F1`), accent-neon (`#00FFA3`). Use Framer Motion for staggered reveals and page transitions. Avoid generic AI aesthetics, system fonts (Inter, Arial), and predictable layouts.

### Python / FastAPI (Backend)

- **Imports** — Order: standard library → third-party packages → local application modules
- **Naming** — Functions: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE`.
- **Types** — Use Pydantic models for all request/response schemas. Add type hints to every function signature.
- **Error Handling** — Raise `HTTPException` with appropriate status codes (400, 401, 404, 500). Return structured error responses.
- **Database** — Always filter queries by `user_id`. Check `.error` after every Supabase `.execute()` call. Use Row-Level Security (RLS) on all tables.
- **Utilities** — Use the shared utilities in `packages/shared/utils/`: structured JSON logging (`logger.py`), rate limiting (`rate_limiter.py`), in-memory caching (`cache.py`), and retry with exponential backoff (`retry.py`).
- **Linting & Formatting** — Format with `black .` and lint with `ruff check .` before committing.

### Testing

- **Backend** — `pytest` for Python tests. Test files live in `tests/`. Run a single test: `pytest tests/test_file.py::TestClass::test_method -v`.
- **Frontend** — Jest and React Testing Library for component tests.
- **Coverage** — Aim for 80%+ coverage on new code. Critical paths (auth, task CRUD, AI agent orchestration) should have near-complete coverage.

### General

- No debug code, `console.log`, or `print` statements in committed code
- No secrets, API keys, or credentials in code — use `.env` files
- Do not commit generated files, build artifacts, or compiled output
- Document non-obvious logic with inline comments (but prefer self-documenting code)

---

## Issue Reporting

We use GitHub Issues to track bugs, feature requests, and improvements.

### Bug Reports

When reporting a bug, include:

- A clear, descriptive title
- Steps to reproduce (minimal reproduction is ideal)
- Expected behavior vs. actual behavior
- Environment details (OS, browser, Node/Python versions)
- Screenshots or error logs if applicable

Use the **Bug Report** issue template (select `Bug Report` when creating a new issue). Label: `type: bug`.

### Feature Requests

When requesting a feature, include:

- A clear, descriptive title
- Problem statement — what problem does this solve?
- Proposed solution — describe the desired behavior
- Alternative approaches you've considered
- Any relevant context or prior art

Use the **Feature Request** issue template (select `Feature Request` when creating a new issue). Label: `type: enhancement`.

### Other Issues

- Documentation issues: label `type: documentation`
- Questions and discussions: use [GitHub Discussions](https://github.com/your-org/second-brain-os/discussions)
- Security vulnerabilities: do **not** file a public issue. Follow the guidance in [SECURITY.md](SECURITY.md).

---

## Documentation Contributions

Documentation is maintained as code in `docs/` and follows the standards defined in [Documentation Standards](docs/operations/48_DocumentationStandards.md).

### Key Rules

- **Markdown** — Use GitHub-Flavored Markdown (GFM). Every code block must specify a language identifier.
- **File naming** — `{NN}_{TitleCaseWithUnderscores}.md` (e.g., `02_PRD.md`, `48_DocumentationStandards.md`).
- **Each document** — Must include a Document Control table, content sections, and a Revision History.
- **No images** — Use ASCII art or Mermaid.js diagrams instead of screenshots or embedded images.
- **No emojis** — Enterprise documentation uses professional tone throughout.
- **Cross-references** — Use relative paths from the referencing document to the target (e.g., `[Architecture](../engineering/00_Architecture.md)`).
- **Review** — Documentation PRs are reviewed with the same rigor as code PRs. Every PR that introduces a feature must include or update relevant documentation.

### Document Categories

| Directory | Purpose |
|---|---|
| `docs/product/` | Vision, PRD, features, roadmap |
| `docs/engineering/` | Architecture, API specs, database schema |
| `docs/design/` | UI/UX guidelines, design system |
| `docs/ai/` | Agent definitions, prompt chains, memory schemas |
| `docs/security/` | Threat models, auth flows, compliance |
| `docs/devops/` | CI/CD, infrastructure, deployment |
| `docs/operations/` | Monitoring, runbooks, disaster recovery, SLA, standards |

---

## Community & Support

- **GitHub Discussions** — Ask questions, share ideas, and discuss features. Prefer public discussions over DMs so the whole community benefits.
- **Issue Tracker** — Report bugs and request features via GitHub Issues with appropriate labels.
- **Pull Requests** — All changes go through PRs. Direct pushes to `main` or `develop` are not permitted.
- **Maintainers** — PRs require at least one approving review from a maintainer before merging.
- **Release cadence** — We follow semantic versioning. Releases are cut from `develop` to `main` on a regular cadence.

---

## Attribution

This CONTRIBUTING.md is adapted from best practices established by the open-source community. Thank you for contributing to Second Brain OS.
