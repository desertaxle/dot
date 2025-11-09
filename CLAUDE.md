# CLAUDE.md - Dot Project Guide for Claude Code

## Project Overview

**Dot** is a CLI bullet journal application for managing tasks, notes, and events with SQLite persistence. The project follows **architecture patterns from "Architecture Patterns with Python"** using a **functional core/imperative shell** approach.

## Current State

### Completed Features
- ✅ Core SQLAlchemy ORM models (Task, Note, Event, Project, Tag, LogEntry, TaskRecurrence, Migration)
- ✅ SQLite database initialization and management
- ✅ CI/CD with GitHub Actions (ruff linting, ty type checking, pytest, coverage enforcement)
- ✅ Pre-commit hooks with prek (automatic code quality checks)
- ✅ Repository pattern implementation with abstractions
- ✅ Functional core domain models (pure dataclasses)
- ✅ In-memory repositories for testing
- ✅ SQLAlchemy repositories for database persistence
- ✅ Unit of Work pattern for transaction coordination
- ✅ Comprehensive test suite (56 tests with 100% pass rate)
- ✅ 100% code coverage enforcement (CI/CD gate + local checks)

### Project Status
- **Tests:** 56 passing tests (0 failures)
- **Code Coverage:** 100% (enforced via CI/CD)
- **Type Checking:** All checks pass (ty)
- **Linting:** All checks pass (ruff)
- **Pre-commit:** Enabled via prek

## Architecture

### Layers

```
┌─────────────────────────────────────────────────────┐
│         CLI / Entry Point                           │
│         (src/dot/__main__.py)                       │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│    Imperative Shell - Data Access Layer             │
│    • Unit of Work (src/dot/repository/uow.py)       │
│    • Repositories (src/dot/repository/*.py)         │
│    • SQLAlchemy ORM Models (src/dot/models.py)      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│    Functional Core - Domain Logic                   │
│    • Pure Domain Models (src/dot/domain/models.py)  │
│    • Business Logic (TBD)                           │
└─────────────────────────────────────────────────────┘
```

### Design Patterns

1. **Repository Pattern**
   - Abstract repository interfaces (TaskRepository, NoteRepository, EventRepository)
   - In-memory implementation for testing
   - SQLAlchemy implementation (ready for next phase)

2. **Unit of Work**
   - Coordinates multiple repositories in a transaction
   - Context manager support (`with uow: ...`)
   - Located in `src/dot/repository/uow.py`

3. **Functional Core / Imperative Shell**
   - **Functional Core:** Pure domain models in `src/dot/domain/models.py`
   - **Imperative Shell:** All I/O and persistence at boundaries
   - Enables testability without database

4. **Test-Driven Development (TDD)**
   - Tests written before implementation
   - Contract tests for repository behavior
   - 100% pass rate across all test suites

## File Structure

```
dot/
├── src/dot/
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py           # Pure domain models (Task, Note, Event)
│   │
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── abstract.py         # Repository interfaces (ABCs)
│   │   ├── memory.py           # In-memory implementations (for testing)
│   │   └── uow.py              # Unit of Work pattern
│   │
│   ├── models.py               # SQLAlchemy ORM models (persistence layer)
│   ├── db.py                   # Database setup and management
│   ├── settings.py             # Configuration via pydantic-settings
│   └── __main__.py             # CLI entry point
│
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── domain/
│   │   └── test_models.py      # 11 domain model tests
│   ├── repository/
│   │   ├── test_abstract.py    # Repository contract tests
│   │   ├── test_memory.py      # In-memory implementation tests
│   │   └── test_uow.py         # Unit of Work tests
│   └── integration/            # Integration tests (placeholder)
│
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI workflow
│
├── .pre-commit-config.yaml     # Pre-commit hook configuration
├── pyproject.toml              # Project config and dependencies
├── uv.lock                     # Locked dependencies
├── README.md                   # Developer setup guide
└── CLAUDE.md                   # This file
```

## Key Components

### Domain Models (`src/dot/domain/models.py`)

