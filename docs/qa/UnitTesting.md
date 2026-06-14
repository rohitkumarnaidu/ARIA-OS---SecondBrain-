# Unit Testing Strategy

## 1. Unit Testing Philosophy

### Test Behavior, Not Implementation

Unit tests verify **what** the code does, not **how** it does it. Implementation details (internal data structures, private method names, refactoring artifacts) are opaque to tests. A behavior-oriented test suite allows fearless refactoring: you can rewrite the internals of a module and verify correctness without changing a single test.

```python
# ❌ Implementation-coupled test
def test_task_service_internal():
    svc = TaskService()
    svc._tasks = []
    svc._counter = 0
    svc._add_to_internal_list("Test")
    assert svc._counter == 1
    assert len(svc._tasks) == 1

# ✅ Behavior-oriented test
def test_creates_task_and_returns_expected_object():
    svc = TaskService()
    task = svc.create(title="Test", priority="high")
    assert task.title == "Test"
    assert task.priority == "high"
    assert task.status == "pending"
```

**Frontend equivalent (React Testing Library):**

```typescript
// ❌ Implementation-coupled: testing internal state
it('adds task to internal array', () => {
  const { result } = renderHook(() => useTaskStore())
  act(() => result.current.addTask({ title: 'Test' }))
  expect(result.current.tasks.length).toBe(1)
})

// ✅ Behavior-oriented: testing what the user sees
it('shows new task in the list after creation', async () => {
  const user = userEvent.setup()
  render(<TaskList />)
  await user.click(screen.getByRole('button', { name: /add task/i }))
  await user.type(screen.getByRole('textbox', { name: /title/i }), 'Test')
  await user.click(screen.getByRole('button', { name: /save/i }))
  expect(screen.getByText('Test')).toBeInTheDocument()
})
```

### FIRST Principles

Every unit test should satisfy the FIRST acronym:

| Principle | Meaning | Enforcement |
|---|---|---|
| **F**ast | Tests execute in milliseconds | CI timeout per test file < 30s; total unit suite < 5min |
| **I**solated | No shared state, no test-order dependencies | `conftest.py` fixtures with `scope="function"`; `beforeEach` reset in Vitest |
| **R**epeatable | Same result every run, on any machine | Deterministic seeds for random data; mock all IO |
| **S**elf-validating | Pass/fail binary, no manual inspection | Assertions only; no print-debugging in test output |
| **T**imely | Written alongside production code | Coverage gate enforced in CI; PRs must include or update tests |

```python
# Fixture isolation example
@pytest.fixture(autouse=True)
def reset_task_store():
    """Every test gets a fresh store — zero shared state."""
    TaskService._instance = None
    yield
    TaskService._instance = None
```

### Given-When-Then Test Structure

Tests follow a consistent narrative pattern:

```
test__[scenario]__[expected_behavior]
```

```python
def test__task_with_due_date_before_today__marked_as_overdue():
    # Given
    task = Task(title="Overdue", due_date=datetime.now() - timedelta(days=1))

    # When
    result = task_service.check_status(task)

    # Then
    assert result.status == "overdue"
    assert result.priority_score > 0.8
```

```typescript
it('adds 1 + 2 to equal 3', () => {
  // Given
  const calculator = new Calculator()
  // When
  const result = calculator.add(1, 2)
  // Then
  expect(result).toBe(3)
})
```

---

## 2. Test Framework Setup

### 2.1 Python / pytest

**Configuration (`pyproject.toml`):**

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests", "packages"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
filterwarnings = ["error"]
markers = {
    "unit": "Unit tests (fast, no external deps)",
    "integration": "Integration tests (require Supabase)",
    "e2e": "End-to-end tests (require browser)",
    "slow": "Tests that take >5 seconds",
    "ai": "Tests requiring AI model (Ollama or Claude)",
    "smoke": "Quick smoke tests for pre-commit",
}
```

**Required dependencies (`requirements-dev.txt`):**

```
pytest>=8.0,<9.0
pytest-asyncio>=0.23,<1.0
pytest-cov>=5.0,<6.0
pytest-mock>=3.12,<4.0
pytest-httpx>=0.30,<1.0
pytest-timeout>=2.2,<3.0
factory_boy>=3.3,<4.0
freezegun>=1.4,<2.0
```

**Running tests:**

```bash
# Quick feedback loop (smoke + unit only)
pytest -m "smoke or unit" -x --timeout=30

# Full unit suite with coverage
pytest -m unit --cov=packages/ai --cov=packages/shared --cov-report=term-missing

# Single test module
pytest tests/test_prompt_loader.py -xvs

# Parallel execution
pytest -n auto -m unit
```

### 2.2 TypeScript / Vitest + React Testing Library

**Configuration (`vitest.config.ts`):**

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.test.{ts,tsx}', '**/__tests__/**/*.{ts,tsx}'],
    exclude: ['node_modules', 'e2e', '.next'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      thresholds: {
        statements: 70,
        branches: 65,
        functions: 75,
        lines: 70,
      },
    },
    testTimeout: 10_000,
    hookTimeout: 10_000,
    retry: process.env.CI ? 2 : 0,
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './app') },
  },
})
```

**Setup file (`vitest.setup.ts`):**

```typescript
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup()
})

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))
```

**Required dependencies (`package.json`):**

```json
{
  "devDependencies": {
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/react-hooks": "^8.0.0",
    "msw": "^2.3.0",
    "jsdom": "^24.0.0"
  }
}
```

---

## 3. Test Structure Per Module

### 3.1 Arrange-Act-Assert (AAA) Pattern

Every test block follows three clearly separated phases:

