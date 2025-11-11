"""Tests for SQLAlchemy ORM model __repr__ methods."""

from datetime import date, datetime, timezone


from dot.models import (
    Event,
    LogEntry,
    Migration,
    Note,
    Project,
    ProjectType,
    Tag,
    Task,
    TaskRecurrence,
    TaskStatus,
)


class TestProjectRepr:
    """Test Project __repr__ method."""

    def test_project_repr_format(self):
        """Test that Project repr has correct format."""
        project = Project(
            id=1,
            name="Test Project",
            type=ProjectType.PROJECT,
        )
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "id=1" in repr_str
        assert "Test Project" in repr_str
        assert "project" in repr_str


class TestProjectLogFields:
    """Test Project log-specific fields."""

    def test_daily_log_with_date(self):
        """Test that DailyLog project has date field."""
        daily_log = Project(
            id=1,
            name="Daily Log",
            type=ProjectType.DAILY_LOG,
            date=date(2025, 11, 10),
        )
        assert daily_log.date == date(2025, 11, 10)
        assert daily_log.type == ProjectType.DAILY_LOG

    def test_daily_log_date_nullable(self):
        """Test that date field is nullable."""
        daily_log = Project(
            id=1,
            name="Daily Log",
            type=ProjectType.DAILY_LOG,
            date=None,
        )
        assert daily_log.date is None

    def test_weekly_log_with_week_start(self):
        """Test that WeeklyLog project has week_start field."""
        weekly_log = Project(
            id=2,
            name="Weekly Log",
            type=ProjectType.WEEKLY_LOG,
            week_start=date(2025, 11, 10),  # Monday
        )
        assert weekly_log.week_start == date(2025, 11, 10)
        assert weekly_log.type == ProjectType.WEEKLY_LOG

    def test_monthly_log_with_year_month(self):
        """Test that MonthlyLog project has year and month fields."""
        monthly_log = Project(
            id=3,
            name="Monthly Log",
            type=ProjectType.MONTHLY_LOG,
            year=2025,
            month=11,
        )
        assert monthly_log.year == 2025
        assert monthly_log.month == 11
        assert monthly_log.type == ProjectType.MONTHLY_LOG

    def test_regular_project_without_log_fields(self):
        """Test that regular project can be created without log fields."""
        project = Project(
            id=4,
            name="Regular Project",
            type=ProjectType.PROJECT,
        )
        assert project.type == ProjectType.PROJECT
        # Log fields should be None or not cause errors
        assert not hasattr(project, "date") or project.date is None


class TestTaskRepr:
    """Test Task __repr__ method."""

    def test_task_repr_format(self):
        """Test that Task repr has correct format."""
        task = Task(
            id=1,
            title="Buy milk",
            status=TaskStatus.TODO,
        )
        repr_str = repr(task)
        assert "Task" in repr_str
        assert "id=1" in repr_str
        assert "Buy milk" in repr_str
        assert "todo" in repr_str


class TestNoteRepr:
    """Test Note __repr__ method."""

    def test_note_repr_format(self):
        """Test that Note repr has correct format."""
        note = Note(
            id=1,
            title="Meeting notes",
            content="Discussed project timeline",
        )
        repr_str = repr(note)
        assert "Note" in repr_str
        assert "id=1" in repr_str
        assert "Meeting notes" in repr_str


class TestEventRepr:
    """Test Event __repr__ method."""

    def test_event_repr_format(self):
        """Test that Event repr has correct format."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1,
            title="Conference",
            content="Annual tech conference",
            occurred_at=now,
        )
        repr_str = repr(event)
        assert "Event" in repr_str
        assert "id=1" in repr_str
        assert "Conference" in repr_str
        assert "occurred_at=" in repr_str


class TestTagRepr:
    """Test Tag __repr__ method."""

    def test_tag_repr_format(self):
        """Test that Tag repr has correct format."""
        tag = Tag(
            id=1,
            name="urgent",
        )
        repr_str = repr(tag)
        assert "Tag" in repr_str
        assert "id=1" in repr_str
        assert "urgent" in repr_str


class TestLogEntryRepr:
    """Test LogEntry __repr__ method."""

    def test_log_entry_repr_with_task(self):
        """Test LogEntry repr when entry is a task."""
        now = datetime.now(timezone.utc)
        log_entry = LogEntry(
            id=1,
            project_id=1,
            task_id=5,
            entry_date=now,
        )
        repr_str = repr(log_entry)
        assert "LogEntry" in repr_str
        assert "id=1" in repr_str
        assert "project_id=1" in repr_str
        assert "type='task'" in repr_str

    def test_log_entry_repr_with_note(self):
        """Test LogEntry repr when entry is a note."""
        now = datetime.now(timezone.utc)
        log_entry = LogEntry(
            id=2,
            project_id=1,
            note_id=5,
            entry_date=now,
        )
        repr_str = repr(log_entry)
        assert "LogEntry" in repr_str
        assert "type='note'" in repr_str

    def test_log_entry_repr_with_event(self):
        """Test LogEntry repr when entry is an event."""
        now = datetime.now(timezone.utc)
        log_entry = LogEntry(
            id=3,
            project_id=1,
            event_id=5,
            entry_date=now,
        )
        repr_str = repr(log_entry)
        assert "LogEntry" in repr_str
        assert "type='event'" in repr_str

    def test_log_entry_repr_with_unknown_type(self):
        """Test LogEntry repr when entry has no task, note, or event."""
        now = datetime.now(timezone.utc)
        log_entry = LogEntry(
            id=4,
            project_id=1,
            entry_date=now,
        )
        repr_str = repr(log_entry)
        assert "LogEntry" in repr_str
        assert "type='unknown'" in repr_str


class TestTaskRecurrenceRepr:
    """Test TaskRecurrence __repr__ method."""

    def test_task_recurrence_repr_format(self):
        """Test that TaskRecurrence repr has correct format."""
        now = datetime.now(timezone.utc)
        recurrence = TaskRecurrence(
            id=1,
            task_id=5,
            cron_expression="0 9 * * MON",
            next_occurrence=now,
        )
        repr_str = repr(recurrence)
        assert "TaskRecurrence" in repr_str
        assert "id=1" in repr_str
        assert "task_id=5" in repr_str
        assert "0 9 * * MON" in repr_str


class TestMigrationRepr:
    """Test Migration __repr__ method."""

    def test_migration_repr_format(self):
        """Test that Migration repr has correct format."""
        now = datetime.now(timezone.utc)
        migration = Migration(
            id=1,
            task_id=5,
            from_log_entry_id=10,
            to_log_entry_id=11,
            migrated_at=now,
        )
        repr_str = repr(migration)
        assert "Migration" in repr_str
        assert "id=1" in repr_str
        assert "task_id=5" in repr_str
        assert "from=10" in repr_str
        assert "to=11" in repr_str
