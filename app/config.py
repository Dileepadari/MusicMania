"""Application configuration.

Values are read from the environment so the same code runs locally and in a
deployment without edits. Only SECRET_KEY has no safe default: the development
fallback below is deliberately obvious so it is never mistaken for a real key.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = BASE_DIR / "data" / "Music_Mania.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    DATABASE = os.environ.get("DATABASE", str(DEFAULT_DATABASE))

    # Artist shown on the /spotlight page.
    SPOTLIGHT_ARTIST_ID = int(os.environ.get("SPOTLIGHT_ARTIST_ID", "12"))
    # Countdown target on the spotlight page (ISO 8601). Hidden once it passes.
    SPOTLIGHT_RELEASE_DATE = os.environ.get("SPOTLIGHT_RELEASE_DATE", "2026-12-05T00:00:00+05:30")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-key"
    WTF_CSRF_ENABLED = False
