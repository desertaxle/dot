"""Tests for log operations."""

import pytest
import whenever

from dot.domain.date_helpers import today
from dot.domain.log_operations import (
    LogEntry,
    add_event_to_log,
    add_note_to_log,
    add_task_to_log,
    create_daily_log,
    create_monthly_log,
    create_weekly_log,
    migrate_task,
)
from dot.domain.models import DailyLog, MonthlyLog, WeeklyLog


class TestLogEntryValidation:
    """Tests for LogEntry validation."""

    def test_log_entry_with_task(self):
        """LogEntry with task_id is valid."""
        entry = LogEntry(id=1, log_id=1, task_id=5)
        assert entry.task_id == 5
        assert entry.note_id is None
        assert entry.event_id is None

    def test_log_entry_with_note(self):
        """LogEntry with note_id is valid."""
        entry = LogEntry(id=1, log_id=1, note_id=5)
        assert entry.note_id == 5
        assert entry.task_id is None
        assert entry.event_id is None

    def test_log_entry_with_event(self):
        """LogEntry with event_id is valid."""
        entry = LogEntry(id=1, log_id=1, event_id=5)
        assert entry.event_id == 5
        assert entry.task_id is None
        assert entry.note_id is None

    def test_log_entry_with_multiple_raises(self):
        """LogEntry with multiple item IDs raises error."""
        with pytest.raises(ValueError, match="exactly one"):
            LogEntry(id=1, log_id=1, task_id=5, note_id=5)

    def test_log_entry_with_none_raises(self):
        """LogEntry with no item IDs raises error."""
        with pytest.raises(ValueError, match="exactly one"):
            LogEntry(id=1, log_id=1)


class TestCreateDailyLog:
    """Tests for create_daily_log operation."""

    def test_create_daily_log_today(self):
        """Create a daily log for today."""
        log = create_daily_log(id=1, name="Today")
        assert isinstance(log, DailyLog)
        assert log.date == today()
        assert log.name == "Today"

    def test_create_daily_log_specific_date(self):
        """Create a daily log for a specific date."""
        date = whenever.Date(2025, 1, 15)
        log = create_daily_log(id=1, name="Jan 15", date=date)
        assert log.date == date

    def test_create_daily_log_with_description(self):
        """Create a daily log with description."""
        log = create_daily_log(id=1, name="Test", description="Test log")
        assert log.description == "Test log"


class TestCreateWeeklyLog:
    """Tests for create_weekly_log operation."""

    def test_create_weekly_log_this_week(self):
        """Create a weekly log for this week."""
        log = create_weekly_log(id=1, name="This Week")
        assert isinstance(log, WeeklyLog)
        assert log.week_start.day_of_week().value == 1  # Monday

    def test_create_weekly_log_specific_week(self):
        """Create a weekly log for a specific week."""
        monday = whenever.Date(2025, 1, 6)  # A known Monday
        log = create_weekly_log(id=1, name="Week", week_start=monday)
        assert log.week_start == monday

    def test_create_weekly_log_invalid_start_raises(self):
        """Creating weekly log with non-Monday start raises error."""
        friday = whenever.Date(2025, 1, 10)  # A known Friday
        with pytest.raises(ValueError, match="Monday"):
            create_weekly_log(id=1, name="Week", week_start=friday)

    def test_weekly_log_week_end(self):
        """Weekly log has correct week_end."""
        monday = whenever.Date(2025, 1, 6)
        log = create_weekly_log(id=1, name="Week", week_start=monday)
        assert log.week_end == whenever.Date(2025, 1, 12)  # Sunday


class TestCreateMonthlyLog:
    """Tests for create_monthly_log operation."""

    def test_create_monthly_log_current_month(self):
        """Create a monthly log for current month."""
        log = create_monthly_log(id=1, name="This Month")
        assert isinstance(log, MonthlyLog)
        today_date = today()
        assert log.year == today_date.year
        assert log.month == today_date.month

    def test_create_monthly_log_specific_month(self):
        """Create a monthly log for a specific month."""
        log = create_monthly_log(id=1, name="Jan 2025", year=2025, month=1)
        assert log.year == 2025
        assert log.month == 1

    def test_create_monthly_log_invalid_month_raises(self):
        """Creating monthly log with invalid month raises error."""
        with pytest.raises(ValueError, match="Month must be 1-12"):
            create_monthly_log(id=1, name="Bad", year=2025, month=13)

    def test_monthly_log_date_boundaries(self):
        """Monthly log has correct date boundaries."""
        log = create_monthly_log(id=1, name="Jan 2025", year=2025, month=1)
        assert log.start_date == whenever.Date(2025, 1, 1)
        assert log.end_date == whenever.Date(2025, 1, 31)

    def test_monthly_log_february_leap_year(self):
        """Monthly log handles February in leap year."""
        log = create_monthly_log(id=1, name="Feb 2024", year=2024, month=2)
        assert log.end_date == whenever.Date(2024, 2, 29)

    def test_monthly_log_december(self):
        """Monthly log handles December correctly."""
        log = create_monthly_log(id=1, name="Dec 2025", year=2025, month=12)
        assert log.start_date == whenever.Date(2025, 12, 1)
        assert log.end_date == whenever.Date(2025, 12, 31)


class TestAddToLog:
    """Tests for adding items to logs."""

    def test_add_task_to_log(self):
        """Add a task to a log."""
        entry = add_task_to_log(log_entry_id=1, log_id=1, task_id=5)
        assert entry.task_id == 5
        assert entry.log_id == 1
        assert entry.entry_date == today()

    def test_add_task_to_log_specific_date(self):
        """Add a task to a log for a specific date."""
        date = whenever.Date(2025, 1, 15)
        entry = add_task_to_log(log_entry_id=1, log_id=1, task_id=5, entry_date=date)
        assert entry.entry_date == date

    def test_add_note_to_log(self):
        """Add a note to a log."""
        entry = add_note_to_log(log_entry_id=1, log_id=1, note_id=5)
        assert entry.note_id == 5
        assert entry.log_id == 1

    def test_add_event_to_log(self):
        """Add an event to a log."""
        entry = add_event_to_log(log_entry_id=1, log_id=1, event_id=5)
        assert entry.event_id == 5
        assert entry.log_id == 1

    def test_log_entries_are_unique(self):
        """Multiple log entries can have different items."""
        task_entry = add_task_to_log(log_entry_id=1, log_id=1, task_id=5)
        note_entry = add_note_to_log(log_entry_id=2, log_id=1, note_id=5)
        event_entry = add_event_to_log(log_entry_id=3, log_id=1, event_id=5)

        assert task_entry.task_id == 5
        assert note_entry.note_id == 5
        assert event_entry.event_id == 5


class TestMigrateTask:
    """Tests for task migration."""

    def test_migrate_task(self):
        """Migrate a task from one log to another."""
        migration = migrate_task(
            migration_id=1,
            task_id=5,
            from_log_entry_id=10,
            to_log_entry_id=20,
        )
        assert migration.task_id == 5
        assert migration.from_log_entry_id == 10
        assert migration.to_log_entry_id == 20
        assert migration.migrated_at is not None

    def test_multiple_migrations(self):
        """Can record multiple migrations."""
        mig1 = migrate_task(1, 5, 10, 20)
        mig2 = migrate_task(2, 5, 20, 30)

        assert mig1.from_log_entry_id == 10
        assert mig2.from_log_entry_id == 20
        assert mig1.to_log_entry_id == mig2.from_log_entry_id
