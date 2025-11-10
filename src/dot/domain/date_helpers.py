"""Date and time helper functions using the whenever library."""

import whenever


def today() -> whenever.Date:
    """Get today's date.

    Returns:
        Today's date
    """
    return whenever.Instant.now().to_system_tz().date()


def get_week_start(date: whenever.Date) -> whenever.Date:
    """Get the first day of the week (Monday) for a given date.

    Args:
        date: The date to get the week start for

    Returns:
        The Monday of the week containing the given date
    """
    # day_of_week().value: Monday=1, ..., Sunday=7
    days_since_monday = date.day_of_week().value - 1
    return date.subtract(days=days_since_monday)


def get_week_end(date: whenever.Date) -> whenever.Date:
    """Get the last day of the week (Sunday) for a given date.

    Args:
        date: The date to get the week end for

    Returns:
        The Sunday of the week containing the given date
    """
    week_start = get_week_start(date)
    return week_start.add(days=6)


def get_month_start(year: int, month: int) -> whenever.Date:
    """Get the first day of a specific month.

    Args:
        year: The year
        month: The month (1-12)

    Returns:
        The first day of the specified month
    """
    return whenever.Date(year, month, 1)


def get_month_end(year: int, month: int) -> whenever.Date:
    """Get the last day of a specific month.

    Args:
        year: The year
        month: The month (1-12)

    Returns:
        The last day of the specified month
    """
    if month == 12:
        next_month = whenever.Date(year + 1, 1, 1)
    else:
        next_month = whenever.Date(year, month + 1, 1)
    return next_month.subtract(days=1)


def is_past_date(date: whenever.Date) -> bool:
    """Check if a date is in the past.

    Args:
        date: The date to check

    Returns:
        True if the date is before today, False otherwise
    """
    return date < today()


def is_future_date(date: whenever.Date) -> bool:
    """Check if a date is in the future.

    Args:
        date: The date to check

    Returns:
        True if the date is after today, False otherwise
    """
    return date > today()


def is_today_date(date: whenever.Date) -> bool:
    """Check if a date is today.

    Args:
        date: The date to check

    Returns:
        True if the date is today, False otherwise
    """
    return date == today()