```python
class TestTaskCompletion:
    """Tests for task completion logic - all share the same AAA structure."""

    async def test__mark_task_complete__updates_status_and_timestamp(self):
        # Arrange
        user = await user_factory.create()
        task = await task_factory.create(
            user_id=user.id,
            title="Complete project report",
            status="in_progress",
            priority="high"
        )
        completion_note = "Finished all sections"

        # Act
        result = await self.service.complete_task(
            task_id=task.id,
            user_id=user.id,
            note=completion_note
        )

        # Then
        assert result.status == "completed"
        assert result.completed_at is not None
        assert isinstance(result.completed_at, datetime)
        assert result.completion_note == completion_note
        assert (datetime.utcnow() - result.completed_at).total_seconds() < 5

    async def test__mark_task_complete__with_dependencies_unmet__raises_error(self):
        # Arrange
        user = await user_factory.create()
        dependency = await task_factory.create(user_id=user.id, status="pending")
        task = await task_factory.create(
            user_id=user.id,
            dependency_ids=[dependency.id]
        )

        # Act / Assert
        with pytest.raises(DependencyNotMetError) as exc_info:
            await self.service.complete_task(task_id=task.id, user_id=user.id)

        assert str(exc_info.value).startswith("Cannot complete")
        assert dependency.id in str(exc_info.value)
```

```typescript
describe('TaskCard component', () => {
  it('displays priority badge and due date', () => {
    // Arrange
    const task: Task = {
      id: '1',
      title: 'Review PR',
      priority: 'high',
      dueDate: new Date('2026-06-15'),
      status: 'pending',
    }

    // Act
    render(<TaskCard task={task} onComplete={vi.fn()} />)

    // Assert
    expect(screen.getByText('Review PR')).toBeInTheDocument()
    expect(screen.getByText(/high/i)).toBeInTheDocument()
    expect(screen.getByText(/jun 15/i)).toBeInTheDocument()
  })
})
```

### 3.2 Module-to-Test-File Mapping

```
packages/
├── ai/
│   ├── prompt_loader.py
│   ├── client.py
│   └── agents/
│       ├── briefing_agent.py
│       ├── memory_agent.py
│       ├── learning_agent.py
│       ├── opportunity_agent.py
│       ├── task_agent.py
│       ├── weekly_review_agent.py
│       ├── sleep_agent.py
│       └── nudge_agent.py
│
tests/
├── test_prompt_loader.py       # 16 tests: Parsing, rendering, fallback, edge cases
├── test_agent_prompts.py       # 14 tests: Per-agent content, size, tags
├── agents/
│   ├── test_briefing_agent.py
│   ├── test_memory_agent.py
│   ├── test_learning_agent.py
│   ├── test_opportunity_agent.py
│   ├── test_task_agent.py
│   ├── test_weekly_review_agent.py
│   ├── test_sleep_agent.py
│   └── test_nudge_agent.py
├── shared/
│   ├── test_cache.py
│   ├── test_rate_limiter.py
│   ├── test_security.py
│   └── test_logger.py
└── api/
    ├── test_tasks.py
    ├── test_courses.py
    ├── test_goals.py
    ├── test_habits.py
    ├── test_ideas.py
    ├── test_income.py
    ├── test_opportunities.py
    ├── test_projects.py
    ├── test_resources.py
    ├── test_sleep.py
    ├── test_time.py
    ├── test_chat.py
    └── test_automation.py
```

---

## 4. Unit Test Inventory and Coverage Targets

### 4.1 Coverage Targets by Module

| Module | Lines of Code | Test Files | Tests | Coverage Target | Current |
|---|---|---|---|---|---|
| `packages/ai/prompt_loader.py` | 412 | 1 | 16 | 95% | 96% |
| `packages/ai/client.py` | 186 | 1 | 12 | 90% | 92% |
| `packages/ai/agents/briefing_agent.py` | 312 | 1 | 8 | 90% | 91% |
| `packages/ai/agents/memory_agent.py` | 245 | 1 | 7 | 90% | 88% |
| `packages/ai/agents/learning_agent.py` | 278 | 1 | 8 | 85% | 86% |
| `packages/ai/agents/opportunity_agent.py` | 298 | 1 | 8 | 90% | 90% |
| `packages/ai/agents/task_agent.py` | 234 | 1 | 7 | 90% | 93% |
| `packages/ai/agents/weekly_review_agent.py` | 267 | 1 | 7 | 90% | 89% |
| `packages/ai/agents/sleep_agent.py` | 198 | 1 | 6 | 85% | 87% |
| `packages/ai/agents/nudge_agent.py` | 212 | 1 | 6 | 85% | 84% |
| `packages/shared/utils/cache.py` | 89 | 1 | 6 | 95% | 97% |
| `packages/shared/utils/rate_limiter.py` | 134 | 1 | 7 | 95% | 95% |
| `packages/shared/utils/security.py` | 156 | 1 | 8 | 95% | 96% |
| `packages/shared/utils/logger.py` | 78 | 1 | 5 | 90% | 91% |
| `apps/api/**/*.py` | ~1800 | 13 | ~65 | 80% | 78% |
| `apps/web/**/*.tsx` | ~4500 | 15 | ~80 | 70% | 68% |
| `services/scheduler/*.py` | ~400 | 1 | 10 | 80% | 82% |

### 4.2 Coverage Enforcement (CI)

```yaml
# .github/workflows/ci.yml — Coverage enforcement
- name: Backend coverage
  run: |
    pytest -m unit \
      --cov=packages/ai \
      --cov=packages/shared/utils \
      --cov=apps/api \
      --cov-report=xml \
      --cov-report=term-missing
    # Enforce per-module thresholds
    python scripts/check_coverage.py \
      --module packages/ai --min 90 \
      --module packages/shared/utils --min 90 \
      --module apps/api --min 75
```

**Coverage check script (`scripts/check_coverage.py`):**

