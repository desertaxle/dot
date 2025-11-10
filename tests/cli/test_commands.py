"""Tests for CLI commands using cyclopts."""

import pytest
from unittest.mock import patch

from dot.__main__ import app
from dot.domain.models import Task, TaskStatus, Note, Event
from dot.repository.uow import InMemoryUnitOfWork
from datetime import datetime, timezone


class TestTaskAddCommand:
    """Tests for the task add command."""

    def test_add_task_with_title_only(self, capsys):
        """Test adding a task with just a title."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            # Simulate the CLI call
            app(["tasks", "add", "Buy groceries"], result_action="return_value")

            # Verify the task was added
            tasks = list(mock_uow.tasks.list())
            assert len(tasks) == 1
            assert tasks[0].title == "Buy groceries"
            assert tasks[0].status == TaskStatus.TODO

    def test_add_task_with_description(self, capsys):
        """Test adding a task with title and description."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "add", "Buy groceries", "--description", "Milk, bread, eggs"],
                result_action="return_value",
            )

            tasks = list(mock_uow.tasks.list())
            assert len(tasks) == 1
            assert tasks[0].title == "Buy groceries"
            assert tasks[0].description == "Milk, bread, eggs"

    def test_add_task_with_priority(self, capsys):
        """Test adding a task with priority."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "add", "Urgent task", "--priority", "1"],
                result_action="return_value",
            )

            tasks = list(mock_uow.tasks.list())
            assert len(tasks) == 1
            assert tasks[0].priority == 1

    def test_add_task_output(self, capsys):
        """Test that add task returns confirmation message."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(["tasks", "add", "Test task"], result_action="return_value")
            captured = capsys.readouterr()

            assert "created" in captured.out.lower() or "added" in captured.out.lower()


class TestTaskListCommand:
    """Tests for the task list command."""

    def test_list_empty_tasks(self, capsys):
        """Test listing when no tasks exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(["tasks", "list"], result_action="return_value")
            captured = capsys.readouterr()

            # Should handle empty gracefully
            assert captured.out is not None

    def test_list_multiple_tasks(self, capsys):
        """Test listing multiple tasks."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            # Add some tasks
            task1 = Task(id=1, title="Task 1")
            task2 = Task(id=2, title="Task 2")
            task3 = Task(id=3, title="Task 3", status=TaskStatus.DONE)
            mock_uow.tasks.add(task1)
            mock_uow.tasks.add(task2)
            mock_uow.tasks.add(task3)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Task 1" in captured.out
            assert "Task 2" in captured.out
            assert "Task 3" in captured.out

    def test_list_excludes_cancelled_by_default(self, capsys):
        """Test that cancelled tasks are hidden by default."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            # Add tasks with different statuses
            task_todo = Task(id=1, title="Todo task", status=TaskStatus.TODO)
            task_done = Task(id=2, title="Done task", status=TaskStatus.DONE)
            task_cancelled = Task(
                id=3, title="Cancelled task", status=TaskStatus.CANCELLED
            )

            mock_uow.tasks.add(task_todo)
            mock_uow.tasks.add(task_done)
            mock_uow.tasks.add(task_cancelled)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Todo task" in captured.out
            assert "Done task" in captured.out
            assert "Cancelled task" not in captured.out

    def test_list_all_includes_cancelled(self, capsys):
        """Test that --all flag includes cancelled tasks."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task_cancelled = Task(
                id=1, title="Cancelled task", status=TaskStatus.CANCELLED
            )
            mock_uow.tasks.add(task_cancelled)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "list", "--all"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Cancelled task" in captured.out


class TestTaskShowCommand:
    """Tests for the task show command."""

    def test_show_existing_task(self, capsys):
        """Test showing an existing task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Test task", description="A test", priority=1)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "show", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Test task" in captured.out
            assert "A test" in captured.out

    def test_show_nonexistent_task(self):
        """Test showing a task that doesn't exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["tasks", "show", "999"], result_action="return_value")


