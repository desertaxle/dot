"""Tests for in-memory repository implementations."""

import pytest

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