```python
"""Enforce per-module code coverage thresholds."""
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

COVERAGE_XML = Path("coverage.xml")
THRESHOLDS = {
    "packages/ai": 90.0,
    "packages/shared/utils": 90.0,
    "packages/config": 80.0,
    "packages/database": 85.0,
    "apps/api": 75.0,
    "services/scheduler": 75.0,
}

def main():
    if not COVERAGE_XML.exists():
        print("❌ coverage.xml not found. Run pytest --cov first.")
        sys.exit(1)

    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()
    failures = []

    for package, threshold in THRESHOLDS.items():
        # Sum line-rate for all source files in this package
        total_lines = 0
        covered_lines = 0
        for cls in root.findall(".//class"):
            filename = cls.get("filename", "")
            if package in filename:
                line_rate = float(cls.get("line-rate", 0))
                # approximation: use total lines from the class
                lines_elem = cls.find("lines")
                if lines_elem is not None:
                    n_lines = len(lines_elem.findall("line"))
                    covered = int(n_lines * line_rate)
                    total_lines += n_lines
                    covered_lines += covered

        if total_lines == 0:
            print(f"⚠  {package}: no lines found, skipping")
            continue

        actual = (covered_lines / total_lines) * 100
        status = "✅" if actual >= threshold else "❌"
        print(f"{status} {package}: {actual:.1f}% (threshold {threshold}%)")

        if actual < threshold:
            failures.append(f"{package}: {actual:.1f}% < {threshold}%")

    if failures:
        print("\n❌ Coverage failures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 5. Python Testing Patterns

### 5.1 Fixtures — The Right Way

**Module-level `conftest.py`:**

```python
# tests/conftest.py
import asyncio
import sys
from pathlib import Path

# Ensure packages/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

import pytest
from pytest_httpx import HTTPXMock


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_supabase(mocker):
    """Mock Supabase client for all tests."""
    mock = mocker.patch("config.core.supabase.SupabaseClient")
    instance = mock.return_value
    instance.table.return_value.select.return_value = instance
    instance.execute.return_value.data = []
    instance.execute.return_value.error = None
    return instance


@pytest.fixture
def mock_llm(mocker):
    """Mock LLM client — returns predictable JSON."""
    from ai.client import LLMClient
    mock = mocker.patch.object(LLMClient, "generate_json")
    mock.return_value = {"status": "ok", "data": []}
    return mock


@pytest.fixture
def sample_user_id():
    """Deterministic user ID for test isolation."""
    return "test-user-001"


@pytest.fixture
def sample_task_data():
    """Standard task creation payload."""
    return {
        "title": "Test task",
        "priority": "medium",
        "status": "pending",
        "due_date": "2026-06-20T00:00:00Z",
        "user_id": "test-user-001",
    }
```

**Agent-specific `conftest.py`:**

```python
# tests/agents/conftest.py
import pytest
from datetime import datetime, timedelta
from ai.prompt_loader import prompts


@pytest.fixture(autouse=True)
def ensure_prompts_loaded():
    """Verify prompt files are accessible before each test."""
    assert prompts.get_agent("briefing_agent") is not None, \
        "briefing_agent prompt not found!"
    assert prompts.get_agent("memory_agent") is not None
    assert prompts.get_agent("task_agent") is not None
    yield


@pytest.fixture
def mock_supabase_response(mocker):
    """Factory fixture for mock Supabase responses."""

    def _response(data: list, error: str | None = None):
        mock = mocker.MagicMock()
        mock.data = data
        mock.error = error
        return mock

    return _response
```

### 5.2 Mocking Strategies

| Scenario | Tool | Example |
|---|---|---|
| External API calls | `pytest-httpx` / `httpx_mock` | Mocking Claude API responses |
| Database queries | `pytest-mock` patching supabase | Return deterministic rows |
| File system reads | `mocker.patch("builtins.open")` | Simulate missing prompt file |
| Environment variables | `mocker.patch.dict(os.environ)` | Toggle `USE_LOCAL_AI` |
| Time-dependent logic | `freezegun` / `mocker.patch("datetime.now")` | Freeze time for scheduling |
| Async generators | Custom fixture | Mock streaming AI responses |

```python
# Mocking Claude API with httpx_mock
@pytest.mark.asyncio
async def test_claude_fallback_on_ollama_timeout(httpx_mock):
    """When Ollama times out, agent should fall back to Claude."""
    # Arrange
    httpx_mock.add_response(
        url="http://localhost:11434/api/generate",
        status_code=504,
        timeout=True,
    )
    httpx_mock.add_response(
        url="https://api.anthropic.com/v1/messages",
        json={
            "content": [{"text": '{"summary": "Fallback response"}'}],
            "model": "claude-sonnet-4",
        },
    )

    # Act
    result = await briefing_agent.generate_briefing(user_id="test-user")

    # Assert
    assert result["summary"] == "Fallback response"
```

### 5.3 Parametrized Tests

```python
@pytest.mark.parametrize(
    "priority,expected_score",
    [
        ("urgent", 1.0),
        ("high", 0.8),
        ("medium", 0.5),
        ("low", 0.2),
        (None, 0.5),  # default
    ],
)
def test_priority_scoring(priority, expected_score):
    score = task_service.calculate_priority_score(priority)
    assert score == expected_score


@pytest.mark.parametrize(
    "status,expected_visible",
    [
        ("pending", True),
        ("in_progress", True),
        ("completed", False),
        ("archived", False),
        ("cancelled", False),
    ],
)
def test_task_visibility_in_active_view(status, expected_visible):
    task = Task(status=status)
    assert task.is_visible_in_active_view() == expected_visible


# Edge case matrix — exhaustive
@pytest.mark.parametrize(
    "title,max_length,expected_valid",
    [
        ("Valid Title", 200, True),
        ("", 200, False),
        ("A" * 200, 200, True),
        ("A" * 201, 200, False),
        ("   ", 200, False),           # whitespace only
        ("<script>alert(1)</script>", 200, True),  # sanitized later
        ("Normal - with symbols! @#$%", 200, True),
    ],
)
def test_task_title_validation(title, max_length, expected_valid):
    errors = task_service.validate_title(title, max_length)
    assert (len(errors) == 0) == expected_valid
```

### 5.4 Async Tests with pytest-asyncio

```python
@pytest.mark.asyncio
async def test_briefing_generates_all_sections():
    """Weekly briefing must contain all 5 required sections."""
    # Given
    user_id = "test-user-001"

    # When
    briefing = await briefing_agent.generate_daily_briefing(user_id)

    # Then
    assert "tasks" in briefing
    assert "goals" in briefing
    assert "courses" in briefing
    assert "habits" in briefing
    assert "wellness" in briefing
    assert isinstance(briefing["tasks"], list)
    assert isinstance(briefing["goals"], list)
    assert len(briefing["tasks"]) <= 5  # top 5 tasks


