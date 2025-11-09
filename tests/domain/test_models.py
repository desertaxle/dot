"""Tests for domain models."""

from datetime import datetime, timezone


from dot.domain.models import Event, Note, Task, TaskStatus


class TestTask:
    """Tests for Task domain model."""

    def test_create_task_with_required_fields(self):
        """Task can be created with required fields."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Buy groceries",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.status == TaskStatus.TODO
        assert task.created_at == now
        assert task.updated_at == now

    def test_create_task_with_optional_fields(self):
        """Task can be created with optional fields."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Buy groceries",
            description="Get milk and eggs",
            status=TaskStatus.TODO,
            priority=1,
            created_at=now,
            updated_at=now,
        )

        assert task.description == "Get milk and eggs"
        assert task.priority == 1

    def test_task_with_defaults(self):
        """Task has sensible defaults."""
        task = Task(id=1, title="Test task")

        assert task.status == TaskStatus.TODO
        assert task.description is None
        assert task.priority is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_statuses(self):
        """Task status can be any valid status."""
        now = datetime.now(timezone.utc)

        todo_task = Task(
            id=1, title="Todo", status=TaskStatus.TODO, created_at=now, updated_at=now
        )
        done_task = Task(
            id=2,
            title="Done",
            status=TaskStatus.DONE,
            created_at=now,
            updated_at=now,
        )
        cancelled_task = Task(
            id=3,
            title="Cancelled",
            status=TaskStatus.CANCELLED,
            created_at=now,
            updated_at=now,
        )

        assert todo_task.status == TaskStatus.TODO
        assert done_task.status == TaskStatus.DONE
        assert cancelled_task.status == TaskStatus.CANCELLED


class TestNote:
    """Tests for Note domain model."""

    def test_create_note_with_required_fields(self):
        """Note can be created with required fields."""
        now = datetime.now(timezone.utc)
        note = Note(
            id=1,
            title="My thoughts",
            created_at=now,
            updated_at=now,
        )

        assert note.id == 1
        assert note.title == "My thoughts"
        assert note.created_at == now
        assert note.updated_at == now

    def test_create_note_with_content(self):
        """Note can be created with content."""
        now = datetime.now(timezone.utc)
        note = Note(
            id=1,
            title="My thoughts",
            content="This is a long thought...",
            created_at=now,
            updated_at=now,
        )

        assert note.content == "This is a long thought..."

    def test_note_with_defaults(self):
        """Note has sensible defaults."""
        note = Note(id=1, title="Test note")

        assert note.content is None
        assert isinstance(note.created_at, datetime)
        assert isinstance(note.updated_at, datetime)


class TestEvent:
    """Tests for Event domain model."""

    def test_create_event_with_required_fields(self):
        """Event can be created with required fields."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1,
            title="Had coffee",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )

        assert event.id == 1
        assert event.title == "Had coffee"
        assert event.occurred_at == now
        assert event.created_at == now
        assert event.updated_at == now

    def test_create_event_with_content(self):
        """Event can be created with content."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1,
            title="Had coffee",
            content="Met with Alice at the cafe",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )

        assert event.content == "Met with Alice at the cafe"

    def test_event_with_defaults(self):
        """Event has sensible defaults."""
        occurred_at = datetime.now(timezone.utc)
        event = Event(id=1, title="Test event", occurred_at=occurred_at)

        assert event.content is None
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)
        assert event.occurred_at == occurred_at

    def test_event_occurred_at_can_be_in_past(self):
        """Event occurred_at can be any time."""
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        event = Event(
            id=1,
            title="Past event",
            occurred_at=past,
        )

        assert event.occurred_at == past
