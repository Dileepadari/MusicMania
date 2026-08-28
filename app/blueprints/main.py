"""Home, playlist, search and about pages."""
from __future__ import annotations

from flask import Blueprint, g, render_template

from app.repositories import albums as albums_repo
from app.repositories import artists as artists_repo
from app.repositories import songs as songs_repo
from app.repositories import users as users_repo
from app.security import login_required

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def index():
    top_songs = songs_repo.list_top(6)
    return render_template(
        "index.html",
        featured_artists=artists_repo.list_featured(),
        top_albums=albums_repo.list_top(6),
        top_songs=top_songs,
        covers=songs_repo.cover_by_album(),
        playlist_ids=users_repo.playlist_song_ids(g.user["userid"]),
    )


@bp.route("/playlist")
@login_required
def playlist():
    return render_template("playlist.html", songs=users_repo.playlist_songs(g.user["userid"]))


@bp.route("/search")
@login_required
def search():
    return render_template("search.html")


@bp.route("/about")
@login_required
def about():
    return render_template("about.html")
