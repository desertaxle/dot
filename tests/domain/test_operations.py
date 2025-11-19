"""Tests for domain operations."""

from datetime import datetime
from uuid import UUID

import pytest

from dot.domain.models import TaskStatus
from dot.domain.operations import create_task, mark_cancelled, mark_done, reopen_task


def test_create_task_with_title_only() -> None:
    """Test creating a task with just a title."""
    task = create_task("Buy milk")

    assert isinstance(task.id, UUID)
    assert task.title == "Buy milk"
    assert task.description is None
    assert task.status == TaskStatus.TODO
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)
    assert task.created_at == task.updated_at


def test_create_task_with_description() -> None:
    """Test creating a task with title and description."""
    task = create_task("Buy groceries", description="Milk, eggs, bread")

    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.status == TaskStatus.TODO


def test_create_task_validates_empty_title() -> None:
    """Test that create_task rejects empty titles."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_task("")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_task("   ")


def test_create_task_validates_title_length() -> None:
    """Test that create_task rejects too-long titles."""
    long_title = "x" * 501
    with pytest.raises(ValueError, match="Title cannot exceed 500 characters"):
        create_task(long_title)


def test_create_task_validates_description_length() -> None:
    """Test that create_task rejects too-long descriptions."""
    long_description = "x" * 5001
    with pytest.raises(ValueError, match="Description cannot exceed 5000 characters"):
        create_task("Valid title", description=long_description)


def test_mark_done_changes_status() -> None:
    """Test marking a task as done."""
    task = create_task("Test task")
    assert task.status == TaskStatus.TODO

    done_task = mark_done(task)

    assert done_task.status == TaskStatus.DONE
    assert done_task.id == task.id
    assert done_task.title == task.title
    assert done_task.description == task.description
    assert done_task.created_at == task.created_at
    assert done_task.updated_at > task.updated_at


def test_mark_cancelled_changes_status() -> None:
    """Test marking a task as cancelled."""
    task = create_task("Test task")
    assert task.status == TaskStatus.TODO

    cancelled_task = mark_cancelled(task)

    assert cancelled_task.status == TaskStatus.CANCELLED
    assert cancelled_task.id == task.id
    assert cancelled_task.updated_at > task.updated_at


def test_reopen_task_from_done() -> None:
    """Test reopening a done task."""
    task = create_task("Test task")
    done_task = mark_done(task)
    assert done_task.status == TaskStatus.DONE

    reopened_task = reopen_task(done_task)

    assert reopened_task.status == TaskStatus.TODO
    assert reopened_task.id == task.id
    assert reopened_task.updated_at > done_task.updated_at


def test_reopen_task_from_cancelled() -> None:
    """Test reopening a cancelled task."""
    task = create_task("Test task")
    cancelled_task = mark_cancelled(task)
    assert cancelled_task.status == TaskStatus.CANCELLED

    reopened_task = reopen_task(cancelled_task)

    assert reopened_task.status == TaskStatus.TODO
    assert reopened_task.id == task.id


def test_mark_done_on_already_done_task() -> None:
    """Test that marking an already done task as done is idempotent."""
    task = create_task("Test task")
    done_task = mark_done(task)
    done_again = mark_done(done_task)

    assert done_again.status == TaskStatus.DONE


def test_state_transitions() -> None:
    """Test various state transitions."""
    task = create_task("Test task")

    # TODO -> DONE
    done_task = mark_done(task)
    assert done_task.status == TaskStatus.DONE

    # DONE -> CANCELLED
    cancelled_task = mark_cancelled(done_task)
    assert cancelled_task.status == TaskStatus.CANCELLED

    # CANCELLED -> TODO
    reopened_task = reopen_task(cancelled_task)
    assert reopened_task.status == TaskStatus.TODO


# Event Operation Tests


def test_create_event_with_title_only() -> None:
    """Test creating an event with just a title."""
    from dot.domain.operations import create_event

    event = create_event("Team standup")

    assert isinstance(event.id, UUID)
    assert event.title == "Team standup"
    assert event.description is None
    assert isinstance(event.occurred_at, datetime)
    assert isinstance(event.created_at, datetime)
    # When no occurred_at is provided, it defaults to now (approximately)
    assert abs((event.occurred_at - event.created_at).total_seconds()) < 1


def test_create_event_with_description() -> None:
    """Test creating an event with title and description."""
    from dot.domain.operations import create_event

    event = create_event("Team standup", description="Daily sync meeting")

    assert event.title == "Team standup"
    assert event.description == "Daily sync meeting"


def test_create_event_with_custom_occurred_at() -> None:
    """Test creating an event with a custom occurred_at timestamp."""
    from dot.domain.operations import create_event

    custom_time = datetime(2025, 11, 17, 14, 30)
    event = create_event("Historical event", occurred_at=custom_time)

    assert event.title == "Historical event"
    assert event.occurred_at == custom_time


def test_create_event_validates_empty_title() -> None:
    """Test that create_event rejects empty titles."""
    from dot.domain.operations import create_event

    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_event("")

    with pytest.raises(ValueError, match="Title cannot be empty"):
        create_event("   ")


def test_create_event_validates_title_length() -> None:
    """Test that create_event rejects too-long titles."""
    from dot.domain.operations import create_event

    long_title = "x" * 501
    with pytest.raises(ValueError, match="Title cannot exceed 500 characters"):
        create_event(long_title)


def test_create_event_validates_description_length() -> None:
    """Test that create_event rejects too-long descriptions."""
    from dot.domain.operations import create_event

    long_description = "x" * 5001
    with pytest.raises(ValueError, match="Description cannot exceed 5000 characters"):
        create_event("Valid title", description=long_description)
