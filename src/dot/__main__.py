"""CLI entry point for Dot bullet journal application."""

import sys
from uuid import UUID

from cyclopts import App
from rich.console import Console
from rich.table import Table

from dot.db import get_session
from dot.domain.models import TaskStatus
from dot.domain.operations import create_task, mark_cancelled, mark_done
from dot.models import Base
from dot.repository.sqlalchemy import SQLAlchemyTaskRepository
from dot.settings import Settings

# Initialize console for output
console = Console()

# Create the main app
app = App(name="dot", help="Bullet journal CLI for tasks, events, and notes")

# Create task subcommand group
task_app = App(name="task", help="Manage tasks")


def _init_database(settings: Settings) -> None:
    """Initialize database tables if they don't exist.

    Args:
        settings: Application settings
    """
    from dot.db import get_engine

    settings.ensure_dot_home_exists()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)


@task_app.command
def create(title: str, description: str | None = None) -> None:
    """Create a new task.

    Args:
        title: Task title (required)
        description: Optional task description
    """
    try:
        # Create domain task
        task = create_task(title, description)

        # Initialize database and save
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyTaskRepository(session)
            repo.add(task)

            # Success output
            console.print(f"✓ Task created: {task.title}", style="green")
            console.print(f"  ID: {task.id}")
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except ValueError as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@task_app.command
def list(status: str | None = None) -> None:
    """List all tasks or filter by status.

    Args:
        status: Optional status filter (TODO, DONE, CANCELLED)
    """
    try:
        # Validate status if provided
        status_filter = None
        if status is not None:
            try:
                status_filter = TaskStatus(status.upper())
            except ValueError:
                console.print(
                    f"✗ Error: Invalid status '{status}'. Must be TODO, DONE, or CANCELLED",
                    style="red",
                )
                sys.exit(1)

        # Initialize database and fetch tasks
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyTaskRepository(session)
            tasks = repo.list(status_filter)

            if not tasks:
                console.print("No tasks found.")
                sys.exit(0)

            # Create and populate table
            table = Table(title="Tasks")
            table.add_column("ID", style="cyan")
            table.add_column("Title")
            table.add_column("Status")
            table.add_column("Created")

            for task in tasks:
                # Format ID (show first 8 chars)
                short_id = str(task.id)[:8]

                # Color-code status
                status_style = {
                    TaskStatus.TODO: "white",
                    TaskStatus.DONE: "green",
                    TaskStatus.CANCELLED: "red",
                }.get(task.status, "white")

                # Format datetime
                created_str = task.created_at.strftime("%Y-%m-%d %H:%M")

                table.add_row(
                    short_id,
                    task.title,
                    f"[{status_style}]{task.status.value}[/{status_style}]",
                    created_str,
                )

            console.print(table)
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@task_app.command
def done(task_id: str) -> None:
    """Mark a task as done.

    Args:
        task_id: Task ID (full UUID or first 8 characters)
    """
    try:
        # Initialize database
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyTaskRepository(session)

            # Try to find task by full UUID or short ID
            task = None
            try:
                # Try as full UUID first
                full_uuid = UUID(task_id)
                task = repo.get(full_uuid)
            except ValueError:
                # Not a valid UUID, try as short ID
                all_tasks = repo.list()
                matches = [t for t in all_tasks if str(t.id).startswith(task_id)]

                if len(matches) == 0:
                    console.print(f"✗ Error: Task not found: {task_id}", style="red")
                    sys.exit(1)
                elif len(matches) > 1:
                    console.print(
                        f"✗ Error: Ambiguous ID. Multiple tasks match '{task_id}':",
                        style="red",
                    )
                    for t in matches:
                        console.print(f"  - {t.id} ({t.title})")
                    console.print("\n  Please use a longer ID prefix.")
                    sys.exit(1)
                else:
                    task = matches[0]

            if task is None:
                console.print(f"✗ Error: Task not found: {task_id}", style="red")
                sys.exit(1)

            # Mark as done
            assert task is not None  # Type narrowing for type checker
            updated_task = mark_done(task)
            repo.update(updated_task)

            console.print(f"✓ Task marked as DONE: {updated_task.title}", style="green")
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@task_app.command
def cancel(task_id: str) -> None:
    """Mark a task as cancelled.

    Args:
        task_id: Task ID (full UUID or first 8 characters)
    """
    try:
        # Initialize database
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyTaskRepository(session)

            # Try to find task by full UUID or short ID
            task = None
            try:
                # Try as full UUID first
                full_uuid = UUID(task_id)
                task = repo.get(full_uuid)
            except ValueError:
                # Not a valid UUID, try as short ID
                all_tasks = repo.list()
                matches = [t for t in all_tasks if str(t.id).startswith(task_id)]

                if len(matches) == 0:
                    console.print(f"✗ Error: Task not found: {task_id}", style="red")
                    sys.exit(1)
                elif len(matches) > 1:
                    console.print(
                        f"✗ Error: Ambiguous ID. Multiple tasks match '{task_id}':",
                        style="red",
                    )
                    for t in matches:
                        console.print(f"  - {t.id} ({t.title})")
                    console.print("\n  Please use a longer ID prefix.")
                    sys.exit(1)
                else:
                    task = matches[0]

            if task is None:
                console.print(f"✗ Error: Task not found: {task_id}", style="red")
                sys.exit(1)

            # Mark as cancelled
            assert task is not None  # Type narrowing for type checker
            updated_task = mark_cancelled(task)
            repo.update(updated_task)

            console.print(
                f"✓ Task marked as CANCELLED: {updated_task.title}", style="green"
            )
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


