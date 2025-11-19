"""SQLAlchemy repository implementations."""

from datetime import UTC, date
from uuid import UUID

from sqlalchemy.orm import Session

from dot.domain.models import Event, Note, Task, TaskStatus
from dot.models import EventORM, NoteORM, TaskORM
from dot.repository.abstract import EventRepository, NoteRepository, TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def add(self, task: Task) -> None:
        """Add a new task."""
        task_orm = self._to_orm(task)
        self._session.add(task_orm)
        self._session.commit()

    def get(self, task_id: UUID) -> Task | None:
        """Get a task by ID."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task_orm is None:
            return None
        return self._to_domain(task_orm)

    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status."""
        query = self._session.query(TaskORM)
        if status is not None:
            query = query.filter(TaskORM.status == status.value)
        task_orms = query.all()
        return [self._to_domain(task_orm) for task_orm in task_orms]

    def update(self, task: Task) -> None:
        """Update an existing task."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task.id).first()
        if task_orm is not None:
            task_orm.title = task.title
            task_orm.description = task.description
            task_orm.status = task.status.value
            task_orm.updated_at = task.updated_at
            self._session.commit()

    def delete(self, task_id: UUID) -> None:
        """Delete a task."""
        task_orm = self._session.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task_orm is not None:
            self._session.delete(task_orm)
            self._session.commit()

    def list_by_date(self, target_date: date) -> list[Task]:
        """List tasks created on a specific date."""
        from datetime import datetime, timedelta

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        task_orms = (
            self._session.query(TaskORM)
            .filter(TaskORM.created_at >= start_of_day)
            .filter(TaskORM.created_at < end_of_day)
            .all()
        )
        return [self._to_domain(task_orm) for task_orm in task_orms]

    @staticmethod
    def _to_orm(task: Task) -> TaskORM:
        """Convert domain Task to ORM TaskORM.

        Args:
            task: Domain task

        Returns:
            ORM task
        """
        return TaskORM(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            created_at=task.created_at.replace(tzinfo=None),
            updated_at=task.updated_at.replace(tzinfo=None),
        )

    @staticmethod
    def _to_domain(task_orm: TaskORM) -> Task:
        """Convert ORM TaskORM to domain Task.

        Args:
            task_orm: ORM task

        Returns:
            Domain task
        """
        return Task(
            id=task_orm.id,
            title=task_orm.title,
            description=task_orm.description,
            status=TaskStatus(task_orm.status),
            created_at=task_orm.created_at.replace(tzinfo=UTC),
            updated_at=task_orm.updated_at.replace(tzinfo=UTC),
        )


class SQLAlchemyEventRepository(EventRepository):
    """SQLAlchemy implementation of EventRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def add(self, event: Event) -> None:
        """Add a new event."""
        event_orm = self._to_orm(event)
        self._session.add(event_orm)
        self._session.commit()

    def get(self, event_id: UUID) -> Event | None:
        """Get an event by ID."""
        event_orm = (
            self._session.query(EventORM).filter(EventORM.id == event_id).first()
        )
        if event_orm is None:
            return None
        return self._to_domain(event_orm)

    def list(self) -> list[Event]:
        """List all events, sorted chronologically by occurred_at."""
        event_orms = self._session.query(EventORM).order_by(EventORM.occurred_at).all()
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def list_by_date(self, target_date: date) -> list[Event]:
        """List events that occurred on a specific date, sorted chronologically."""
        from datetime import datetime, timedelta

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        event_orms = (
            self._session.query(EventORM)
            .filter(EventORM.occurred_at >= start_of_day)
            .filter(EventORM.occurred_at < end_of_day)
            .order_by(EventORM.occurred_at)
            .all()
        )
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def list_by_range(self, start_date: date, end_date: date) -> list[Event]:
        """List events within a date range (inclusive), sorted chronologically."""
        from datetime import datetime, timedelta

        start_of_range = datetime.combine(start_date, datetime.min.time())
        end_of_range = datetime.combine(end_date, datetime.min.time()) + timedelta(
            days=1
        )

        event_orms = (
            self._session.query(EventORM)
            .filter(EventORM.occurred_at >= start_of_range)
            .filter(EventORM.occurred_at < end_of_range)
            .order_by(EventORM.occurred_at)
            .all()
        )
        return [self._to_domain(event_orm) for event_orm in event_orms]

    def delete(self, event_id: UUID) -> None:
        """Delete an event."""
        event_orm = (
            self._session.query(EventORM).filter(EventORM.id == event_id).first()
        )
        if event_orm is not None:
            self._session.delete(event_orm)
            self._session.commit()

    @staticmethod
    def _to_orm(event: Event) -> EventORM:
        """Convert domain Event to ORM EventORM.

        Args:
            event: Domain event

        Returns:
            ORM event
        """
        return EventORM(
            id=event.id,
            title=event.title,
            description=event.description,
            occurred_at=event.occurred_at.replace(tzinfo=None),
            created_at=event.created_at.replace(tzinfo=None),
        )

    @staticmethod
    def _to_domain(event_orm: EventORM) -> Event:
        """Convert ORM EventORM to domain Event.

        Args:
            event_orm: ORM event

        Returns:
            Domain event
        """
        return Event(
            id=event_orm.id,
            title=event_orm.title,
            description=event_orm.description,
            occurred_at=event_orm.occurred_at.replace(tzinfo=UTC),
            created_at=event_orm.created_at.replace(tzinfo=UTC),
        )


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy session
        """
        self._session = session

    def add(self, note: Note) -> None:
        """Add a new note."""
        note_orm = self._to_orm(note)
        self._session.add(note_orm)
        self._session.commit()

    def get(self, note_id: UUID) -> Note | None:
        """Get a note by ID."""
        note_orm = self._session.query(NoteORM).filter(NoteORM.id == note_id).first()
        if note_orm is None:
            return None
        return self._to_domain(note_orm)

    def list(self) -> list[Note]:
        """List all notes, sorted by creation date (most recent first)."""
        note_orms = (
            self._session.query(NoteORM).order_by(NoteORM.created_at.desc()).all()
        )
        return [self._to_domain(note_orm) for note_orm in note_orms]

    def list_by_date(self, target_date: date) -> list[Note]:
        """List notes created on a specific date, sorted by creation time."""
        from datetime import datetime, timedelta

        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        note_orms = (
            self._session.query(NoteORM)
            .filter(NoteORM.created_at >= start_of_day)
            .filter(NoteORM.created_at < end_of_day)
            .order_by(NoteORM.created_at)
            .all()
        )
        return [self._to_domain(note_orm) for note_orm in note_orms]

    def delete(self, note_id: UUID) -> None:
        """Delete a note."""
        note_orm = self._session.query(NoteORM).filter(NoteORM.id == note_id).first()
        if note_orm is not None:
            self._session.delete(note_orm)
            self._session.commit()

    @staticmethod
    def _to_orm(note: Note) -> NoteORM:
        """Convert domain Note to ORM NoteORM.

        Args:
            note: Domain note

        Returns:
            ORM note
        """
        return NoteORM(
            id=note.id,
            title=note.title,
            content=note.content,
            created_at=note.created_at.replace(tzinfo=None),
        )

    @staticmethod
    def _to_domain(note_orm: NoteORM) -> Note:
        """Convert ORM NoteORM to domain Note.

        Args:
            note_orm: ORM note

        Returns:
            Domain note
        """
        return Note(
            id=note_orm.id,
            title=note_orm.title,
            content=note_orm.content,
            created_at=note_orm.created_at.replace(tzinfo=UTC),
        )
