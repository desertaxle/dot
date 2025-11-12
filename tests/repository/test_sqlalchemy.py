"""Tests for SQLAlchemy repository implementations."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
import whenever
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


from dot.domain.log_operations import LogEntry
from dot.domain.models import Event, Note, Project, Task, TaskStatus
from dot.models import Base
from dot.repository.sqlalchemy import (
    SQLAlchemyEventRepository,
    SQLAlchemyLogEntryRepository,
    SQLAlchemyNoteRepository,
    SQLAlchemyProjectRepository,
    SQLAlchemyTaskRepository,
)
from tests.repository.test_abstract import (
    EventRepositoryContract,
    LogEntryRepositoryContract,
    NoteRepositoryContract,
    ProjectRepositoryContract,
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
        task_id = uuid4()
        task = Task(
            id=task_id,
            title="Nonexistent",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(task)

        # Verify task was not added
        assert self.repository.get(task_id) is None

    def test_add_task_without_id_auto_generates_uuid(self):
        """Test that adding a task without an ID auto-generates a UUID."""
        # Create task without ID
        task = Task(title="Test task", status=TaskStatus.TODO)
        assert task.id is None

        # Add to repository
        self.repository.add(task)

        # Verify UUID was auto-generated
        assert task.id is not None
        assert isinstance(task.id, UUID)

        # Verify it can be retrieved
        retrieved = self.repository.get(task.id)
        assert retrieved is not None
        assert retrieved.title == "Test task"

    def test_domain_to_orm_with_none_id(self):
        """Test _domain_to_orm with a task that has id=None (defensive check)."""
        from dot.models import Task as OrmTask

        # Create task without ID
        task = Task(title="Test task", status=TaskStatus.TODO)
        assert task.id is None

        # Call _domain_to_orm (private method - defensive code test)
        orm_task = self.repository._domain_to_orm(task)

        # Verify ORM object was created without ID set
        assert isinstance(orm_task, OrmTask)
        assert orm_task.title == "Test task"
        # ID was not set in kwargs, so ORM object's id should not be in __dict__ yet
        # (it would be auto-generated on insert)


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
        note_id = uuid4()
        note = Note(
            id=note_id,
            title="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(note)

        # Verify note was not added
        assert self.repository.get(note_id) is None

    def test_add_note_without_id_auto_generates_uuid(self):
        """Test that adding a note without an ID auto-generates a UUID."""
        # Create note without ID
        note = Note(title="Test note")
        assert note.id is None

        # Add to repository
        self.repository.add(note)

        # Verify UUID was auto-generated
        assert note.id is not None
        assert isinstance(note.id, UUID)

        # Verify it can be retrieved
        retrieved = self.repository.get(note.id)
        assert retrieved is not None
        assert retrieved.title == "Test note"

    def test_domain_to_orm_with_none_id(self):
        """Test _domain_to_orm with a note that has id=None (defensive check)."""
        from dot.models import Note as OrmNote

        # Create note without ID
        note = Note(title="Test note")
        assert note.id is None

        # Call _domain_to_orm (private method - defensive code test)
        orm_note = self.repository._domain_to_orm(note)

        # Verify ORM object was created without ID set
        assert isinstance(orm_note, OrmNote)
        assert orm_note.title == "Test note"


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
        event_id = uuid4()
        event = Event(
            id=event_id,
            title="Nonexistent",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(event)

        # Verify event was not added
        assert self.repository.get(event_id) is None

    def test_add_event_without_id_auto_generates_uuid(self):
        """Test that adding an event without an ID auto-generates a UUID."""
        # Create event without ID
        now = datetime.now(timezone.utc)
        event = Event(title="Test event", occurred_at=now)
        assert event.id is None

        # Add to repository
        self.repository.add(event)

        # Verify UUID was auto-generated
        assert event.id is not None
        assert isinstance(event.id, UUID)

        # Verify it can be retrieved
        retrieved = self.repository.get(event.id)
        assert retrieved is not None
        assert retrieved.title == "Test event"

    def test_domain_to_orm_with_none_id(self):
        """Test _domain_to_orm with an event that has id=None (defensive check)."""
        from dot.models import Event as OrmEvent

        # Create event without ID
        now = datetime.now(timezone.utc)
        event = Event(title="Test event", occurred_at=now)
        assert event.id is None

        # Call _domain_to_orm (private method - defensive code test)
        orm_event = self.repository._domain_to_orm(event)

        # Verify ORM object was created without ID set
        assert isinstance(orm_event, OrmEvent)
        assert orm_event.title == "Test event"


class TestSQLAlchemyProjectRepository(ProjectRepositoryContract):
    """Test SQLAlchemyProjectRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyProjectRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()


