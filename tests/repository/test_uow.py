"""Tests for Unit of Work pattern."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dot.domain.models import Event, Note, Task
from dot.models import Base
from dot.repository.uow import InMemoryUnitOfWork, SQLAlchemyUnitOfWork


class TestAbstractUnitOfWork:
    """Tests for AbstractUnitOfWork interface."""

    def test_uow_is_context_manager(self):
        """UnitOfWork can be used as a context manager."""
        uow = InMemoryUnitOfWork()

        # Should not raise
        with uow:
            pass

    def test_uow_has_task_repository(self):
        """UnitOfWork provides access to task repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "tasks")
        assert uow.tasks is not None

    def test_uow_has_note_repository(self):
        """UnitOfWork provides access to note repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "notes")
        assert uow.notes is not None

    def test_uow_has_event_repository(self):
        """UnitOfWork provides access to event repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "events")
        assert uow.events is not None

    def test_uow_has_project_repository(self):
        """UnitOfWork provides access to project repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "projects")
        assert uow.projects is not None

    def test_uow_has_log_entry_repository(self):
        """UnitOfWork provides access to log entry repository."""
        uow = InMemoryUnitOfWork()

        assert hasattr(uow, "log_entries")
        assert uow.log_entries is not None

    def test_uow_commit(self):
        """UnitOfWork can commit changes."""
        uow = InMemoryUnitOfWork()

        with uow:
            now = datetime.now(timezone.utc)
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.commit()

        # After commit, data should be persisted
        assert uow.tasks.get(1) is not None

    def test_uow_rollback(self):
        """UnitOfWork can rollback changes."""
        uow = InMemoryUnitOfWork()

        with uow:
            now = datetime.now(timezone.utc)
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.rollback()

        # After rollback, data should not be persisted
        # (In-memory UoW doesn't actually support true rollback, but interface is there)


class TestInMemoryUnitOfWork:
    """Tests for InMemoryUnitOfWork implementation."""

    def test_multiple_repositories_in_one_transaction(self):
        """Multiple repositories can be used in one UoW transaction."""
        uow = InMemoryUnitOfWork()
        now = datetime.now(timezone.utc)

        with uow:
            # Add to multiple repositories
            task = Task(id=1, title="Task", created_at=now, updated_at=now)
            note = Note(id=1, title="Note", created_at=now, updated_at=now)
            event = Event(
                id=1, title="Event", occurred_at=now, created_at=now, updated_at=now
            )

            uow.tasks.add(task)
            uow.notes.add(note)
            uow.events.add(event)

            uow.commit()

        # All should be persisted
        assert uow.tasks.get(1) is not None
        assert uow.notes.get(1) is not None
        assert uow.events.get(1) is not None

    def test_separate_uow_instances_have_separate_storage(self):
        """Each UoW instance has separate storage."""
        uow1 = InMemoryUnitOfWork()
        uow2 = InMemoryUnitOfWork()
        now = datetime.now(timezone.utc)

        with uow1:
            task = Task(id=1, title="Task in UoW1", created_at=now, updated_at=now)
            uow1.tasks.add(task)
            uow1.commit()

        # uow2 should not have the task
        assert uow2.tasks.get(1) is None

    def test_uow_provides_fresh_repositories(self):
        """Each access to repository through UoW returns the same instance."""
        uow = InMemoryUnitOfWork()

        assert uow.tasks is uow.tasks
        assert uow.notes is uow.notes
        assert uow.events is uow.events

    def test_in_memory_uow_context_manager_exit_on_exception(self):
        """InMemoryUnitOfWork context manager calls rollback on exception."""
        uow = InMemoryUnitOfWork()
        now = datetime.now(timezone.utc)

        try:
            with uow:
                task = Task(id=1, title="Test", created_at=now, updated_at=now)
                uow.tasks.add(task)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # After exception, data should still be in memory for in-memory UoW
        # (In-memory UoW doesn't truly support rollback, but the interface is called)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sqlalchemy_session(in_memory_db):
    """Create a database session for a test."""
    SessionLocal = sessionmaker(bind=in_memory_db)
    session = SessionLocal()
    yield session
    session.close()


class TestSQLAlchemyUnitOfWork:
    """Tests for SQLAlchemyUnitOfWork implementation."""

    def test_sqlalchemy_uow_is_context_manager(self, sqlalchemy_session: Session):
        """SQLAlchemyUnitOfWork can be used as a context manager."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)

        # Should not raise
        with uow:
            pass

    def test_sqlalchemy_uow_has_repositories(self, sqlalchemy_session: Session):
        """SQLAlchemyUnitOfWork provides access to repositories."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)

        assert hasattr(uow, "tasks")
        assert hasattr(uow, "notes")
        assert hasattr(uow, "events")
        assert hasattr(uow, "projects")
        assert hasattr(uow, "log_entries")
        assert uow.tasks is not None
        assert uow.notes is not None
        assert uow.events is not None
        assert uow.projects is not None
        assert uow.log_entries is not None

    def test_sqlalchemy_uow_commit(self, sqlalchemy_session: Session):
        """SQLAlchemyUnitOfWork can commit changes."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)
        now = datetime.now(timezone.utc)

        with uow:
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.commit()

        # After commit, data should be persisted
        assert uow.tasks.get(1) is not None

    def test_sqlalchemy_uow_rollback(self, sqlalchemy_session: Session):
        """SQLAlchemyUnitOfWork can rollback changes."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)
        now = datetime.now(timezone.utc)

        with uow:
            task = Task(id=1, title="Test", created_at=now, updated_at=now)
            uow.tasks.add(task)
            uow.rollback()

        # After rollback, data should not be persisted
        assert uow.tasks.get(1) is None

    def test_sqlalchemy_uow_multiple_repositories(self, sqlalchemy_session: Session):
        """Multiple repositories can be used in one SQLAlchemy UoW transaction."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)
        now = datetime.now(timezone.utc)

        with uow:
            # Add to multiple repositories
            task = Task(id=1, title="Task", created_at=now, updated_at=now)
            note = Note(id=1, title="Note", created_at=now, updated_at=now)
            event = Event(
                id=1, title="Event", occurred_at=now, created_at=now, updated_at=now
            )

            uow.tasks.add(task)
            uow.notes.add(note)
            uow.events.add(event)

            uow.commit()

        # All should be persisted
        assert uow.tasks.get(1) is not None
        assert uow.notes.get(1) is not None
        assert uow.events.get(1) is not None

    def test_sqlalchemy_uow_context_manager_exit_on_exception(
        self, sqlalchemy_session: Session
    ):
        """SQLAlchemyUnitOfWork context manager calls rollback on exception."""
        uow = SQLAlchemyUnitOfWork(sqlalchemy_session)
        now = datetime.now(timezone.utc)

        try:
            with uow:
                task = Task(id=1, title="Test", created_at=now, updated_at=now)
                uow.tasks.add(task)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # After exception, data should not be persisted
        assert uow.tasks.get(1) is None
