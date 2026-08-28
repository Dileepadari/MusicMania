"""Session helpers shared by every blueprint."""
from __future__ import annotations

import functools
from typing import Callable

from flask import g, redirect, request, session, url_for

SESSION_KEY = "user_id"


def login_user(user_id: int) -> None:
    session.clear()
    session[SESSION_KEY] = int(user_id)


def logout_user() -> None:
    session.pop(SESSION_KEY, None)


def current_user_id() -> int | None:
    return session.get(SESSION_KEY)


def login_required(view: Callable) -> Callable:
    """Send anonymous visitors to the login page, remembering where they wanted to go."""

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)

    return wrapped
