# Research: Bullet Journal CLI

**Feature**: 001-bullet-journal-cli
**Date**: 2025-11-17
**Status**: Complete

## Technology Decisions

### Decision 1: CLI Framework - Cyclopts

**Decision**: Use cyclopts for CLI command routing and argument parsing

**Rationale**:
- User-specified requirement
- Modern Python CLI framework with type-safe command definitions
- Integrates well with Python 3.14's type system
- Supports subcommands naturally (task, event, note, log commands)
- Automatic help generation from type hints and docstrings

**Best Practices**:
- Use type hints for all command parameters (str, int, datetime, etc.)
- Leverage cyclopts app decorators for command registration
- Group related commands under command groups (tasks, events, notes, log)
- Use docstrings for automatic help text generation
- Handle errors gracefully with appropriate exit codes

**Alternatives Considered**:
- Click: More verbose, decorator-heavy
- Typer: Good option but cyclopts preferred by user
- argparse: Standard library but less elegant for complex CLIs

**Integration Pattern**:
```python
from cyclopts import App

app = App()

@app.command
def task_create(title: str, description: str | None = None):
    """Create a new task"""
    # Implementation
```

### Decision 2: ORM - SQLAlchemy 2.0+

**Decision**: Use SQLAlchemy 2.0+ for database persistence

**Rationale**:
- User-specified requirement
- Already used in existing Dot project (per constitution history)
- Supports the repository pattern well
- 2.0+ has improved type hints and async support (if needed later)
- Enables separation of ORM models from domain models

**Best Practices**:
- Define ORM models in `src/dot/models.py` separate from domain models
- Use declarative base with mapped dataclasses for type safety
- Repository layer converts between ORM models and domain models
- Use sessions via Unit of Work pattern for transaction management
- Enable foreign key constraints in SQLite

**Alternatives Considered**:
- Direct SQLite: Too low-level, violates repository pattern
- Other ORMs (Peewee, Tortoise): Less established in Python ecosystem

**Integration Pattern**:
```python
# ORM Model (src/dot/models.py)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TaskORM(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    # ...

# Repository converts ORM ↔ Domain
```

### Decision 3: Configuration - Pydantic Settings

**Decision**: Use pydantic-settings for application configuration

**Rationale**:
- User-specified requirement
- Already used in existing Dot project (per pyproject.toml)
- Type-safe configuration with validation
- Supports environment variables and .env files
- Ideal for managing database path configuration

**Best Practices**:
- Define Settings class in `src/dot/settings.py`
- Use BaseSettings from pydantic-settings
- Support both environment variables and default values
- Validate paths on initialization
- Default to `~/.dot/` for database storage
- Allow override via DOT_HOME environment variable

**Alternatives Considered**:
- configparser: Less type-safe, more verbose
- python-decouple: Similar but pydantic-settings more feature-rich
- Environment variables only: No validation or type safety

**Integration Pattern**:
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    dot_home: Path = Path.home() / ".dot"

    @property
    def db_path(self) -> Path:
        return self.dot_home / "dot.db"
