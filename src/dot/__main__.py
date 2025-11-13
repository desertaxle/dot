"""Dot CLI application."""

import sys
from datetime import datetime
from typing import Optional
from uuid import UUID

import whenever
from cyclopts import App

from .db import get_database, init_database
from .domain.log_operations import LogEntry
from .domain.models import Event, Note, Task, TaskStatus
from .output import (
    build_event_detail_panel,
    build_event_tree,
    build_log_tree,
    build_note_detail_panel,
    build_note_tree,
    build_task_detail_panel,
    build_task_tree,
    console,
    print_error,
    print_success,
)
from .repository.uow import AbstractUnitOfWork, SQLAlchemyUnitOfWork
from .settings import settings

# Initialize database
settings.dot_home.mkdir(parents=True, exist_ok=True)
init_database(settings.db_path)

app = App()
tasks_app = App(name="tasks", alias=("task", "t"))
notes_app = App(name="notes", alias=("note", "n"))
events_app = App(name="events", alias=("event", "e"))
logs_app = App(name="logs", alias=("log", "l"))

app.command(tasks_app)
app.command(notes_app)
app.command(events_app)
app.command(logs_app)


def get_uow() -> SQLAlchemyUnitOfWork:
    """Get a Unit of Work instance with a database session."""
    db = get_database()
    session = next(db.get_session())
    return SQLAlchemyUnitOfWork(session)


def add_to_daily_log(
    uow: AbstractUnitOfWork,
    item_date: whenever.Date,
    task_id: UUID | None = None,
    note_id: UUID | None = None,
    event_id: UUID | None = None,
) -> None:
    """Add an item to the appropriate daily log.

    Args:
        uow: Unit of Work with access to repositories
        item_date: Date for the daily log
        task_id: ID of task to add (if task)
        note_id: ID of note to add (if note)
        event_id: ID of event to add (if event)
    """
    # Get or create daily log for the date
    daily_log = uow.projects.get_daily_log(item_date)

    # ID should always be set after get_daily_log
    assert daily_log.id is not None

    # Create log entry
    log_entry = LogEntry(
        log_id=daily_log.id,
        task_id=task_id,
        note_id=note_id,
        event_id=event_id,
        entry_date=item_date,
    )

    # Add to repository
    uow.log_entries.add(log_entry)


# ===== TASK COMMANDS =====


@tasks_app.command
def add(title: str, description: Optional[str] = None, priority: Optional[int] = None):  # noqa: F811
    """Add a new task."""
    try:
        with get_uow() as uow:
            task = Task(
                title=title,
                description=description,
                priority=priority,
            )
            uow.tasks.add(task)
            uow.commit()  # Commit to get database-assigned ID

            # Add to today's daily log
            today = whenever.Instant.now().to_system_tz().date()
            add_to_daily_log(uow, today, task_id=task.id)
            uow.commit()

            print_success(f"Task created: {title}")
    except Exception as e:
        print_error(f"Error creating task: {e}")
        sys.exit(1)


@tasks_app.command
def list(all: bool = False):  # noqa: A001, F811
    """List all tasks."""
    try:
        with get_uow() as uow:
            task_list = uow.tasks.list()

            tree = build_task_tree(task_list, show_cancelled=all)
            console.print(tree)
    except Exception as e:
        print_error(f"Error listing tasks: {e}")
        sys.exit(1)


@tasks_app.command
def show(task_id: str):  # noqa: F811
    """Show task details."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(UUID(task_id))
            if not task:
                print_error(f"Task {task_id} not found.")
                sys.exit(1)

            panel = build_task_detail_panel(task)
            console.print(panel)
    except Exception as e:
        print_error(f"Error showing task: {e}")
        sys.exit(1)


@tasks_app.command
def done(task_id: str):
    """Mark a task as done."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(UUID(task_id))
            if not task:
                print_error(f"Task {task_id} not found.")
                sys.exit(1)

            task.status = TaskStatus.DONE
            task.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.tasks.update(task)
            uow.commit()
            print_success(f"Task marked as done: {task.title}")
    except Exception as e:
        print_error(f"Error marking task done: {e}")
        sys.exit(1)


