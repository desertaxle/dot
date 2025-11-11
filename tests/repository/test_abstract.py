"""Tests for repository abstractions - tests the contract repositories must follow."""

from datetime import datetime, timezone

import whenever

from dot.domain.log_operations import LogEntry
from dot.domain.models import DailyLog, Event, Note, Project, Task, TaskStatus
from dot.repository.abstract import (
    EventRepository,
    LogEntryRepository,
    NoteRepository,
    ProjectRepository,
    TaskRepository,
)


class TaskRepositoryContract:
    """Contract that all TaskRepository implementations must follow."""

    repository: TaskRepository

    def test_add_task(self):
        """Repository can add a task."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test task",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )

        self.repository.add(task)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test task"

    def test_get_nonexistent_task(self):
        """Repository returns None for nonexistent task."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_tasks(self):
        """Repository can list all tasks."""
        now = datetime.now(timezone.utc)
        task1 = Task(id=1, title="Task 1", created_at=now, updated_at=now)
        task2 = Task(id=2, title="Task 2", created_at=now, updated_at=now)

        self.repository.add(task1)
        self.repository.add(task2)

        tasks = self.repository.list()
        assert len(tasks) == 2
        assert any(t.id == 1 for t in tasks)
        assert any(t.id == 2 for t in tasks)

    def test_update_task(self):
        """Repository can update a task."""
        now = datetime.now(timezone.utc)
        task = Task(id=1, title="Original", created_at=now, updated_at=now)

        self.repository.add(task)

        updated_task = Task(
            id=1,
            title="Updated",
            status=TaskStatus.DONE,
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_task)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.status == TaskStatus.DONE

    def test_delete_task(self):
        """Repository can delete a task."""
        now = datetime.now(timezone.utc)
        task = Task(id=1, title="To delete", created_at=now, updated_at=now)

        self.repository.add(task)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_task(self):
        """Deleting nonexistent task doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)


class NoteRepositoryContract:
    """Contract that all NoteRepository implementations must follow."""

    repository: NoteRepository

    def test_add_note(self):
        """Repository can add a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="Test note", created_at=now, updated_at=now)

        self.repository.add(note)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test note"

    def test_get_nonexistent_note(self):
        """Repository returns None for nonexistent note."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_notes(self):
        """Repository can list all notes."""
        now = datetime.now(timezone.utc)
        note1 = Note(id=1, title="Note 1", created_at=now, updated_at=now)
        note2 = Note(id=2, title="Note 2", created_at=now, updated_at=now)

        self.repository.add(note1)
        self.repository.add(note2)

        notes = self.repository.list()
        assert len(notes) == 2
        assert any(n.id == 1 for n in notes)
        assert any(n.id == 2 for n in notes)

    def test_update_note(self):
        """Repository can update a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="Original", created_at=now, updated_at=now)

        self.repository.add(note)

        updated_note = Note(
            id=1,
            title="Updated",
            content="New content",
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_note)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "New content"

    def test_delete_note(self):
        """Repository can delete a note."""
        now = datetime.now(timezone.utc)
        note = Note(id=1, title="To delete", created_at=now, updated_at=now)

        self.repository.add(note)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_note(self):
        """Deleting nonexistent note doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)


class EventRepositoryContract:
    """Contract that all EventRepository implementations must follow."""

    repository: EventRepository

    def test_add_event(self):
        """Repository can add an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="Test event", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.title == "Test event"

    def test_get_nonexistent_event(self):
        """Repository returns None for nonexistent event."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_events(self):
        """Repository can list all events."""
        now = datetime.now(timezone.utc)
        event1 = Event(
            id=1, title="Event 1", occurred_at=now, created_at=now, updated_at=now
        )
        event2 = Event(
            id=2, title="Event 2", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event1)
        self.repository.add(event2)

        events = self.repository.list()
        assert len(events) == 2
        assert any(e.id == 1 for e in events)
        assert any(e.id == 2 for e in events)

    def test_update_event(self):
        """Repository can update an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="Original", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)

        updated_event = Event(
            id=1,
            title="Updated",
            content="New content",
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_event)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "New content"

    def test_delete_event(self):
        """Repository can delete an event."""
        now = datetime.now(timezone.utc)
        event = Event(
            id=1, title="To delete", occurred_at=now, created_at=now, updated_at=now
        )

        self.repository.add(event)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_event(self):
        """Deleting nonexistent event doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)


class ProjectRepositoryContract:
    """Contract that all ProjectRepository implementations must follow."""

    repository: ProjectRepository

    def test_add_project(self):
        """Repository can add a project."""
        now = datetime.now(timezone.utc)
        project = Project(
            id=1,
            name="Test Project",
            description="A test project",
            created_at=now,
            updated_at=now,
        )

        self.repository.add(project)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.name == "Test Project"

    def test_get_nonexistent_project(self):
        """Repository returns None for nonexistent project."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_projects(self):
        """Repository can list all projects."""
        now = datetime.now(timezone.utc)
        project1 = Project(id=1, name="Project 1", created_at=now, updated_at=now)
        project2 = Project(id=2, name="Project 2", created_at=now, updated_at=now)

        self.repository.add(project1)
        self.repository.add(project2)

        projects = self.repository.list()
        assert len(projects) == 2
        assert any(p.id == 1 for p in projects)
        assert any(p.id == 2 for p in projects)

    def test_update_project(self):
        """Repository can update a project."""
        now = datetime.now(timezone.utc)
        project = Project(id=1, name="Original", created_at=now, updated_at=now)

        self.repository.add(project)

        updated_project = Project(
            id=1,
            name="Updated",
            description="Updated description",
            created_at=now,
            updated_at=now,
        )
        self.repository.update(updated_project)

        retrieved = self.repository.get(1)
        assert retrieved is not None
        assert retrieved.name == "Updated"
        assert retrieved.description == "Updated description"

    def test_delete_project(self):
        """Repository can delete a project."""
        now = datetime.now(timezone.utc)
        project = Project(id=1, name="To delete", created_at=now, updated_at=now)

        self.repository.add(project)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_project(self):
        """Deleting nonexistent project doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)

    def test_get_daily_log_creates_if_not_exists(self):
        """get_daily_log creates a daily log if it doesn't exist."""
        today = whenever.Instant.now().to_system_tz().date()

        daily_log = self.repository.get_daily_log(today)

        assert daily_log is not None
        assert isinstance(daily_log, DailyLog)
        assert daily_log.date == today
        assert daily_log.name == f"Daily Log {today}"

    def test_get_daily_log_returns_existing(self):
        """get_daily_log returns existing daily log for the date."""
        today = whenever.Instant.now().to_system_tz().date()

        # Create first time
        daily_log1 = self.repository.get_daily_log(today)

        # Get again - should return same log
        daily_log2 = self.repository.get_daily_log(today)

        assert daily_log1.id == daily_log2.id
        assert daily_log1.date == daily_log2.date


