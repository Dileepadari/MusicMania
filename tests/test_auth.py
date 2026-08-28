def test_anonymous_visitor_is_sent_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_with_legacy_plaintext_password_still_works(client):
    """The migration hashes seeded passwords, so the original ones must still log in."""
    response = client.post("/login", data={"username": "Delhi", "password": "Delhiking"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_login_rejects_a_wrong_password(client):
    response = client.post("/login", data={"username": "Delhi", "password": "nope"})
    assert response.status_code == 401
    assert b"Incorrect username or password" in response.data


def test_password_is_not_stored_in_plaintext(app):
    from app.database import get_db

    with app.app_context():
        stored = get_db().execute(
            "SELECT password FROM Users WHERE username = 'Delhi'"
        ).fetchone()["password"]
    assert stored != "Delhiking"
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
            "username": "Delhi",
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
        data={"username": "Delhi", "password": "Delhiking"},
    )
    assert response.headers["Location"] == "/"


def test_logout_clears_the_session(auth_client):
    auth_client.get("/logout")
    assert auth_client.get("/").status_code == 302
