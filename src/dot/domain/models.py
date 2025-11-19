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


@dataclass(frozen=True)
class Event:
    """An event in the bullet journal.

    Events are immutable and represent things that happened or will happen.
    """

    id: UUID
    title: str
    description: str | None
    occurred_at: datetime
    created_at: datetime