```

### Decision 4: CLI Output - Rich

**Decision**: Use rich for formatted CLI output

**Rationale**:
- User-specified requirement
- Already in dependencies (per pyproject.toml)
- Provides tables, colors, and formatted output
- Makes CLI output professional and readable
- Supports different output formats (tables, trees, panels)

**Best Practices**:
- Use Tables for list views (tasks, events, notes)
- Use colors to distinguish status (green=done, red=cancelled, white=todo)
- Use Panels for detailed single-item views
- Keep output readable in both color and no-color terminals
- Support --no-color flag for scripting

**Alternatives Considered**:
- Plain text: Works but less user-friendly
- tabulate: Good tables but less full-featured than rich
- colorama: Only colors, not full formatting

**Integration Pattern**:
```python
from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Tasks")
table.add_column("ID", style="cyan")
table.add_column("Title")
table.add_column("Status", style="green")
console.print(table)
```

## Architectural Patterns

### Pattern 1: Functional Core / Imperative Shell

**Decision**: Maintain strict separation between pure domain logic and I/O

**Rationale**:
- Constitution principle I (NON-NEGOTIABLE)
- Enables fast unit testing without database
- Clear separation of concerns
- Business logic easy to reason about

**Implementation**:
- Domain models: Pure dataclasses in `src/dot/domain/models.py`
- Domain operations: Pure functions in `src/dot/domain/operations.py`
- Imperative shell: Repositories, database, CLI in separate modules
- No database imports in domain layer

### Pattern 2: Repository Pattern

**Decision**: Use abstract repository interfaces with in-memory and SQLAlchemy implementations

**Rationale**:
- Constitution principle II (NON-NEGOTIABLE)
- Existing pattern in Dot project
- Enables fast testing with in-memory repositories
- Clean separation of data access logic

**Implementation**:
- Abstract interfaces: `src/dot/repository/abstract.py`
- In-memory: `src/dot/repository/memory.py` (for tests)
- SQLAlchemy: `src/dot/repository/sqlalchemy.py` (for production)
- Unit of Work: Coordinate transactions across repositories

### Pattern 3: Unit of Work

**Decision**: Use Unit of Work pattern for transaction management

**Rationale**:
- Already established in Dot project (per constitution history)
- Coordinates multiple repository operations in a transaction
- Ensures data consistency
- Context manager pattern (`with uow: ...`)

**Implementation**:
- Abstract UnitOfWork in `src/dot/repository/abstract.py`
- Provides access to all repositories
- Commit/rollback transaction semantics
- Used by CLI layer to coordinate operations

## Database Design Considerations

### Decision: SQLite Storage Location

**Decision**: Store database in `~/.dot/dot.db` by default, configurable via settings

**Rationale**:
- User-friendly default (hidden dot directory)
- Follows Unix conventions for user data
- Easy to backup/restore
- Allows override for advanced users or testing

**Implementation**:
- Create directory if not exists
- Validate write permissions on startup
- Support DOT_HOME environment variable for override

### Decision: Schema Versioning

**Decision**: Use Alembic for database migrations (if needed in future)

**Rationale**:
- Standard for SQLAlchemy projects
- Enables schema evolution
- Not needed for MVP but plan for it
- Keep schema simple initially

**Note**: For MVP, simple `create_all()` is sufficient. Add migrations when schema changes are needed.

## Testing Strategy

### Decision: TDD with Contract Tests

**Decision**: Write tests first, starting with contract tests for repositories

**Rationale**:
- Constitution principle III (NON-NEGOTIABLE)
- Contract tests ensure both in-memory and SQLAlchemy implementations work identically
- Fast test suite with in-memory repositories
- Integration tests with real database for confidence

**Test Organization**:
1. Domain tests: Pure logic, no database (fastest)
2. Contract tests: Repository behavior (medium speed)
3. Integration tests: Full workflows with database (slower)
4. CLI tests: Command-line interface (medium speed)

### Decision: 100% Coverage Target

**Decision**: Maintain 100% code coverage with no exceptions

**Rationale**:
- Constitution principle IV (NON-NEGOTIABLE)
- Already configured in pyproject.toml (fail_under = 100)
- Ensures all code paths tested
- Catches regressions immediately

**Coverage Strategy**:
- Exclude only `__main__.py` entry point (configured in pyproject.toml)
- Test all domain logic paths
- Test all repository operations
- Test all CLI commands
- Test error handling paths

## Command Structure

### Decision: Hierarchical Command Groups

**Decision**: Organize CLI into logical command groups

**Rationale**:
- Natural mapping to user stories
- Intuitive command discovery
- Extensible for future features

**Command Structure**:
```
dot task create <title> [--description DESC]
dot task list [--status STATUS]
dot task done <id>
dot task cancel <id>

dot event create <title> [--date DATE] [--description DESC]
dot event list [--date DATE] [--range START END]

dot note create <title> <content>
dot note list
dot note show <id>

dot log [DATE]
```

**Rationale for Structure**:
- `dot <entity> <action>` pattern is intuitive
- Follows REST-like naming (create, list, show)
- Easy to discover via `dot --help`, `dot task --help`, etc.
- Maps cleanly to repository operations

## Date/Time Handling

### Decision: Use whenever library for date/time

**Rationale**:
- Already in dependencies (per pyproject.toml)
- Better than stdlib datetime for user-facing date parsing
- Handles timezones and relative dates well
- Type-safe with modern Python

**Implementation**:
- Parse user input with whenever
- Store as ISO format strings or timestamps in database
- Display with whenever formatting

## Summary

All technology decisions are aligned with user requirements and constitution principles. The architecture follows the established Dot project patterns (functional core/imperative shell, repository pattern, TDD, 100% coverage). No research gaps remain - implementation can proceed to Phase 1 (design).

**Ready for Phase 1**: Data model design and contract definition.
