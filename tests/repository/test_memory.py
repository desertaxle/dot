"""Tests for in-memory repository implementations."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from dot.domain.models import Event, Note, Project, Task, TaskStatus
from dot.repository.memory import (
    InMemoryEventRepository,
    InMemoryLogEntryRepository,
    InMemoryMigrationRepository,
    InMemoryNoteRepository,
    InMemoryProjectRepository,
    InMemoryTaskRepository,
)
from tests.repository.test_abstract import (
    EventRepositoryContract,
    LogEntryRepositoryContract,
    MigrationRepositoryContract,
    NoteRepositoryContract,
    ProjectRepositoryContract,
    TaskRepositoryContract,
)


class TestInMemoryTaskRepository(TaskRepositoryContract):
    """Test InMemoryTaskRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryTaskRepository()


class TestInMemoryNoteRepository(NoteRepositoryContract):
    """Test InMemoryNoteRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryNoteRepository()


class TestInMemoryEventRepository(EventRepositoryContract):
    """Test InMemoryEventRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryEventRepository()


class TestInMemoryTaskRepositoryEdgeCases:
    """Test edge cases for InMemoryTaskRepository."""

    def test_update_nonexistent_task(self):
        """Updating nonexistent task doesn't raise error."""
        repository = InMemoryTaskRepository()
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
        repository.update(task)

        # Verify task was not added
        assert repository.get(task_id) is None


class TestInMemoryNoteRepositoryEdgeCases:
    """Test edge cases for InMemoryNoteRepository."""

    def test_update_nonexistent_note(self):
        """Updating nonexistent note doesn't raise error."""
        repository = InMemoryNoteRepository()
        now = datetime.now(timezone.utc)
        note_id = uuid4()
        note = Note(
            id=note_id,
            title="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        repository.update(note)

        # Verify note was not added
        assert repository.get(note_id) is None


class TestInMemoryEventRepositoryEdgeCases:
    """Test edge cases for InMemoryEventRepository."""

    def test_update_nonexistent_event(self):
        """Updating nonexistent event doesn't raise error."""
        repository = InMemoryEventRepository()
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
        repository.update(event)

        # Verify event was not added
        assert repository.get(event_id) is None


class TestInMemoryProjectRepository(ProjectRepositoryContract):
    """Test InMemoryProjectRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryProjectRepository()


class TestInMemoryLogEntryRepository(LogEntryRepositoryContract):
    """Test InMemoryLogEntryRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryLogEntryRepository()


class TestInMemoryProjectRepositoryEdgeCases:
    """Test edge cases for InMemoryProjectRepository."""

    def test_update_nonexistent_project(self):
        """Updating nonexistent project doesn't raise error."""
        repository = InMemoryProjectRepository()
        now = datetime.now(timezone.utc)
        project_id = uuid4()
        project = Project(
            id=project_id,
            name="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        repository.update(project)

        # Verify project was not added
        assert repository.get(project_id) is None


class TestInMemoryMigrationRepository(MigrationRepositoryContract):
    """Test InMemoryMigrationRepository against the contract."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test repository."""
        self.repository = InMemoryMigrationRepository()


class TestInMemoryMigrationRepositoryEdgeCases:
    """Test edge cases for InMemoryMigrationRepository."""

    def test_add_migration_without_id_auto_generates(self):
        """Adding migration without ID auto-generates UUID."""
        from dot.domain.log_operations import Migration

        repository = InMemoryMigrationRepository()
        # Create migration without ID (dataclass defaults to None)
        migration = Migration(
            id=uuid4(),  # type: ignore[arg-type]
            task_id=uuid4(),
            from_log_entry_id=uuid4(),
            to_log_entry_id=uuid4(),
        )
        # Set ID to None to test auto-generation
        migration.id = None  # type: ignore[assignment]

        repository.add(migration)

        # Verify ID was auto-generated
        assert migration.id is not None
        retrieved = repository.get(migration.id)
        assert retrieved is not None
