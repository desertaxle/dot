"""In-memory repository implementations for testing."""

from typing import Dict, List, Optional

from dot.domain.models import Event, Note, Task
from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation of TaskRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._tasks: Dict[int, Task] = {}

    def add(self, task: Task) -> None:
        """Add a task to storage."""
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def list(self) -> List[Task]:
        """List all tasks."""
        return list(self._tasks.values())

    def update(self, task: Task) -> None:
        """Update an existing task."""
        if task.id in self._tasks:
            self._tasks[task.id] = task

    def delete(self, task_id: int) -> None:
        """Delete a task by ID."""
        self._tasks.pop(task_id, None)


class InMemoryNoteRepository(NoteRepository):
    """In-memory implementation of NoteRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._notes: Dict[int, Note] = {}

    def add(self, note: Note) -> None:
        """Add a note to storage."""
        self._notes[note.id] = note

    def get(self, note_id: int) -> Optional[Note]:
        """Get a note by ID."""
        return self._notes.get(note_id)

    def list(self) -> List[Note]:
        """List all notes."""
        return list(self._notes.values())

    def update(self, note: Note) -> None:
        """Update an existing note."""
        if note.id in self._notes:
            self._notes[note.id] = note

    def delete(self, note_id: int) -> None:
        """Delete a note by ID."""
        self._notes.pop(note_id, None)


class InMemoryEventRepository(EventRepository):
    """In-memory implementation of EventRepository."""

    def __init__(self):
        """Initialize with empty storage."""
        self._events: Dict[int, Event] = {}

    def add(self, event: Event) -> None:
        """Add an event to storage."""
        self._events[event.id] = event

    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID."""
        return self._events.get(event_id)

    def list(self) -> List[Event]:
        """List all events."""
        return list(self._events.values())

    def update(self, event: Event) -> None:
        """Update an existing event."""
        if event.id in self._events:
            self._events[event.id] = event

    def delete(self, event_id: int) -> None:
        """Delete an event by ID."""
        self._events.pop(event_id, None)
