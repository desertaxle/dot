"""In-memory repository implementations for testing."""

from datetime import date
from uuid import UUID

from dot.domain.models import Event, Task, TaskStatus
from dot.repository.abstract import EventRepository, TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation of TaskRepository for testing."""

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._tasks: dict[UUID, Task] = {}

    def add(self, task: Task) -> None:
        """Add a new task."""
        self._tasks[task.id] = task

    def get(self, task_id: UUID) -> Task | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status."""
        if status is None:
            return list(self._tasks.values())
        return [task for task in self._tasks.values() if task.status == status]

    def update(self, task: Task) -> None:
        """Update an existing task."""
        if task.id in self._tasks:
            self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        """Delete a task."""
        self._tasks.pop(task_id, None)

    def list_by_date(self, date: date) -> list[Task]:
        """List tasks created on a specific date."""
        return [task for task in self._tasks.values() if task.created_at.date() == date]


class InMemoryEventRepository(EventRepository):
    """In-memory implementation of EventRepository for testing."""

    def __init__(self) -> None:
        """Initialize the in-memory repository."""
        self._events: dict[UUID, Event] = {}

    def add(self, event: Event) -> None:
        """Add a new event."""
        self._events[event.id] = event

    def get(self, event_id: UUID) -> Event | None:
        """Get an event by ID."""
        return self._events.get(event_id)

    def list(self) -> list[Event]:
        """List all events."""
        return list(self._events.values())

    def list_by_date(self, date: date) -> list[Event]:
        """List events that occurred on a specific date."""
        return [
            event for event in self._events.values() if event.occurred_at.date() == date
        ]

    def list_by_range(self, start_date: date, end_date: date) -> list[Event]:
        """List events within a date range (inclusive)."""
        return [
            event
            for event in self._events.values()
            if start_date <= event.occurred_at.date() <= end_date
        ]

    def delete(self, event_id: UUID) -> None:
        """Delete an event."""
        self._events.pop(event_id, None)
