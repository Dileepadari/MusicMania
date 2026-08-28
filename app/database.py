"""SQLite access: one connection per request, plus the schema migrations.

The original code opened a module-level connection at import time and shared it
across requests, which sqlite3 forbids across threads. Here every request gets
its own connection from ``g`` and it is closed when the request ends.
"""
from __future__ import annotations

import sqlite3
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

    with app.app_context():
        applied = migrate(get_db())
        if applied:
            app.logger.info("database migrations applied: %s", ", ".join(applied))


@click.command("migrate")
def migrate_command() -> None:
    """Apply pending schema migrations to the configured database."""
    applied = migrate(get_db())
    click.echo("up to date" if not applied else "applied: " + ", ".join(applied))
