"""Dot CLI application."""

import sys
from datetime import datetime
from typing import Optional

import whenever
from cyclopts import App

from .db import get_database, init_database
from .domain.log_operations import LogEntry
from .domain.models import Event, Note, Task, TaskStatus
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
    task_id: int | None = None,
    note_id: int | None = None,
    event_id: int | None = None,
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

    # Create log entry
    log_entry = LogEntry(
        id=0,  # Will be assigned by repository
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
                id=0,  # ID will be assigned by the database
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

            print(f"✓ Task created: {title}")
    except Exception as e:
        print(f"✗ Error creating task: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def list(all: bool = False):  # noqa: A001, F811
    """List all tasks."""
    try:
        with get_uow() as uow:
            task_list = uow.tasks.list()

            if not all:
                task_list = [t for t in task_list if t.status != TaskStatus.CANCELLED]

            if not task_list:
                print("No tasks found.")
                return

            for task in task_list:
                status_symbol = (
                    "✓"
                    if task.status == TaskStatus.DONE
                    else "✗"
                    if task.status == TaskStatus.CANCELLED
                    else "○"
                )
                priority_str = f" [P{task.priority}]" if task.priority else ""
                print(f"{status_symbol} ({task.id}) {task.title}{priority_str}")
    except Exception as e:
        print(f"✗ Error listing tasks: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def show(task_id: int):  # noqa: F811
    """Show task details."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(task_id)
            if not task:
                print(f"✗ Task {task_id} not found.", file=sys.stderr)
                sys.exit(1)

            print(f"Task: {task.title}")
            print(f"ID: {task.id}")
            print(f"Status: {task.status.value}")
            if task.description:
                print(f"Description: {task.description}")
            if task.priority:
                print(f"Priority: {task.priority}")
            print(f"Created: {task.created_at}")
            print(f"Updated: {task.updated_at}")
    except Exception as e:
        print(f"✗ Error showing task: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def done(task_id: int):
    """Mark a task as done."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(task_id)
            if not task:
                print(f"✗ Task {task_id} not found.", file=sys.stderr)
                sys.exit(1)

            task.status = TaskStatus.DONE
            task.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.tasks.update(task)
            uow.commit()
            print(f"✓ Task marked as done: {task.title}")
    except Exception as e:
        print(f"✗ Error marking task done: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def cancel(task_id: int):
    """Cancel a task (strike it without deleting)."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(task_id)
            if not task:
                print(f"✗ Task {task_id} not found.", file=sys.stderr)
                sys.exit(1)

            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.tasks.update(task)
            uow.commit()
            print(f"✓ Task cancelled: {task.title}")
    except Exception as e:
        print(f"✗ Error cancelling task: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def delete(task_id: int):  # noqa: F811
    """Delete a task permanently."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(task_id)
            if not task:
                print(f"✗ Task {task_id} not found.", file=sys.stderr)
                sys.exit(1)

            uow.tasks.delete(task_id)
            uow.commit()
            print(f"✓ Task deleted: {task.title}")
    except Exception as e:
        print(f"✗ Error deleting task: {e}", file=sys.stderr)
        sys.exit(1)


@tasks_app.command
def update(  # noqa: F811
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
):
    """Update a task."""
    try:
        with get_uow() as uow:
            task = uow.tasks.get(task_id)
            if not task:
                print(f"✗ Task {task_id} not found.", file=sys.stderr)
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
            print(f"✓ Task updated: {task.title}")
    except Exception as e:
        print(f"✗ Error updating task: {e}", file=sys.stderr)
        sys.exit(1)


# ===== NOTE COMMANDS =====


@notes_app.command
def add(title: str, content: Optional[str] = None):  # noqa: F811
    """Add a new note."""
    try:
        with get_uow() as uow:
            note = Note(id=0, title=title, content=content)
            uow.notes.add(note)
            uow.commit()  # Commit to get database-assigned ID

            # Add to today's daily log
            today = whenever.Instant.now().to_system_tz().date()
            add_to_daily_log(uow, today, note_id=note.id)
            uow.commit()

            print(f"✓ Note created: {title}")
    except Exception as e:
        print(f"✗ Error creating note: {e}", file=sys.stderr)
        sys.exit(1)


@notes_app.command
def list():  # noqa: A001, F811
    """List all notes."""
    try:
        with get_uow() as uow:
            notes_list = uow.notes.list()

            if not notes_list:
                print("No notes found.")
                return

            for note in notes_list:
                print(f"📝 ({note.id}) {note.title}")
    except Exception as e:
        print(f"✗ Error listing notes: {e}", file=sys.stderr)
        sys.exit(1)


@notes_app.command
def show(note_id: int):  # noqa: F811
    """Show note details."""
    try:
        with get_uow() as uow:
            note = uow.notes.get(note_id)
            if not note:
                print(f"✗ Note {note_id} not found.", file=sys.stderr)
                sys.exit(1)

            print(f"Note: {note.title}")
            print(f"ID: {note.id}")
            if note.content:
                print(f"Content: {note.content}")
            print(f"Created: {note.created_at}")
            print(f"Updated: {note.updated_at}")
    except Exception as e:
        print(f"✗ Error showing note: {e}", file=sys.stderr)
        sys.exit(1)


@notes_app.command
def delete(note_id: int):  # noqa: F811
    """Delete a note."""
    try:
        with get_uow() as uow:
            note = uow.notes.get(note_id)
            if not note:
                print(f"✗ Note {note_id} not found.", file=sys.stderr)
                sys.exit(1)

            uow.notes.delete(note_id)
            uow.commit()
            print(f"✓ Note deleted: {note.title}")
    except Exception as e:
        print(f"✗ Error deleting note: {e}", file=sys.stderr)
        sys.exit(1)


@notes_app.command
def update(  # noqa: F811
    note_id: int, title: Optional[str] = None, content: Optional[str] = None
):
    """Update a note."""
    try:
        with get_uow() as uow:
            note = uow.notes.get(note_id)
            if not note:
                print(f"✗ Note {note_id} not found.", file=sys.stderr)
                sys.exit(1)

            if title is not None:
                note.title = title
            if content is not None:
                note.content = content

            note.updated_at = datetime.now(datetime.now().astimezone().tzinfo)
            uow.notes.update(note)
            uow.commit()
            print(f"✓ Note updated: {note.title}")
    except Exception as e:
        print(f"✗ Error updating note: {e}", file=sys.stderr)
        sys.exit(1)


# ===== EVENT COMMANDS =====


@events_app.command
def add(title: str, date: str, content: Optional[str] = None):  # noqa: F811
    """Add a new event."""
    try:
        occurred_at = datetime.fromisoformat(date)
        # Ensure timezone-aware datetime
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=datetime.now().astimezone().tzinfo)

        with get_uow() as uow:
            event = Event(id=0, title=title, occurred_at=occurred_at, content=content)
            uow.events.add(event)
            uow.commit()  # Commit to get database-assigned ID

            # Add to daily log for the event's date
            event_date = (
                whenever.Instant.from_py_datetime(occurred_at).to_system_tz().date()
            )
            add_to_daily_log(uow, event_date, event_id=event.id)
            uow.commit()

            print(f"✓ Event created: {title}")
    except ValueError:
        print(
            "✗ Invalid date format. Use ISO format: 2024-01-15T10:00:00",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error creating event: {e}", file=sys.stderr)
        sys.exit(1)


@events_app.command
def list():  # noqa: A001, F811
    """List all events."""
    try:
        with get_uow() as uow:
            events_list = uow.events.list()

            if not events_list:
                print("No events found.")
                return

            for event in events_list:
                print(f"📅 ({event.id}) {event.title} - {event.occurred_at}")
    except Exception as e:
        print(f"✗ Error listing events: {e}", file=sys.stderr)
        sys.exit(1)


@events_app.command
def show(event_id: int):  # noqa: F811
    """Show event details."""
    try:
        with get_uow() as uow:
            event = uow.events.get(event_id)
            if not event:
                print(f"✗ Event {event_id} not found.", file=sys.stderr)
                sys.exit(1)

            print(f"Event: {event.title}")
            print(f"ID: {event.id}")
            print(f"Occurred: {event.occurred_at}")
            if event.content:
                print(f"Content: {event.content}")
            print(f"Created: {event.created_at}")
            print(f"Updated: {event.updated_at}")
    except Exception as e:
        print(f"✗ Error showing event: {e}", file=sys.stderr)
        sys.exit(1)


@events_app.command
def delete(event_id: int):  # noqa: F811
    """Delete an event."""
    try:
        with get_uow() as uow:
            event = uow.events.get(event_id)
            if not event:
                print(f"✗ Event {event_id} not found.", file=sys.stderr)
                sys.exit(1)

            uow.events.delete(event_id)
            uow.commit()
            print(f"✓ Event deleted: {event.title}")
    except Exception as e:
        print(f"✗ Error deleting event: {e}", file=sys.stderr)
        sys.exit(1)


@events_app.command
def update(  # noqa: F811
    event_id: int,
    title: Optional[str] = None,
    date: Optional[str] = None,
    content: Optional[str] = None,
):
    """Update an event."""
    try:
        with get_uow() as uow:
            event = uow.events.get(event_id)
            if not event:
                print(f"✗ Event {event_id} not found.", file=sys.stderr)
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
            print(f"✓ Event updated: {event.title}")
    except ValueError:
        print(
            "✗ Invalid date format. Use ISO format: 2024-01-15T10:00:00",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error updating event: {e}", file=sys.stderr)
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

            # Display log header
            print(f"\n=== Daily Log: {log_date} ===\n")

            if not entries:
                print("(No entries)")
                return

            # Display entries chronologically
            for entry in entries:
                if entry.task_id:
                    task = uow.tasks.get(entry.task_id)
                    if task:
                        status_icon = (
                            "✓"
                            if task.status == TaskStatus.DONE
                            else "✗"
                            if task.status == TaskStatus.CANCELLED
                            else "○"
                        )
                        print(f"{status_icon} Task: {task.title}")

                elif entry.note_id:
                    note = uow.notes.get(entry.note_id)
                    if note:
                        print(f"📝 Note: {note.title}")

                elif entry.event_id:
                    event = uow.events.get(entry.event_id)
                    if event:
                        print(f"📅 Event: {event.title}")

            print()  # Blank line at end
    except Exception as e:
        print(f"✗ Error showing today's log: {e}", file=sys.stderr)
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

            # Display log header
            print(f"\n=== Daily Log: {log_date} ===\n")

            if not entries:
                print("(No entries)")
                return

            # Display entries chronologically
            for entry in entries:
                if entry.task_id:
                    task = uow.tasks.get(entry.task_id)
                    if task:
                        status_icon = (
                            "✓"
                            if task.status == TaskStatus.DONE
                            else "✗"
                            if task.status == TaskStatus.CANCELLED
                            else "○"
                        )
                        print(f"{status_icon} Task: {task.title}")

                elif entry.note_id:
                    note = uow.notes.get(entry.note_id)
                    if note:
                        print(f"📝 Note: {note.title}")

                elif entry.event_id:
                    event = uow.events.get(entry.event_id)
                    if event:
                        print(f"📅 Event: {event.title}")

            print()  # Blank line at end
    except Exception as e:
        print(f"✗ Error showing log: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    app()
