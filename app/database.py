"""SQLite access: one connection per request, plus the schema migrations.

The original code opened a module-level connection at import time and shared it
across requests, which sqlite3 forbids across threads. Here every request gets
its own connection from ``g`` and it is closed when the request ends.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

import click
from flask import Flask, current_app, g
from werkzeug.security import generate_password_hash

# Prefixes werkzeug uses for the hashes it produces. Anything else in the
# password column is a legacy plaintext value that needs upgrading.
HASH_PREFIXES = ("pbkdf2:", "scrypt:", "argon2:")


def get_db() -> sqlite3.Connection:
    """Return this request's connection, opening it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
    return get_db().execute(sql, params).fetchall()


def query_one(sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
    return get_db().execute(sql, params).fetchone()


def execute(sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
    db = get_db()
    cursor = db.execute(sql, params)
    db.commit()
    return cursor


def executemany(sql: str, seq_of_params: Iterable[Sequence[Any]]) -> None:
    db = get_db()
    db.executemany(sql, seq_of_params)
    db.commit()


# --------------------------------------------------------------------------- #
# Building a database from scratch
# --------------------------------------------------------------------------- #

#: The schema this app expects. Written out rather than shipped as a binary
#: SQLite file: a committed database is a file nobody can review in a diff, and
#: this one used to carry real accounts and their passwords.
SCHEMA = """
CREATE TABLE IF NOT EXISTS Artists (
    uniqid      INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    birth       TEXT,
    languages   TEXT,
    image_url   TEXT,
    Albums      NUMERIC,
    Tracks      NUMERIC,
    Awards      TEXT,
    description TEXT,
    self_page   TEXT,
    wiki_url    TEXT,
    special     INTEGER DEFAULT 0,
    rating      INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Albums (
    uniqid       INTEGER PRIMARY KEY AUTOINCREMENT,
    author       TEXT,
    name         TEXT,
    year         INTEGER,
    rating       REAL DEFAULT 1,
    duration     TEXT,
    tracks       INTEGER,
    "index"      INTEGER,
    img_url      TEXT,
    release_date TEXT,
    director     TEXT,
    producer     TEXT,
    cast         TEXT
);

CREATE TABLE IF NOT EXISTS Songs (
    uniqid     INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT,
    album_name TEXT,
    album_id   INTEGER,
    rating     REAL,
    duration   TEXT,
    artists    TEXT
);

CREATE TABLE IF NOT EXISTS Users (
    userid    INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT,
    img_url   TEXT,
    playlist  TEXT,
    firstname TEXT,
    lastname  TEXT,
    password  TEXT
);

CREATE TABLE IF NOT EXISTS Reviews (
    review_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    userid      INTEGER,
    review      TEXT,
    date        TEXT,
    rating      INTEGER,
    target_type TEXT,
    target_id   INTEGER
);

CREATE TABLE IF NOT EXISTS PlaylistEntries (
    userid   INTEGER NOT NULL,
    song_id  INTEGER NOT NULL,
    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (userid, song_id)
);
"""

#: Demo accounts, created through the same hashing the signup form uses. Named
#: so nobody mistakes them for real ones.
DEMO_USERS = (
    ("demo", "demo1234", "Demo", "Listener", (8, 7, 26, 27, 28)),
    ("critic", "critic1234", "Ana", "Reviewer", (14, 142)),
)

DEMO_REVIEWS = (
    (2, "artist", 12, 5, "Nothing else sounds like this. Put it on and drive."),
    (1, "artist", 12, 4, "The early albums hold up better than I expected."),
    (2, "album", 1, 4, "Two skippable tracks, the rest is on repeat."),
)


def create_schema(db: sqlite3.Connection) -> None:
    """Create every table this app reads. Safe to run against an existing file."""
    db.executescript(SCHEMA)
    db.commit()


def load_catalogue(db: sqlite3.Connection, path: Path | None = None) -> dict[str, int]:
    """Load artists, albums and songs from the committed catalogue file.

    Only fills a table that is empty, so this never doubles up a catalogue or
    overwrites edits made through the app.
    """
    path = path or Path(current_app.config["CATALOGUE"])
    catalogue = json.loads(path.read_text(encoding="utf-8"))

    loaded: dict[str, int] = {}
    for table in ("Artists", "Albums", "Songs"):
        rows = catalogue.get(table, [])
        if not rows:
            continue
        if db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]:
            continue
        columns = list(rows[0])
        placeholders = ", ".join("?" for _ in columns)
        quoted = ", ".join(f'"{c}"' for c in columns)
        db.executemany(
            f'INSERT INTO "{table}" ({quoted}) VALUES ({placeholders})',
            [tuple(row.get(c) for c in columns) for row in rows],
        )
        loaded[table] = len(rows)
    db.commit()
    return loaded


def seed_demo(db: sqlite3.Connection) -> int:
    """Add the demo accounts, their playlists and a few reviews.

    Refuses to touch a database that already has users, so it cannot overwrite
    a real account or double up on a second run.
    """
    if db.execute("SELECT COUNT(*) FROM Users").fetchone()[0]:
        return 0

    for username, password, first, last, playlist in DEMO_USERS:
        db.execute(
            "INSERT INTO Users (username, img_url, playlist, firstname, lastname, password)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                username,
                "images/delhi.jpg",
                ",".join(str(song) for song in playlist),
                first,
                last,
                generate_password_hash(password),
            ),
        )
        userid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.executemany(
            "INSERT OR IGNORE INTO PlaylistEntries (userid, song_id) VALUES (?, ?)",
            [(userid, song) for song in playlist],
        )

    db.executemany(
        "INSERT INTO Reviews (userid, review, date, rating, target_type, target_id)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        [
            (userid, text, "10/09/2026", rating, target_type, target_id)
            for userid, target_type, target_id, rating, text in DEMO_REVIEWS
        ],
    )
    db.commit()
    return len(DEMO_USERS)


