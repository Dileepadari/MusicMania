"""Signup, login, logout."""
from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, redirect, render_template, request, url_for

from app.repositories import users as users_repo
from app.security import login_required, login_user, logout_user

bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 6


def _safe_redirect_target(target: str | None) -> str:
    """Only follow a ``next`` parameter that points back at this site."""
    if not target:
        return url_for("main.index")
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/"):
        return url_for("main.index")
    return target


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = users_repo.get_by_username(username)
        if user and users_repo.verify_password(user, password):
            login_user(user["userid"])
            return redirect(_safe_redirect_target(request.args.get("next")))
        return render_template("auth/login.html", error="Incorrect username or password."), 401
    return render_template("auth/login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form = {
            "username": request.form.get("username", "").strip(),
            "firstname": request.form.get("firstname", "").strip(),
            "lastname": request.form.get("lastname", "").strip(),
        }
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = _validate_signup(form, password, confirm)
        if error:
            return render_template("auth/signup.html", error=error, form=form), 400

        user_id = users_repo.create(
            form["username"], password, form["firstname"], form["lastname"]
        )
        login_user(user_id)
        return redirect(url_for("main.index"))
    return render_template("auth/signup.html", form={})


def _validate_signup(form: dict[str, str], password: str, confirm: str) -> str | None:
    if not all([form["username"], form["firstname"], form["lastname"], password]):
        return "Every field is required."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return "The two passwords do not match."
    if users_repo.get_by_username(form["username"]):
        return "That username is already taken."
    return None


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
