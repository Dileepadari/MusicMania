"""Queries against the Songs table."""
from __future__ import annotations

import sqlite3

from app.database import query_all, query_one

_SELECT = """
    SELECT uniqid, name, album_name, album_id, rating, duration, artists
    FROM Songs
"""


def list_top(limit: int = 3) -> list[sqlite3.Row]:
    return query_all(_SELECT + " ORDER BY rating DESC LIMIT ?", (limit,))


def list_by_album(album_id: int) -> list[sqlite3.Row]:
    return query_all(_SELECT + " WHERE album_id = ? ORDER BY uniqid", (album_id,))


def get(song_id: int) -> sqlite3.Row | None:
    return query_one(_SELECT + " WHERE uniqid = ?", (song_id,))


def average_rating(album_id: int) -> float | None:
    row = query_one("SELECT AVG(rating) AS avg FROM Songs WHERE album_id = ?", (album_id,))
    return round(row["avg"], 2) if row and row["avg"] is not None else None


def cover_by_album() -> dict[int, str]:
    """Map album id -> cover image, for song cards that show album art."""
    rows = query_all("SELECT uniqid, img_url FROM Albums")
    return {row["uniqid"]: row["img_url"] for row in rows}
