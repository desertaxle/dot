"""Pure business logic functions for domain operations."""

from dataclasses import replace
from datetime import date, datetime
from uuid import uuid4

from dot.domain.models import DailyLogEntry, Event, Note, Task, TaskStatus


def create_task(title: str, description: str | None = None) -> Task:
    """Create a new task with validation.

    Args:
        title: Task title (required)
        description: Optional detailed description

    Returns:
        New Task instance

    Raises:
        ValueError: If validation fails
    """
    # Validate title
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 500:
        raise ValueError("Title cannot exceed 500 characters")

    # Validate description
    if description is not None and len(description) > 5000:
        raise ValueError("Description cannot exceed 5000 characters")

    now = datetime.utcnow()

    return Task(
        id=uuid4(),
        title=title,
        description=description,
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )


def mark_done(task: Task) -> Task:
    """Mark a task as done.

    Args:
        task: The task to mark as done

    Returns:
        New Task instance with DONE status
    """
    return replace(task, status=TaskStatus.DONE, updated_at=datetime.utcnow())


def mark_cancelled(task: Task) -> Task:
    """Mark a task as cancelled.

    Args:
        task: The task to mark as cancelled

    Returns:
        New Task instance with CANCELLED status
    """
    return replace(task, status=TaskStatus.CANCELLED, updated_at=datetime.utcnow())


def reopen_task(task: Task) -> Task:
    """Reopen a done or cancelled task.

    Args:
        task: The task to reopen

    Returns:
        New Task instance with TODO status
    """
    return replace(task, status=TaskStatus.TODO, updated_at=datetime.utcnow())


def create_event(
    title: str,
    description: str | None = None,
    occurred_at: datetime | None = None,
) -> Event:
    """Create a new event with validation.

    Args:
        title: Event title (required)
        description: Optional detailed description
        occurred_at: When the event occurred (defaults to now)

    Returns:
        New Event instance

    Raises:
        ValueError: If validation fails
    """
    # Validate title
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 500:
        raise ValueError("Title cannot exceed 500 characters")

    # Validate description
    if description is not None and len(description) > 5000:
        raise ValueError("Description cannot exceed 5000 characters")

    now = datetime.utcnow()

    return Event(
        id=uuid4(),
        title=title,
        description=description,
        occurred_at=occurred_at if occurred_at is not None else now,
        created_at=now,
    )


def create_note(title: str, content: str) -> "Note":
    """Create a new note with validation.

    Args:
        title: Note title (required)
        content: Note content (can be empty)

    Returns:
        New Note instance

    Raises:
        ValueError: If validation fails
    """
    from datetime import datetime
    from uuid import uuid4

    from dot.domain.models import Note

    # Validate title
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")

    if len(title) > 500:
        raise ValueError("Title cannot exceed 500 characters")

    # Validate content length
    if len(content) > 100000:
        raise ValueError("Content cannot exceed 100000 characters")

    now = datetime.utcnow()

    return Note(
        id=uuid4(),
        title=title,
        content=content,
        created_at=now,
    )


def build_daily_log(
    tasks: list[Task],
    events: list[Event],
    notes: list[Note],
    target_date: date,
) -> DailyLogEntry:
    """Build a daily log entry for a specific date.

    Args:
        tasks: List of tasks to include (pre-filtered by the caller)
        events: List of events to include (pre-filtered by the caller)
        notes: List of notes to include (pre-filtered by the caller)
        target_date: The date for this log entry

    Returns:
        A DailyLogEntry containing all provided items for the target date

    Note:
        This function does NOT filter by date - it assumes the caller has already
        filtered the items appropriately. This keeps the domain logic pure.
    """
    return DailyLogEntry(
        date=target_date,
        tasks=tasks,
        events=events,
        notes=notes,
    )
