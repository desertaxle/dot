"""Tests for repository abstractions - tests the contract repositories must follow."""

from datetime import datetime, timezone


from dot.domain.models import Event, Note, Task, TaskStatus
from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository


class TaskRepositoryContract:
    """Contract that all TaskRepository implementations must follow."""

    repository: TaskRepository

    def test_add_task(self):
        """Repository can add a task."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test task",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

        self.repository.add(task)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test task"

    def test_get_nonexistent_task(self):
        """Repository returns None for nonexistent task."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_tasks(self):
        """Repository can list all tasks."""
        now = datetime.now(timezone.utc)
        task1 = Task(id=1, title="Task 1", created_at=now, updated_at=now)
        task2 = Task(id=2, title="Task 2", created_at=now, updated_at=now)

        self.repository.add(task1)
        self.repository.add(task2)

        tasks = self.repository.list()
        assert len(tasks) == 2
        assert any(t.id == 1 for t in tasks)
        assert any(t.id == 2 for t in tasks)

    def test_update_task(self):
        """Repository can update a task."""
        now = datetime.now(timezone.utc)
        task = Task(id=1, title="Original", created_at=now, updated_at=now)

        self.repository.add(task)

        updated_task = Task(
            id=1,
            title="Updated",
            status=TaskStatus.DONE,
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_task)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.status == TaskStatus.DONE

    def test_delete_task(self):
        """Repository can delete a task."""
        now = datetime.now(timezone.utc)
        task = Task(id=1, title="To delete", created_at=now, updated_at=now)

        self.repository.add(task)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_task(self):
        """Deleting nonexistent task doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)


class NoteRepositoryContract:
    """Contract that all NoteRepository implementations must follow."""

    repository: NoteRepository

    def test_add_note(self):
        """Repository can add a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="Test note", created_at=now, updated_at=now)

        self.repository.add(note)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test note"

    def test_get_nonexistent_note(self):
        """Repository returns None for nonexistent note."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_notes(self):
        """Repository can list all notes."""
        now = datetime.now(timezone.utc)
        note1 = Note(id=1, title="Note 1", created_at=now, updated_at=now)
        note2 = Note(id=2, title="Note 2", created_at=now, updated_at=now)

        self.repository.add(note1)
        self.repository.add(note2)

        notes = self.repository.list()
        assert len(notes) == 2
        assert any(n.id == 1 for n in notes)
        assert any(n.id == 2 for n in notes)

    def test_update_note(self):
        """Repository can update a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="Original", created_at=now, updated_at=now)

        self.repository.add(note)

        updated_note = Note(
            id=1,
            title="Updated",
            content="New content",
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_note)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "New content"

    def test_delete_note(self):
        """Repository can delete a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="To delete", created_at=now, updated_at=now)

        self.repository.add(note)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_note(self):
        """Deleting nonexistent note doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)


class EventRepositoryContract:
    """Contract that all EventRepository implementations must follow."""

    repository: EventRepository

    def test_add_event(self):
        """Repository can add an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="Test event", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test event"

    def test_get_nonexistent_event(self):
        """Repository returns None for nonexistent event."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_events(self):
        """Repository can list all events."""
        now = datetime.now(timezone.utc)
        event1 = Event(
            id=1, title="Event 1", occurred_at=now, created_at=now, updated_at=now
        )
        event2 = Event(
            id=2, title="Event 2", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event1)
        self.repository.add(event2)

        events = self.repository.list()
        assert len(events) == 2
        assert any(e.id == 1 for e in events)
        assert any(e.id == 2 for e in events)

    def test_update_event(self):
        """Repository can update an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="Original", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)

        updated_event = Event(
            id=1,
            title="Updated",
            content="New content",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_event)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "New content"

    def test_delete_event(self):
        """Repository can delete an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="To delete", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_event(self):
        """Deleting nonexistent event doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)