@pytest.mark.asyncio
async def test_concurrent_briefings_isolated():
    """Two concurrent briefings for different users must not interfere."""
    user_a = "user-alpha"
    user_b = "user-beta"

    results = await asyncio.gather(
        briefing_agent.generate_daily_briefing(user_a),
        briefing_agent.generate_daily_briefing(user_b),
    )

    assert results[0]["user_id"] == user_a
    assert results[1]["user_id"] == user_b
    assert results[0] != results[1]  # data differs


@pytest.mark.asyncio
async def test_task_agent_streams_response():
    """Task agent supports streaming for real-time suggestions."""
    chunks = []
    async for chunk in task_agent.stream_breakdown(
        user_id="test-user",
        task_title="Build authentication system"
    ):
        chunks.append(chunk)
    assert len(chunks) >= 1
    assert all(isinstance(c, str) for c in chunks)
```

---

## 6. TypeScript Testing Patterns

### 6.1 React Testing Library Queries

| Query | When to Use | Priority |
|---|---|---|
| `getByRole` | Interactive elements (buttons, links, inputs) | ⭐ Best |
| `getByLabelText` | Form inputs with labels | ⭐ Best |
| `getByPlaceholderText` | Inputs with placeholder only | ✅ Good |
| `getByText` | Non-interactive text elements | ✅ Good |
| `getByDisplayValue` | Form elements with current value | ✅ Good |
| `getByAltText` | Images | ✅ Good |
| `getByTitle` | Elements with title attribute | ⚠️ Fallback |
| `getByTestId` | Only when no semantic query works | ❌ Last resort |

```typescript
it('submits task form and shows success toast', async () => {
  const user = userEvent.setup()

  render(<TaskForm />)

  // Use getByRole for interactive elements
  const titleInput = screen.getByRole('textbox', { name: /task title/i })
  const submitButton = screen.getByRole('button', { name: /create task/i })

  await user.type(titleInput, 'Write unit testing guide')
  await user.selectOptions(
    screen.getByRole('combobox', { name: /priority/i }),
    'high'
  )
  await user.click(submitButton)

  // Assert success state
  expect(await screen.findByText(/task created/i)).toBeInTheDocument()
})
```

### 6.2 userEvent vs fireEvent

```typescript
// ❌ fireEvent — does not simulate browser behavior
it('clicks button with fireEvent', () => {
  fireEvent.click(screen.getByRole('button'))
})

// ✅ userEvent — simulates full browser interaction chain
it('clicks button with userEvent', async () => {
  const user = userEvent.setup()
  await user.click(screen.getByRole('button'))
  // userEvent triggers: hover → mouseDown → mouseUp → click → blur
})
```

### 6.3 Mock Service Worker (MSW) for API Mocks

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/tasks', () => {
    return HttpResponse.json([
      { id: '1', title: 'Test task', priority: 'high', status: 'pending' },
    ])
  }),

  http.post('/api/tasks', async ({ request }) => {
    const body = await request.json() as { title: string }
    return HttpResponse.json(
      { id: 'new-1', title: body.title, priority: 'medium', status: 'pending' },
      { status: 201 }
    )
  }),

  http.get('/api/chat', () => {
    return HttpResponse.json({
      response: 'Here is your daily briefing...',
      timestamp: new Date().toISOString(),
    })
  }),
]

// mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

```typescript
// vitest.setup.ts — MSW integration
import { server } from './mocks/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

---

## 7. PromptLoader Unit Tests

The `PromptLoader` is the backbone of the AI agent system. Its tests cover four categories:

### 7.1 Frontmatter Parsing

```python
# tests/test_prompt_loader.py — Frontmatter parsing
import pytest
from pathlib import Path
from ai.prompt_loader import PromptLoader

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "prompts"


@pytest.fixture
def loader():
    return PromptLoader(prompts_dir=str(FIXTURE_DIR))


def test_parses_valid_frontmatter(loader):
    """A standard prompt file with valid YAML frontmatter."""
    entry = loader.get_agent("valid_agent")
    assert entry is not None
    assert entry.frontmatter["version"] == "2.1.0"
    assert entry.frontmatter["status"] == "active"
    assert entry.frontmatter["max_tokens"] == 4096
    assert entry.frontmatter["temperature"] == 0.5
    assert entry.frontmatter["model"] == "ollama/mistral:7b"
    assert len(entry.body) > 0


def test_parses_body_without_frontmatter(loader):
    """Files without YAML frontmatter are treated as pure body."""
    entry = loader.get_agent("no_frontmatter")
    assert entry is not None
    assert entry.frontmatter == {}  # empty
    assert entry.body.startswith("This is a prompt without frontmatter.")


def test_invalid_yaml_frontmatter_returns_none(loader):
    """Malformed YAML frontmatter should not crash the loader."""
    entry = loader.get_agent("invalid_yaml")
    assert entry is None  # gracefully skipped


def test_missing_file_returns_none(loader):
    """Asking for a non-existent prompt returns None gracefully."""
    entry = loader.get_agent("nonexistent_agent")
    assert entry is None


def test_frontmatter_type_enforcement(loader):
    """max_tokens and temperature must be numbers, not strings."""
    errors = loader.validate_frontmatter("numeric_fields_agent")
    assert any("max_tokens must be a number" in e for e in errors)


def test_frontmatter_required_fields(loader):
    """Required fields: version, status, model, max_tokens, temperature."""
    errors = loader.validate_frontmatter("minimal_agent")
    assert len(errors) == 0  # all required present

    errors = loader.validate_frontmatter("missing_fields_agent")
    assert any("missing required field" in e.lower() for e in errors)
```

### 7.2 Fallback Logic

