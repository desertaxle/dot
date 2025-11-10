"""Tests for in-memory repository implementations."""

from datetime import datetime, timezone

import pytest

from dot.domain.models import Event, Note, Task, TaskStatus
from dot.repository.memory import (
    InMemoryEventRepository,
    InMemoryNoteRepository,
    InMemoryTaskRepository,
)
from tests.repository.test_abstract import (
    EventRepositoryContract,
    NoteRepositoryContract,
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
        task = Task(
            id=9999,
            title="Nonexistent",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        repository.update(task)

        # Verify task was not added
        assert repository.get(9999) is None


class TestInMemoryNoteRepositoryEdgeCases:
    """Test edge cases for InMemoryNoteRepository."""

    def test_update_nonexistent_note(self):
        """Updating nonexistent note doesn't raise error."""
        repository = InMemoryNoteRepository()
        now = datetime.now(timezone.utc)
        note = Note(
            id=9999,
            title="Nonexistent",
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        repository.update(note)

        # Verify note was not added
        assert repository.get(9999) is None


class TestInMemoryEventRepositoryEdgeCases:
    """Test edge cases for InMemoryEventRepository."""

    def test_update_nonexistent_event(self):
        """Updating nonexistent event doesn't raise error."""
        repository = InMemoryEventRepository()
        now = datetime.now(timezone.utc)
        event = Event(
            id=9999,
            title="Nonexistent",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        # Should not raise
        repository.update(event)

        # Verify event was not added
        assert repository.get(9999) is None
