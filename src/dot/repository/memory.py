"""In-memory repository implementations for testing."""

from typing import Dict, List, Optional
from uuid import UUID, uuid4

import whenever

from dot.domain.log_operations import LogEntry, Migration
from dot.domain.models import DailyLog, Event, Note, Project, Task
from dot.repository.abstract import (
    EventRepository,
    LogEntryRepository,
    MigrationRepository,
    NoteRepository,
    ProjectRepository,
    TaskRepository,
)


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation of TaskRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._tasks: Dict[UUID, Task] = {}

    def add(self, task: Task) -> None:
        """Add a task to storage."""
        # Auto-assign ID if not set
        if task.id is None:
            task.id = uuid4()
        self._tasks[task.id] = task

    def get(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list(self) -> List[Task]:
        """List all tasks."""
        return list(self._tasks.values())

    def update(self, task: Task) -> None:
        """Update an existing task."""
        if task.id in self._tasks:
            self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        """Delete a task by ID."""
        self._tasks.pop(task_id, None)


class InMemoryNoteRepository(NoteRepository):
    """In-memory implementation of NoteRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._notes: Dict[UUID, Note] = {}

    def add(self, note: Note) -> None:
        """Add a note to storage."""
        # Auto-assign ID if not set
        if note.id is None:
            note.id = uuid4()
        self._notes[note.id] = note

    def get(self, note_id: UUID) -> Optional[Note]:
        """Get a note by ID."""
        return self._notes.get(note_id)

    def list(self) -> List[Note]:
        """List all notes."""
        return list(self._notes.values())

    def update(self, note: Note) -> None:
        """Update an existing note."""
        if note.id in self._notes:
            self._notes[note.id] = note

    def delete(self, note_id: UUID) -> None:
        """Delete a note by ID."""
        self._notes.pop(note_id, None)


class InMemoryEventRepository(EventRepository):
    """In-memory implementation of EventRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._events: Dict[UUID, Event] = {}

    def add(self, event: Event) -> None:
        """Add an event to storage."""
        # Auto-assign ID if not set
        if event.id is None:
            event.id = uuid4()
        self._events[event.id] = event

    def get(self, event_id: UUID) -> Optional[Event]:
        """Get an event by ID."""
        return self._events.get(event_id)

    def list(self) -> List[Event]:
        """List all events."""
        return list(self._events.values())

    def update(self, event: Event) -> None:
        """Update an existing event."""
        if event.id in self._events:
            self._events[event.id] = event

    def delete(self, event_id: UUID) -> None:
        """Delete an event by ID."""
        self._events.pop(event_id, None)


class InMemoryProjectRepository(ProjectRepository):
    """In-memory implementation of ProjectRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._projects: Dict[UUID, Project] = {}

    def add(self, project: Project) -> None:
        """Add a project to storage."""
        # Auto-assign ID if not set
        if project.id is None:
            project.id = uuid4()
        self._projects[project.id] = project

    def get(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID."""
        return self._projects.get(project_id)

    def list(self) -> List[Project]:
        """List all projects."""
        return list(self._projects.values())

    def update(self, project: Project) -> None:
        """Update an existing project."""
        if project.id in self._projects:
            self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        """Delete a project by ID."""
        self._projects.pop(project_id, None)

    def get_daily_log(self, log_date: whenever.Date) -> DailyLog:
        """Get or create a daily log for the given date."""
        # Search for existing daily log
        for project in self._projects.values():
            if (
                isinstance(project, DailyLog) and project.date == log_date
            ):  # pragma: no branch
                return project

        # Create new daily log
        daily_log = DailyLog(
            name=f"Daily Log {log_date}",
            date=log_date,
        )
        # Assign ID and add to storage
        self.add(daily_log)
        return daily_log


class InMemoryLogEntryRepository(LogEntryRepository):
    """In-memory implementation of LogEntryRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._entries: Dict[UUID, LogEntry] = {}

    def add(self, log_entry: LogEntry) -> None:
        """Add a log entry to storage."""
        # Auto-assign ID if not set
        if log_entry.id is None:
            log_entry.id = uuid4()
        self._entries[log_entry.id] = log_entry

    def get(self, entry_id: UUID) -> Optional[LogEntry]:
        """Get a log entry by ID."""
        return self._entries.get(entry_id)

    def list(self) -> List[LogEntry]:
        """List all log entries."""
        return list(self._entries.values())

    def delete(self, entry_id: UUID) -> None:
        """Delete a log entry by ID."""
        self._entries.pop(entry_id, None)

    def get_by_log_id(self, log_id: UUID) -> List[LogEntry]:
        """Get all log entries for a specific log."""
        entries = [e for e in self._entries.values() if e.log_id == log_id]
        # Sort chronologically
        return sorted(entries, key=lambda e: e.entry_date)


class InMemoryMigrationRepository(MigrationRepository):
    """In-memory implementation of MigrationRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._migrations: Dict[UUID, Migration] = {}

    def add(self, migration: Migration) -> None:
        """Add a migration to storage."""
        # Auto-assign ID if not set
        if migration.id is None:
            migration.id = uuid4()
        self._migrations[migration.id] = migration

    def get(self, migration_id: UUID) -> Optional[Migration]:
        """Get a migration by ID."""
        return self._migrations.get(migration_id)

    def list(self) -> List[Migration]:
        """List all migrations."""
        return list(self._migrations.values())

    def get_by_task_id(self, task_id: UUID) -> List[Migration]:
        """Get all migrations for a specific task."""
        return [m for m in self._migrations.values() if m.task_id == task_id]
