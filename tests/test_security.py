def test_username_field_is_not_sql_injectable(client):
    """The old code interpolated the username straight into the SQL string."""
    response = client.post(
        "/login", data={"username": "' OR '1'='1", "password": "anything"}
    )
    assert response.status_code == 401


def test_a_dropped_table_attempt_leaves_the_database_intact(client, app):
    client.post("/login", data={"username": "x'; DROP TABLE Users;--", "password": "x"})
    from app.database import get_db

    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) AS n FROM Users").fetchone()["n"]
    assert count >= 2


def test_review_text_is_escaped_in_the_page(auth_client):
    auth_client.post(
        "/review/album/1",
        data={"rating": "4", "review": "<script>alert('xss')</script>"},
    )
    body = auth_client.get("/album/1").data
    assert b"<script>alert" not in body
    assert b"&lt;script&gt;" in body