```python
def test_fallback_when_prompt_directory_missing(tmp_path):
    """Loader with missing directory should not crash."""
    loader = PromptLoader(prompts_dir=str(tmp_path / "nonexistent"))
    entries = loader.list_prompts()
    assert entries == []


def test_fallback_when_single_file_unreadable(loader, mocker):
    """A single unreadable file should not block other prompts."""
    mocker.patch.object(Path, "read_text", side_effect=PermissionError)
    entries = loader.list_prompts()
    assert len(entries) == 0  # all files fail, but no crash


def test_get_returns_none_then_agent_uses_fallback():
    """Agent should gracefully degrade when prompt unavailable."""
    loader = PromptLoader(prompts_dir="nonexistent")
    assert loader.get_agent("briefing_agent") is None

    # The agent module must handle None
    from ai.agents.briefing_agent import generate_daily_briefing
    result = generate_daily_briefing("test-user", loader=loader)
    assert result is not None  # falls back to inline prompt
```

### 7.3 Rendering with Context

```python
def test_render_with_kwargs(loader):
    """Render should substitute {placeholders} in prompt body."""
    entry = loader.get_template("context_assembly")
    rendered = entry.render(
        user_name="John",
        task_count=5,
        current_date="2026-06-11"
    )
    assert "John" in rendered
    assert "5" in rendered
    assert "2026-06-11" in rendered


def test_render_with_missing_placeholder(loader):
    """Missing kwargs leave placeholder as-is (no crash)."""
    entry = loader.get_template("context_assembly")
    rendered = entry.render(user_name="John")
    assert "{task_count}" in rendered  # not substituted


def test_render_with_extra_kwargs(loader):
    """Extra kwargs are ignored."""
    entry = loader.get_template("context_assembly")
    rendered = entry.render(
        user_name="John",
        task_count=5,
        unused_param="should be ignored"
    )
    assert "John" in rendered
    assert "should be ignored" not in rendered  # no injection
```

### 7.4 Edge Cases

```python
def test_unicode_content(loader):
    """Prompt files with Unicode characters (emojis, non-ASCII)."""
    entry = loader.get_agent("unicode_agent")
    assert entry is not None
    assert "你好" in entry.body or "😊" in entry.body


def test_bom_stripped(loader):
    """UTF-8 BOM should be automatically removed."""
    entry = loader.get_agent("bom_file")
    assert entry is not None
    assert not entry.body.startswith("\ufeff")


def test_very_large_prompt(loader):
    """Large prompts (>100KB) should load without memory issues."""
    entry = loader.get_agent("large_prompt")
    assert entry is not None
    assert len(entry.body) > 100_000


def test_crlf_line_endings(loader):
    """CRLF line endings should be handled correctly."""
    entry = loader.get_agent("crlf_file")
    assert entry is not None
    assert "\r\n" not in entry.body  # normalized


def test_empty_prompt_file(loader):
    """Empty prompt file (only frontmatter, no body)."""
    entry = loader.get_agent("empty_body")
    assert entry is not None
    assert entry.body == ""
    assert entry.frontmatter["status"] == "active"


def test_duplicate_prompt_names_across_categories(loader):
    """Same filename in different categories should not conflict."""
    system = loader.get_system("duplicate_name")
    agent = loader.get_agent("duplicate_name")
    assert system is not None
    assert agent is not None
    assert system.file_path != agent.file_path
```

---

## 8. Agent Module Unit Tests

### 8.1 Mock LLM Client

```python
# tests/agents/test_briefing_agent.py
import pytest
from datetime import date
from ai.agents import briefing_agent


@pytest.fixture
def mock_llm_json(mocker):
    """Mock LLM to return a predictable briefing structure."""
    mock = mocker.patch("ai.client.LLMClient.generate_json")
    mock.return_value = {
        "date": "2026-06-11",
        "greeting": "Good morning, John!",
        "task_summary": {
            "total_pending": 3,
            "overdue": 1,
            "due_today": 2,
        },
        "top_priority": "Complete project report",
        "wellness_tip": "Take a 5-minute stretch break",
        "focus_suggestion": "Deep work block from 9 AM to 11 AM",
        "today_sections": [
            {"type": "tasks", "title": "Tasks Due Today", "items": [...]},
            {"type": "courses", "title": "Courses in Progress", "items": [...]},
            {"type": "habits", "title": "Habits to Track", "items": [...]},
        ],
    }
    return mock


@pytest.mark.asyncio
async def test_briefing_constructs_correct_prompt(mock_llm_json):
    """Verify the prompt sent to LLM contains user context."""
    user_data = {
        "user_name": "John",
        "task_count": 8,
        "overdue_count": 2,
        "habit_streaks": {"meditation": 5, "reading": 3},
    }

    result = await briefing_agent.generate_daily_briefing(user_data)

    assert result["greeting"] == "Good morning, John!"
    assert result["task_summary"]["overdue"] == 1
    assert result["wellness_tip"] is not None
```

### 8.2 Verify Prompt Construction

```python
def test_task_agent_builds_correct_system_prompt():
    """System prompt should reference prompt_loader content."""
    from ai.prompt_loader import prompts
    from ai.agents.task_agent import build_task_breakdown

    prompt = prompts.get_agent("task_agent")
    assert prompt is not None
    assert "Task Decomposition" in prompt.body
    assert "priority" in prompt.body.lower()


def test_memory_agent_prompt_includes_retention_rules():
    """Memory agent prompt must define retention/discard logic."""
    prompt = prompts.get_agent("memory_agent")
    assert prompt is not None
    assert "retention" in prompt.body.lower()
    assert "discard" in prompt.body.lower()
    assert "consolidation" in prompt.body.lower()


@pytest.mark.parametrize("agent_name", [
    "briefing_agent",
    "memory_agent",
    "learning_agent",
    "opportunity_agent",
    "task_agent",
    "weekly_review_agent",
    "sleep_agent",
    "nudge_agent",
])
def test_all_agent_prompts_have_minimum_content(agent_name):
    """Every agent prompt must exceed 1000 characters of body content."""
    prompt = prompts.get_agent(agent_name)
    assert prompt is not None, f"{agent_name} prompt not loaded"
    assert len(prompt.body) > 1000, f"{agent_name} body too short ({len(prompt.body)} chars)"
    assert prompt.frontmatter.get("status") == "active", f"{agent_name} not active"
```

