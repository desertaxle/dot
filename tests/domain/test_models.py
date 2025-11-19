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
