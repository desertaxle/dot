"""SQLAlchemy repository implementations for database persistence."""

from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid7

import whenever
from sqlalchemy.orm import Session

from dot.domain.log_operations import LogEntry
from dot.domain.models import DailyLog, Event, Note, Project, Task, TaskStatus
from dot.models import Event as OrmEvent
from dot.models import LogEntry as OrmLogEntry
from dot.models import Note as OrmNote
from dot.models import Project as OrmProject
from dot.models import ProjectType as OrmProjectType
from dot.models import Task as OrmTask
from dot.models import TaskStatus as OrmTaskStatus
from dot.repository.abstract import (
    EventRepository,
    LogEntryRepository,
    NoteRepository,
    ProjectRepository,
    TaskRepository,
)


class SQLAlchemyTaskRepository(TaskRepository):
    """SQLAlchemy implementation of TaskRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, task: Task) -> OrmTask:
        """Convert domain Task to ORM Task."""
        orm_status = OrmTaskStatus(task.status.value)
        kwargs = {
            "title": task.title,
            "description": task.description,
            "status": orm_status,
            "priority": task.priority,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
        # Only set ID if it exists (for updates), convert UUID to string
        if task.id is not None:
            kwargs["id"] = str(task.id)
        orm_task = OrmTask(**kwargs)
        return orm_task

    def _orm_to_domain(self, orm_task: OrmTask) -> Task:
        """Convert ORM Task to domain Task."""
        domain_status = TaskStatus(orm_task.status.value)
        task = Task(
            id=UUID(orm_task.id),
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
        # Generate UUID if not set
        if task.id is None:
            task.id = uuid7()
        orm_task = self._domain_to_orm(task)
        self.session.add(orm_task)
        self.session.flush()

    def get(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID from the database."""
        orm_task = (
            self.session.query(OrmTask).filter(OrmTask.id == str(task_id)).first()
        )
        if orm_task is None:
            return None
        return self._orm_to_domain(orm_task)

    def list(self) -> List[Task]:
        """List all tasks from the database."""
        orm_tasks = self.session.query(OrmTask).all()
        return [self._orm_to_domain(orm_task) for orm_task in orm_tasks]

    def update(self, task: Task) -> None:
        """Update an existing task in the database."""
        orm_task = (
            self.session.query(OrmTask).filter(OrmTask.id == str(task.id)).first()
        )
        if orm_task is not None:
            orm_task.title = task.title
            orm_task.description = task.description
            orm_task.status = OrmTaskStatus(task.status.value)
            orm_task.priority = task.priority
            orm_task.updated_at = task.updated_at
            self.session.flush()

    def delete(self, task_id: UUID) -> None:
        """Delete a task from the database."""
        orm_task = (
            self.session.query(OrmTask).filter(OrmTask.id == str(task_id)).first()
        )
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
        kwargs = {
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at,
            "updated_at": note.updated_at,
        }
        # Only set ID if it exists (for updates), convert UUID to string
        if note.id is not None:
            kwargs["id"] = str(note.id)
        orm_note = OrmNote(**kwargs)
        return orm_note

    def _orm_to_domain(self, orm_note: OrmNote) -> Note:
        """Convert ORM Note to domain Note."""
        note = Note(
            id=UUID(orm_note.id),
            title=orm_note.title,
            content=orm_note.content,
            created_at=orm_note.created_at,
            updated_at=orm_note.updated_at,
        )
        return note

    def add(self, note: Note) -> None:
        """Add a note to the database."""
        # Generate UUID if not set
        if note.id is None:
            note.id = uuid7()
        orm_note = self._domain_to_orm(note)
        self.session.add(orm_note)
        self.session.flush()

    def get(self, note_id: UUID) -> Optional[Note]:
        """Get a note by ID from the database."""
        orm_note = (
            self.session.query(OrmNote).filter(OrmNote.id == str(note_id)).first()
        )
        if orm_note is None:
            return None
        return self._orm_to_domain(orm_note)

    def list(self) -> List[Note]:
        """List all notes from the database."""
        orm_notes = self.session.query(OrmNote).all()
        return [self._orm_to_domain(orm_note) for orm_note in orm_notes]

    def update(self, note: Note) -> None:
        """Update an existing note in the database."""
        orm_note = (
            self.session.query(OrmNote).filter(OrmNote.id == str(note.id)).first()
        )
        if orm_note is not None:
            orm_note.title = note.title
            orm_note.content = note.content
            orm_note.updated_at = note.updated_at
            self.session.flush()

    def delete(self, note_id: UUID) -> None:
        """Delete a note from the database."""
        orm_note = (
            self.session.query(OrmNote).filter(OrmNote.id == str(note_id)).first()
        )
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
        kwargs = {
            "title": event.title,
            "content": event.content,
            "occurred_at": event.occurred_at,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }
        # Only set ID if it exists (for updates), convert UUID to string
        if event.id is not None:
            kwargs["id"] = str(event.id)
        orm_event = OrmEvent(**kwargs)
        return orm_event

    def _orm_to_domain(self, orm_event: OrmEvent) -> Event:
        """Convert ORM Event to domain Event."""
        event = Event(
            id=UUID(orm_event.id),
            title=orm_event.title,
            content=orm_event.content,
            occurred_at=orm_event.occurred_at,
            created_at=orm_event.created_at,
            updated_at=orm_event.updated_at,
        )
        return event

    def add(self, event: Event) -> None:
        """Add an event to the database."""
        # Generate UUID if not set
        if event.id is None:
            event.id = uuid7()
        orm_event = self._domain_to_orm(event)
        self.session.add(orm_event)
        self.session.flush()

    def get(self, event_id: UUID) -> Optional[Event]:
        """Get an event by ID from the database."""
        orm_event = (
            self.session.query(OrmEvent).filter(OrmEvent.id == str(event_id)).first()
        )
        if orm_event is None:
            return None
        return self._orm_to_domain(orm_event)

    def list(self) -> List[Event]:
        """List all events from the database."""
        orm_events = self.session.query(OrmEvent).all()
        return [self._orm_to_domain(orm_event) for orm_event in orm_events]

    def update(self, event: Event) -> None:
        """Update an existing event in the database."""
        orm_event = (
            self.session.query(OrmEvent).filter(OrmEvent.id == str(event.id)).first()
        )
        if orm_event is not None:
            orm_event.title = event.title
            orm_event.content = event.content
            orm_event.occurred_at = event.occurred_at
            orm_event.updated_at = event.updated_at
            self.session.flush()

    def delete(self, event_id: UUID) -> None:
        """Delete an event from the database."""
        orm_event = (
            self.session.query(OrmEvent).filter(OrmEvent.id == str(event_id)).first()
        )
        if orm_event is not None:
            self.session.delete(orm_event)
            self.session.flush()


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, project: Project) -> OrmProject:
        """Convert domain Project to ORM Project."""
        # Determine project type and type-specific fields
        project_type = OrmProjectType.PROJECT
        date_field = None
        week_start_field = None
        year_field = None
        month_field = None

        if isinstance(project, DailyLog):
            project_type = OrmProjectType.DAILY_LOG
            # Convert whenever.Date to Python date
            date_field = date(project.date.year, project.date.month, project.date.day)

        kwargs = {
            "name": project.name,
            "description": project.description,
            "type": project_type,
            "date": date_field,
            "week_start": week_start_field,
            "year": year_field,
            "month": month_field,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }
        # Only set ID if it exists (for updates), convert UUID to string
        if project.id is not None:
            kwargs["id"] = str(project.id)
        orm_project = OrmProject(**kwargs)
        return orm_project

    def _orm_to_domain(self, orm_project: OrmProject) -> Project:
        """Convert ORM Project to domain Project."""
        # Convert based on project type
        if (
            orm_project.type == OrmProjectType.DAILY_LOG
            and orm_project.date is not None
        ):
            # Convert Python date to whenever.Date
            whenever_date = whenever.Date(
                orm_project.date.year,
                orm_project.date.month,
                orm_project.date.day,
            )
            return DailyLog(
                id=UUID(orm_project.id),
                name=orm_project.name,
                description=orm_project.description,
                date=whenever_date,
                created_at=orm_project.created_at,
                updated_at=orm_project.updated_at,
            )
        else:
            # Regular project
            return Project(
                id=UUID(orm_project.id),
                name=orm_project.name,
                description=orm_project.description,
                created_at=orm_project.created_at,
                updated_at=orm_project.updated_at,
            )

    def add(self, project: Project) -> None:
        """Add a project to the database."""
        # Generate UUID if not set
        if project.id is None:
            project.id = uuid7()
        orm_project = self._domain_to_orm(project)
        self.session.add(orm_project)
        self.session.flush()

    def get(self, project_id: UUID) -> Optional[Project]:
        """Get a project by ID from the database."""
        orm_project = (
            self.session.query(OrmProject)
            .filter(OrmProject.id == str(project_id))
            .first()
        )
        if orm_project is None:
            return None
        return self._orm_to_domain(orm_project)

    def list(self) -> List[Project]:
        """List all projects from the database."""
        orm_projects = self.session.query(OrmProject).all()
        return [self._orm_to_domain(orm_project) for orm_project in orm_projects]

    def update(self, project: Project) -> None:
        """Update an existing project in the database."""
        orm_project = (
            self.session.query(OrmProject)
            .filter(OrmProject.id == str(project.id))
            .first()
        )
        if orm_project is not None:
            orm_project.name = project.name
            orm_project.description = project.description
            orm_project.updated_at = project.updated_at

            self.session.flush()

    def delete(self, project_id: UUID) -> None:
        """Delete a project from the database."""
        orm_project = (
            self.session.query(OrmProject)
            .filter(OrmProject.id == str(project_id))
            .first()
        )
        if orm_project is not None:
            self.session.delete(orm_project)
            self.session.flush()

    def get_daily_log(self, log_date: whenever.Date) -> DailyLog:
        """Get or create a daily log for the given date."""
        # Convert whenever.Date to Python date for query
        py_date = date(log_date.year, log_date.month, log_date.day)

        # Search for existing daily log
        orm_project = (
            self.session.query(OrmProject)
            .filter(
                OrmProject.type == OrmProjectType.DAILY_LOG,
                OrmProject.date == py_date,
            )
            .first()
        )

        if orm_project is not None:
            return self._orm_to_domain(orm_project)  # type: ignore

        # Create new daily log
        now = datetime.now(timezone.utc)
        daily_log = DailyLog(
            name=f"Daily Log {log_date}",
            date=log_date,
            created_at=now,
            updated_at=now,
        )

        # Generate UUID and add to database
        daily_log.id = uuid7()
        orm_daily_log = self._domain_to_orm(daily_log)
        self.session.add(orm_daily_log)
        self.session.flush()
        return daily_log


