"""Business logic operations for task recurrence."""

from dataclasses import dataclass
from datetime import datetime

import whenever
from croniter import croniter

from dot.domain.validation import validate_cron


@dataclass
class RecurrenceSettings:
    """Settings for a recurring task."""

    cron_expression: str
    next_occurrence: whenever.Instant
    last_occurrence: whenever.Instant | None = None

    def __post_init__(self) -> None:
        """Validate cron expression on initialization."""
        validate_cron(self.cron_expression)


def setup_recurrence(
    cron_expression: str, start_date: whenever.Instant | None = None
) -> RecurrenceSettings:
    """Set up a recurring pattern for a task.

    Args:
        cron_expression: Valid cron expression (e.g., "0 9 * * *" for 9am daily)
        start_date: When to start the recurrence (defaults to now)

    Returns:
        RecurrenceSettings configured with the cron pattern

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    validate_cron(cron_expression)

    if start_date is None:
        start_date = whenever.Instant.now()

    # Calculate next occurrence from the start date
    next_occ = get_next_occurrence(cron_expression, start_date)

    return RecurrenceSettings(
        cron_expression=cron_expression,
        next_occurrence=next_occ,
        last_occurrence=None,
    )


def get_next_occurrence(
    cron_expression: str, from_date: whenever.Instant | None = None
) -> whenever.Instant:
    """Calculate the next occurrence of a cron pattern.

    Args:
        cron_expression: Valid cron expression
        from_date: Reference datetime (defaults to now)

    Returns:
        The next instant when the cron pattern occurs

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    validate_cron(cron_expression)

    if from_date is None:
        from_date = whenever.Instant.now()

    # Convert whenever.Instant to naive datetime for croniter
    as_datetime = from_date.py_datetime().replace(tzinfo=None)
    cron = croniter(cron_expression, as_datetime)
    next_dt = cron.get_next(datetime)

    # Convert back to whenever.Instant
    return whenever.Instant.from_utc(
        next_dt.year,
        next_dt.month,
        next_dt.day,
        next_dt.hour,
        next_dt.minute,
        next_dt.second,
        nanosecond=next_dt.microsecond * 1000,
    )


def get_previous_occurrence(
    cron_expression: str, from_date: whenever.Instant | None = None
) -> whenever.Instant:
    """Calculate the previous occurrence of a cron pattern.

    Args:
        cron_expression: Valid cron expression
        from_date: Reference datetime (defaults to now)

    Returns:
        The previous instant when the cron pattern occurred

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    validate_cron(cron_expression)

    if from_date is None:
        from_date = whenever.Instant.now()

    # Convert whenever.Instant to naive datetime for croniter
    as_datetime = from_date.py_datetime().replace(tzinfo=None)
    cron = croniter(cron_expression, as_datetime)
    prev_dt = cron.get_prev(datetime)

    # Convert back to whenever.Instant
    return whenever.Instant.from_utc(
        prev_dt.year,
        prev_dt.month,
        prev_dt.day,
        prev_dt.hour,
        prev_dt.minute,
        prev_dt.second,
        nanosecond=prev_dt.microsecond * 1000,
    )


def generate_next_occurrences(
    cron_expression: str,
    count: int = 5,
    from_date: whenever.Instant | None = None,
) -> list[whenever.Instant]:
    """Generate multiple future occurrences of a cron pattern.

    Args:
        cron_expression: Valid cron expression
        count: Number of occurrences to generate (default: 5)
        from_date: Reference datetime (defaults to now)

    Returns:
        List of upcoming instant occurrences

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    validate_cron(cron_expression)

    if from_date is None:
        from_date = whenever.Instant.now()

    # Convert whenever.Instant to naive datetime for croniter
    as_datetime = from_date.py_datetime().replace(tzinfo=None)
    cron = croniter(cron_expression, as_datetime)

    occurrences = []
    for _ in range(count):
        next_dt = cron.get_next(datetime)
        occurrences.append(
            whenever.Instant.from_utc(
                next_dt.year,
                next_dt.month,
                next_dt.day,
                next_dt.hour,
                next_dt.minute,
                next_dt.second,
                nanosecond=next_dt.microsecond * 1000,
            )
        )

    return occurrences


def update_next_occurrence(
    settings: RecurrenceSettings,
) -> RecurrenceSettings:
    """Update recurrence settings to the next occurrence.

    Args:
        settings: Current recurrence settings

    Returns:
        Updated recurrence settings with next_occurrence moved forward

    Raises:
        InvalidCronError: If cron expression is invalid
    """
    next_occ = get_next_occurrence(settings.cron_expression, settings.next_occurrence)

    return RecurrenceSettings(
        cron_expression=settings.cron_expression,
        next_occurrence=next_occ,
        last_occurrence=settings.next_occurrence,
    )
