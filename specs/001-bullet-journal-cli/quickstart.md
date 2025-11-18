# Quickstart: Bullet Journal CLI

**Feature**: 001-bullet-journal-cli
**Audience**: Developers implementing the feature
**Date**: 2025-11-17

## Prerequisites

Before starting implementation:

1. ✅ Specification complete ([spec.md](spec.md))
2. ✅ Implementation plan complete ([plan.md](plan.md))
3. ✅ Research complete ([research.md](research.md))
4. ✅ Data model defined ([data-model.md](data-model.md))
5. ✅ CLI contracts defined ([contracts/cli-commands.md](contracts/cli-commands.md))
6. ✅ Constitution compliance verified (all gates passed)

## Development Setup

### 1. Verify Branch

```bash
git status
# Should show: On branch 001-bullet-journal-cli
```

### 2. Install Dependencies

Dependencies are already in `pyproject.toml`:
- cyclopts >= 4.2.1
- SQLAlchemy >= 2.0.0
- pydantic-settings >= 2.11.0
- rich >= 14.2.0
- whenever >= 0.6.0

No new dependencies needed.

### 3. Project Structure

The following directory structure will be created during implementation:

```
src/dot/
├── domain/
│   ├── __init__.py        # Empty (package marker)
│   ├── models.py          # Task, Event, Note, DailyLogEntry dataclasses
│   └── operations.py      # Pure business logic functions
├── repository/
│   ├── __init__.py        # Empty (package marker)
│   ├── abstract.py        # TaskRepository, EventRepository, NoteRepository interfaces
│   ├── memory.py          # In-memory implementations
│   └── sqlalchemy.py      # SQLAlchemy implementations
├── models.py              # TaskORM, EventORM, NoteORM SQLAlchemy models
├── db.py                  # Database initialization and session management
├── settings.py            # Settings class using pydantic-settings
└── __main__.py            # CLI entry point with cyclopts commands

tests/
├── domain/
│   ├── test_models.py     # Tests for domain dataclasses
│   └── test_operations.py # Tests for pure business logic
├── repository/
│   ├── test_abstract.py   # Contract tests for repository interfaces
│   ├── test_memory.py     # Tests for in-memory implementations
│   └── test_sqlalchemy.py # Tests for SQLAlchemy implementations
├── integration/
│   └── test_workflows.py  # End-to-end tests with real database
└── cli/
    └── test_commands.py   # CLI command tests
```

## Implementation Order

Follow this order to maintain TDD and constitution compliance:

### Phase 1: Foundation (P1 - Task Management)

**User Story**: Task Management (Create, list, mark done/cancelled)

#### Step 1: Domain Models

1. **Write tests first** (`tests/domain/test_models.py`):
   - Test Task dataclass creation
   - Test TaskStatus enum values
   - Test immutability (frozen dataclass)

2. **Implement** (`src/dot/domain/models.py`):
   - TaskStatus enum
   - Task dataclass
   - Validation in `__post_init__` if needed

3. **Run tests**: `pytest tests/domain/test_models.py`
   - Must pass with 100% coverage

#### Step 2: Domain Operations

1. **Write tests first** (`tests/domain/test_operations.py`):
   - Test create_task (valid and invalid inputs)
   - Test mark_done, mark_cancelled, reopen_task
   - Test validation errors

2. **Implement** (`src/dot/domain/operations.py`):
   - `create_task()`
   - `mark_done()`
   - `mark_cancelled()`
   - `reopen_task()`

3. **Run tests**: `pytest tests/domain/`

#### Step 3: ORM Models

1. **Write tests first** (`tests/test_orm_models.py` or in repository tests):
   - Test TaskORM creation
   - Test database roundtrip

2. **Implement** (`src/dot/models.py`):
   - SQLAlchemy Base
   - TaskORM model with correct types

#### Step 4: Repository Interfaces

1. **Write contract tests first** (`tests/repository/test_abstract.py`):
   - Define test suite that works for ANY implementation
   - Test add, get, list, update, delete operations
   - Test list_by_date operation

2. **Implement** (`src/dot/repository/abstract.py`):
   - TaskRepository ABC
   - All abstract methods with docstrings

#### Step 5: In-Memory Repository

1. **Run contract tests** against InMemoryTaskRepository:
   - Use existing contract test suite
   - Should initially fail (Red)

2. **Implement** (`src/dot/repository/memory.py`):
   - InMemoryTaskRepository
   - Simple dict-based storage
   - Convert domain ↔ domain (no conversion needed)

3. **Run tests**: Contract tests should now pass (Green)

#### Step 6: SQLAlchemy Repository

1. **Run contract tests** against SQLAlchemyTaskRepository:
   - Use same contract test suite
   - Should initially fail (Red)

2. **Implement** (`src/dot/repository/sqlalchemy.py`):
   - SQLAlchemyTaskRepository
   - Session management
   - Conversion domain ↔ ORM

3. **Run tests**: Contract tests should now pass (Green)

#### Step 7: Database & Settings

1. **Write tests** (`tests/test_db.py`, `tests/test_settings.py`):
   - Test database initialization
   - Test settings loading
   - Test database path configuration

