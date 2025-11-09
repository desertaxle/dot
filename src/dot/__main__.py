
from cyclopts import App

from .db import init_database
from .settings import settings

# Initialize database
settings.dot_home.mkdir(parents=True, exist_ok=True)
init_database(settings.db_path)

app = App()
tasks_app = App(name="tasks", alias=["task", "t"])

app.command(tasks_app)

@tasks_app.default()
def add_task(name: str):
    pass




if __name__ == "__main__":
    app()
