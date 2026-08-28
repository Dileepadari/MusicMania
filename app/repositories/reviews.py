"""Reviews, scoped to the artist or album they were written about."""
from __future__ import annotations

import sqlite3
from datetime import date

from app.database import execute, query_all, query_one

ARTIST = "artist"
ALBUM = "album"


def list_for(target_type: str, target_id: int) -> list[sqlite3.Row]:
    return query_all(
        """
        SELECT r.review_id, r.review, r.date, r.rating,
               u.userid, u.username, u.firstname, u.lastname, u.img_url
        FROM Reviews r
        LEFT JOIN Users u ON u.userid = r.userid
        WHERE r.target_type = ? AND r.target_id = ?
        ORDER BY r.review_id DESC
        """,
        (target_type, target_id),
    )


def average_for(target_type: str, target_id: int) -> float | None:
    row = query_one(
        "SELECT AVG(rating) AS avg FROM Reviews WHERE target_type = ? AND target_id = ?",
        (target_type, target_id),
    )
    return round(row["avg"], 1) if row and row["avg"] is not None else None


def add(user_id: int, target_type: str, target_id: int, rating: int, review: str) -> int:
    cursor = execute(
        "INSERT INTO Reviews (userid, review, date, rating, target_type, target_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, review, date.today().strftime("%d/%m/%Y"), rating, target_type, target_id),
    )
    return int(cursor.lastrowid)