class SQLAlchemyLogEntryRepository(LogEntryRepository):
    """SQLAlchemy implementation of LogEntryRepository."""

    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session

    def _domain_to_orm(self, log_entry: LogEntry) -> OrmLogEntry:
        """Convert domain LogEntry to ORM LogEntry."""
        # Convert whenever.Date to datetime for entry_date
        entry_datetime = datetime(
            log_entry.entry_date.year,
            log_entry.entry_date.month,
            log_entry.entry_date.day,
            tzinfo=timezone.utc,
        )

        kwargs = {
            "project_id": str(
                log_entry.log_id
            ),  # Domain uses log_id, ORM uses project_id, convert UUID to string
            "task_id": str(log_entry.task_id) if log_entry.task_id else None,
            "note_id": str(log_entry.note_id) if log_entry.note_id else None,
            "event_id": str(log_entry.event_id) if log_entry.event_id else None,
            "entry_date": entry_datetime,
        }
        # Only set ID if it exists (for updates), convert UUID to string
        if log_entry.id is not None:
            kwargs["id"] = str(log_entry.id)
        orm_log_entry = OrmLogEntry(**kwargs)
        return orm_log_entry

    def _orm_to_domain(self, orm_log_entry: OrmLogEntry) -> LogEntry:
        """Convert ORM LogEntry to domain LogEntry."""
        # Convert datetime to whenever.Date (use date portion only)
        entry_date = whenever.Date(
            orm_log_entry.entry_date.year,
            orm_log_entry.entry_date.month,
            orm_log_entry.entry_date.day,
        )

        log_entry = LogEntry(
            id=UUID(orm_log_entry.id),
            log_id=UUID(
                orm_log_entry.project_id
            ),  # ORM uses project_id, domain uses log_id
            task_id=UUID(orm_log_entry.task_id) if orm_log_entry.task_id else None,
            note_id=UUID(orm_log_entry.note_id) if orm_log_entry.note_id else None,
            event_id=UUID(orm_log_entry.event_id) if orm_log_entry.event_id else None,
            entry_date=entry_date,
        )
        return log_entry

    def add(self, log_entry: LogEntry) -> None:
        """Add a log entry to the database."""
        # Generate UUID if not set
        if log_entry.id is None:
            log_entry.id = uuid7()
        orm_log_entry = self._domain_to_orm(log_entry)
        self.session.add(orm_log_entry)
        self.session.flush()

    def get(self, entry_id: UUID) -> Optional[LogEntry]:
        """Get a log entry by ID from the database."""
        orm_log_entry = (
            self.session.query(OrmLogEntry)
            .filter(OrmLogEntry.id == str(entry_id))
            .first()
        )
        if orm_log_entry is None:
            return None
        return self._orm_to_domain(orm_log_entry)

    def list(self) -> List[LogEntry]:
        """List all log entries from the database."""
        orm_log_entries = self.session.query(OrmLogEntry).all()
        return [self._orm_to_domain(orm_log_entry) for orm_log_entry in orm_log_entries]

    def delete(self, entry_id: UUID) -> None:
        """Delete a log entry from the database."""
        orm_log_entry = (
            self.session.query(OrmLogEntry)
            .filter(OrmLogEntry.id == str(entry_id))
            .first()
        )
        if orm_log_entry is not None:
            self.session.delete(orm_log_entry)
            self.session.flush()

    def get_by_log_id(self, log_id: UUID) -> List[LogEntry]:
        """Get all log entries for a specific log."""
        orm_log_entries = (
            self.session.query(OrmLogEntry)
            .filter(OrmLogEntry.project_id == str(log_id))
            .order_by(OrmLogEntry.entry_date)
            .all()
        )
        return [self._orm_to_domain(orm_log_entry) for orm_log_entry in orm_log_entries]
