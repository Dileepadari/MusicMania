"""JSON endpoints used by the front end."""
from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from app.repositories import songs as songs_repo
from app.repositories import users as users_repo
from app.security import current_user_id

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.before_request
def require_login():
    """API calls get a 401 rather than a redirect to an HTML page."""
    if current_user_id() is None or g.get("user") is None:
        return jsonify({"error": "authentication required"}), 401
    return None


@bp.post("/playlist")
def add_to_playlist():
    song_id, error = _song_id_from_request()
    if error:
        return error
    users_repo.add_to_playlist(g.user["userid"], song_id)
    return jsonify({"song_id": song_id, "in_playlist": True})


@bp.delete("/playlist/<int:song_id>")
def remove_from_playlist(song_id: int):
    users_repo.remove_from_playlist(g.user["userid"], song_id)
    return jsonify({"song_id": song_id, "in_playlist": False})


def _song_id_from_request() -> tuple[int, None] | tuple[None, tuple]:
    payload = request.get_json(silent=True) or {}
    raw = payload.get("song_id")
    try:
        song_id = int(raw)
    except (TypeError, ValueError):
        return None, (jsonify({"error": "song_id must be an integer"}), 400)
    if songs_repo.get(song_id) is None:
        return None, (jsonify({"error": "no such song"}), 404)
    return song_id, None
