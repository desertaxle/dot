"""Tests for domain models."""

from datetime import datetime, timezone
from uuid import uuid4

import whenever

from dot.domain.models import Event, MonthlyLog, Note, Task, TaskStatus, WeeklyLog


class TestTask:
    """Tests for Task domain model."""

    def test_create_task_with_required_fields(self):
        """Task can be created with required fields."""
        now = datetime.now(timezone.utc)
        task_id = uuid4()
        task = Task(
            id=task_id,
            title="Buy groceries",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

        assert task.id == task_id
        assert task.title == "Buy groceries"
        assert task.status == TaskStatus.TODO
        assert task.created_at == now
        assert task.updated_at == now

    def test_create_task_with_optional_fields(self):
        """Task can be created with optional fields."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=uuid4(),
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
        task = Task(id=uuid4(), title="Test task")

        assert task.status == TaskStatus.TODO
        assert task.description is None
        assert task.priority is None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_statuses(self):
        """Task status can be any valid status."""
        now = datetime.now(timezone.utc)

        todo_task = Task(
            id=uuid4(),
            title="Todo",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        done_task = Task(
            id=uuid4(),
            title="Done",
            status=TaskStatus.DONE,
            created_at=now,
            updated_at=now,
        )
        cancelled_task = Task(
            id=uuid4(),
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
        note_id = uuid4()
        note = Note(
            id=note_id,
            title="My thoughts",
            created_at=now,
            updated_at=now,
        )

        assert note.id == note_id
        assert note.title == "My thoughts"
        assert note.created_at == now
        assert note.updated_at == now

    def test_create_note_with_content(self):
        """Note can be created with content."""
        now = datetime.now(timezone.utc)
        note = Note(
            id=uuid4(),
            title="My thoughts",
            content="This is a long thought...",
            created_at=now,
            updated_at=now,
        )

        assert note.content == "This is a long thought..."

    def test_note_with_defaults(self):
        """Note has sensible defaults."""
        note = Note(id=uuid4(), title="Test note")

        assert note.content is None
        assert isinstance(note.created_at, datetime)
        assert isinstance(note.updated_at, datetime)


class TestEvent:
    """Tests for Event domain model."""

    def test_create_event_with_required_fields(self):
        """Event can be created with required fields."""
        now = datetime.now(timezone.utc)
        event_id = uuid4()
        event = Event(
            id=event_id,
            title="Had coffee",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )

        assert event.id == event_id
        assert event.title == "Had coffee"
        assert event.occurred_at == now
        assert event.created_at == now
        assert event.updated_at == now

    def test_create_event_with_content(self):
        """Event can be created with content."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=uuid4(),
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
        event = Event(id=uuid4(), title="Test event", occurred_at=occurred_at)

        assert event.content is None
        assert isinstance(event.created_at, datetime)
        assert isinstance(event.updated_at, datetime)
        assert event.occurred_at == occurred_at

    def test_event_occurred_at_can_be_in_past(self):
        """Event occurred_at can be any time."""
        past = datetime(2020, 1, 1, tzinfo=timezone.utc)
        event = Event(
            id=uuid4(),
            title="Past event",
            occurred_at=past,
        )

        assert event.occurred_at == past

    def test_event_defaults_to_current_datetime(self):
        """Event occurred_at defaults to current datetime when not specified."""
        before = datetime.now(timezone.utc)
        event = Event(title="Event with default time")
        after = datetime.now(timezone.utc)

        # occurred_at should be between before and after
        assert before <= event.occurred_at <= after
        assert event.occurred_at.tzinfo == timezone.utc


class TestLogDefaults:
    """Tests for Log subclass default factories."""

    def test_weekly_log_default_week_start(self):
        """WeeklyLog without week_start uses current week."""
        log = WeeklyLog(id=uuid4(), name="This Week")
        assert log.week_start is not None
        # Should be a Monday (day_of_week value = 1)
        assert log.week_start.day_of_week().value == 1

    def test_monthly_log_default_year_month(self):
        """MonthlyLog without year/month uses current month."""
        log = MonthlyLog(id=uuid4(), name="This Month")
        today = whenever.Instant.now().to_system_tz().date()
        assert log.year == today.year
        assert log.month == today.month