class TestTaskDoneCommand:
    """Tests for the task done command."""

    def test_mark_task_done(self, capsys):
        """Test marking a task as done."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task to complete", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "done", "1"], result_action="return_value")

            updated_task = mock_uow.tasks.get(1)
            assert updated_task is not None
            assert updated_task.status == TaskStatus.DONE

    def test_mark_nonexistent_task_done(self):
        """Test marking a non-existent task as done."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["tasks", "done", "999"], result_action="return_value")

    def test_done_output(self, capsys):
        """Test done command output."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "done", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "done" in captured.out.lower() or "completed" in captured.out.lower()


class TestTaskCancelCommand:
    """Tests for the task cancel command."""

    def test_cancel_task(self, capsys):
        """Test cancelling a task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task to cancel", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "cancel", "1"], result_action="return_value")

            updated_task = mock_uow.tasks.get(1)
            assert updated_task is not None
            assert updated_task.status == TaskStatus.CANCELLED

    def test_cancelled_task_not_in_default_list(self, capsys):
        """Test that cancelled task doesn't appear in default list."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task to cancel", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            # Cancel the task
            task.status = TaskStatus.CANCELLED
            mock_uow.tasks.update(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Task to cancel" not in captured.out

    def test_cancel_nonexistent_task(self):
        """Test cancelling a non-existent task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["tasks", "cancel", "999"], result_action="return_value")

    def test_cancel_output(self, capsys):
        """Test cancel command output."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "cancel", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "cancel" in captured.out.lower()


class TestTaskDeleteCommand:
    """Tests for the task delete command."""

    def test_delete_task(self):
        """Test deleting a task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task to delete")
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "delete", "1"], result_action="return_value")

            # Task should no longer exist
            deleted_task = mock_uow.tasks.get(1)
            assert deleted_task is None

    def test_delete_nonexistent_task(self):
        """Test deleting a non-existent task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["tasks", "delete", "999"], result_action="return_value")

    def test_delete_output(self, capsys):
        """Test delete command output."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task", status=TaskStatus.TODO)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["tasks", "delete", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "delete" in captured.out.lower() or "removed" in captured.out.lower()


class TestTaskUpdateCommand:
    """Tests for the task update command."""

    def test_update_task_title(self):
        """Test updating a task's title."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Old title")
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "update", "1", "--title", "New title"],
                result_action="return_value",
            )

            updated_task = mock_uow.tasks.get(1)
            assert updated_task is not None
            assert updated_task.title == "New title"

    def test_update_task_description(self):
        """Test updating a task's description."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task", description="Old description")
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "update", "1", "--description", "New description"],
                result_action="return_value",
            )

            updated_task = mock_uow.tasks.get(1)
            assert updated_task is not None
            assert updated_task.description == "New description"

    def test_update_task_priority(self):
        """Test updating a task's priority."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Task", priority=3)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "update", "1", "--priority", "1"],
                result_action="return_value",
            )

            updated_task = mock_uow.tasks.get(1)
            assert updated_task is not None
            assert updated_task.priority == 1

    def test_update_nonexistent_task(self):
        """Test updating a non-existent task."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(
                    ["tasks", "update", "999", "--title", "New title"],
                    result_action="return_value",
                )

    def test_update_output(self, capsys):
        """Test update command output."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            task = Task(id=1, title="Old", priority=None)
            mock_uow.tasks.add(task)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["tasks", "update", "1", "--title", "New"],
                result_action="return_value",
            )
            captured = capsys.readouterr()

            assert "update" in captured.out.lower()


class TestNoteAddCommand:
    """Tests for the note add command."""

    def test_add_note_with_title_only(self, capsys):
        """Test adding a note with just a title."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(["notes", "add", "Important note"], result_action="return_value")

            notes = list(mock_uow.notes.list())
            assert len(notes) == 1
            assert notes[0].title == "Important note"

    def test_add_note_with_content(self, capsys):
        """Test adding a note with title and content."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(
                ["notes", "add", "Title", "--content", "This is the content"],
                result_action="return_value",
            )

            notes = list(mock_uow.notes.list())
            assert len(notes) == 1
            assert notes[0].title == "Title"
            assert notes[0].content == "This is the content"


class TestNoteListCommand:
    """Tests for the note list command."""

    def test_list_empty_notes(self, capsys):
        """Test listing when no notes exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(["notes", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert captured.out is not None

    def test_list_multiple_notes(self, capsys):
        """Test listing multiple notes."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            note1 = Note(id=1, title="Note 1")
            note2 = Note(id=2, title="Note 2")
            mock_uow.notes.add(note1)
            mock_uow.notes.add(note2)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["notes", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Note 1" in captured.out
            assert "Note 2" in captured.out


class TestNoteShowCommand:
    """Tests for the note show command."""

    def test_show_existing_note(self, capsys):
        """Test showing an existing note."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            note = Note(id=1, title="Test note", content="Content here")
            mock_uow.notes.add(note)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["notes", "show", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Test note" in captured.out
            assert "Content here" in captured.out

    def test_show_nonexistent_note(self):
        """Test showing a note that doesn't exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["notes", "show", "999"], result_action="return_value")


class TestNoteDeleteCommand:
    """Tests for the note delete command."""

    def test_delete_note(self):
        """Test deleting a note."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            note = Note(id=1, title="Note to delete")
            mock_uow.notes.add(note)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["notes", "delete", "1"], result_action="return_value")

            deleted_note = mock_uow.notes.get(1)
            assert deleted_note is None


class TestNoteUpdateCommand:
    """Tests for the note update command."""

    def test_update_note_title(self):
        """Test updating a note's title."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            note = Note(id=1, title="Old title")
            mock_uow.notes.add(note)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["notes", "update", "1", "--title", "New title"],
                result_action="return_value",
            )

            updated_note = mock_uow.notes.get(1)
            assert updated_note is not None
            assert updated_note.title == "New title"

    def test_update_note_content(self):
        """Test updating a note's content."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            note = Note(id=1, title="Note", content="Old content")
            mock_uow.notes.add(note)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["notes", "update", "1", "--content", "New content"],
                result_action="return_value",
            )

            updated_note = mock_uow.notes.get(1)
            assert updated_note is not None
            assert updated_note.content == "New content"


class TestEventAddCommand:
    """Tests for the event add command."""

    def test_add_event_with_title_and_date(self, capsys):
        """Test adding an event with title and date."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(
                [
                    "events",
                    "add",
                    "Conference",
                    "--date",
                    "2024-01-15T10:00:00",
                ],
                result_action="return_value",
            )

            events = list(mock_uow.events.list())
            assert len(events) == 1
            assert events[0].title == "Conference"

    def test_add_event_with_content(self, capsys):
        """Test adding an event with content."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(
                [
                    "events",
                    "add",
                    "Meeting",
                    "--date",
                    "2024-01-15T10:00:00",
                    "--content",
                    "Team sync",
                ],
                result_action="return_value",
            )

            events = list(mock_uow.events.list())
            assert len(events) == 1
            assert events[0].content == "Team sync"


