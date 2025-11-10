"""Abstract repository interfaces - define the contract all repositories must follow."""

from abc import ABC, abstractmethod
from typing import List, Optional

from dot.domain.models import Event, Note, Task


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
