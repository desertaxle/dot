from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    dot_home: Path = Field(default=Path.home().joinpath(".dot"))
    db_path: Path = Field(
        default_factory=lambda data: data["dot_home"].joinpath("journal.db")
    )


settings = Settings()