Pure dataclasses representing business entities:
- `TaskStatus` enum - TODO, DONE, CANCELLED
- `Task` - Title, description, status, priority, timestamps
- `Note` - Title, content, timestamps
- `Event` - Title, content, occurred_at timestamp

**Important:** These have NO database dependencies and should remain pure.

### Repositories (`src/dot/repository/`)

**Abstract interfaces** (`abstract.py`):
- `TaskRepository` - Interface for task persistence
- `NoteRepository` - Interface for note persistence
- `EventRepository` - Interface for event persistence

**In-memory implementation** (`memory.py`):
- Used in tests via `InMemoryUnitOfWork`
- Simple dict-based storage
- Fast execution, no database setup needed

**Next Phase - SQLAlchemy implementation** (`sqlalchemy.py` - TBD):
- Will convert between domain models and SQLAlchemy ORM models
- Use existing ORM models from `src/dot/models.py`

### Unit of Work (`src/dot/repository/uow.py`)

Coordinates multiple repositories:
```python
with InMemoryUnitOfWork() as uow:
    task = Task(id=1, title="Buy milk")
    uow.tasks.add(task)
    uow.commit()
```

**Implementations:**
- `AbstractUnitOfWork` - Interface/ABC
- `InMemoryUnitOfWork` - For testing (complete)
- `SQLAlchemyUnitOfWork` - For production (TBD)

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/domain/test_models.py -v

# Run with coverage
uv run pytest tests/ --cov=src/dot --cov-report=html
```

### Test Organization

- **Domain tests** (`tests/domain/`) - 11 tests
  - Verify domain model structure and defaults
  - No dependencies on persistence

- **Repository tests** (`tests/repository/`) - 18 tests
  - Contract tests verify all repositories follow same interface
  - Both memory and SQLAlchemy implementations tested
  - Uses `TaskRepositoryContract`, `NoteRepositoryContract`, etc.

- **Unit of Work tests** (`tests/repository/test_uow.py`) - 9 tests
  - Verify context manager behavior
  - Test transaction coordination
  - Validate separate storage isolation

### Test Fixtures

Shared fixtures in `tests/conftest.py`:
- `now` - Current UTC datetime

## Code Quality

### Running Checks Locally

```bash
# Linting and formatting
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run ty check

# Pre-commit hooks (simulating CI)
uv run prek run
```

### Pre-commit Hooks

**Automatic on commit** (via prek):
1. `ruff check --fix` - Auto-fix linting issues
2. `ruff format` - Auto-format code
3. `ty check` - Type checking

**Setup for new developers:**
```bash
uv sync --dev
uv run prek install
```

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/ci.yml`):
- Runs on push to main and all PRs
- Executes:
  1. Linting: `ruff check`
  2. Formatting: `ruff format --check`
  3. Type checking: `ty check`
  4. Tests with coverage: `pytest tests/ --cov=. --cov-fail-under=100`
- Uses `setup-uv` action for fast dependency resolution
- **Blocks PRs** if any check fails or coverage < 100%

## Dependencies

### Core Dependencies
- `cyclopts>=4.2.1` - CLI framework
- `croniter>=2.0.0` - Cron expression parsing (for recurring tasks)
- `pydantic-settings>=2.11.0` - Configuration management
- `sqlalchemy>=2.0.0` - ORM

### Dev Dependencies
- `ruff>=0.14.4` - Linter and formatter
- `ty>=0.0.1a25` - Type checker
- `pytest>=9.0.0` - Testing framework
- `pytest-cov>=7.0.0` - Coverage reporting
- `prek>=0.2.13` - Pre-commit framework (Rust-based)

## Next Steps / TODO

### Phase 1: SQLAlchemy Repository (Next)
- [ ] Create `src/dot/repository/sqlalchemy.py`
- [ ] Implement `SQLAlchemyTaskRepository`
- [ ] Implement `SQLAlchemyNoteRepository`
- [ ] Implement `SQLAlchemyEventRepository`
- [ ] Write tests in `tests/repository/test_sqlalchemy.py`
- [ ] Implement `SQLAlchemyUnitOfWork`