class TestEventListCommand:
    """Tests for the event list command."""

    def test_list_empty_events(self, capsys):
        """Test listing when no events exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            app(["events", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert captured.out is not None

    def test_list_multiple_events(self, capsys):
        """Test listing multiple events."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            now = datetime.now(timezone.utc)
            event1 = Event(id=1, title="Event 1", occurred_at=now)
            event2 = Event(id=2, title="Event 2", occurred_at=now)
            mock_uow.events.add(event1)
            mock_uow.events.add(event2)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["events", "list"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Event 1" in captured.out
            assert "Event 2" in captured.out


class TestEventShowCommand:
    """Tests for the event show command."""

    def test_show_existing_event(self, capsys):
        """Test showing an existing event."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            now = datetime.now(timezone.utc)
            event = Event(id=1, title="Test event", content="Details", occurred_at=now)
            mock_uow.events.add(event)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["events", "show", "1"], result_action="return_value")
            captured = capsys.readouterr()

            assert "Test event" in captured.out
            assert "Details" in captured.out

    def test_show_nonexistent_event(self):
        """Test showing an event that doesn't exist."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()
            mock_get_uow.return_value = mock_uow

            with pytest.raises(SystemExit):
                app(["events", "show", "999"], result_action="return_value")


class TestEventDeleteCommand:
    """Tests for the event delete command."""

    def test_delete_event(self):
        """Test deleting an event."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            now = datetime.now(timezone.utc)
            event = Event(id=1, title="Event to delete", occurred_at=now)
            mock_uow.events.add(event)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(["events", "delete", "1"], result_action="return_value")

            deleted_event = mock_uow.events.get(1)
            assert deleted_event is None


class TestEventUpdateCommand:
    """Tests for the event update command."""

    def test_update_event_title(self):
        """Test updating an event's title."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            now = datetime.now(timezone.utc)
            event = Event(id=1, title="Old title", occurred_at=now)
            mock_uow.events.add(event)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["events", "update", "1", "--title", "New title"],
                result_action="return_value",
            )

            updated_event = mock_uow.events.get(1)
            assert updated_event is not None
            assert updated_event.title == "New title"

    def test_update_event_content(self):
        """Test updating an event's content."""
        with patch("dot.__main__.get_uow") as mock_get_uow:
            mock_uow = InMemoryUnitOfWork()

            now = datetime.now(timezone.utc)
            event = Event(id=1, title="Event", content="Old content", occurred_at=now)
            mock_uow.events.add(event)
            mock_uow.commit()

            mock_get_uow.return_value = mock_uow

            app(
                ["events", "update", "1", "--content", "New content"],
                result_action="return_value",
            )

            updated_event = mock_uow.events.get(1)
            assert updated_event is not None
            assert updated_event.content == "New content"
