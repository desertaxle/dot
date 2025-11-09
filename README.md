# dot

A CLI bullet journal for task, event, and notes management with SQLite persistence.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager

### Installation

1. Clone the repository and install dependencies:

```bash
git clone https://github.com/desertaxle/dot.git
cd dot
uv sync --dev
```

2. Install pre-commit hooks:

```bash
uv run prek install
```

### Pre-commit Hooks

This project uses [prek](https://prek.j178.dev/) for automatic code quality checks before commits. The following hooks run automatically:

- **ruff check** - Linting with automatic fixes (`--fix`)
- **ruff format** - Code formatting
- **ty** - Type checking

If ruff finds formatting issues, they will be automatically fixed. You'll need to stage the changes again before committing.

To manually run all pre-commit hooks:

```bash
uv run prek run
```

To run specific hooks:

```bash
uv run prek run ruff
uv run prek run ruff-format
uv run prek run ty
```

### Running Checks Locally

Run the CI checks manually:

```bash
uv run ruff check src/
uv run ruff format --check src/
uv run ty check
```

### Testing and Coverage

This project requires 100% code coverage. Run tests locally:

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests with coverage report (shows missing lines)
uv run pytest tests/ --cov=. --cov-report=term-missing -v

# Generate HTML coverage report
uv run pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in browser to view detailed coverage
```

**Coverage Requirements:**
- Minimum coverage: 100%
- Branch coverage enabled (all if/else paths must be tested)
- Enforced in CI/CD - PRs cannot merge without 100% coverage

## License

TBD
