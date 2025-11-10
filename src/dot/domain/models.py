"""Pure domain models - database-agnostic business entities."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import whenever


def _get_week_start_default() -> whenever.Date:
    """Get the start of the current week (Monday).

    Helper function for WeeklyLog default factory.
    """
    today = whenever.Instant.now().to_system_tz().date()
    # day_of_week().value: Monday=1, ..., Sunday=7
    days_since_monday = today.day_of_week().value - 1
    return today.subtract(days=days_since_monday)


def _get_current_year_month() -> tuple[int, int]:
    """Get the current year and month.

    Helper function for MonthlyLog default factory.
    """
    today = whenever.Instant.now().to_system_tz().date()
    return today.year, today.month


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


@dataclass
class Project:
    """A project or container for log entries - pure domain model."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DailyLog(Project):
    """A daily log for a specific date - pure domain model."""

    date: whenever.Date = field(
        default_factory=lambda: whenever.Instant.now().to_system_tz().date()
    )


@dataclass
class WeeklyLog(Project):
    """A weekly log for a specific week - pure domain model."""

    week_start: whenever.Date = field(default_factory=lambda: _get_week_start_default())

    @property
    def week_end(self) -> whenever.Date:
        """Get the last day of the week."""
        return self.week_start.add(days=6)


@dataclass
class MonthlyLog(Project):
    """A monthly log for a specific month - pure domain model."""

    year: int = field(default_factory=lambda: _get_current_year_month()[0])
    month: int = field(default_factory=lambda: _get_current_year_month()[1])

    def __post_init__(self) -> None:
        """Validate month is in valid range."""
        if not (1 <= self.month <= 12):
            msg = f"Month must be 1-12, got {self.month}"
            raise ValueError(msg)

    @property
    def start_date(self) -> whenever.Date:
        """Get the first day of the month."""
        return whenever.Date(self.year, self.month, 1)

    @property
    def end_date(self) -> whenever.Date:
        """Get the last day of the month."""
        # Get first day of next month, then subtract 1 day
        if self.month == 12:
            next_month_start = whenever.Date(self.year + 1, 1, 1)
        else:
            next_month_start = whenever.Date(self.year, self.month + 1, 1)
        return next_month_start.subtract(days=1)