class TestSQLAlchemyLogEntryRepository(LogEntryRepositoryContract):
    """Test SQLAlchemyLogEntryRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyLogEntryRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()


class TestSQLAlchemyProjectRepositoryEdgeCases:
    """Test edge cases for SQLAlchemyProjectRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyProjectRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()

    def test_update_nonexistent_project(self):
        """Updating nonexistent project doesn't raise error."""
        now = datetime.now(timezone.utc)
        project_id = uuid4()
        project = Project(
            id=project_id,
            name="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        self.repository.update(project)

        # Verify project was not added
        assert self.repository.get(project_id) is None

    def test_add_project_without_id_auto_generates_uuid(self):
        """Test that adding a project without an ID auto-generates a UUID."""
        # Create project without ID
        project = Project(name="Test project")
        assert project.id is None

        # Add to repository
        self.repository.add(project)

        # Verify UUID was auto-generated
        assert project.id is not None
        assert isinstance(project.id, UUID)

        # Verify it can be retrieved
        retrieved = self.repository.get(project.id)
        assert retrieved is not None
        assert retrieved.name == "Test project"

    def test_domain_to_orm_with_none_id(self):
        """Test _domain_to_orm with a project that has id=None (defensive check)."""
        from dot.models import Project as OrmProject

        # Create project without ID
        project = Project(name="Test project")
        assert project.id is None

        # Call _domain_to_orm (private method - defensive code test)
        orm_project = self.repository._domain_to_orm(project)

        # Verify ORM object was created without ID set
        assert isinstance(orm_project, OrmProject)
        assert orm_project.name == "Test project"


class TestSQLAlchemyLogEntryRepositoryEdgeCases:
    """Test edge cases for SQLAlchemyLogEntryRepository."""

    @pytest.fixture(autouse=True)
    def setup(self, session: Session):
        """Set up test repository."""
        self.repository = SQLAlchemyLogEntryRepository(session)
        self.session = session

    def teardown_method(self):
        """Clean up after each test."""
        self.session.rollback()

    def test_add_log_entry_without_id_auto_generates_uuid(self):
        """Test that adding a log entry without an ID auto-generates a UUID."""
        # Create log entry without ID
        log_id = uuid4()
        task_id = uuid4()
        entry_date = whenever.Date(2025, 1, 15)
        log_entry = LogEntry(
            log_id=log_id,
            task_id=task_id,
            entry_date=entry_date,
        )
        assert log_entry.id is None

        # Add to repository
        self.repository.add(log_entry)

        # Verify UUID was auto-generated
        assert log_entry.id is not None
        assert isinstance(log_entry.id, UUID)

        # Verify it can be retrieved
        retrieved = self.repository.get(log_entry.id)
        assert retrieved is not None
        assert retrieved.log_id == log_id
        assert retrieved.task_id == task_id

    def test_domain_to_orm_with_none_id(self):
        """Test _domain_to_orm with a log entry that has id=None (defensive check)."""
        from dot.models import LogEntry as OrmLogEntry

        # Create log entry without ID
        log_id = uuid4()
        task_id = uuid4()
        entry_date = whenever.Date(2025, 1, 15)
        log_entry = LogEntry(
            log_id=log_id,
            task_id=task_id,
            entry_date=entry_date,
        )
        assert log_entry.id is None

        # Call _domain_to_orm (private method - defensive code test)
        orm_log_entry = self.repository._domain_to_orm(log_entry)

        # Verify ORM object was created without ID set
        assert isinstance(orm_log_entry, OrmLogEntry)
        assert orm_log_entry.project_id == str(log_id)
        assert orm_log_entry.task_id == str(task_id)