### 8.3 Test All Code Paths

```python
@pytest.mark.asyncio
async def test_nudge_agent_empty_courses_returns_empty():
    """No active courses should return an empty nudge list."""
    result = await nudge_agent.generate_course_nudges(
        user_id="test-user",
        active_courses=[],
    )
    assert result["nudges"] == []
    assert result["total_nudges"] == 0


@pytest.mark.asyncio
async def test_nudge_agent_behind_schedule_detected():
    """Course with <60% progress past midpoint should flag as behind."""
    courses = [
        {"id": "c1", "title": "Linear Algebra", "progress": 0.3, "time_elapsed": 0.7},
        {"id": "c2", "title": "Data Structures", "progress": 0.8, "time_elapsed": 0.5},
    ]
    result = await nudge_agent.generate_course_nudges(
        user_id="test-user",
        active_courses=courses,
    )
    behind = [n for n in result["nudges"] if n["type"] == "behind_schedule"]
    assert len(behind) == 1
    assert behind[0]["course_id"] == "c1"


@pytest.mark.asyncio
async def test_sleep_agent_wind_down_variants():
    """Sleep agent should generate different messages for different phases."""
    phases = ["wind_down", "sleep_time", "morning_reflection"]
    for phase in phases:
        result = await sleep_agent.generate_message(
            user_id="test-user",
            phase=phase,
        )
        assert result is not None
        assert result["phase"] == phase
        assert len(result["message"]) > 20
```

---

## 9. API Endpoint Unit Tests

### 9.1 Mock Supabase

```python
# tests/api/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_tasks_returns_200_with_pagination(sample_user_id, mock_supabase):
    """GET /api/tasks should return paginated results."""
    mock_supabase.execute.return_value.data = [
        {"id": "1", "title": "Task 1", "status": "pending", "user_id": sample_user_id},
        {"id": "2", "title": "Task 2", "status": "completed", "user_id": sample_user_id},
    ]

    response = client.get(
        "/api/tasks/",
        headers={"Authorization": f"Bearer test-token-{sample_user_id}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"


def test_list_tasks_empty_returns_200(mock_supabase):
    """Empty task list should return 200 with empty array, not 404."""
    mock_supabase.execute.return_value.data = []

    response = client.get("/api/tasks/", headers={"Authorization": "Bearer test-token"})

    assert response.status_code == 200
    assert response.json() == []
```

### 9.2 Test All HTTP Status Codes

```python
def test_get_task_returns_404_for_missing_id(mock_supabase):
    """Non-existent task ID should return 404."""
    mock_supabase.execute.return_value.data = []

    response = client.get(
        "/api/tasks/nonexistent-id",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_task_returns_201(mock_supabase, sample_task_data):
    """Successful task creation should return 201."""
    mock_supabase.execute.return_value.data = [{
        **sample_task_data,
        "id": "new-id-123",
        "created_at": "2026-06-11T10:00:00Z",
    }]

    response = client.post(
        "/api/tasks/",
        json=sample_task_data,
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 201
    assert response.json()["id"] == "new-id-123"


def test_create_task_returns_422_for_invalid_data():
    """Invalid task payload should return 422 with validation details."""
    response = client.post(
        "/api/tasks/",
        json={"title": "", "priority": "invalid"},  # empty title, bad priority
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("title" in e["loc"] for e in errors)


def test_delete_task_returns_204(mock_supabase):
    """Successful deletion should return 204 No Content."""
    mock_supabase.execute.return_value.data = [{"id": "task-to-delete"}]

    response = client.delete(
        "/api/tasks/task-to-delete",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 204


def test_unauthorized_access_returns_401():
    """Missing auth header should return 401."""
    response = client.get("/api/tasks/")
    assert response.status_code == 401


def test_rate_limit_exceeded_returns_429(sample_user_id, mock_supabase):
    """Exceeding rate limit should return 429."""
    headers = {"Authorization": f"Bearer test-token-{sample_user_id}"}
    # Hit the endpoint 101 times (limit is 100/min)
    for _ in range(100):
        client.get("/api/tasks/", headers=headers)
    response = client.get("/api/tasks/", headers=headers)

    assert response.status_code == 429
```

### 9.3 Test Validation

```python
@pytest.mark.parametrize("payload,expected_status", [
    ({"title": "A", "priority": "low"}, 201),           # valid
    ({"title": "A" * 201, "priority": "low"}, 422),     # title too long
    ({"title": "Valid", "priority": "ultra"}, 422),      # invalid priority
    ({"title": "Valid"}, 201),                            # missing priority → defaults
    ({}, 422),                                            # missing title
    ({"title": "  ", "priority": "medium"}, 422),         # whitespace title
])
def test_create_task_validation_cases(payload, expected_status, mocker):
    """Exhaustive validation boundary testing."""
    mock_supabase = mocker.patch("config.core.supabase.SupabaseClient")
    mock_supabase.return_value.execute.return_value.data = [{
        **payload,
        "id": "test-id",
        "user_id": "test-user",
        "created_at": "2026-06-11T10:00:00Z",
    }]
    if "priority" not in payload:
        mock_supabase.return_value.execute.return_value.data[0]["priority"] = "medium"

    response = client.post(
        "/api/tasks/",
        json=payload,
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == expected_status
```

---

## 10. Test Data Factories and Fixtures

### 10.1 Factory Boy (Python)

