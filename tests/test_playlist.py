def test_add_and_remove_a_track(auth_client):
    response = auth_client.post("/api/playlist", json={"song_id": 9})
    assert response.status_code == 200
    assert response.get_json() == {"song_id": 9, "in_playlist": True}
    assert b"You &amp; I" in auth_client.get("/playlist").data

    response = auth_client.delete("/api/playlist/9")
    assert response.get_json() == {"song_id": 9, "in_playlist": False}
    assert b"You &amp; I" not in auth_client.get("/playlist").data


def test_adding_the_same_track_twice_is_idempotent(auth_client):
    auth_client.post("/api/playlist", json={"song_id": 9})
    auth_client.post("/api/playlist", json={"song_id": 9})
    body = auth_client.get("/playlist").data.decode()
    assert body.count('data-playlist-row="9"') == 1


def test_membership_is_exact_not_a_substring_match(auth_client):
    """Song 4 must not look 'in playlist' just because song 14 is."""
    auth_client.post("/api/playlist", json={"song_id": 14})
    response = auth_client.get("/playlist")
    assert b'data-playlist-row="14"' in response.data
    assert b'data-playlist-row="4"' not in response.data


def test_unknown_song_is_rejected(auth_client):
    assert auth_client.post("/api/playlist", json={"song_id": 999999}).status_code == 404


def test_non_integer_song_id_is_rejected(auth_client):
    assert auth_client.post("/api/playlist", json={"song_id": "abc"}).status_code == 400


def test_api_requires_a_login(client):
    response = client.post("/api/playlist", json={"song_id": 9})
    assert response.status_code == 401
    assert response.get_json()["error"] == "authentication required"
