"""Business logic operations for logs and log entries."""

from dataclasses import dataclass, field
from uuid import UUID

import whenever

from dot.domain.date_helpers import get_week_start
from dot.domain.models import DailyLog, MonthlyLog, WeeklyLog


@dataclass
class LogEntry:
    """A reference to an entry (task, note, or event) in a log."""

    log_id: UUID
    id: UUID | None = None
    task_id: UUID | None = None
    note_id: UUID | None = None
    event_id: UUID | None = None
    entry_date: whenever.Date = field(
        default_factory=lambda: whenever.Instant.now().to_system_tz().date()
    )

    def __post_init__(self) -> None:
        """Validate that exactly one of task/note/event is set."""
        count = sum(
            [
                self.task_id is not None,
                self.note_id is not None,
                self.event_id is not None,
            ]
        )
        if count != 1:
            raise ValueError(
                "LogEntry must have exactly one of: task_id, note_id, event_id"
            )


@dataclass
class Migration:
    """Record of a task being migrated from one log to another."""

    id: UUID
    task_id: UUID
    from_log_entry_id: UUID
    to_log_entry_id: UUID
    migrated_at: whenever.Instant = field(default_factory=whenever.Instant.now)


def create_daily_log(
    id: UUID,
    name: str,
    date: whenever.Date | None = None,
    description: str | None = None,
) -> DailyLog:
    """Create a daily log for a specific date.

    Args:
        id: Unique log identifier
        name: Log name
        date: Date for the log (defaults to today)
        description: Optional description

    Returns:
        A new DailyLog instance
    """
    if date is None:
        date = whenever.Instant.now().to_system_tz().date()

    return DailyLog(id=id, name=name, description=description, date=date)


def create_weekly_log(
    id: UUID,
    name: str,
    week_start: whenever.Date | None = None,
    description: str | None = None,
) -> WeeklyLog:
    """Create a weekly log for a week.

    Args:
        id: Unique log identifier
        name: Log name
        week_start: First day of the week (Monday, defaults to this week)
        description: Optional description

    Returns:
        A new WeeklyLog instance
    """
    if week_start is None:
        week_start = get_week_start(whenever.Instant.now().to_system_tz().date())
    elif week_start.day_of_week().value != 1:  # Monday is 1
        raise ValueError(f"week_start must be a Monday, got {week_start.day_of_week()}")

    return WeeklyLog(id=id, name=name, description=description, week_start=week_start)


def create_monthly_log(
    id: UUID,
    name: str,
    year: int | None = None,
    month: int | None = None,
    description: str | None = None,
) -> MonthlyLog:
    """Create a monthly log for a month.

    Args:
        id: Unique log identifier
        name: Log name
        year: Year (defaults to current year)
        month: Month 1-12 (defaults to current month)
        description: Optional description

    Returns:
        A new MonthlyLog instance

    Raises:
        ValueError: If month is not 1-12
    """
    today = whenever.Instant.now().to_system_tz().date()

    if year is None:
        year = today.year
    if month is None:
        month = today.month

    return MonthlyLog(id=id, name=name, description=description, year=year, month=month)


def add_task_to_log(
    log_entry_id: UUID,
    log_id: UUID,
    task_id: UUID,
    entry_date: whenever.Date | None = None,
) -> LogEntry:
    """Add a task to a log.

    Args:
        log_entry_id: Unique identifier for this log entry
        log_id: The log to add the task to
        task_id: The task to add
        entry_date: Date the task appears in the log (defaults to today)

    Returns:
        A LogEntry linking the task to the log
    """
    if entry_date is None:
        entry_date = whenever.Instant.now().to_system_tz().date()

    return LogEntry(
        id=log_entry_id,
        log_id=log_id,
        task_id=task_id,
        entry_date=entry_date,
    )


def add_note_to_log(
    log_entry_id: UUID,
    log_id: UUID,
    note_id: UUID,
    entry_date: whenever.Date | None = None,
) -> LogEntry:
    """Add a note to a log.

    Args:
        log_entry_id: Unique identifier for this log entry
        log_id: The log to add the note to
        note_id: The note to add
        entry_date: Date the note appears in the log (defaults to today)

    Returns:
        A LogEntry linking the note to the log
    """
    if entry_date is None:
        entry_date = whenever.Instant.now().to_system_tz().date()

    return LogEntry(
        id=log_entry_id,
        log_id=log_id,
        note_id=note_id,
        entry_date=entry_date,
    )


def add_event_to_log(
    log_entry_id: UUID,
    log_id: UUID,
    event_id: UUID,
    entry_date: whenever.Date | None = None,
) -> LogEntry:
    """Add an event to a log.

    Args:
        log_entry_id: Unique identifier for this log entry
        log_id: The log to add the event to
        event_id: The event to add
        entry_date: Date the event appears in the log (defaults to today)

    Returns:
        A LogEntry linking the event to the log
    """
    if entry_date is None:
        entry_date = whenever.Instant.now().to_system_tz().date()

    return LogEntry(
        id=log_entry_id,
        log_id=log_id,
        event_id=event_id,
        entry_date=entry_date,
    )


def migrate_task(
    migration_id: UUID,
    task_id: UUID,
    from_log_entry_id: UUID,
    to_log_entry_id: UUID,
) -> Migration:
    """Record a task migration from one log to another.

    Args:
        migration_id: Unique identifier for this migration
        task_id: The task being migrated
        from_log_entry_id: The log entry it's migrated from
        to_log_entry_id: The log entry it's migrated to

    Returns:
        A Migration record
    """
    return Migration(
        id=migration_id,
        task_id=task_id,
        from_log_entry_id=from_log_entry_id,
        to_log_entry_id=to_log_entry_id,
    )
