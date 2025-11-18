"""Abstract repository interfaces defining contracts for data access."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from dot.domain.models import Task, TaskStatus


class TaskRepository(ABC):
    """Abstract interface for task repository implementations."""

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a new task.

        Args:
            task: The task to add
        """
        pass

    @abstractmethod
    def get(self, task_id: UUID) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task ID

        Returns:
            The task if found, None otherwise
        """
        pass

    @abstractmethod
    def list(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of tasks matching the criteria
        """
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task.

        Args:
            task: The updated task
        """
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """Delete a task.

        Args:
            task_id: The task ID to delete
        """
        pass

    @abstractmethod
    def list_by_date(self, date: date) -> list[Task]:
        """List tasks created on a specific date.

        Args:
            date: The date to filter by

        Returns:
            List of tasks created on the specified date
        """
        pass
