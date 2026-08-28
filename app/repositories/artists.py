"""Queries against the Artists table."""
from __future__ import annotations

import sqlite3

from app.database import query_all, query_one

_SELECT = """
    SELECT uniqid, name, birth, languages, image_url,
           "Albums" AS album_count, "Tracks" AS track_count,
           "Awards" AS awards, description, self_page, wiki_url, special, rating
    FROM Artists
"""


def list_all() -> list[sqlite3.Row]:
    return query_all(_SELECT + " ORDER BY rating DESC, name")


def list_featured() -> list[sqlite3.Row]:
    """Artists flagged ``special``, shown in the Top Artists row on the home page."""
    return query_all(_SELECT + " WHERE special = 1 ORDER BY rating DESC, name")


def get_by_id(artist_id: int) -> sqlite3.Row | None:
    return query_one(_SELECT + " WHERE uniqid = ?", (artist_id,))


def get_by_name(name: str) -> sqlite3.Row | None:
    return query_one(_SELECT + " WHERE name = ?", (name,))


def list_others(exclude_id: int, limit: int = 4) -> list[sqlite3.Row]:
    return query_all(
        _SELECT + " WHERE uniqid != ? ORDER BY rating DESC, name LIMIT ?",
        (exclude_id, limit),
    )
