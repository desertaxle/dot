"""Shared pytest configuration and fixtures."""

from datetime import datetime, timezone

import pytest


@pytest.fixture
def now():
    """Current time in UTC."""
    return datetime.now(timezone.utc)
