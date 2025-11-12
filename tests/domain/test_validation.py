"""Tests for domain validation functions."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from dot.domain.models import Event, Task
from dot.domain.validation import (
    InvalidCronError,
    InvalidDateError,
    InvalidEventError,
    InvalidTaskError,
    validate_cron,
    validate_dates,
    validate_event,
    validate_task,
)


class TestTaskValidation:
    """Tests for task validation."""

    def test_validate_valid_task(self):
        """Valid task passes validation."""
        task = Task(id=uuid4(), title="Test task")
        validate_task(task)  # Should not raise

    def test_validate_task_with_priority(self):
        """Task with valid priority passes validation."""
        task = Task(id=uuid4(), title="Test task", priority=2)
        validate_task(task)  # Should not raise

    def test_validate_empty_title(self):
        """Task with empty title fails validation."""
        task = Task(id=uuid4(), title="")
        with pytest.raises(InvalidTaskError, match="title cannot be empty"):
            validate_task(task)

    def test_validate_whitespace_only_title(self):
        """Task with whitespace-only title fails validation."""
        task = Task(id=uuid4(), title="   ")
        with pytest.raises(InvalidTaskError, match="title cannot be empty"):
            validate_task(task)

    def test_validate_invalid_priority_low(self):
        """Task with priority < 1 fails validation."""
        task = Task(id=uuid4(), title="Test task", priority=0)
        with pytest.raises(InvalidTaskError, match="priority must be 1-3"):
            validate_task(task)

    def test_validate_invalid_priority_high(self):
        """Task with priority > 3 fails validation."""
        task = Task(id=uuid4(), title="Test task", priority=4)
        with pytest.raises(InvalidTaskError, match="priority must be 1-3"):
            validate_task(task)

    def test_validate_invalid_priority_type(self):
        """Task with non-integer priority fails validation."""
        task = Task(id=uuid4(), title="Test task")
        task.priority = "high"  # type: ignore
        with pytest.raises(InvalidTaskError, match="priority must be 1-3"):
            validate_task(task)

    def test_validate_invalid_task_status(self):
        """Task with invalid status fails validation."""
        task = Task(id=uuid4(), title="Test task")
        task.status = "invalid"  # type: ignore
        with pytest.raises(InvalidTaskError, match="Invalid task status"):
            validate_task(task)

    def test_validate_dates_invalid_order(self):
        """Task with created_at > updated_at fails validation."""
        now = datetime.now(timezone.utc)
        earlier = now.replace(hour=now.hour - 1)  # One hour earlier
        task = Task(
            id=uuid4(),
            title="Test task",
            created_at=now,
            updated_at=earlier,  # Before created_at
        )
        with pytest.raises(InvalidTaskError):
            validate_task(task)


class TestEventValidation:
    """Tests for event validation."""

    def test_validate_valid_event(self):
        """Valid event passes validation."""
        now = datetime.now(timezone.utc)
        event = Event(id=uuid4(), title="Test event", occurred_at=now)
        validate_event(event)  # Should not raise

    def test_validate_event_empty_title(self):
        """Event with empty title fails validation."""
        now = datetime.now(timezone.utc)
        event = Event(id=uuid4(), title="", occurred_at=now)
        with pytest.raises(InvalidEventError, match="title cannot be empty"):
            validate_event(event)

    def test_validate_event_future_occurred_at(self):
        """Event with future occurred_at fails validation."""
        future = datetime.now(timezone.utc).replace(
            year=datetime.now(timezone.utc).year + 1
        )  # Far future
        event = Event(id=uuid4(), title="Test event", occurred_at=future)
        with pytest.raises(InvalidEventError, match="cannot be in the future"):
            validate_event(event)


class TestDateValidation:
    """Tests for date validation."""

    def test_validate_dates_equal(self):
        """Equal created_at and updated_at is valid."""
        now = datetime.now(timezone.utc)
        validate_dates(now, now)  # Should not raise

    def test_validate_dates_created_before_updated(self):
        """created_at before updated_at is valid."""
        now = datetime.now(timezone.utc)
        earlier = now.replace(hour=now.hour - 1)
        validate_dates(earlier, now)  # Should not raise

    def test_validate_dates_created_after_updated(self):
        """created_at after updated_at fails validation."""
        now = datetime.now(timezone.utc)
        later = now.replace(hour=now.hour + 1)
        with pytest.raises(InvalidDateError, match="cannot be after"):
            validate_dates(later, now)


class TestCronValidation:
    """Tests for cron expression validation."""

    def test_validate_valid_cron_daily(self):
        """Valid daily cron expression passes."""
        validate_cron("0 9 * * *")  # Should not raise

    def test_validate_valid_cron_weekly(self):
        """Valid weekly cron expression passes."""
        validate_cron("0 9 * * MON")  # Should not raise

    def test_validate_valid_cron_every_minute(self):
        """Valid every-minute cron expression passes."""
        validate_cron("* * * * *")  # Should not raise

    def test_validate_invalid_cron_bad_syntax(self):
        """Invalid cron expression fails."""
        with pytest.raises(InvalidCronError):
            validate_cron("not a cron")

    def test_validate_invalid_cron_bad_hour(self):
        """Cron with invalid hour fails."""
        with pytest.raises(InvalidCronError):
            validate_cron("0 25 * * *")  # Hour 25 is invalid

    def test_validate_invalid_cron_bad_day(self):
        """Cron with invalid day fails."""
        with pytest.raises(InvalidCronError):
            validate_cron("0 9 32 * *")  # Day 32 is invalid