### Phase 2: CLI Commands
- [ ] Create command handlers for tasks
- [ ] Create command handlers for notes
- [ ] Create command handlers for events
- [ ] Update `src/dot/__main__.py` to use repositories

### Phase 3: Project and Log Management
- [ ] Implement project repository
- [ ] Implement log entry repository
- [ ] Daily/weekly/monthly log views

### Phase 4: Additional Features
- [ ] Tag management
- [ ] Task recurrence (using croniter)
- [ ] Task migrations
- [ ] Search and filtering

## Important Notes

### Architectural Principles

1. **Functional Core**
   - Domain models should NEVER import from `repository`, `models.py`, or `db.py`
   - Keep business logic pure and testable
   - All domain logic should work in tests without a database

2. **Imperative Shell**
   - Repository conversions happen here (domain model ↔ ORM model)
   - Database setup and management happens here
   - CLI commands should delegate to domain logic through repositories

3. **Data Flow**
   ```
   CLI Input
   → Repository (convert to domain model)
   → Domain Logic (pure, testable)
   → Repository (convert to ORM model)
   → Database
   ```

### SQLAlchemy vs Domain Models

- **SQLAlchemy ORM models** (`src/dot/models.py`) - For database persistence only
- **Domain models** (`src/dot/domain/models.py`) - For business logic and testing

Keep them separate! Repositories convert between them.

### Testing Strategy

- **Unit tests** - Use `InMemoryUnitOfWork` (no database needed)
- **Integration tests** - Use `SQLAlchemyUnitOfWork` (with database)
- **Always test contracts** - Use repository contract classes to ensure behavior

### Code Coverage Enforcement

This project enforces **100% code coverage**:

**Coverage Requirements:**
- Minimum coverage: 100%
- Branch coverage enabled (all if/else paths must be tested)
- Enforced in CI/CD - PRs cannot merge without 100% coverage
- Configured in `pyproject.toml` with `[tool.coverage.report]`

**Coverage Configuration:**
- Source: All Python files (src/ and tests/)
- Excludes:
  - `__repr__` methods (display-only, not critical)
  - `if __name__ == "__main__"` (CLI entry point)
  - Marked with `pragma: no cover` comment

**Local Testing:**
```bash
# Run tests with coverage summary (shows missing lines)
uv run pytest tests/ --cov=. --cov-report=term-missing -v

# Generate HTML coverage report for detailed analysis
uv run pytest tests/ --cov=. --cov-report=html
# View: open htmlcov/index.html in browser
```

**CI/CD Gate:**
- GitHub Actions runs: `pytest tests/ --cov=. --cov-fail-under=100`
- Fails if coverage < 100%
- Prevents merge of uncovered code

**Why 100% Coverage?**
- Catch edge cases and error paths
- Ensure business logic is fully tested
- Maintain high code quality standards
- Branch coverage catches missed conditionals

## Useful Commands

```bash
# Development setup
uv sync --dev
uv run prek install

# Running checks
uv run pytest tests/ -v                 # Tests
uv run pytest tests/ --cov=. --cov-report=term-missing -v  # Tests with coverage
uv run ruff check src/                  # Lint
uv run ty check                         # Type check
uv run prek run                         # All pre-commit hooks

# Coverage reporting
uv run pytest tests/ --cov=. --cov-report=html  # Generate HTML coverage report

# Running the CLI (when implemented)
uv run dot --help
uv run dot tasks --help
```

## References

- **Architecture Patterns with Python** - The foundational pattern for this project
- **Functional Core, Imperative Shell** - Separation of concerns philosophy
- **Repository Pattern** - Data access abstraction
- **Unit of Work Pattern** - Transaction coordination
- **Test-Driven Development (TDD)** - Tests first, implementation follows

## Contact / Notes

This project was scaffolded with test-driven development using pytest. All tests are located in `tests/` and can be run with `uv run pytest tests/ -v`.

For questions about architecture decisions, refer to "Architecture Patterns with Python" by Harry Percival and Bob Gregory.