@tasks_app.command
def cancel(task_id: str):
    """Cancel a task (strike it without deleting)."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(UUID(task_id))
            if not task:
                print_error(f"Task {task_id} not found.")
                sys.exit(1)

            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.tasks.update(task)
            uow.commit()
            print_success(f"Task cancelled: {task.title}")
    except Exception as e:
        print_error(f"Error cancelling task: {e}")
        sys.exit(1)


@tasks_app.command
def delete(task_id: str):  # noqa: F811
    """Delete a task permanently."""
    try:
        task_uuid = UUID(task_id)
        with get_uow() as uow:
            task = uow.tasks.get(task_uuid)
            if not task:
                print_error(f"Task {task_id} not found.")
                sys.exit(1)

            uow.tasks.delete(task_uuid)
            uow.commit()
            print_success(f"Task deleted: {task.title}")
    except Exception as e:
        print_error(f"Error deleting task: {e}")
        sys.exit(1)


@tasks_app.command
def update(  # noqa: F811
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
):
    """Update a task."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(UUID(task_id))
            if not task:
                print_error(f"Task {task_id} not found.")
                sys.exit(1)

            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority

            task.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.tasks.update(task)
            uow.commit()
            print_success(f"Task updated: {task.title}")
    except Exception as e:
        print_error(f"Error updating task: {e}")
        sys.exit(1)


# ===== NOTE COMMANDS =====


@notes_app.command
def add(title: str, content: Optional[str] = None):  # noqa: F811
    """Add a new note."""
    try:
        with get_uow() as uow:
            note = Note(title=title, content=content)
            uow.notes.add(note)
            uow.commit()  # Commit to get database-assigned ID

            # Add to today's daily log
            today = whenever.Instant.now().to_system_tz().date()
            add_to_daily_log(uow, today, note_id=note.id)
            uow.commit()

            print_success(f"Note created: {title}")
    except Exception as e:
        print_error(f"Error creating note: {e}")
        sys.exit(1)


@notes_app.command
def list():  # noqa: A001, F811
    """List all notes."""
    try:
        with get_uow() as uow:
            notes_list = uow.notes.list()

            tree = build_note_tree(notes_list)
            console.print(tree)
    except Exception as e:
        print_error(f"Error listing notes: {e}")
        sys.exit(1)


@notes_app.command
def show(note_id: str):  # noqa: F811
    """Show note details."""
    try:
        with get_uow() as uow:
            note = uow.notes.get(UUID(note_id))
            if not note:
                print_error(f"Note {note_id} not found.")
                sys.exit(1)

            panel = build_note_detail_panel(note)
            console.print(panel)
    except Exception as e:
        print_error(f"Error showing note: {e}")
        sys.exit(1)


@notes_app.command
def delete(note_id: str):  # noqa: F811
    """Delete a note."""
    try:
        note_uuid = UUID(note_id)
        with get_uow() as uow:
            note = uow.notes.get(note_uuid)
            if not note:
                print_error(f"Note {note_id} not found.")
                sys.exit(1)

            uow.notes.delete(note_uuid)
            uow.commit()
            print_success(f"Note deleted: {note.title}")
    except Exception as e:
        print_error(f"Error deleting note: {e}")
        sys.exit(1)


@notes_app.command
def update(  # noqa: F811
    note_id: str, title: Optional[str] = None, content: Optional[str] = None
):
    """Update a note."""
    try:
        with get_uow() as uow:
            note = uow.notes.get(UUID(note_id))
            if not note:
                print_error(f"Note {note_id} not found.")
                sys.exit(1)

            if title is not None:
                note.title = title
            if content is not None:
                note.content = content

            note.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.notes.update(note)
            uow.commit()
            print_success(f"Note updated: {note.title}")
    except Exception as e:
        print_error(f"Error updating note: {e}")
        sys.exit(1)


# ===== EVENT COMMANDS =====


@events_app.command
def add(title: str, date: Optional[str] = None, content: Optional[str] = None):  # noqa: F811
    """Add a new event."""
    try:
        if date is not None:
            occurred_at = datetime.fromisoformat(date)
            # Ensure timezone-aware datetime
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(
                    tzinfo=datetime.now().astimezone().tzinfo
                )
            event = Event(title=title, occurred_at=occurred_at, content=content)
        else:
            # Use default occurred_at (current datetime)
            event = Event(title=title, content=content)

        with get_uow() as uow:
            uow.events.add(event)
            uow.commit()  # Commit to get database-assigned ID

            # Add to daily log for the event's date
            event_date = (
                whenever.Instant.from_py_datetime(event.occurred_at)
                .to_system_tz()
                .date()
            )
            add_to_daily_log(uow, event_date, event_id=event.id)
            uow.commit()

            print_success(f"Event created: {title}")
    except ValueError:
        print_error("Invalid date format. Use ISO format: 2024-01-15T10:00:00")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error creating event: {e}")
        sys.exit(1)


@events_app.command
def list():  # noqa: A001, F811
    """List all events."""
    try:
        with get_uow() as uow:
            events_list = uow.events.list()

            tree = build_event_tree(events_list)
            console.print(tree)
    except Exception as e:
        print_error(f"Error listing events: {e}")
        sys.exit(1)


