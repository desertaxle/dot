"""Tests for date helper functions."""

import whenever

from dot.domain.date_helpers import (
    get_month_end,
    get_month_start,
    get_week_end,
    get_week_start,
    is_future_date,
    is_past_date,
    is_today_date,
    today,
)


class TestWeekHelpers:
    """Tests for week-related date helpers."""

    def test_get_week_start_returns_monday(self):
        """Week start returns Monday of the week."""
        # Use a known Friday
        friday = whenever.Date(2025, 1, 10)
        monday = get_week_start(friday)
        assert monday.day_of_week().value == 1  # Monday
        assert monday == whenever.Date(2025, 1, 6)

    def test_get_week_start_monday_returns_same_day(self):
        """Week start on Monday returns the same Monday."""
        monday = whenever.Date(2025, 1, 6)
        assert get_week_start(monday) == monday

    def test_get_week_end_returns_sunday(self):
        """Week end returns Sunday of the week."""
        friday = whenever.Date(2025, 1, 10)
        sunday = get_week_end(friday)
        assert sunday.day_of_week().value == 7  # Sunday
        assert sunday == whenever.Date(2025, 1, 12)

    def test_get_week_end_sunday_returns_same_day(self):
        """Week end on Sunday returns the same Sunday."""
        sunday = whenever.Date(2025, 1, 12)
        assert get_week_end(sunday) == sunday

    def test_week_start_and_end_span_7_days(self):
        """Week start and end are exactly 6 days apart."""
        date = whenever.Date(2025, 1, 10)
        start = get_week_start(date)
        end = get_week_end(date)
        assert (end - start).in_months_days()[1] == 6


class TestMonthHelpers:
    """Tests for month-related date helpers."""

    def test_get_month_start_january(self):
        """January month start is Jan 1."""
        start = get_month_start(2025, 1)
        assert start == whenever.Date(2025, 1, 1)

    def test_get_month_end_january(self):
        """January month end is Jan 31."""
        end = get_month_end(2025, 1)
        assert end == whenever.Date(2025, 1, 31)

    def test_get_month_end_february_leap_year(self):
        """February in leap year ends on 29th."""
        end = get_month_end(2024, 2)
        assert end == whenever.Date(2024, 2, 29)

    def test_get_month_end_february_non_leap_year(self):
        """February in non-leap year ends on 28th."""
        end = get_month_end(2025, 2)
        assert end == whenever.Date(2025, 2, 28)

    def test_get_month_end_december(self):
        """December month end is Dec 31."""
        end = get_month_end(2025, 12)
        assert end == whenever.Date(2025, 12, 31)

    def test_month_boundaries_span_correct_days(self):
        """Month start and end span the correct number of days."""
        start = get_month_start(2025, 1)
        end = get_month_end(2025, 1)
        assert (end - start).in_months_days()[1] == 30  # Jan has 31 days (0-based)


class TestDateComparison:
    """Tests for date comparison helpers."""

    def test_is_today_with_today(self):
        """is_today_date returns True for today."""
        assert is_today_date(today())

    def test_is_today_with_yesterday(self):
        """is_today_date returns False for yesterday."""
        yesterday = today().subtract(days=1)
        assert not is_today_date(yesterday)

    def test_is_today_with_tomorrow(self):
        """is_today_date returns False for tomorrow."""
        tomorrow = today().add(days=1)
        assert not is_today_date(tomorrow)

    def test_is_past_date_with_yesterday(self):
        """is_past_date returns True for yesterday."""
        yesterday = today().subtract(days=1)
        assert is_past_date(yesterday)

    def test_is_past_date_with_today(self):
        """is_past_date returns False for today."""
        assert not is_past_date(today())

    def test_is_past_date_with_tomorrow(self):
        """is_past_date returns False for tomorrow."""
        tomorrow = today().add(days=1)
        assert not is_past_date(tomorrow)

    def test_is_future_date_with_tomorrow(self):
        """is_future_date returns True for tomorrow."""
        tomorrow = today().add(days=1)
        assert is_future_date(tomorrow)

    def test_is_future_date_with_today(self):
        """is_future_date returns False for today."""
        assert not is_future_date(today())

    def test_is_future_date_with_yesterday(self):
        """is_future_date returns False for yesterday."""
        yesterday = today().subtract(days=1)
        assert not is_future_date(yesterday)
