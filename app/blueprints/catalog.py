"""Artist, album and spotlight pages."""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from app.repositories import albums as albums_repo
from app.repositories import artists as artists_repo
from app.repositories import reviews as reviews_repo
from app.repositories import songs as songs_repo
from app.repositories import users as users_repo
from app.security import login_required

bp = Blueprint("catalog", __name__)


@bp.route("/artists")
@login_required
def artists():
    return render_template("catalog/artists.html", artists=artists_repo.list_all())


@bp.route("/artist/<path:artist_name>")
@login_required
def artist(artist_name: str):
    record = artists_repo.get_by_name(artist_name)
    if record is None:
        abort(404)
    return render_template(
        "catalog/artist.html",
        artist=record,
        albums=albums_repo.list_by_artist(record["uniqid"]),
        others=artists_repo.list_others(record["uniqid"]),
        reviews=reviews_repo.list_for(reviews_repo.ARTIST, record["uniqid"]),
        review_average=reviews_repo.average_for(reviews_repo.ARTIST, record["uniqid"]),
    )


@bp.route("/album/<int:album_id>")
@login_required
def album(album_id: int):
    record = albums_repo.get(album_id)
    if record is None:
        abort(404)
    tracks = songs_repo.list_by_album(album_id)
    track_average = songs_repo.average_rating(album_id)
    return render_template(
        "catalog/album.html",
        album=record,
        tracks=tracks,
        track_average=track_average,
        overall_rating=_overall(record["rating"], track_average),
        playlist_ids=users_repo.playlist_song_ids(g.user["userid"]),
        reviews=reviews_repo.list_for(reviews_repo.ALBUM, album_id),
        review_average=reviews_repo.average_for(reviews_repo.ALBUM, album_id),
    )


@bp.route("/spotlight")
@login_required
def spotlight():
    artist_id = current_app.config["SPOTLIGHT_ARTIST_ID"]
    record = artists_repo.get_by_id(artist_id)
    if record is None:
        abort(404)
    return render_template(
        "catalog/spotlight.html",
        artist=record,
        albums=albums_repo.list_by_artist(artist_id),
        reviews=reviews_repo.list_for(reviews_repo.ARTIST, artist_id),
        review_average=reviews_repo.average_for(reviews_repo.ARTIST, artist_id),
        release_date=_release_countdown(),
    )


@bp.route("/review/<target_type>/<int:target_id>", methods=["POST"])
@login_required
def add_review(target_type: str, target_id: int):
    if target_type not in (reviews_repo.ARTIST, reviews_repo.ALBUM):
        abort(404)

    back = _review_target_url(target_type, target_id)
    rating = request.form.get("rating", type=int)
    review = request.form.get("review", "").strip()

    if rating is None or not 1 <= rating <= 5:
        flash("Pick a rating between 1 and 5 stars.", "error")
    elif not review:
        flash("Write a few words to go with your rating.", "error")
    else:
        reviews_repo.add(g.user["userid"], target_type, target_id, rating, review)
        flash("Thanks, your review is live.", "success")
    # No #reviews fragment: the flash message at the top of the page is the
    # confirmation, and an anchor jump competes with it as images settle.
    return redirect(back)


def _review_target_url(target_type: str, target_id: int) -> str:
    if target_type == reviews_repo.ALBUM:
        if albums_repo.get(target_id) is None:
            abort(404)
        return url_for("catalog.album", album_id=target_id)

    record = artists_repo.get_by_id(target_id)
    if record is None:
        abort(404)
    if target_id == current_app.config["SPOTLIGHT_ARTIST_ID"]:
        return url_for("catalog.spotlight")
    return url_for("catalog.artist", artist_name=record["name"])


def _overall(album_rating: object, track_average: float | None) -> float | None:
    """Blend the album's own rating with the average of its tracks."""
    try:
        album_value = float(album_rating)
    except (TypeError, ValueError):
        return track_average
    if track_average is None:
        return round(album_value, 2)
    return round((album_value + track_average) / 2, 2)


def _release_countdown() -> str | None:
    """The configured release date, or None once it is in the past."""
    raw = current_app.config.get("SPOTLIGHT_RELEASE_DATE")
    if not raw:
        return None
    try:
        target = datetime.fromisoformat(raw)
    except ValueError:
        current_app.logger.warning("SPOTLIGHT_RELEASE_DATE is not ISO 8601: %r", raw)
        return None
    now = datetime.now(target.tzinfo) if target.tzinfo else datetime.now()
    return raw if target > now else None