2. **Implement** (`src/dot/db.py`, `src/dot/settings.py`):
   - Settings class with dot_home, db_path
   - Database initialization function
   - Session factory

#### Step 8: CLI Commands

1. **Write tests first** (`tests/cli/test_commands.py`):
   - Test `dot task create`
   - Test `dot task list`
   - Test `dot task done`
   - Test `dot task cancel`
   - Use in-memory repositories for fast tests

2. **Implement** (`src/dot/__main__.py`):
   - Cyclopts app setup
   - Task commands with rich output
   - Error handling with proper exit codes

3. **Integration tests** (`tests/integration/test_workflows.py`):
   - Test full workflow with real database
   - Create task → list → mark done → list again

#### Step 9: Verify Coverage

```bash
pytest --cov=src/dot --cov-report=term-missing
# Must show 100% coverage
```

### Phase 2: Event Tracking (P2)

Repeat the same TDD process:

1. Domain models (Event dataclass)
2. Domain operations (create_event)
3. ORM models (EventORM)
4. Repository interface (EventRepository)
5. In-memory repository
6. SQLAlchemy repository
7. CLI commands (event create, list)
8. Integration tests
9. Verify coverage

### Phase 3: Note Taking (P3)

Repeat the TDD process for notes:

1. Domain models (Note dataclass)
2. Domain operations (create_note)
3. ORM models (NoteORM)
4. Repository interface (NoteRepository)
5. In-memory repository
6. SQLAlchemy repository
7. CLI commands (note create, list, show)
8. Integration tests
9. Verify coverage

### Phase 4: Daily Log (P4)

1. Domain models (DailyLogEntry dataclass)
2. Domain operations (build_daily_log)
3. Update repository interfaces (add list_by_date methods)
4. Implement list_by_date in repositories
5. CLI command (dot log)
6. Integration tests
7. Verify coverage

## Running Tests

### Unit Tests (Fast)

```bash
pytest tests/domain/        # Pure domain logic
pytest tests/repository/    # Repository contracts
```

### Integration Tests (Slower)

```bash
pytest tests/integration/   # With real database
pytest tests/cli/           # CLI commands
```

### Full Suite with Coverage

```bash
pytest --cov=src/dot --cov-report=term-missing
```

Must maintain 100% coverage at all times.

## Quality Gates

Before committing:

```bash
# Linting
uv run ruff check src/ tests/

# Type checking
uv run ty

# Tests with coverage
uv run pytest --cov=src/dot --cov-report=term-missing

# Pre-commit hooks (runs all above)
git commit -m "message"  # prek will run automatically
```

All must pass.

## Manual Testing

After implementation, test manually:

```bash
# Initialize (first time)
dot task create "Buy groceries"

# Verify database created
ls ~/.dot/
# Should show dot.db

# Test all commands
dot task list
dot task done <id>
dot task list  # Should show task as DONE

dot event create "Team meeting" --date "2025-11-17 14:00"
dot event list

dot note create "Ideas" "Build a CLI bullet journal"
dot note list
dot note show <id>

dot log  # Today's log
dot log 2025-11-17  # Specific date
```

## Troubleshooting

### Database Issues

If database gets corrupted during development:

```bash
rm -rf ~/.dot/dot.db
# Re-run commands to recreate
```

### Import Errors

If imports fail, ensure you're in the virtual environment:

```bash
source .venv/bin/activate  # or equivalent
```

### Coverage Not 100%

Find uncovered lines:

```bash
pytest --cov=src/dot --cov-report=html
open htmlcov/index.html
```

Click on files to see line-by-line coverage.

## Common Pitfalls

1. **Forgetting to write tests first**: Tests must fail (Red) before implementation
2. **Importing database in domain layer**: Domain must be pure, no SQLAlchemy imports
3. **Not using frozen dataclasses**: Domain models must be immutable
4. **Skipping contract tests**: Contract tests ensure all repository implementations behave identically
5. **Testing with SQLAlchemy instead of in-memory**: Most tests should use in-memory repositories for speed

## Next Steps

After completing implementation:

1. Run full test suite: `pytest`
2. Verify coverage: `pytest --cov=src/dot`
3. Run quality gates: `uv run ruff check`, `uv run ty`
4. Manual smoke test: Try all CLI commands
5. Commit changes: `git commit`
6. Review: Request code review if applicable

## Reference Documents

- [Specification](spec.md) - User stories and requirements
- [Implementation Plan](plan.md) - Architecture and structure
- [Research](research.md) - Technology decisions and best practices
- [Data Model](data-model.md) - Domain and ORM models
- [CLI Contracts](contracts/cli-commands.md) - Command specifications
- [Constitution](../../.specify/memory/constitution.md) - Project principles

## Constitution Checklist

Before starting each phase:

- [ ] Tests written first (Red-Green-Refactor)
- [ ] Domain logic in pure functions (Functional Core)
- [ ] Repositories for data access (Repository Pattern)
- [ ] 100% coverage maintained
- [ ] Simplest solution chosen (YAGNI)

This ensures compliance with all five constitution principles.
