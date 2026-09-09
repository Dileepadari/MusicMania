"""Test fixtures.

Each test builds a throwaway database from the committed catalogue and the demo
accounts, rather than copying a checked-in `.db`. The old fixture copied one, and
that file carried real accounts: the login below used a real person's password,
in plaintext, in a public repository.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from app.config import TestConfig  # noqa: E402
from app.database import DEMO_USERS, create_schema, load_catalogue, seed_demo  # noqa: E402

CATALOGUE = Path(__file__).resolve().parent.parent / "data" / "catalogue.json"

#: The account the authenticated fixtures sign in as, from the demo seed.
DEMO_USERNAME, DEMO_PASSWORD = DEMO_USERS[0][0], DEMO_USERS[0][1]


@pytest.fixture
def app(tmp_path):
    database = tmp_path / "test.db"

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    create_schema(connection)
    load_catalogue(connection, CATALOGUE)
    seed_demo(connection)
    connection.close()

    class Config(TestConfig):
        DATABASE = str(database)

    application = create_app(Config)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A client logged in as the demo account."""
    response = client.post(
        "/login",
        data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 302, "demo login failed"
    return client
