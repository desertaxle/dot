"""Tests for log operations."""

from uuid import uuid4

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
        task_id = uuid4()
        entry = LogEntry(id=uuid4(), log_id=uuid4(), task_id=task_id)
        assert entry.task_id == task_id
        assert entry.note_id is None
        assert entry.event_id is None

    def test_log_entry_with_note(self):
        """LogEntry with note_id is valid."""
        note_id = uuid4()
        entry = LogEntry(id=uuid4(), log_id=uuid4(), note_id=note_id)
        assert entry.note_id == note_id
        assert entry.task_id is None
        assert entry.event_id is None

    def test_log_entry_with_event(self):
        """LogEntry with event_id is valid."""
        event_id = uuid4()
        entry = LogEntry(id=uuid4(), log_id=uuid4(), event_id=event_id)
        assert entry.event_id == event_id
        assert entry.task_id is None
        assert entry.note_id is None

    def test_log_entry_with_multiple_raises(self):
        """LogEntry with multiple item IDs raises error."""
        with pytest.raises(ValueError, match="exactly one"):
            LogEntry(id=uuid4(), log_id=uuid4(), task_id=uuid4(), note_id=uuid4())

    def test_log_entry_with_none_raises(self):
        """LogEntry with no item IDs raises error."""
        with pytest.raises(ValueError, match="exactly one"):
            LogEntry(id=uuid4(), log_id=uuid4())


class TestCreateDailyLog:
    """Tests for create_daily_log operation."""

    def test_create_daily_log_today(self):
        """Create a daily log for today."""
        log = create_daily_log(id=uuid4(), name="Today")
        assert isinstance(log, DailyLog)
        assert log.date == today()
        assert log.name == "Today"

    def test_create_daily_log_specific_date(self):
        """Create a daily log for a specific date."""
        date = whenever.Date(2025, 1, 15)
        log = create_daily_log(id=uuid4(), name="Jan 15", date=date)
        assert log.date == date

    def test_create_daily_log_with_description(self):
        """Create a daily log with description."""
        log = create_daily_log(id=uuid4(), name="Test", description="Test log")
        assert log.description == "Test log"


class TestCreateWeeklyLog:
    """Tests for create_weekly_log operation."""

    def test_create_weekly_log_this_week(self):
        """Create a weekly log for this week."""
        log = create_weekly_log(id=uuid4(), name="This Week")
        assert isinstance(log, WeeklyLog)
        assert log.week_start.day_of_week().value == 1  # Monday

    def test_create_weekly_log_specific_week(self):
        """Create a weekly log for a specific week."""
        monday = whenever.Date(2025, 1, 6)  # A known Monday
        log = create_weekly_log(id=uuid4(), name="Week", week_start=monday)
        assert log.week_start == monday

    def test_create_weekly_log_invalid_start_raises(self):
        """Creating weekly log with non-Monday start raises error."""
        friday = whenever.Date(2025, 1, 10)  # A known Friday
        with pytest.raises(ValueError, match="Monday"):
            create_weekly_log(id=uuid4(), name="Week", week_start=friday)

    def test_weekly_log_week_end(self):
        """Weekly log has correct week_end."""
        monday = whenever.Date(2025, 1, 6)
        log = create_weekly_log(id=uuid4(), name="Week", week_start=monday)
        assert log.week_end == whenever.Date(2025, 1, 12)  # Sunday


class TestCreateMonthlyLog:
    """Tests for create_monthly_log operation."""

    def test_create_monthly_log_current_month(self):
        """Create a monthly log for current month."""
        log = create_monthly_log(id=uuid4(), name="This Month")
        assert isinstance(log, MonthlyLog)
        today_date = today()
        assert log.year == today_date.year
        assert log.month == today_date.month

    def test_create_monthly_log_specific_month(self):
        """Create a monthly log for a specific month."""
        log = create_monthly_log(id=uuid4(), name="Jan 2025", year=2025, month=1)
        assert log.year == 2025
        assert log.month == 1

    def test_create_monthly_log_invalid_month_raises(self):
        """Creating monthly log with invalid month raises error."""
        with pytest.raises(ValueError, match="Month must be 1-12"):
            create_monthly_log(id=uuid4(), name="Bad", year=2025, month=13)

    def test_monthly_log_date_boundaries(self):
        """Monthly log has correct date boundaries."""
        log = create_monthly_log(id=uuid4(), name="Jan 2025", year=2025, month=1)
        assert log.start_date == whenever.Date(2025, 1, 1)
        assert log.end_date == whenever.Date(2025, 1, 31)

    def test_monthly_log_february_leap_year(self):
        """Monthly log handles February in leap year."""
        log = create_monthly_log(id=uuid4(), name="Feb 2024", year=2024, month=2)
        assert log.end_date == whenever.Date(2024, 2, 29)

    def test_monthly_log_december(self):
        """Monthly log handles December correctly."""
        log = create_monthly_log(id=uuid4(), name="Dec 2025", year=2025, month=12)
        assert log.start_date == whenever.Date(2025, 12, 1)
        assert log.end_date == whenever.Date(2025, 12, 31)


