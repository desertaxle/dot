# Data Model: Bullet Journal CLI

**Feature**: 001-bullet-journal-cli
**Date**: 2025-11-17
**Status**: Complete

## Overview

The Bullet Journal CLI uses a dual-model approach following the Functional Core / Imperative Shell pattern:

1. **Domain Models** (Functional Core): Pure Python dataclasses with no database dependencies
2. **ORM Models** (Imperative Shell): SQLAlchemy models for database persistence

Repositories handle conversion between domain and ORM models.

## Domain Models

Located in `src/dot/domain/models.py` - these are pure, immutable dataclasses.

### TaskStatus Enum

```python
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "TODO"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
```

**Purpose**: Represent the three possible states of a task
**Values**: TODO (default), DONE, CANCELLED
**Usage**: Domain logic uses this enum for type safety

### Task

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class Task:
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
```

**Fields**:
- `id`: Unique identifier (UUID for distribution-friendly IDs)
- `title`: Task title (required, non-empty string)
- `description`: Optional detailed description
- `status`: Current status (TODO, DONE, or CANCELLED)
- `created_at`: When the task was created
- `updated_at`: When the task was last modified

**Validation Rules** (enforced in domain operations):
- Title must not be empty
- Title max length: 500 characters
- Description max length: 5000 characters
- created_at <= updated_at

**State Transitions**:
- TODO → DONE (mark as complete)
- TODO → CANCELLED (cancel task)
- DONE → TODO (reopen task)
- CANCELLED → TODO (reopen task)
- DONE → CANCELLED (mark completed task as cancelled)
- CANCELLED → DONE (mark cancelled task as done)

### Event

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class Event:
    id: UUID
    title: str
    description: str | None
    occurred_at: datetime
    created_at: datetime
```

**Fields**:
- `id`: Unique identifier (UUID)
- `title`: Event title (required, non-empty string)
- `description`: Optional detailed description
- `occurred_at`: When the event happened or will happen
- `created_at`: When the event was recorded in the system

**Validation Rules**:
- Title must not be empty
- Title max length: 500 characters
- Description max length: 5000 characters
- occurred_at can be past, present, or future

**Notes**:
- Events are immutable once created (no update operation)
- occurred_at defaults to current time if not specified
- Events can represent both past events (logging) and future events (planning)

### Note

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class Note:
    id: UUID
    title: str
    content: str
    created_at: datetime
```

**Fields**:
- `id`: Unique identifier (UUID)
- `title`: Note title (required, non-empty string)
- `content`: Note content (required, non-empty string)
- `created_at`: When the note was created

**Validation Rules**:
- Title must not be empty
- Title max length: 500 characters
- Content must not be empty
- Content max length: 50,000 characters

**Notes**:
- Notes are immutable once created (no update operation)
- If edits needed, create new note and delete old one

### DailyLogEntry

```python
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DailyLogEntry:
    date: date
    tasks: list[Task]
    events: list[Event]
    notes: list[Note]