@events_app.command
def show(event_id: str):  # noqa: F811
    """Show event details."""
    try:
        with get_uow() as uow:
            event = uow.events.get(UUID(event_id))
            if not event:
                print_error(f"Event {event_id} not found.")
                sys.exit(1)

            panel = build_event_detail_panel(event)
            console.print(panel)
    except Exception as e:
        print_error(f"Error showing event: {e}")
        sys.exit(1)


@events_app.command
def delete(event_id: str):  # noqa: F811
    """Delete an event."""
    try:
        event_uuid = UUID(event_id)
        with get_uow() as uow:
            event = uow.events.get(event_uuid)
            if not event:
                print_error(f"Event {event_id} not found.")
                sys.exit(1)

            uow.events.delete(event_uuid)
            uow.commit()
            print_success(f"Event deleted: {event.title}")
    except Exception as e:
        print_error(f"Error deleting event: {e}")
        sys.exit(1)


@events_app.command
def update(  # noqa: F811
    event_id: str,
    title: Optional[str] = None,
    date: Optional[str] = None,
    content: Optional[str] = None,
):
    """Update an event."""
    try:
        with get_uow() as uow:
            event = uow.events.get(UUID(event_id))
            if not event:
                print_error(f"Event {event_id} not found.")
                sys.exit(1)

            if title is not None:
                event.title = title
            if date is not None:
                occurred_at = datetime.fromisoformat(date)
                # Ensure timezone-aware datetime
                if occurred_at.tzinfo is None:
                    occurred_at = occurred_at.replace(
                        tzinfo=datetime.now().astimezone().tzinfo
                    )
                event.occurred_at = occurred_at
            if content is not None:
                event.content = content

            event.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.events.update(event)
            uow.commit()
            print_success(f"Event updated: {event.title}")
    except ValueError:
        print_error("Invalid date format. Use ISO format: 2024-01-15T10:00:00")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error updating event: {e}")
        sys.exit(1)


# ===== LOG COMMANDS =====


@logs_app.command
def today():
    """View today's daily log."""
    try:
        log_date = whenever.Instant.now().to_system_tz().date()

        with get_uow() as uow:
            # Get daily log (will auto-create if doesn't exist)
            daily_log = uow.projects.get_daily_log(log_date)

            # Get all log entries for this log
            entries = uow.log_entries.get_by_log_id(daily_log.id)

            # Collect items with their timestamps for sorting
            items_with_timestamps = []

            for entry in entries:
                if entry.task_id:
                    task = uow.tasks.get(entry.task_id)
                    if task:
                        items_with_timestamps.append((entry.created_at, task))
                elif entry.note_id:
                    note = uow.notes.get(entry.note_id)
                    if note:
                        items_with_timestamps.append((entry.created_at, note))
                elif entry.event_id:
                    event = uow.events.get(entry.event_id)
                    if event:
                        items_with_timestamps.append((entry.created_at, event))

            # Sort chronologically by when added to log
            items_with_timestamps.sort(key=lambda x: x[0])
            sorted_items = [item for _, item in items_with_timestamps]

            # Convert whenever.Date to datetime for display
            log_datetime = datetime(log_date.year, log_date.month, log_date.day)

            tree = build_log_tree(log_datetime, sorted_items)
            console.print(tree)
    except Exception as e:
        print_error(f"Error showing today's log: {e}")
        sys.exit(1)


@logs_app.command
def show(date: Optional[str] = None):  # noqa: F811
    """View a daily log for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
    """
    try:
        if date is None:
            log_date = whenever.Instant.now().to_system_tz().date()
        else:
            # Parse date string (YYYY-MM-DD format)
            log_date = whenever.Date.parse_iso(date)

        with get_uow() as uow:
            # Get daily log (will auto-create if doesn't exist)
            daily_log = uow.projects.get_daily_log(log_date)

            # Get all log entries for this log
            entries = uow.log_entries.get_by_log_id(daily_log.id)

            # Collect items with their timestamps for sorting
            items_with_timestamps = []

            for entry in entries:
                if entry.task_id:
                    task = uow.tasks.get(entry.task_id)
                    if task:
                        items_with_timestamps.append((entry.created_at, task))
                elif entry.note_id:
                    note = uow.notes.get(entry.note_id)
                    if note:
                        items_with_timestamps.append((entry.created_at, note))
                elif entry.event_id:
                    event = uow.events.get(entry.event_id)
                    if event:
                        items_with_timestamps.append((entry.created_at, event))

            # Sort chronologically by when added to log
            items_with_timestamps.sort(key=lambda x: x[0])
            sorted_items = [item for _, item in items_with_timestamps]

            # Convert whenever.Date to datetime for display
            log_datetime = datetime(log_date.year, log_date.month, log_date.day)

            tree = build_log_tree(log_datetime, sorted_items)
            console.print(tree)
    except Exception as e:
        print_error(f"Error showing log: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
