"""Tests for SQLAlchemy repository implementations."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from dot.domain.models import Event, Note, Task, TaskStatus
from dot.models import Base
from dot.repository.sqlalchemy import (
    SQLAlchemyEventRepository,
    SQLAlchemyNoteRepository,
    SQLAlchemyTaskRepository,
)
from tests.repository.test_abstract import (
    EventRepositoryContract,
    NoteRepositoryContract,
    TaskRepositoryContract,
)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(in_memory_db: Engine):
    """Create a database session for a test."""
    SessionLocal = sessionmaker(bind=in_memory_db)
    session = SessionLocal()
    yield session
    session.close()


class TestSQLAlchemyTaskRepository(TaskRepositoryContract):
    """Test SQLAlchemyTaskRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyTaskRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()


class TestSQLAlchemyNoteRepository(NoteRepositoryContract):
    """Test SQLAlchemyNoteRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyNoteRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()


class TestSQLAlchemyEventRepository(EventRepositoryContract):
    """Test SQLAlchemyEventRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyEventRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()


class TestSQLAlchemyTaskRepositoryEdgeCases:
    """Test edge cases for SQLAlchemyTaskRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyTaskRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()

    def test_update_nonexistent_task(self):
        """Updating nonexistent task doesn't raise error."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=9999,
            title="Nonexistent",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(task)

        # Verify task was not added
        assert self.repository.get(9999) is None


class TestSQLAlchemyNoteRepositoryEdgeCases:
    """Test edge cases for SQLAlchemyNoteRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyNoteRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()

    def test_update_nonexistent_note(self):
        """Updating nonexistent note doesn't raise error."""
        now = datetime.now(timezone.utc)
        note = Note(
            id=9999,
            title="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(note)

        # Verify note was not added
        assert self.repository.get(9999) is None


class TestSQLAlchemyEventRepositoryEdgeCases:
    """Test edge cases for SQLAlchemyEventRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyEventRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()

    def test_update_nonexistent_event(self):
        """Updating nonexistent event doesn't raise error."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=9999,
            title="Nonexistent",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(event)

        # Verify event was not added
        assert self.repository.get(9999) is None