class TestAddToLog:
    """Tests for adding items to logs."""

    def test_add_task_to_log(self):
        """Add a task to a log."""
        task_id = uuid4()
        log_id = uuid4()
        entry = add_task_to_log(log_entry_id=uuid4(), log_id=log_id, task_id=task_id)
        assert entry.task_id == task_id
        assert entry.log_id == log_id
        assert entry.entry_date == today()

    def test_add_task_to_log_specific_date(self):
        """Add a task to a log for a specific date."""
        date = whenever.Date(2025, 1, 15)
        entry = add_task_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), task_id=uuid4(), entry_date=date
        )
        assert entry.entry_date == date

    def test_add_note_to_log(self):
        """Add a note to a log."""
        note_id = uuid4()
        log_id = uuid4()
        entry = add_note_to_log(log_entry_id=uuid4(), log_id=log_id, note_id=note_id)
        assert entry.note_id == note_id
        assert entry.log_id == log_id

    def test_add_event_to_log(self):
        """Add an event to a log."""
        event_id = uuid4()
        log_id = uuid4()
        entry = add_event_to_log(log_entry_id=uuid4(), log_id=log_id, event_id=event_id)
        assert entry.event_id == event_id
        assert entry.log_id == log_id

    def test_add_note_to_log_specific_date(self):
        """Add a note to a log with specific date."""
        date = whenever.Date(2025, 1, 15)
        note_id = uuid4()
        entry = add_note_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), note_id=note_id, entry_date=date
        )
        assert entry.note_id == note_id
        assert entry.entry_date == date

    def test_add_event_to_log_specific_date(self):
        """Add an event to a log with specific date."""
        date = whenever.Date(2025, 1, 15)
        event_id = uuid4()
        entry = add_event_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), event_id=event_id, entry_date=date
        )
        assert entry.event_id == event_id
        assert entry.entry_date == date

    def test_log_entries_are_unique(self):
        """Multiple log entries can have different items."""
        task_id = uuid4()
        note_id = uuid4()
        event_id = uuid4()
        task_entry = add_task_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), task_id=task_id
        )
        note_entry = add_note_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), note_id=note_id
        )
        event_entry = add_event_to_log(
            log_entry_id=uuid4(), log_id=uuid4(), event_id=event_id
        )

        assert task_entry.task_id == task_id
        assert note_entry.note_id == note_id
        assert event_entry.event_id == event_id


class TestMigrateTask:
    """Tests for task migration."""

    def test_migrate_task(self):
        """Migrate a task from one log to another."""
        task_id = uuid4()
        from_entry_id = uuid4()
        to_entry_id = uuid4()
        migration = migrate_task(
            migration_id=uuid4(),
            task_id=task_id,
            from_log_entry_id=from_entry_id,
            to_log_entry_id=to_entry_id,
        )
        assert migration.task_id == task_id
        assert migration.from_log_entry_id == from_entry_id
        assert migration.to_log_entry_id == to_entry_id
        assert migration.migrated_at is not None

    def test_multiple_migrations(self):
        """Can record multiple migrations."""
        task_id = uuid4()
        entry_10 = uuid4()
        entry_20 = uuid4()
        entry_30 = uuid4()
        mig1 = migrate_task(uuid4(), task_id, entry_10, entry_20)
        mig2 = migrate_task(uuid4(), task_id, entry_20, entry_30)

        assert mig1.from_log_entry_id == entry_10
        assert mig2.from_log_entry_id == entry_20
        assert mig1.to_log_entry_id == mig2.from_log_entry_id
