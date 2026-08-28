def test_a_review_appears_on_the_album_it_was_written_about(auth_client):
    response = auth_client.post(
        "/review/album/1", data={"rating": "5", "review": "Loud and excellent."}
    )
    assert response.status_code == 302

    assert b"Loud and excellent." in auth_client.get("/album/1").data
    # And nowhere else.
    assert b"Loud and excellent." not in auth_client.get("/album/2").data
    assert b"Loud and excellent." not in auth_client.get("/spotlight").data


def test_a_review_without_a_rating_is_rejected(auth_client):
    auth_client.post("/review/album/1", data={"review": "No stars given."})
    assert b"No stars given." not in auth_client.get("/album/1").data


def test_a_review_without_text_is_rejected(auth_client):
    before = auth_client.get("/album/1").data.count(b"review__body")
    auth_client.post("/review/album/1", data={"rating": "4", "review": "   "})
    after = auth_client.get("/album/1").data.count(b"review__body")
    assert after == before


def test_an_out_of_range_rating_is_rejected(auth_client):
    auth_client.post("/review/album/1", data={"rating": "9", "review": "Off the scale."})
    assert b"Off the scale." not in auth_client.get("/album/1").data


def test_reviewing_an_unknown_target_is_a_404(auth_client):
    assert auth_client.post(
        "/review/album/999999", data={"rating": "4", "review": "Ghost album."}
    ).status_code == 404
    assert auth_client.post(
        "/review/wombat/1", data={"rating": "4", "review": "Wrong type."}
    ).status_code == 404
