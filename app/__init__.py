"""Music Mania - Flask application factory."""
from __future__ import annotations

from flask import Flask, g, render_template, session

from app import database
from app.config import Config
from app.repositories import users as users_repo
from app.security import SESSION_KEY


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    database.init_app(app)
    _register_blueprints(app)
    _register_hooks(app)
    _register_filters(app)
    _register_error_handlers(app)
    return app


def _register_blueprints(app: Flask) -> None:
    from app.blueprints import api, auth, catalog, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(api.bp)


def _register_hooks(app: Flask) -> None:
    @app.before_request
    def load_current_user() -> None:
        """Expose the signed-in user as ``g.user`` for the whole request."""
        user_id = session.get(SESSION_KEY)
        g.user = users_repo.get(user_id) if user_id is not None else None
        if user_id is not None and g.user is None:
            # Session points at a user that no longer exists.
            session.pop(SESSION_KEY, None)

    @app.context_processor
    def inject_user() -> dict:
        return {"current_user": g.get("user")}


def _register_filters(app: Flask) -> None:
    import os

    from flask import url_for

    PLACEHOLDER = "img/placeholder.svg"

    @app.template_filter("media")
    def media(path: str | None) -> str:
        """Resolve an image path from the database to a static URL.

        Paths in the database are inconsistent: some start with a slash, some do
        not, some are empty, and a few name a file that was never committed.
        Normalise all of that in one place and fall back to the placeholder
        rather than rendering a broken image.
        """
        cleaned = (path or "").strip().lstrip("/")
        if not cleaned or not os.path.isfile(os.path.join(app.static_folder, cleaned)):
            cleaned = PLACEHOLDER
        return url_for("static", filename=cleaned)

    @app.template_filter("tidy")
    def tidy(value: object) -> str:
        """Trim the stray whitespace that the seed data is full of."""
        return " ".join(str(value or "").split())

    @app.template_filter("stars")
    def stars(rating: object, out_of: int = 5) -> str:
        """Render a rating as filled/empty star characters."""
        try:
            filled = max(0, min(out_of, int(round(float(rating or 0)))))
        except (TypeError, ValueError):
            filled = 0
        return "★" * filled + "☆" * (out_of - filled)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500
