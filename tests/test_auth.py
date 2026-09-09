"""Login, signup and password handling."""

from tests.conftest import DEMO_PASSWORD, DEMO_USERNAME


def test_anonymous_visitor_is_sent_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_a_seeded_account_can_log_in(client):
    """Demo accounts are hashed when they are created, and must still log in."""
    response = client.post("/login", data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_login_rejects_a_wrong_password(client):
    response = client.post("/login", data={"username": DEMO_USERNAME, "password": "nope"})
    assert response.status_code == 401
    assert b"Incorrect username or password" in response.data


def test_password_is_not_stored_in_plaintext(app):
    from app.database import get_db

    with app.app_context():
        stored = get_db().execute(
            "SELECT password FROM Users WHERE username = 'demo'"
        ).fetchone()["password"]
    assert stored != DEMO_PASSWORD
    assert stored.startswith(("pbkdf2:", "scrypt:", "argon2:"))


def test_signup_rejects_mismatched_passwords(client):
    response = client.post(
        "/signup",
        data={
            "username": "newbie",
            "firstname": "New",
            "lastname": "Bie",
            "password": "hunter22",
            "confirm_password": "hunter23",
        },
    )
    assert response.status_code == 400
    assert b"do not match" in response.data


def test_signup_rejects_a_duplicate_username(client):
    response = client.post(
        "/signup",
        data={
            "username": DEMO_USERNAME,
            "firstname": "New",
            "lastname": "Bie",
            "password": "hunter22",
            "confirm_password": "hunter22",
        },
    )
    assert response.status_code == 400
    assert b"already taken" in response.data


def test_signup_logs_the_new_user_straight_in(client):
    response = client.post(
        "/signup",
        data={
            "username": "newbie",
            "firstname": "New",
            "lastname": "Bie",
            "password": "hunter22",
            "confirm_password": "hunter22",
        },
    )
    assert response.status_code == 302
    assert client.get("/").status_code == 200


def test_login_ignores_an_offsite_next_parameter(client):
    response = client.post(
        "/login?next=https://evil.example.com",
        data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
    )
    assert response.headers["Location"] == "/"


def test_logout_clears_the_session(auth_client):
    auth_client.get("/logout")
    assert auth_client.get("/").status_code == 302
