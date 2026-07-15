# =============================================================================
# Second Brain OS — Makefile
# Common development commands for the monorepo
# =============================================================================

.PHONY: help dev-api dev-web dev-scheduler lint test validate-prompts \
        docker-up docker-down docker-build clean setup install \
        deploy-api deploy-web deploy-scheduler deploy-all deploy-rollback

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

# ── Turborepo Build System ───────────────────────────────────────────────────

turbo-build: ## Build all packages with Turborepo (cached)
	npx turbo run build

turbo-lint: ## Lint all packages in parallel
	npx turbo run lint

turbo-type-check: ## Type-check all packages in parallel
	npx turbo run type-check

turbo-test: ## Test all packages with Turborepo
	npx turbo run test

turbo-clean: ## Clear Turborepo cache
	npx turbo clean

turbo: ## Run all Turbo checks (build + lint + type-check)
	npx turbo run build lint type-check

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

docker-up: ## Start all Docker services (development targets)
	docker compose up -d

docker-up-dev: ## Start Docker services with logs (development targets)
	docker compose up

docker-up-prod: ## Start all Docker services using production targets
	DOCKER_TARGET=production docker compose up -d

docker-down: ## Stop all Docker services
	docker compose down

docker-build: ## Build all Docker images (development targets)
	docker compose build

docker-build-prod: ## Build all Docker images using production targets
	DOCKER_TARGET=production docker compose build

docker-logs: ## Follow Docker logs
	docker compose logs -f

docker-clean: ## Remove all containers, images, and volumes
	docker compose down -v

docker-prune: ## Remove all unused Docker resources (images, containers, volumes)
	docker system prune -af --volumes

# ── Deployment (Production) ──────────────────────────────────────────────────

deploy-api: ## Deploy API backend to Railway
	@echo "=== Deploying API to Railway ==="
	@echo "Linking project..."
	railway link 2>/dev/null || true
	railway up --service secondbrain-api
	@echo ""
	@echo "Verifying health..."
	@sleep 10
	@echo "✓ Deployment complete. Run 'make verify-api' to check health."

deploy-web: ## Deploy frontend to Vercel
	@echo "=== Deploying Frontend to Vercel ==="
	cd apps/web && vercel --prod
	@echo ""
	@echo "✓ Deployment complete. Run 'make verify-web' to check."

deploy-scheduler: ## Deploy scheduler to Railway
	@echo "=== Deploying Scheduler to Railway ==="
	@echo "Linking project..."
	railway link 2>/dev/null || true
	railway up --service secondbrain-scheduler
	@echo ""
	@echo "✓ Deployment complete. Run 'make verify-scheduler' to check."

deploy-all: ## Deploy all services (API → Scheduler → Frontend)
	@echo "=== Full Production Deployment ==="
	@echo ""
	@echo "Step 1/3: Deploying API..."
	$(MAKE) deploy-api
	@echo ""
	@echo "Step 2/3: Deploying Scheduler..."
	$(MAKE) deploy-scheduler
	@echo ""
	@echo "Step 3/3: Deploying Frontend..."
	$(MAKE) deploy-web
	@echo ""
	@echo "✅ All services deployed!"
	@echo "Run 'make verify-all' for post-deployment checks."

deploy-rollback: ## Rollback all services to previous deployments
	@echo "=== Rollback Procedure ==="
	@echo ""
	@echo "Step 1: Rollback Frontend"
	@echo "  vercel rollback secondbrain-os --safe=10"
	@echo ""
	@echo "Step 2: Rollback API"
	@echo "  railway rollback --service secondbrain-api"
	@echo ""
	@echo "Step 3: Rollback Scheduler"
	@echo "  railway rollback --service secondbrain-scheduler"
	@echo ""
	@echo "Run these commands manually to confirm each rollback."
	@echo "See docs/operations/production-deployment.md for detailed procedures."

# ── Deployment Verification ──────────────────────────────────────────────────

verify-api: ## Verify API health endpoint
	@echo "Checking API health..."
	@curl -s https://api.secondbrain-os.com/health/ready | python -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\",\"unknown\")}'); sys.exit(0 if d.get('status')=='healthy' else 1)" || echo "⚠ API health check failed"

verify-web: ## Verify frontend is serving
	@echo "Checking frontend..."
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://secondbrain-os.vercel.app || echo "⚠ Frontend check failed"

verify-scheduler: ## Verify scheduler health
	@echo "Checking scheduler health..."
	@curl -s https://scheduler.secondbrain-os.com/health | python -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\",\"unknown\")}, Jobs: {d.get(\"jobs\",\"?\")}')" || echo "⚠ Scheduler health check failed"

verify-all: ## Verify all services post-deployment
	$(MAKE) verify-api
	$(MAKE) verify-web
	$(MAKE) verify-scheduler
	@echo ""
	@echo "✅ Post-deployment verification complete."

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
	cd apps/web && node scripts/sync-figma-tokens.mjs

token-check: ## Check for hardcoded color values (token drift)
	cd apps/web && node scripts/check-token-drift.mjs

token-check-fix: ## Auto-fix hardcoded color values
	cd apps/web && node scripts/check-token-drift.mjs --fix

# ── Infrastructure ────────────────────────────────────────────────────────────

setup-ci: ## Create .github/ directory with CI workflow templates
	@echo "✓ .github/ directory already configured"

ifeq ($(OS),Windows_NT)
  PENTEST_SCRIPT = scripts/run-pentest.ps1
  OWASP_SCRIPT = scripts/owasp-check.ps1
  SQLI_SCRIPT = scripts/sql-injection-audit.ps1
  ZAP_SCRIPT = scripts/zap-pentest.ps1
  SHELL_CMD = powershell
else
  PENTEST_SCRIPT = scripts/run-pentest.sh
  OWASP_SCRIPT = scripts/owasp-check.sh
  SQLI_SCRIPT = scripts/sql-injection-audit.ps1
  ZAP_SCRIPT = scripts/zap-pentest.sh
  SHELL_CMD = bash
endif

pentest: ## Run full penetration test suite (SAST + DAST + custom attacks)
	$(SHELL_CMD) $(PENTEST_SCRIPT)

owasp-check: ## Run OWASP Top 10 static analysis
	$(SHELL_CMD) $(OWASP_SCRIPT)

sqli-audit: ## Run SQL injection pattern audit
	$(SHELL_CMD) $(SQLI_SCRIPT)

zap-scan: ## Run OWASP ZAP DAST active scan (requires Docker)
	$(SHELL_CMD) $(ZAP_SCRIPT)

# ── Document Validation ───────────────────────────────────────────────────────

validate-docs: validate-links validate-doc-ids validate-prompts
	@echo "All document validations passed"

validate-links:
	pwsh ./scripts/check-links.ps1

validate-doc-ids:
	python scripts/validate-doc-ids.py

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
