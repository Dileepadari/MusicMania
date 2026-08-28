"""Queries against the Albums table.

``Albums."index"`` is the owning artist's ``uniqid``. It is aliased to
``artist_id`` here so nothing downstream has to quote a SQL keyword.
"""
from __future__ import annotations

import sqlite3

from app.database import query_all, query_one

_SELECT = """
    SELECT uniqid, author, name, year, rating, duration, tracks,
           "index" AS artist_id, img_url, release_date, director, producer, "cast" AS cast_list
    FROM Albums
"""


def list_all() -> list[sqlite3.Row]:
    return query_all(_SELECT + " ORDER BY rating DESC")


def list_top(limit: int = 3) -> list[sqlite3.Row]:
    return query_all(_SELECT + " ORDER BY rating DESC LIMIT ?", (limit,))


def list_by_artist(artist_id: int) -> list[sqlite3.Row]:
    return query_all(_SELECT + ' WHERE "index" = ? ORDER BY year DESC', (artist_id,))


def get(album_id: int) -> sqlite3.Row | None:
    return query_one(_SELECT + " WHERE uniqid = ?", (album_id,))
