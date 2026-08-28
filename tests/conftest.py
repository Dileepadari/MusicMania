"""Test fixtures. Each test gets a throwaway copy of the seeded catalogue."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.config import TestConfig  # noqa: E402

SEED_DB = Path(__file__).resolve().parent.parent / "data" / "Music_Mania.db"


@pytest.fixture
def app(tmp_path):
    database = tmp_path / "test.db"
    shutil.copy(SEED_DB, database)

    class Config(TestConfig):
        DATABASE = str(database)

    application = create_app(Config)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A client logged in as the seeded user 'Delhi'."""
    response = client.post(
        "/login", data={"username": "Delhi", "password": "Delhiking"}, follow_redirects=False
    )
    assert response.status_code == 302, "seed login failed"
    return client