# --------------------------------------------------------------------------- #
# Migrations
# --------------------------------------------------------------------------- #

def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _table_exists(db: sqlite3.Connection, table: str) -> bool:
    row = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()
    return row is not None


def migrate(db: sqlite3.Connection) -> list[str]:
    """Bring an existing Music_Mania.db up to the schema this app expects.

    Every step is idempotent, so running it on an already-migrated database is a
    no-op. Returns a list of the steps that actually did something.
    """
    applied: list[str] = []

    # 1. Reviews used to be a flat list with no target, so every review showed up
    #    on every page. Give them a target and point the existing rows at the
    #    spotlight artist, which is the only place they were ever written from.
    if _table_exists(db, "Reviews"):
        review_columns = _columns(db, "Reviews")
        if "target_type" not in review_columns:
            db.execute("ALTER TABLE Reviews ADD COLUMN target_type TEXT")
            db.execute("ALTER TABLE Reviews ADD COLUMN target_id INTEGER")
            db.execute(
                "UPDATE Reviews SET target_type = 'artist', target_id = ? "
                "WHERE target_type IS NULL",
                (12,),
            )
            applied.append("reviews.target")

    # 2. Playlists were a comma-joined string in Users.playlist. Normalise them
    #    into a join table so membership is a query rather than a substring test
    #    (song 4 used to match the playlist "14,").
    if not _table_exists(db, "PlaylistEntries"):
        db.execute(
            """
            CREATE TABLE PlaylistEntries (
                userid  INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (userid, song_id)
            )
            """
        )
        applied.append("playlist.table")

        if _table_exists(db, "Users") and "playlist" in _columns(db, "Users"):
            rows = db.execute("SELECT userid, playlist FROM Users").fetchall()
            entries = [
                (row["userid"], int(part))
                for row in rows
                for part in (row["playlist"] or "").split(",")
                if part.strip().isdigit()
            ]
            if entries:
                db.executemany(
                    "INSERT OR IGNORE INTO PlaylistEntries (userid, song_id) VALUES (?, ?)",
                    entries,
                )
                applied.append(f"playlist.migrated({len(entries)})")

    # 3. Passwords were stored in plaintext. Hash whatever is still readable.
    if _table_exists(db, "Users"):
        legacy = [
            row
            for row in db.execute("SELECT userid, password FROM Users").fetchall()
            if row["password"] and not str(row["password"]).startswith(HASH_PREFIXES)
        ]
        if legacy:
            db.executemany(
                "UPDATE Users SET password = ? WHERE userid = ?",
                [(generate_password_hash(str(r["password"])), r["userid"]) for r in legacy],
            )
            applied.append(f"users.password_hashed({len(legacy)})")

    db.commit()
    return applied


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(migrate_command)
    app.cli.add_command(init_db_command)

    with app.app_context():
        db = get_db()
        # A checkout has no database: the file used to be committed, which is
        # how real accounts ended up in the repository. Build it instead.
        create_schema(db)
        loaded = load_catalogue(db)
        if loaded:
            app.logger.info(
                "catalogue loaded: %s",
                ", ".join(f"{table} {count}" for table, count in loaded.items()),
            )
        applied = migrate(db)
        if applied:
            app.logger.info("database migrations applied: %s", ", ".join(applied))


@click.command("migrate")
def migrate_command() -> None:
    """Apply pending schema migrations to the configured database."""
    applied = migrate(get_db())
    click.echo("up to date" if not applied else "applied: " + ", ".join(applied))


@click.command("init-db")
@click.option("--demo/--no-demo", default=True, help="Also add the demo accounts.")
def init_db_command(demo: bool) -> None:
    """Create the database, load the catalogue and optionally seed demo users."""
    db = get_db()
    create_schema(db)
    loaded = load_catalogue(db)
    click.echo(
        "catalogue: " + (", ".join(f"{t} {n}" for t, n in loaded.items()) or "already present")
    )
    if demo:
        added = seed_demo(db)
        click.echo(f"demo users: {added} added" if added else "demo users: skipped, users exist")
