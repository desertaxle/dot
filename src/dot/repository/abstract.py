"""Abstract repository interfaces - define the contract all repositories must follow."""

from abc import ABC, abstractmethod
from typing import List, Optional

import whenever

from dot.domain.log_operations import LogEntry
from dot.domain.models import DailyLog, Event, Note, Project, Task


class TaskRepository(ABC):
    """Abstract repository for Task entities."""

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a task to the repository."""
        pass  # pragma: no cover

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> List[Task]:
        """List all tasks."""
        pass  # pragma: no cover

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, task_id: int) -> None:
        """Delete a task by ID."""
        pass  # pragma: no cover


class NoteRepository(ABC):
    """Abstract repository for Note entities."""

    @abstractmethod
    def add(self, note: Note) -> None:
        """Add a note to the repository."""
        pass  # pragma: no cover

    @abstractmethod
    def get(self, note_id: int) -> Optional[Note]:
        """Get a note by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> List[Note]:
        """List all notes."""
        pass  # pragma: no cover

    @abstractmethod
    def update(self, note: Note) -> None:
        """Update an existing note."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, note_id: int) -> None:
        """Delete a note by ID."""
        pass  # pragma: no cover


class EventRepository(ABC):
    """Abstract repository for Event entities."""

    @abstractmethod
    def add(self, event: Event) -> None:
        """Add an event to the repository."""
        pass  # pragma: no cover

    @abstractmethod
    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> List[Event]:
        """List all events."""
        pass  # pragma: no cover

    @abstractmethod
    def update(self, event: Event) -> None:
        """Update an existing event."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, event_id: int) -> None:
        """Delete an event by ID."""
        pass  # pragma: no cover


class ProjectRepository(ABC):
    """Abstract repository for Project entities (including logs)."""

    @abstractmethod
    def add(self, project: Project) -> None:
        """Add a project to the repository."""
        pass  # pragma: no cover

    @abstractmethod
    def get(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> List[Project]:
        """List all projects."""
        pass  # pragma: no cover

    @abstractmethod
    def update(self, project: Project) -> None:
        """Update an existing project."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, project_id: int) -> None:
        """Delete a project by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def get_daily_log(self, log_date: whenever.Date) -> DailyLog:
        """Get or create a daily log for the given date.

        Args:
            log_date: The date for the daily log.

        Returns:
            The daily log for the date (created if it doesn't exist).
        """
        pass  # pragma: no cover


class LogEntryRepository(ABC):
    """Abstract repository for LogEntry entities."""

    @abstractmethod
    def add(self, log_entry: LogEntry) -> None:
        """Add a log entry to the repository."""
        pass  # pragma: no cover

    @abstractmethod
    def get(self, entry_id: int) -> Optional[LogEntry]:
        """Get a log entry by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> List[LogEntry]:
        """List all log entries."""
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, entry_id: int) -> None:
        """Delete a log entry by ID."""
        pass  # pragma: no cover

    @abstractmethod
    def get_by_log_id(self, log_id: int) -> List[LogEntry]:
        """Get all log entries for a specific log.

        Args:
            log_id: The ID of the log/project.

        Returns:
            List of log entries for the log, ordered chronologically.
        """
        pass  # pragma: no cover