```

**Purpose**: Aggregate view for displaying all items for a specific date

**Fields**:
- `date`: The date for this log entry
- `tasks`: All tasks created on this date
- `events`: All events that occurred on this date
- `notes`: All notes created on this date

**Notes**:
- This is a read-only view model, not persisted
- Generated dynamically by querying repositories
- Tasks filtered by created_at date
- Events filtered by occurred_at date
- Notes filtered by created_at date

## ORM Models

Located in `src/dot/models.py` - SQLAlchemy declarative models for database persistence.

### TaskORM

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum
from datetime import datetime
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="TODO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Table**: `tasks`
**Indexes**:
- Primary key on `id`
- Index on `created_at` for daily log queries
- Index on `status` for filtering

**Constraints**:
- title NOT NULL
- status NOT NULL, CHECK (status IN ('TODO', 'DONE', 'CANCELLED'))

### EventORM

```python
class EventORM(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**Table**: `events`
**Indexes**:
- Primary key on `id`
- Index on `occurred_at` for date range queries

**Constraints**:
- title NOT NULL
- occurred_at NOT NULL

### NoteORM

```python
class NoteORM(Base):
    __tablename__ = "notes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(String(50000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**Table**: `notes`
**Indexes**:
- Primary key on `id`
- Index on `created_at` for chronological listing

**Constraints**:
- title NOT NULL
- content NOT NULL

## Repository Contracts

### TaskRepository

```python
from abc import ABC, abstractmethod
from uuid import UUID

class TaskRepository(ABC):
    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a new task"""
        pass

    @abstractmethod
    def get(self, task_id: UUID) -> Task | None:
        """Get task by ID"""
        pass

    @abstractmethod
    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status"""
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task"""
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """Delete a task"""
        pass

    @abstractmethod
    def list_by_date(self, date: date) -> list[Task]:
        """List tasks created on a specific date"""
        pass
```

### EventRepository

```python
class EventRepository(ABC):
    @abstractmethod
    def add(self, event: Event) -> None:
        """Add a new event"""
        pass

    @abstractmethod
    def get(self, event_id: UUID) -> Event | None:
        """Get event by ID"""
        pass

    @abstractmethod
    def list(self) -> list[Event]:
        """List all events"""
        pass

    @abstractmethod
    def list_by_date(self, date: date) -> list[Event]:
        """List events that occurred on a specific date"""
        pass

    @abstractmethod
    def list_by_range(self, start: date, end: date) -> list[Event]:
        """List events within a date range (inclusive)"""
        pass

    @abstractmethod
    def delete(self, event_id: UUID) -> None:
        """Delete an event"""
        pass
```

### NoteRepository

```python
class NoteRepository(ABC):
    @abstractmethod
    def add(self, note: Note) -> None:
        """Add a new note"""
        pass

    @abstractmethod
    def get(self, note_id: UUID) -> Note | None:
        """Get note by ID"""
        pass

    @abstractmethod
    def list(self) -> list[Note]:
        """List all notes"""
        pass

    @abstractmethod
    def list_by_date(self, date: date) -> list[Note]:
        """List notes created on a specific date"""
        pass

    @abstractmethod
    def delete(self, note_id: UUID) -> None:
        """Delete a note"""
        pass
```

## Domain Operations

Located in `src/dot/domain/operations.py` - pure functions for business logic.

### Task Operations

```python
def create_task(title: str, description: str | None = None) -> Task:
    """Create a new task with validation"""
    # Validates title, creates Task with UUID and timestamps

def mark_done(task: Task) -> Task:
    """Mark a task as done"""
    # Returns new Task with status=DONE, updated_at=now

def mark_cancelled(task: Task) -> Task:
    """Mark a task as cancelled"""
    # Returns new Task with status=CANCELLED, updated_at=now

def reopen_task(task: Task) -> Task:
    """Reopen a done or cancelled task"""
    # Returns new Task with status=TODO, updated_at=now
```

### Event Operations

```python
def create_event(title: str, description: str | None = None,
                 occurred_at: datetime | None = None) -> Event:
    """Create a new event with validation"""
    # Validates title, uses current time if occurred_at not provided
```

### Note Operations

```python
def create_note(title: str, content: str) -> Note:
    """Create a new note with validation"""
    # Validates title and content, creates Note with UUID and timestamp
```

### Log Operations

```python
def build_daily_log(tasks: list[Task], events: list[Event],
                    notes: list[Note], date: date) -> DailyLogEntry:
    """Build a daily log entry for a specific date"""
    # Filters items by date, returns DailyLogEntry
```

## Validation Rules Summary

| Entity | Field | Rule |
|--------|-------|------|
| Task | title | Required, non-empty, max 500 chars |
| Task | description | Optional, max 5000 chars |
| Task | status | Must be TODO, DONE, or CANCELLED |
| Event | title | Required, non-empty, max 500 chars |
| Event | description | Optional, max 5000 chars |
| Event | occurred_at | Required, any valid datetime |
| Note | title | Required, non-empty, max 500 chars |
| Note | content | Required, non-empty, max 50000 chars |

## Database Schema

### Tables

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,  -- UUID as string
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('TODO', 'DONE', 'CANCELLED')),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_status ON tasks(status);

CREATE TABLE events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    occurred_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_events_occurred_at ON events(occurred_at);

CREATE TABLE notes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_notes_created_at ON notes(created_at);
```

## Model Conversion

Repository implementations convert between domain and ORM models:

```python
# Domain → ORM
def to_orm(task: Task) -> TaskORM:
    return TaskORM(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

# ORM → Domain
def to_domain(task_orm: TaskORM) -> Task:
    return Task(
        id=task_orm.id,
        title=task_orm.title,
        description=task_orm.description,
        status=TaskStatus(task_orm.status),
        created_at=task_orm.created_at,
        updated_at=task_orm.updated_at
    )
```

## Summary

- **3 Domain Entities**: Task, Event, Note (pure dataclasses)
- **1 View Model**: DailyLogEntry (read-only aggregate)
- **3 ORM Models**: TaskORM, EventORM, NoteORM (SQLAlchemy)
- **3 Repository Interfaces**: TaskRepository, EventRepository, NoteRepository
- **All validation rules enforced in domain operations**
- **Immutable domain models** (frozen dataclasses)
- **Repository layer handles ORM ↔ Domain conversion**

This design maintains the functional core/imperative shell separation required by the constitution.
