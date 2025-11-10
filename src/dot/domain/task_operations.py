"""Business logic operations for tasks."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone

from dot.domain.models import Task, TaskStatus
from dot.domain.validation import InvalidTaskError, validate_task


@dataclass
class TaskCreated:
    """Event: Task was created."""

    task: Task


@dataclass
class TaskCompleted:
    """Event: Task was marked as done."""

    task: Task


@dataclass
class TaskCancelled:
    """Event: Task was cancelled."""

    task: Task


@dataclass
class TaskReopened:
    """Event: Task was reopened (DONE or CANCELLED back to TODO)."""

    task: Task


@dataclass
class TaskUpdated:
    """Event: Task was updated."""

    task: Task


def create_task(
    id: int,
    title: str,
    description: str | None = None,
    priority: int | None = None,
) -> Task:
    """Create a new task.

    Args:
        id: Unique task identifier
        title: Task title
        description: Optional task description
        priority: Optional priority (1-3, where 1 is highest)

    Returns:
        A new Task instance

    Raises:
        InvalidTaskError: If task data is invalid
    """
    task = Task(
        id=id,
        title=title,
        description=description,
        priority=priority,
        status=TaskStatus.TODO,
    )
    validate_task(task)
    return task


def complete_task(task: Task) -> Task:
    """Mark a task as completed.

    Args:
        task: The task to complete

    Returns:
        Updated task with DONE status

    Raises:
        InvalidTaskError: If task cannot be completed
    """
    if task.status == TaskStatus.DONE:
        raise InvalidTaskError("Task is already completed")

    completed = replace(
        task, status=TaskStatus.DONE, updated_at=datetime.now(timezone.utc)
    )
    validate_task(completed)
    return completed


def cancel_task(task: Task) -> Task:
    """Cancel a task.

    Args:
        task: The task to cancel

    Returns:
        Updated task with CANCELLED status

    Raises:
        InvalidTaskError: If task cannot be cancelled
    """
    if task.status == TaskStatus.CANCELLED:
        raise InvalidTaskError("Task is already cancelled")

    cancelled = replace(
        task, status=TaskStatus.CANCELLED, updated_at=datetime.now(timezone.utc)
    )
    validate_task(cancelled)
    return cancelled


def reopen_task(task: Task) -> Task:
    """Reopen a completed or cancelled task.

    Args:
        task: The task to reopen

    Returns:
        Updated task with TODO status

    Raises:
        InvalidTaskError: If task is already TODO or cannot be reopened
    """
    if task.status == TaskStatus.TODO:
        raise InvalidTaskError("Task is already open (TODO status)")

    reopened = replace(
        task, status=TaskStatus.TODO, updated_at=datetime.now(timezone.utc)
    )
    validate_task(reopened)
    return reopened


def update_task(
    task: Task,
    title: str | None = None,
    description: str | None = None,
    priority: int | None = None,
) -> Task:
    """Update task attributes.

    Args:
        task: The task to update
        title: New title (if provided)
        description: New description (if provided)
        priority: New priority (if provided)

    Returns:
        Updated task

    Raises:
        InvalidTaskError: If updated task is invalid
    """
    updated = replace(
        task,
        title=title if title is not None else task.title,
        description=description if description is not None else task.description,
        priority=priority if priority is not None else task.priority,
        updated_at=datetime.now(timezone.utc),
    )
    validate_task(updated)
    return updated


def set_priority(task: Task, priority: int | None) -> Task:
    """Set or clear task priority.

    Args:
        task: The task to update
        priority: Priority level (1-3) or None to clear

    Returns:
        Updated task with new priority

    Raises:
        InvalidTaskError: If priority is invalid
    """
    updated = replace(task, priority=priority, updated_at=datetime.now(timezone.utc))
    validate_task(updated)
    return updated
