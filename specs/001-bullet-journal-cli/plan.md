# Implementation Plan: Bullet Journal CLI

**Branch**: `001-bullet-journal-cli` | **Date**: 2025-11-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-bullet-journal-cli/spec.md`

## Summary

Build a command-line bullet journal application for tracking tasks, events, and notes with SQLite persistence. The system follows a functional core/imperative shell architecture using the repository pattern, enabling users to manage their productivity through an intuitive CLI interface.

## Technical Context

**Language/Version**: Python 3.14 (per pyproject.toml)
**Primary Dependencies**: cyclopts (CLI framework), SQLAlchemy 2.0+ (ORM), pydantic-settings (configuration), rich (CLI output)
**Storage**: SQLite database stored in user-configurable home directory
**Testing**: pytest with 100% coverage requirement
**Target Platform**: Command-line interface (cross-platform via Python)
**Project Type**: Single project (CLI application)
**Performance Goals**: Sub-second response for all commands, support 1000+ items
**Constraints**: Must follow functional core/imperative shell pattern, 100% test coverage, TDD workflow
**Scale/Scope**: Single-user desktop application, local SQLite storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with `.specify/memory/constitution.md`:

- [x] **Functional Core / Imperative Shell**: Business logic in pure functions? Side effects confined to repositories/CLI?
  - ✅ Domain models will be pure dataclasses in `src/dot/domain/`
  - ✅ Repositories handle all database I/O
  - ✅ CLI layer coordinates between user input and domain logic

- [x] **Repository Pattern**: All data access uses abstract repository interfaces?
  - ✅ Will create TaskRepository, EventRepository, NoteRepository interfaces
  - ✅ In-memory implementations for testing
  - ✅ SQLAlchemy implementations for production

- [x] **Test-First Development**: Tests written before implementation? Red-Green-Refactor cycle followed?
  - ✅ All tasks.md will specify tests before implementation
  - ✅ Contract tests for repositories
  - ✅ Integration tests for CLI commands

- [x] **100% Code Coverage**: Coverage maintained at 100%? No exceptions?
  - ✅ pyproject.toml configured with fail_under = 100
  - ✅ Pre-commit hooks enforce coverage
  - ✅ CI/CD gates on coverage

- [x] **Simplicity & YAGNI**: Simplest solution chosen? Complexity justified in Complexity Tracking table?
  - ✅ Using established patterns already in the codebase
  - ✅ Dependencies are minimal and necessary (CLI, ORM, config, styling)
  - ✅ No premature optimization or unnecessary abstractions

*Note: All gates pass. No complexity violations.*

## Project Structure

### Documentation (this feature)

```text
specs/001-bullet-journal-cli/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/dot/
├── domain/              # Pure domain models (functional core)
│   ├── __init__.py
│   ├── models.py        # Task, Event, Note dataclasses
│   └── operations.py    # Pure business logic functions
├── repository/          # Repository pattern (imperative shell)
│   ├── __init__.py
│   ├── abstract.py      # TaskRepository, EventRepository, NoteRepository interfaces
│   ├── memory.py        # In-memory implementations for testing
│   └── sqlalchemy.py    # SQLAlchemy implementations
├── models.py            # SQLAlchemy ORM models
├── db.py                # Database setup and management
├── settings.py          # Pydantic settings (database path configuration)
└── __main__.py          # CLI entry point (cyclopts commands)

tests/
├── domain/              # Unit tests for pure domain logic
│   ├── test_models.py
│   └── test_operations.py
├── repository/          # Contract tests for repository interfaces
│   ├── test_abstract.py
│   ├── test_memory.py
│   └── test_sqlalchemy.py
├── integration/         # End-to-end tests with database
│   └── test_workflows.py
└── cli/                 # CLI command tests
    └── test_commands.py
```

**Structure Decision**: Using the established Dot project structure (single project, Option 1) with functional core in `src/dot/domain/` and imperative shell in `src/dot/repository/`. CLI layer in `src/dot/__main__.py` uses cyclopts for command routing and rich for output formatting.

## Complexity Tracking

> **No violations** - all architecture follows established patterns

This section is empty because the implementation follows all constitution principles without exceptions.

## Phase 0: Research (Complete)

**Status**: ✅ Complete

**Output**: [research.md](research.md)

**Key Decisions**:
- CLI Framework: cyclopts (user-specified, modern type-safe CLI)
- ORM: SQLAlchemy 2.0+ (user-specified, established pattern)
- Configuration: pydantic-settings (user-specified, type-safe config)
- Output Styling: rich (user-specified, professional tables and formatting)
- Date/Time: whenever (already in dependencies, better than stdlib)
- Architecture: Functional core/imperative shell with repository pattern

**All research items resolved** - no NEEDS CLARIFICATION remaining.

## Phase 1: Design & Contracts (Complete)

**Status**: ✅ Complete

**Outputs**:
- [data-model.md](data-model.md) - Domain and ORM models defined
- [contracts/cli-commands.md](contracts/cli-commands.md) - CLI command specifications
- [quickstart.md](quickstart.md) - Implementation guide with TDD workflow
- [CLAUDE.md](/CLAUDE.md) - Updated agent context

**Data Model Summary**:
- 3 Domain Entities: Task, Event, Note (frozen dataclasses)
- 1 View Model: DailyLogEntry (read-only aggregate)
- 3 ORM Models: TaskORM, EventORM, NoteORM (SQLAlchemy)
- 3 Repository Interfaces: TaskRepository, EventRepository, NoteRepository

**CLI Commands Summary**:
- Task commands: create, list, done, cancel
- Event commands: create, list (with date filtering)
- Note commands: create, list, show
- Log command: unified daily view

**Constitution Re-Check Post-Design**: ✅ All principles still complied with

## Phase 2: Tasks (Next Step)

**Status**: ⏳ Ready to start

**Command**: `/speckit.tasks`

The tasks.md file will be generated by the `/speckit.tasks` command, which will:
1. Read the spec.md for user stories
2. Read the plan.md for architecture decisions
3. Read the data-model.md for entities
4. Read the contracts for implementation details
5. Generate a detailed, dependency-ordered task list

Tasks will be organized by user story (P1-P4) with TDD workflow for each.

## Implementation Readiness

✅ **All planning complete** - ready for task generation and implementation

**Artifacts Generated**:
1. ✅ plan.md (this file)
2. ✅ research.md
3. ✅ data-model.md
4. ✅ contracts/cli-commands.md
5. ✅ quickstart.md
6. ✅ CLAUDE.md (updated)

**Next Command**: `/speckit.tasks` to generate tasks.md

