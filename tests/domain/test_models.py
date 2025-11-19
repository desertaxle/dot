"""Tests for domain models."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from dot.domain.models import Task, TaskStatus


def test_task_status_enum_values() -> None:
    """Test that TaskStatus enum has correct values."""
    assert TaskStatus.TODO == "TODO"
    assert TaskStatus.DONE == "DONE"
    assert TaskStatus.CANCELLED == "CANCELLED"


def test_task_creation() -> None:
    """Test creating a Task dataclass."""
    task_id = uuid4()
    now = datetime.utcnow()

    task = Task(
        id=task_id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )

    assert task.id == task_id
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.status == TaskStatus.TODO
    assert task.created_at == now
    assert task.updated_at == now


def test_task_without_description() -> None:
    """Test creating a Task without description."""
    task = Task(
        id=uuid4(),
        title="Quick task",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    assert task.description is None


def test_task_immutability() -> None:
    """Test that Task is immutable (frozen dataclass)."""
    task = Task(
        id=uuid4(),
        title="Test task",
        description=None,
        status=TaskStatus.TODO,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    with pytest.raises(AttributeError):
        task.title = "Changed"  # type: ignore


def test_task_with_different_statuses() -> None:
    """Test creating tasks with different statuses."""
    task_id = uuid4()
    now = datetime.utcnow()

    todo_task = Task(
        id=task_id,
        title="Task",
        description=None,
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    assert todo_task.status == TaskStatus.TODO

    done_task = Task(
        id=task_id,
        title="Task",
        description=None,
        status=TaskStatus.DONE,
        created_at=now,
        updated_at=now,
    )
    assert done_task.status == TaskStatus.DONE

    cancelled_task = Task(
        id=task_id,
        title="Task",
        description=None,
        status=TaskStatus.CANCELLED,
        created_at=now,
        updated_at=now,
    )
    assert cancelled_task.status == TaskStatus.CANCELLED


# Event Model Tests


def test_event_creation() -> None:
    """Test creating an Event dataclass."""
    from dot.domain.models import Event

    event_id = uuid4()
    now = datetime.utcnow()
    occurred = now - timedelta(hours=2)

    event = Event(
        id=event_id,
        title="Team meeting",
        description="Discuss Q4 plans",
        occurred_at=occurred,
        created_at=now,
    )

    assert event.id == event_id
    assert event.title == "Team meeting"
    assert event.description == "Discuss Q4 plans"
    assert event.occurred_at == occurred
    assert event.created_at == now


def test_event_without_description() -> None:
    """Test creating an Event without description."""
    from dot.domain.models import Event

    event = Event(
        id=uuid4(),
        title="Quick event",
        description=None,
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    assert event.description is None


def test_event_occurred_in_past() -> None:
    """Test creating an Event that occurred in the past."""
    from dot.domain.models import Event

    now = datetime.utcnow()
    past = now - timedelta(days=7)

    event = Event(
        id=uuid4(),
        title="Past event",
        description=None,
        occurred_at=past,
        created_at=now,
    )

    assert event.occurred_at < event.created_at


def test_event_occurred_in_future() -> None:
    """Test creating an Event scheduled for the future."""
    from dot.domain.models import Event

    now = datetime.utcnow()
    future = now + timedelta(days=7)

    event = Event(
        id=uuid4(),
        title="Future event",
        description=None,
        occurred_at=future,
        created_at=now,
    )

    assert event.occurred_at > event.created_at


def test_event_immutability() -> None:
    """Test that Event is immutable (frozen dataclass)."""
    from dot.domain.models import Event

    event = Event(
        id=uuid4(),
        title="Test event",
        description=None,
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    with pytest.raises(AttributeError):
        event.title = "Changed"  # type: ignore


# Note Model Tests


def test_note_creation() -> None:
    """Test creating a Note with all required fields."""
    from dot.domain.models import Note

    note_id = uuid4()
    now = datetime.utcnow()

    note = Note(
        id=note_id,
        title="Meeting Notes",
        content="Discussed project timeline and deliverables",
        created_at=now,
    )

    assert note.id == note_id
    assert note.title == "Meeting Notes"
    assert note.content == "Discussed project timeline and deliverables"
    assert note.created_at == now


def test_note_with_empty_content() -> None:
    """Test creating a Note with empty content is allowed."""
    from dot.domain.models import Note

    note = Note(
        id=uuid4(),
        title="Empty Note",
        content="",
        created_at=datetime.utcnow(),
    )

    assert note.title == "Empty Note"
    assert note.content == ""


def test_note_immutability() -> None:
    """Test that Note is immutable (frozen dataclass)."""
    from dot.domain.models import Note

    note = Note(
        id=uuid4(),
        title="Test note",
        content="Test content",
        created_at=datetime.utcnow(),
    )

    with pytest.raises(AttributeError):
        note.title = "Changed"  # type: ignore


# DailyLogEntry Model Tests


def test_daily_log_entry_creation() -> None:
    """Test creating a DailyLogEntry with all fields."""
    from datetime import date

    from dot.domain.models import DailyLogEntry, Event, Note

    log_date = date(2025, 11, 17)
    now = datetime.utcnow()

    task = Task(
        id=uuid4(),
        title="Buy groceries",
        description=None,
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )

    event = Event(
        id=uuid4(),
        title="Team meeting",
        description=None,
        occurred_at=now,
        created_at=now,
    )

    note = Note(
        id=uuid4(),
        title="Meeting notes",
        content="Important discussion points",
        created_at=now,
    )

    log_entry = DailyLogEntry(
        date=log_date,
        tasks=[task],
        events=[event],
        notes=[note],
    )

    assert log_entry.date == log_date
    assert len(log_entry.tasks) == 1
    assert log_entry.tasks[0] == task
    assert len(log_entry.events) == 1
    assert log_entry.events[0] == event
    assert len(log_entry.notes) == 1
    assert log_entry.notes[0] == note


def test_daily_log_entry_empty() -> None:
    """Test creating an empty DailyLogEntry."""
    from datetime import date

    from dot.domain.models import DailyLogEntry

    log_date = date(2025, 11, 17)

    log_entry = DailyLogEntry(
        date=log_date,
        tasks=[],
        events=[],
        notes=[],
    )

    assert log_entry.date == log_date
    assert len(log_entry.tasks) == 0
    assert len(log_entry.events) == 0
    assert len(log_entry.notes) == 0


def test_daily_log_entry_multiple_items() -> None:
    """Test DailyLogEntry with multiple tasks, events, and notes."""
    from datetime import date

    from dot.domain.models import DailyLogEntry, Event, Note

    log_date = date(2025, 11, 17)
    now = datetime.utcnow()

    tasks = [
        Task(
            id=uuid4(),
            title=f"Task {i}",
            description=None,
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        for i in range(3)
    ]

    events = [
        Event(
            id=uuid4(),
            title=f"Event {i}",
            description=None,
            occurred_at=now,
            created_at=now,
        )
        for i in range(2)
    ]

    notes = [
        Note(
            id=uuid4(),
            title=f"Note {i}",
            content=f"Content {i}",
            created_at=now,
        )
        for i in range(4)
    ]

    log_entry = DailyLogEntry(
        date=log_date,
        tasks=tasks,
        events=events,
        notes=notes,
    )

    assert len(log_entry.tasks) == 3
    assert len(log_entry.events) == 2
    assert len(log_entry.notes) == 4


def test_daily_log_entry_immutability() -> None:
    """Test that DailyLogEntry is immutable (frozen dataclass)."""
    from datetime import date

    from dot.domain.models import DailyLogEntry

    log_entry = DailyLogEntry(
        date=date(2025, 11, 17),
        tasks=[],
        events=[],
        notes=[],
    )

    with pytest.raises(AttributeError):
        log_entry.date = date(2025, 11, 18)  # type: ignore
