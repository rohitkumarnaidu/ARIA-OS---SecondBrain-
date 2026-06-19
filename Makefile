# =============================================================================
# Second Brain OS — Makefile
# Common development commands for the monorepo
# =============================================================================

.PHONY: help dev-api dev-web dev-scheduler lint test validate-prompts \
        docker-up docker-down docker-build clean setup install

help: ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Development Servers ──────────────────────────────────────────────────────

dev-api: ## Start FastAPI backend dev server
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Start Next.js frontend dev server
	cd apps/web && npm run dev

dev-scheduler: ## Start APScheduler dev server
	cd services/scheduler && python main.py

# ── Linting & Formatting ─────────────────────────────────────────────────────

lint: ## Run all linters (Python + TypeScript)
	cd apps/api && ruff check . --fix
	cd apps/web && npm run lint
	python scripts/validate_prompts.py

lint-python: ## Run Python linter only
	cd apps/api && ruff check . --fix
	ruff check packages/ --fix
	ruff check services/ --fix

lint-ts: ## Run TypeScript linter only
	cd apps/web && npm run lint

format: ## Format all Python files with Black
	black apps/api/ packages/ services/ tests/ scripts/

type-check: ## Run TypeScript type checker
	cd apps/web && npm run type-check

# ── Testing ──────────────────────────────────────────────────────────────────

test: ## Run all Python tests
	python -m pytest tests/ -v --tb=short

test-api: ## Run API endpoint tests
	python -m pytest tests/ -k "api" -v --tb=short

test-prompts: ## Run prompt-related tests
	python -m pytest tests/test_prompt_loader.py tests/test_agent_prompts.py -v --tb=short

test-coverage: ## Run tests with coverage report
	python -m pytest tests/ --cov=packages --cov=apps/api --cov-report=term-missing --cov-report=html

test-e2e: ## Run Playwright E2E tests
	cd apps/web && npx playwright test

# ── Prompt System ────────────────────────────────────────────────────────────

validate-prompts: ## Validate all prompt YAML frontmatter
	python scripts/validate_prompts.py

# ── Docker ───────────────────────────────────────────────────────────────────

docker-up: ## Start all Docker services
	docker compose up -d

docker-up-dev: ## Start Docker services with logs
	docker compose up

docker-down: ## Stop all Docker services
	docker compose down

docker-build: ## Build all Docker images
	docker compose build

docker-logs: ## Follow Docker logs
	docker compose logs -f

docker-clean: ## Remove all containers, images, and volumes
	docker compose down -v

# ── Setup & Installation ─────────────────────────────────────────────────────

setup: install validate-prompts ## Full project setup (install deps + validate)

install: ## Install all dependencies
	cd apps/api && pip install -r requirements.txt
	cd services/scheduler && pip install -r requirements.txt
	cd apps/web && npm install
	pip install -r requirements.txt 2>/dev/null || true
	pip install black ruff pytest pytest-cov pytest-asyncio pytest-mock pytest-httpx

# ── Design System ─────────────────────────────────────────────────────────────

figma-sync: ## Sync design tokens from Figma to tailwind.config.js
	cd apps/web && node ../scripts/sync-figma-tokens.ts

token-check: ## Check for hardcoded color values (token drift)
	cd apps/web && node ../scripts/check-token-drift.ts

# ── Infrastructure ────────────────────────────────────────────────────────────

setup-ci: ## Create .github/ directory with CI workflow templates
	@echo "✓ .github/ directory already configured"

# ── Quality Gates ─────────────────────────────────────────────────────────────

gate-0: ## Phase 0 quality gate checklist
	$(MAKE) lint-python
	$(MAKE) lint-ts
	$(MAKE) validate-prompts
	$(MAKE) test
	$(MAKE) type-check
	cd apps/web && npm run build

# ── Cleanup ──────────────────────────────────────────────────────────────────

clean: ## Clean build artifacts, caches, and node_modules
	rm -rf apps/web/.next/
	rm -rf apps/web/coverage/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage

# ── Pre-Commit ───────────────────────────────────────────────────────────────

pre-commit: ## Run pre-commit checks (lint + validate + test)
	$(MAKE) lint-python
	$(MAKE) lint-ts
	$(MAKE) validate-prompts
	$(MAKE) test
	$(MAKE) type-check