```python
# tests/factories.py
import factory
import uuid
from datetime import datetime, timedelta
from typing import Optional


class TaskFactory(factory.DictFactory):
    """Factory for task data dicts (not ORM models, since we mock Supabase)."""

    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.Sequence(lambda n: f"Test Task {n}")
    priority = factory.Iterator(["low", "medium", "high", "urgent"])
    status = factory.Iterator(["pending", "in_progress", "completed", "archived"])
    due_date = factory.LazyFunction(
        lambda: (datetime.utcnow() + timedelta(days=7)).isoformat()
    )
    created_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
    user_id = "test-user-001"
    goal_id = None
    dependency_ids = factory.List([])
    tags = factory.List(["test"])


class UserFactory(factory.DictFactory):
    class Meta:
        model = dict

    id = factory.Sequence(lambda n: f"user-{n:03d}")
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    name = factory.Sequence(lambda n: f"Test User {n}")
    preferences = factory.LazyFunction(lambda: {
        "theme": "dark",
        "briefing_time": "07:00",
        "weekly_review_day": "sunday",
    })


class BriefingFactory(factory.DictFactory):
    class Meta:
        model = dict

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user_id = "test-user-001"
    date = factory.LazyFunction(lambda: datetime.utcnow().date().isoformat())
    content = factory.LazyFunction(lambda: {
        "greeting": "Good morning!",
        "task_summary": {"total": 3, "overdue": 0, "due_today": 1},
        "sections": [],
    })
    generated_at = factory.LazyFunction(lambda: datetime.utcnow().isoformat())
```

**Usage in tests:**

```python
def test_multiple_task_priorities():
    tasks = TaskFactory.create_batch(10)
    priorities = [t["priority"] for t in tasks]
    assert all(p in ["low", "medium", "high", "urgent"] for p in priorities)
    assert len(set(priorities)) >= 3  # at least 3 different priorities


def test_filter_overdue_tasks():
    future = TaskFactory.create(due_date=(datetime.utcnow() + timedelta(days=1)).isoformat())
    overdue = TaskFactory.create(due_date=(datetime.utcnow() - timedelta(days=1)).isoformat())

    result = task_service.filter_overdue([future, overdue])
    assert len(result) == 1
    assert result[0]["id"] == overdue["id"]
```

### 10.2 test-data-bot (TypeScript)

```typescript
// tests/factories.ts
import { build, fake, sequence, oneOf, perBuild } from '@jackfranklin/test-data-bot'

export interface Task {
  id: string
  title: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'pending' | 'in_progress' | 'completed' | 'archived'
  dueDate: Date
  userId: string
  tags: string[]
}

export const taskFactory = build<Task>('Task', {
  fields: {
    id: fake((f) => f.string.uuid()),
    title: sequence((n) => `Test Task ${n}`),
    priority: oneOf('low', 'medium', 'high', 'urgent'),
    status: oneOf('pending', 'in_progress', 'completed'),
    dueDate: fake((f) => f.date.future()),
    userId: perBuild(() => 'test-user-001'),
    tags: ['test'],
  },
})

export const userFactory = build<{ id: string; email: string; name: string }>('User', {
  fields: {
    id: fake((f) => f.string.uuid()),
    email: sequence((n) => `user${n}@test.com`),
    name: sequence((n) => `Test User ${n}`),
  },
})
```

**Usage in tests:**

```typescript
it('renders a list of 5 tasks', () => {
  const tasks = Array.from({ length: 5 }, () => taskFactory())
  render(<TaskList tasks={tasks} />)
  expect(screen.getAllByRole('listitem')).toHaveLength(5)
})

it('allows filtering by priority', async () => {
  const user = userEvent.setup()
  const tasks = [
    taskFactory({ priority: 'high' }),
    taskFactory({ priority: 'low' }),
    taskFactory({ priority: 'medium' }),
  ]
  render(<TaskList tasks={tasks} />)

  await user.click(screen.getByRole('button', { name: /filter by priority/i }))
  await user.click(screen.getByRole('option', { name: /high/i }))

  expect(screen.queryByText(tasks[1].title)).not.toBeInTheDocument()
  expect(screen.getByText(tasks[0].title)).toBeInTheDocument()
})
```

---

## 11. Code Coverage Targets

### 11.1 Per-Module Targets

| Layer | Coverage | Branch | Function | Line | Enforced |
|---|---|---|---|---|---|
| Core AI (agents, prompt_loader, client) | 90% | 85% | 95% | 90% | ✅ CI |
| Shared utilities (cache, security, logger) | 95% | 90% | 95% | 95% | ✅ CI |
| Database schemas & config | 85% | 80% | 90% | 85% | ✅ CI |
| API endpoints | 80% | 75% | 85% | 80% | ✅ CI |
| Frontend stores (Zustand) | 85% | 80% | 90% | 85% | ✅ CI |
| Frontend components | 70% | 65% | 75% | 70% | ✅ CI |
| Frontend hooks | 85% | 80% | 90% | 85% | ✅ CI |
| Scheduler / cron jobs | 80% | 75% | 85% | 80% | ✅ CI |

### 11.2 Coverage Badge

```markdown
![Coverage](https://img.shields.io/badge/coverage-86%25-yellow)
```

Generated by `pytest-cov` + `coverage-badge`:

```bash
coverage-badge -o coverage.svg
```

---

## 12. Coverage Reporting and Enforcement in CI

### 12.1 CI Workflow

```yaml
# .github/workflows/test.yml
name: Unit Tests + Coverage
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r apps/api/requirements.txt
          pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-httpx

      - name: Run unit tests with coverage
        run: |
          pytest -m unit \
            --cov=packages/ai \
            --cov=packages/shared/utils \
            --cov=packages/config \
            --cov=packages/database \
            --cov=apps/api \
            --cov=services/scheduler \
            --cov-report=xml \
            --cov-report=term-missing \
            --junitxml=junit.xml

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml

      - name: Check coverage thresholds
        run: python scripts/check_coverage.py

      - name: Publish coverage to PR comment
        uses: romeovs/lcov-reporter-action@v0.4.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          lcov-file: coverage.xml
```

### 12.2 Coverage Drops

If coverage decreases by >2% in any module:

1. CI marks the build as **yellow (warning)** for 2-5% decrease
2. CI marks the build as **red (failing)** for >5% decrease
3. A PR comment is automatically generated with the diff:

