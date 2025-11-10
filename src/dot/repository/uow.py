"""Unit of Work pattern implementation."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository
from dot.repository.memory import (
    InMemoryEventRepository,
    InMemoryNoteRepository,
    InMemoryTaskRepository,
)
from dot.repository.sqlalchemy import (
    SQLAlchemyEventRepository,
    SQLAlchemyNoteRepository,
    SQLAlchemyTaskRepository,
)


class AbstractUnitOfWork(ABC):
    """Abstract Unit of Work - coordinates multiple repositories in one transaction."""

    @property
    @abstractmethod
    def tasks(self) -> TaskRepository:
        """Get the task repository."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def notes(self) -> NoteRepository:
        """Get the note repository."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def events(self) -> EventRepository:
        """Get the event repository."""
        pass  # pragma: no cover

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass  # pragma: no cover

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the current transaction."""
        pass  # pragma: no cover

    def __enter__(self):
        """Enter context manager."""
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass  # pragma: no cover


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


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy Unit of Work implementation for database persistence."""

    def __init__(self, session: Session):
        """Initialize with a database session.

        Args:
            session: SQLAlchemy session for database operations.
        """
        self.session = session
        self._tasks = SQLAlchemyTaskRepository(session)
        self._notes = SQLAlchemyNoteRepository(session)
        self._events = SQLAlchemyEventRepository(session)

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
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.session.rollback()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.session.close()
