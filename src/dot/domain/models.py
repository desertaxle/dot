"""Pure domain models - database-agnostic business entities."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    """Status options for tasks."""

    TODO = "todo"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A task or todo item - pure domain model."""

    id: int
    title: str
    status: TaskStatus = TaskStatus.TODO
    description: Optional[str] = None
    priority: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Note:
    """A note or information entry - pure domain model."""

    id: int
    title: str
    content: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Event:
    """An event that happened - pure domain model."""

    id: int
    title: str
    occurred_at: datetime
    content: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
