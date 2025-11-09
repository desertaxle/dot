"""SQLAlchemy repository implementations for database persistence."""

from typing import List, Optional

from sqlalchemy.orm import Session

from dot.domain.models import Event, Note, Task, TaskStatus
from dot.models import Event as OrmEvent
from dot.models import Note as OrmNote
from dot.models import Task as OrmTask
from dot.models import TaskStatus as OrmTaskStatus
from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, task: Task) -> OrmTask:
        """Convert domain Task to ORM Task."""
        orm_status = OrmTaskStatus(task.status.value)
        orm_task = OrmTask(
            id=task.id,
            title=task.title,
            description=task.description,
            status=orm_status,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        return orm_task

    def _orm_to_domain(self, orm_task: OrmTask) -> Task:
        """Convert ORM Task to domain Task."""
        domain_status = TaskStatus(orm_task.status.value)
        task = Task(
            id=orm_task.id,
            title=orm_task.title,
            description=orm_task.description,
            status=domain_status,
            priority=orm_task.priority,
            created_at=orm_task.created_at,
            updated_at=orm_task.updated_at,
        )
        return task

    def add(self, task: Task) -> None:
        """Add a task to the database."""
        orm_task = self._domain_to_orm(task)
        self.session.add(orm_task)
        self.session.flush()

    def get(self, task_id: int) -> Optional[Task]:
        """Get a task by ID from the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task_id).first()
        if orm_task is None:
            return None
        return self._orm_to_domain(orm_task)

    def list(self) -> List[Task]:
        """List all tasks from the database."""
        orm_tasks = self.session.query(OrmTask).all()
        return [self._orm_to_domain(orm_task) for orm_task in orm_tasks]

    def update(self, task: Task) -> None:
        """Update an existing task in the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task.id).first()
        if orm_task is not None:
            orm_task.title = task.title
            orm_task.description = task.description
            orm_task.status = OrmTaskStatus(task.status.value)
            orm_task.priority = task.priority
            orm_task.updated_at = task.updated_at
            self.session.flush()

    def delete(self, task_id: int) -> None:
        """Delete a task from the database."""
        orm_task = self.session.query(OrmTask).filter(OrmTask.id == task_id).first()
        if orm_task is not None:
            self.session.delete(orm_task)
            self.session.flush()


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, note: Note) -> OrmNote:
        """Convert domain Note to ORM Note."""
        orm_note = OrmNote(
            id=note.id,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
        return orm_note

    def _orm_to_domain(self, orm_note: OrmNote) -> Note:
        """Convert ORM Note to domain Note."""
        note = Note(
            id=orm_note.id,
            title=orm_note.title,
            content=orm_note.content,
            created_at=orm_note.created_at,
            updated_at=orm_note.updated_at,
        )
        return note

    def add(self, note: Note) -> None:
        """Add a note to the database."""
        orm_note = self._domain_to_orm(note)
        self.session.add(orm_note)
        self.session.flush()

    def get(self, note_id: int) -> Optional[Note]:
        """Get a note by ID from the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note_id).first()
        if orm_note is None:
            return None
        return self._orm_to_domain(orm_note)

    def list(self) -> List[Note]:
        """List all notes from the database."""
        orm_notes = self.session.query(OrmNote).all()
        return [self._orm_to_domain(orm_note) for orm_note in orm_notes]

    def update(self, note: Note) -> None:
        """Update an existing note in the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note.id).first()
        if orm_note is not None:
            orm_note.title = note.title
            orm_note.content = note.content
            orm_note.updated_at = note.updated_at
            self.session.flush()

    def delete(self, note_id: int) -> None:
        """Delete a note from the database."""
        orm_note = self.session.query(OrmNote).filter(OrmNote.id == note_id).first()
        if orm_note is not None:
            self.session.delete(orm_note)
            self.session.flush()


class SQLAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, event: Event) -> OrmEvent:
        """Convert domain Event to ORM Event."""
        orm_event = OrmEvent(
            id=event.id,
            title=event.title,
            content=event.content,
            occurred_at=event.occurred_at,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        return orm_event

    def _orm_to_domain(self, orm_event: OrmEvent) -> Event:
        """Convert ORM Event to domain Event."""
        event = Event(
            id=orm_event.id,
            title=orm_event.title,
            content=orm_event.content,
            occurred_at=orm_event.occurred_at,
            created_at=orm_event.created_at,
            updated_at=orm_event.updated_at,
        )
        return event

    def add(self, event: Event) -> None:
        """Add an event to the database."""
        orm_event = self._domain_to_orm(event)
        self.session.add(orm_event)
        self.session.flush()

    def get(self, event_id: int) -> Optional[Event]:
        """Get an event by ID from the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event_id).first()
        if orm_event is None:
            return None
        return self._orm_to_domain(orm_event)

    def list(self) -> List[Event]:
        """List all events from the database."""
        orm_events = self.session.query(OrmEvent).all()
        return [self._orm_to_domain(orm_event) for orm_event in orm_events]

    def update(self, event: Event) -> None:
        """Update an existing event in the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event.id).first()
        if orm_event is not None:
            orm_event.title = event.title
            orm_event.content = event.content
            orm_event.occurred_at = event.occurred_at
            orm_event.updated_at = event.updated_at
            self.session.flush()

    def delete(self, event_id: int) -> None:
        """Delete an event from the database."""
        orm_event = self.session.query(OrmEvent).filter(OrmEvent.id == event_id).first()
        if orm_event is not None:
            self.session.delete(orm_event)
            self.session.flush()
