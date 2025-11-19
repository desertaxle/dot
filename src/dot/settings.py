"""Settings configuration for Dot CLI application."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with configurable database path.

    Configuration can be provided via:
    - Environment variables (DOT_HOME)
    - Default values
    """

    dot_home: Path = Path.home() / ".dot"

    @property
    def db_path(self) -> Path:
        """Get the full path to the SQLite database file."""
        return self.dot_home / "dot.db"

    def ensure_dot_home_exists(self) -> None:
        """Create the dot_home directory if it doesn't exist."""
        self.dot_home.mkdir(parents=True, exist_ok=True)
