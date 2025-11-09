"""Tests for SQLAlchemy repository implementations."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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
    return engine


@pytest.fixture
def session(in_memory_db):
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