```
⚠️ Coverage Alert: @developer

Coverage decreased in these modules:
- packages/ai: 92.1% → 87.4% (-4.7%) — FAILS THRESHOLD
- apps/api: 78.3% → 77.0% (-1.3%) — OK

Please add tests for:
- packages/ai/agents/briefing_agent.py:68-72 (new code, uncovered)
- packages/ai/prompt_loader.py:112-118 (error handling path)
```

---

## 13. Test Maintenance

### 13.1 Flaky Test Detection

```yaml
# .github/workflows/flaky-detector.yml — runs nightly
name: Flaky Test Detector
on:
  schedule:
    - cron: '0 6 * * *'  # daily at 6 AM

jobs:
  flaky-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests 5x with different random seeds
        run: |
          for seed in 42 123 456 789 1000; do
            echo "=== Seed: $seed ==="
            pytest -m unit --randomly-seed=$seed --timeout=60 || true
          done
```

**Flaky test quarantine process:**

1. A test fails >10% of runs → moved to `@pytest.mark.flaky` quarantine
2. Flaky tests are excluded from CI pass/fail but reported separately
3. A GitHub Issue is auto-created with the flaky test name and stack trace
4. Root cause must be resolved within 1 sprint
5. Fixed test must pass 10 consecutive CI runs before returning to main suite

```python
# Example of documenting a quarantined flaky test
@pytest.mark.flaky(reason="Race condition in async event loop teardown")
@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Flaky in CI — see issue #342"
)
async def test_async_timer_concurrent_starts():
    ...
```

### 13.2 Test Review in PRs

Every PR must include test changes following these rules:

| Situation | Required Action |
|---|---|
| New function added | Add tests for all code paths |
| Bug fix | Add regression test that reproduces the bug |
| Refactoring (no behavior change) | Existing tests must pass unchanged |
| Prompt change | Update `frontmatter.version`; tests remain valid |
| UI component change | Update or add component tests |
| Dependency upgrade | Run full suite; no test changes needed |
| Error handling change | Add tests for new error paths |
| Performance optimization | Add benchmark assertions |

**PR Review Checklist for Tests:**

```markdown
## Test Review Checklist

- [ ] Tests follow AAA / Given-When-Then pattern
- [ ] No test depends on another test's side effects
- [ ] All mocked external services have `assert_called_once` or similar
- [ ] Edge cases covered: empty state, error state, boundary values
- [ ] No hardcoded IDs or dates that will expire
- [ ] Factory fixtures used instead of inline dicts
- [ ] Test names describe scenario and expected outcome
- [ ] TypeScript tests prefer getByRole/getByLabelText over getByTestId
- [ ] No test prints to stdout (no print-debugging)
- [ ] Coverage thresholds maintained or improved
```

### 13.3 Test Audit Log

```sql
-- Each test run records coverage metadata
CREATE TABLE test_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL,
    commit_sha VARCHAR(40) NOT NULL,
    branch VARCHAR(255) NOT NULL,
    module VARCHAR(255) NOT NULL,
    coverage_pct DECIMAL(5,2) NOT NULL,
    tests_passed INTEGER NOT NULL,
    tests_failed INTEGER NOT NULL,
    tests_skipped INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 13.4 Test Performance Budget

| Metric | Budget | Enforcement |
|---|---|---|
| Max test file execution time | 30s | `pytest-timeout` plugin |
| Total unit suite duration | 5 min | CI timeout |
| Max test function length | 50 lines | Lint rule |
| Max fixtures per test file | 15 | Code review |
| Max mocks per test | 5 | Code review |
| Async test timeout | 10s | `pytest.mark.timeout(10)` |

---

## Appendix A: Test Directory Structure (Final)

```
tests/
├── conftest.py                              # Global fixtures, sys.path
├── factories.py                             # TaskFactory, UserFactory, BriefingFactory
├── test_prompt_loader.py                    # 16 tests — PromptLoader
├── test_agent_prompts.py                    # 14 tests — agent prompt content
├── agents/
│   ├── conftest.py                          # Agent test fixtures
│   ├── test_briefing_agent.py               # 8 tests
│   ├── test_memory_agent.py                 # 7 tests
│   ├── test_learning_agent.py               # 8 tests
│   ├── test_opportunity_agent.py            # 8 tests
│   ├── test_task_agent.py                   # 7 tests
│   ├── test_weekly_review_agent.py          # 7 tests
│   ├── test_sleep_agent.py                  # 6 tests
│   └── test_nudge_agent.py                  # 6 tests
├── shared/
│   ├── test_cache.py                        # 6 tests
│   ├── test_rate_limiter.py                 # 7 tests
│   ├── test_security.py                     # 8 tests
│   └── test_logger.py                       # 5 tests
├── api/
│   ├── conftest.py                          # API test fixtures + TestClient
│   ├── test_tasks.py                        # ~8 tests
│   ├── test_courses.py                      # ~5 tests
│   ├── test_goals.py                        # ~5 tests
│   ├── test_habits.py                       # ~5 tests
│   ├── test_ideas.py                        # ~5 tests
│   ├── test_income.py                       # ~5 tests
│   ├── test_opportunities.py                # ~5 tests
│   ├── test_projects.py                     # ~5 tests
│   ├── test_resources.py                    # ~5 tests
│   ├── test_sleep.py                        # ~4 tests
│   ├── test_time.py                         # ~6 tests
│   ├── test_chat.py                         # ~3 tests
│   └── test_automation.py                   # ~4 tests
├── scheduler/
│   └── test_scheduler.py                    # ~10 tests
└── fixtures/
    └── prompts/                             # Test prompt files for PromptLoader
        ├── valid_agent.md
        ├── no_frontmatter.md
        ├── invalid_yaml.md
        ├── missing_fields_agent.md
        ├── minimal_agent.md
        ├── unicode_agent.md
        ├── bom_file.md
        ├── large_prompt.md
        ├── crlf_file.md
        └── empty_body.md
```

---

*Document ID: SB-QA-UNIT-001 | Version: 1.0.0 | Status: Active | Last Updated: 2026-06-11*
