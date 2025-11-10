"""Validation functions for domain models."""

from datetime import datetime, timezone

from croniter import croniter

from dot.domain.models import Event, Task, TaskStatus


class DomainError(Exception):
    """Base exception for domain validation errors."""

    pass


class InvalidTaskError(DomainError):
    """Raised when a task is in an invalid state."""

    pass


class InvalidEventError(DomainError):
    """Raised when an event is in an invalid state."""

    pass


class InvalidCronError(DomainError):
    """Raised when a cron expression is invalid."""

    pass


class InvalidDateError(DomainError):
    """Raised when dates are in an invalid state."""

    pass


def validate_task(task: Task) -> None:
    """Validate that a task is in a valid state.

    Args:
        task: Task to validate

    Raises:
        InvalidTaskError: If task is invalid
    """
    if not task.title or not task.title.strip():
        raise InvalidTaskError("Task title cannot be empty")

    if task.status not in TaskStatus:
        raise InvalidTaskError(f"Invalid task status: {task.status}")

    if task.priority is not None:
        if not isinstance(task.priority, int) or task.priority < 1 or task.priority > 3:
            raise InvalidTaskError("Task priority must be 1-3 if set")

    try:
        validate_dates(task.created_at, task.updated_at)
    except InvalidDateError as e:
        raise InvalidTaskError(str(e)) from e


def validate_event(event: Event) -> None:
    """Validate that an event is in a valid state.

    Args:
        event: Event to validate

    Raises:
        InvalidEventError: If event is invalid
    """
    if not event.title or not event.title.strip():
        raise InvalidEventError("Event title cannot be empty")

    # Event must have occurred in the past or present
    now = datetime.now(timezone.utc)
    if event.occurred_at > now:
        raise InvalidEventError("Event occurred_at cannot be in the future")

    validate_dates(event.created_at, event.updated_at)


def validate_dates(created_at: datetime, updated_at: datetime) -> None:
    """Validate that created_at is before or equal to updated_at.

    Args:
        created_at: Creation timestamp
        updated_at: Update timestamp

    Raises:
        InvalidDateError: If created_at > updated_at
    """
    if created_at > updated_at:
        raise InvalidDateError(
            f"created_at ({created_at}) cannot be after updated_at ({updated_at})"
        )


def validate_cron(cron_expression: str) -> None:
    """Validate that a cron expression is valid.

    Args:
        cron_expression: Cron expression string

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    try:
        croniter(cron_expression)
    except (KeyError, ValueError) as e:
        raise InvalidCronError(f"Invalid cron expression: {cron_expression}") from e
