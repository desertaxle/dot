"""Tests for recurrence operations."""

import pytest
import whenever

from dot.domain.recurrence_operations import (
    generate_next_occurrences,
    get_next_occurrence,
    get_previous_occurrence,
    setup_recurrence,
    update_next_occurrence,
)
from dot.domain.validation import InvalidCronError


class TestSetupRecurrence:
    """Tests for setup_recurrence operation."""

    def test_setup_daily_recurrence(self):
        """Set up a daily recurring pattern."""
        settings = setup_recurrence("0 9 * * *")
        assert settings.cron_expression == "0 9 * * *"
        assert settings.next_occurrence is not None
        assert settings.last_occurrence is None

    def test_setup_weekly_recurrence(self):
        """Set up a weekly recurring pattern."""
        settings = setup_recurrence("0 9 * * MON")
        assert settings.cron_expression == "0 9 * * MON"
        assert settings.next_occurrence is not None

    def test_setup_with_start_date(self):
        """Set up recurrence with custom start date."""
        start = whenever.Instant.now().add(seconds=5 * 86400)  # 5 days in seconds
        settings = setup_recurrence("0 9 * * *", start)
        assert settings.next_occurrence >= start

    def test_setup_invalid_cron_raises(self):
        """Setting up with invalid cron raises error."""
        with pytest.raises(InvalidCronError):
            setup_recurrence("not a cron")


class TestGetNextOccurrence:
    """Tests for get_next_occurrence operation."""

    def test_get_next_daily_9am(self):
        """Get next occurrence of 9am daily."""
        now = whenever.Instant.now()
        next_occ = get_next_occurrence("0 9 * * *")
        # Next occurrence should be tomorrow at 9am or today if before 9am
        assert next_occ > now

    def test_get_next_with_explicit_start(self):
        """Get next occurrence from a specific start date."""
        start = whenever.Instant.now()
        next_occ = get_next_occurrence("0 9 * * *", start)
        # Next should be after start
        assert next_occ >= start

    def test_get_next_occurrence_monday(self):
        """Get next Monday in UTC."""
        next_monday = get_next_occurrence("0 0 * * MON")
        # Convert to a fixed offset to get UTC date
        utc_date = next_monday.to_fixed_offset(0).date()
        assert utc_date.day_of_week().value == 1  # Monday

    def test_get_previous_occurrence(self):
        """Get previous occurrence."""
        now = whenever.Instant.now()
        prev_occ = get_previous_occurrence("0 9 * * *")
        assert prev_occ < now

    def test_get_previous_occurrence_with_explicit_date(self):
        """Get previous occurrence from an explicit date."""
        start = whenever.Instant.now().add(seconds=86400 * 5)
        prev_occ = get_previous_occurrence("0 9 * * *", start)
        assert prev_occ < start


class TestGenerateNextOccurrences:
    """Tests for generate_next_occurrences operation."""

    def test_generate_5_daily_occurrences(self):
        """Generate 5 daily occurrences."""
        occurrences = generate_next_occurrences("0 9 * * *", count=5)
        assert len(occurrences) == 5
        # Each should be later than previous
        for i in range(1, len(occurrences)):
            assert occurrences[i] > occurrences[i - 1]

    def test_generate_occurrences_with_count(self):
        """Generate specified number of occurrences."""
        occurrences = generate_next_occurrences("0 9 * * *", count=10)
        assert len(occurrences) == 10

    def test_generate_occurrences_from_start_date(self):
        """Generate occurrences from a specific start date."""
        start = whenever.Instant.now().add(seconds=86400)  # 1 day in seconds
        occurrences = generate_next_occurrences("0 9 * * *", count=3, from_date=start)
        assert len(occurrences) == 3
        assert all(occ >= start for occ in occurrences)

    def test_generate_weekly_occurrences(self):
        """Generate weekly occurrences."""
        occurrences = generate_next_occurrences("0 9 * * MON", count=5)
        assert len(occurrences) == 5
        # Each should be a Monday
        for occ in occurrences:
            assert occ.to_system_tz().date().day_of_week().value == 1

    def test_occurrences_are_in_order(self):
        """Generated occurrences are in chronological order."""
        occurrences = generate_next_occurrences("0 9 * * *", count=10)
        for i in range(len(occurrences) - 1):
            assert occurrences[i] < occurrences[i + 1]


class TestUpdateNextOccurrence:
    """Tests for update_next_occurrence operation."""

    def test_update_moves_to_next(self):
        """Updating recurrence moves to next occurrence."""
        settings = setup_recurrence("0 9 * * *")
        original_next = settings.next_occurrence

        updated = update_next_occurrence(settings)
        assert updated.next_occurrence > original_next

    def test_update_sets_last_occurrence(self):
        """Updating recurrence sets last_occurrence."""
        settings = setup_recurrence("0 9 * * *")
        updated = update_next_occurrence(settings)
        assert updated.last_occurrence == settings.next_occurrence

    def test_consecutive_updates(self):
        """Can update multiple times consecutively."""
        settings = setup_recurrence("0 9 * * *")
        updated1 = update_next_occurrence(settings)
        updated2 = update_next_occurrence(updated1)
        updated3 = update_next_occurrence(updated2)

        assert updated1.next_occurrence < updated2.next_occurrence
        assert updated2.next_occurrence < updated3.next_occurrence


class TestRecurrencePatterns:
    """Tests for various recurrence patterns."""

    def test_daily_pattern(self):
        """Daily recurrence pattern works."""
        occ = generate_next_occurrences("0 9 * * *", count=3)
        assert len(occ) == 3

    def test_every_other_day_pattern(self):
        """Every-other-day pattern works."""
        occ = generate_next_occurrences("0 9 */2 * *", count=3)
        assert len(occ) == 3

    def test_weekday_pattern(self):
        """Weekday-only pattern works."""
        occ = generate_next_occurrences("0 9 * * 1-5", count=5)
        assert len(occ) == 5
        # All should be weekdays (1-5 = Mon-Fri in whenever)
        for occurrence in occ:
            assert 1 <= occurrence.to_system_tz().date().day_of_week().value <= 5

    def test_monthly_pattern(self):
        """Monthly pattern works."""
        occ = generate_next_occurrences("0 9 1 * *", count=3)
        assert len(occ) == 3
        # All should be on the 1st of the month
        for occurrence in occ:
            assert occurrence.to_system_tz().date().day == 1