# Create event subcommand group
event_app = App(name="event", help="Manage events")


@event_app.command(name="create")
def create_event_cmd(
    title: str,
    description: str | None = None,
    date: str | None = None,
) -> None:
    """Create a new event.

    Args:
        title: Event title (required)
        description: Optional event description
        date: Optional date (YYYY-MM-DD format, defaults to now)
    """
    try:
        from datetime import datetime

        from dot.domain.operations import create_event
        from dot.repository.sqlalchemy import SQLAlchemyEventRepository

        # Parse date if provided
        occurred_at = None
        if date is not None:
            try:
                occurred_at = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                console.print(
                    f"✗ Error: Invalid date format '{date}'. Use YYYY-MM-DD",
                    style="red",
                )
                sys.exit(1)

        # Create domain event
        event = create_event(title, description, occurred_at)

        # Initialize database and save
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyEventRepository(session)
            repo.add(event)

            # Success output
            console.print(f"✓ Event created: {event.title}", style="green")
            console.print(f"  ID: {event.id}")
            console.print(
                f"  Occurred: {event.occurred_at.strftime('%Y-%m-%d %H:%M')}"
            )
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except ValueError as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@event_app.command(name="list")
def list_events_cmd(
    date: str | None = None,
    range: str | None = None,
) -> None:
    """List events, optionally filtered by date or range.

    Args:
        date: Filter by specific date (YYYY-MM-DD)
        range: Filter by date range (YYYY-MM-DD:YYYY-MM-DD)
    """
    try:
        from datetime import datetime

        from dot.repository.sqlalchemy import SQLAlchemyEventRepository

        # Parse filters
        target_date = None
        start_date = None
        end_date = None

        if date is not None and range is not None:
            console.print(
                "✗ Error: Cannot use both --date and --range filters", style="red"
            )
            sys.exit(1)

        if date is not None:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                console.print(
                    f"✗ Error: Invalid date format '{date}'. Use YYYY-MM-DD",
                    style="red",
                )
                sys.exit(1)

        if range is not None:
            try:
                parts = range.split(":")
                if len(parts) != 2:
                    raise ValueError("Range must be in format YYYY-MM-DD:YYYY-MM-DD")
                start_date = datetime.strptime(parts[0], "%Y-%m-%d").date()
                end_date = datetime.strptime(parts[1], "%Y-%m-%d").date()
            except ValueError as e:
                console.print(f"✗ Error: Invalid range format: {e}", style="red")
                sys.exit(1)

        # Initialize database and fetch events
        settings = Settings()
        _init_database(settings)

        session_gen = get_session(settings)
        session = next(session_gen)
        try:
            repo = SQLAlchemyEventRepository(session)

            # Fetch based on filter
            if target_date is not None:
                events = repo.list_by_date(target_date)
            elif start_date is not None and end_date is not None:
                events = repo.list_by_range(start_date, end_date)
            else:
                events = repo.list()

            # Sort by occurred_at (chronological)
            events = sorted(events, key=lambda e: e.occurred_at)

            if not events:
                console.print("No events found.")
                sys.exit(0)

            # Create and populate table
            table = Table(title="Events")
            table.add_column("ID", style="cyan")
            table.add_column("Title")
            table.add_column("Occurred")

            for event in events:
                # Format ID (show first 8 chars)
                short_id = str(event.id)[:8]

                # Format datetime
                occurred_str = event.occurred_at.strftime("%Y-%m-%d %H:%M")

                table.add_row(short_id, event.title, occurred_str)

            console.print(table)
            sys.exit(0)
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


# Register task commands
app.command(task_app)

# Register event commands
app.command(event_app)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