class LogEntryRepositoryContract:
    """Contract that all LogEntryRepository implementations must follow."""

    repository: LogEntryRepository

    def test_add_log_entry(self):
        """Repository can add a log entry."""
        today = whenever.Instant.now().to_system_tz().date()
        entry = LogEntry(
            id=1,
            log_id=1,
            task_id=10,
            note_id=None,
            event_id=None,
            entry_date=today,
        )

        self.repository.add(entry)
        retrieved = self.repository.get(1)

        assert retrieved is not None
        assert retrieved.id == 1
        assert retrieved.log_id == 1
        assert retrieved.task_id == 10

    def test_get_nonexistent_log_entry(self):
        """Repository returns None for nonexistent log entry."""
        result = self.repository.get(9999)
        assert result is None

    def test_list_log_entries(self):
        """Repository can list all log entries."""
        today = whenever.Instant.now().to_system_tz().date()
        entry1 = LogEntry(id=1, log_id=1, task_id=10, entry_date=today)
        entry2 = LogEntry(id=2, log_id=1, note_id=20, entry_date=today)

        self.repository.add(entry1)
        self.repository.add(entry2)

        entries = self.repository.list()
        assert len(entries) == 2
        assert any(e.id == 1 for e in entries)
        assert any(e.id == 2 for e in entries)

    def test_delete_log_entry(self):
        """Repository can delete a log entry."""
        today = whenever.Instant.now().to_system_tz().date()
        entry = LogEntry(id=1, log_id=1, task_id=10, entry_date=today)

        self.repository.add(entry)
        assert self.repository.get(1) is not None

        self.repository.delete(1)
        assert self.repository.get(1) is None

    def test_delete_nonexistent_log_entry(self):
        """Deleting nonexistent log entry doesn't raise error."""
        # Should not raise
        self.repository.delete(9999)

    def test_get_by_log_id(self):
        """Repository can get all entries for a specific log."""
        today = whenever.Instant.now().to_system_tz().date()
        entry1 = LogEntry(id=1, log_id=1, task_id=10, entry_date=today)
        entry2 = LogEntry(id=2, log_id=1, note_id=20, entry_date=today)
        entry3 = LogEntry(id=3, log_id=2, event_id=30, entry_date=today)

        self.repository.add(entry1)
        self.repository.add(entry2)
        self.repository.add(entry3)

        log1_entries = self.repository.get_by_log_id(1)
        assert len(log1_entries) == 2
        assert all(e.log_id == 1 for e in log1_entries)

        log2_entries = self.repository.get_by_log_id(2)
        assert len(log2_entries) == 1
        assert log2_entries[0].log_id == 2
