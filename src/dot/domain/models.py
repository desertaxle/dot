"""Pure domain models for the bullet journal application."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class TaskStatus(str, Enum):
    """Status of a task."""

    TODO = "TODO"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Task:
    """A task in the bullet journal.

    Tasks are immutable - any state changes create a new Task instance.
    """

    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
