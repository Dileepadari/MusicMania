"""User records and the playlist join table."""
from __future__ import annotations

import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from app.database import execute, query_all, query_one

DEFAULT_AVATAR = "images/delhi.jpg"


def get(user_id: int) -> sqlite3.Row | None:
    return query_one(
        "SELECT userid, username, img_url, firstname, lastname FROM Users WHERE userid = ?",
        (user_id,),
    )


def get_by_username(username: str) -> sqlite3.Row | None:
    return query_one("SELECT * FROM Users WHERE username = ?", (username,))


def list_all() -> dict[int, sqlite3.Row]:
    rows = query_all("SELECT userid, username, img_url, firstname, lastname FROM Users")
    return {row["userid"]: row for row in rows}


def create(username: str, password: str, firstname: str, lastname: str) -> int:
    cursor = execute(
        "INSERT INTO Users (username, img_url, firstname, lastname, password, playlist) "
        "VALUES (?, ?, ?, ?, ?, '')",
        (username, DEFAULT_AVATAR, firstname, lastname, generate_password_hash(password)),
    )
    return int(cursor.lastrowid)


def verify_password(user: sqlite3.Row, password: str) -> bool:
    stored = user["password"]
    if not stored:
        return False
    return check_password_hash(stored, password)


# --------------------------------------------------------------------------- #
# Playlist
# --------------------------------------------------------------------------- #

def playlist_song_ids(user_id: int) -> set[int]:
    rows = query_all("SELECT song_id FROM PlaylistEntries WHERE userid = ?", (user_id,))
    return {row["song_id"] for row in rows}


def playlist_songs(user_id: int) -> list[sqlite3.Row]:
    return query_all(
        """
        SELECT s.uniqid, s.name, s.album_name, s.album_id, s.rating, s.duration, s.artists
        FROM PlaylistEntries p
        JOIN Songs s ON s.uniqid = p.song_id
        WHERE p.userid = ?
        ORDER BY p.added_at DESC, s.name
        """,
        (user_id,),
    )


def add_to_playlist(user_id: int, song_id: int) -> None:
    execute(
        "INSERT OR IGNORE INTO PlaylistEntries (userid, song_id) VALUES (?, ?)",
        (user_id, song_id),
    )


def remove_from_playlist(user_id: int, song_id: int) -> None:
    execute(
        "DELETE FROM PlaylistEntries WHERE userid = ? AND song_id = ?",
        (user_id, song_id),
    )
