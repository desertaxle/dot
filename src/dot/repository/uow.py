"""Unit of Work pattern implementation."""

from abc import ABC, abstractmethod

from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository
from dot.repository.memory import (
    InMemoryEventRepository,
    InMemoryNoteRepository,
    InMemoryTaskRepository,
)


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work - coordinates multiple repositories in one transaction."""

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Get the task repository."""
        pass

    @property
    @abstractmethod
    def notes(self) -> NoteRepository:
        """Get the note repository."""
        pass

    @property
    @abstractmethod
    def events(self) -> EventRepository:
        """Get the event repository."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass

    def __enter__(self):
        """Enter context manager."""
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass


class InMemoryUnitOfWork(AbstractUnitOfWork):
    """In-memory Unit of Work implementation for testing."""

    def __init__(self):
        """Initialize with in-memory repositories."""
        self._tasks = InMemoryTaskRepository()
        self._notes = InMemoryNoteRepository()
        self._events = InMemoryEventRepository()

    @property
    def tasks(self) -> TaskRepository:
        """Get the task repository."""
        return self._tasks

    @property
    def notes(self) -> NoteRepository:
        """Get the note repository."""
        return self._notes

    @property
    def events(self) -> EventRepository:
        """Get the event repository."""
        return self._events

    def commit(self) -> None:
        """Commit the current transaction (no-op for in-memory)."""
        pass

    def rollback(self) -> None:
        """Rollback the current transaction (no-op for in-memory)."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
