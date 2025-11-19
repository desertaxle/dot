"""Abstract repository interfaces defining contracts for data access."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from dot.domain.models import Event, Note, Task, TaskStatus


class TaskRepository(ABC):
    """Abstract interface for task repository implementations."""

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a new task.

        Args:
            task: The task to add
        """
        pass  # pragma: no cover

    @abstractmethod
    def get(self, task_id: UUID) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task ID

        Returns:
            The task if found, None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of tasks matching the criteria
        """
        pass  # pragma: no cover

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task.

        Args:
            task: The updated task
        """
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """Delete a task.

        Args:
            task_id: The task ID to delete
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_by_date(self, date: date) -> list[Task]:
        """List tasks created on a specific date.

        Args:
            date: The date to filter by

        Returns:
            List of tasks created on the specified date
        """
        pass  # pragma: no cover


class EventRepository(ABC):
    """Abstract interface for event repository implementations."""

    @abstractmethod
    def add(self, event: Event) -> None:
        """Add a new event.

        Args:
            event: The event to add
        """
        pass  # pragma: no cover

    @abstractmethod
    def get(self, event_id: UUID) -> Event | None:
        """Get an event by ID.

        Args:
            event_id: The event ID

        Returns:
            The event if found, None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> list[Event]:
        """List all events.

        Returns:
            List of all events
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_by_date(self, date: date) -> list[Event]:
        """List events that occurred on a specific date.

        Args:
            date: The date to filter by

        Returns:
            List of events that occurred on the specified date
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_by_range(self, start_date: date, end_date: date) -> list[Event]:
        """List events within a date range (inclusive).

        Args:
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List of events that occurred within the date range
        """
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, event_id: UUID) -> None:
        """Delete an event.

        Args:
            event_id: The event ID to delete
        """
        pass  # pragma: no cover


class NoteRepository(ABC):
    """Abstract interface for note repository implementations."""

    @abstractmethod
    def add(self, note: Note) -> None:
        """Add a new note.

        Args:
            note: The note to add
        """
        pass  # pragma: no cover

    @abstractmethod
    def get(self, note_id: UUID) -> Note | None:
        """Get a note by ID.

        Args:
            note_id: The note ID

        Returns:
            The note if found, None otherwise
        """
        pass  # pragma: no cover

    @abstractmethod
    def list(self) -> list[Note]:
        """List all notes.

        Returns:
            List of all notes
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_by_date(self, date: date) -> list[Note]:
        """List notes created on a specific date.

        Args:
            date: The date to filter by

        Returns:
            List of notes created on the specified date
        """
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, note_id: UUID) -> None:
        """Delete a note.

        Args:
            note_id: The note ID to delete
        """
        pass  # pragma: no cover
