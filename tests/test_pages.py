import pytest


@pytest.mark.parametrize(
    "path",
    ["/", "/artists", "/search", "/spotlight", "/playlist", "/about"],
)
def test_pages_render_for_a_signed_in_user(auth_client, path):
    response = auth_client.get(path)
    assert response.status_code == 200
    assert b"Music Mania" in response.data


@pytest.mark.parametrize(
    "path",
    ["/", "/artists", "/search", "/spotlight", "/playlist", "/about"],
)
def test_pages_require_a_login(client, path):
    assert client.get(path).status_code == 302


def test_artist_page_lists_that_artist_albums(auth_client):
    response = auth_client.get("/artist/Anirudh Ravichander")
    assert response.status_code == 200
    assert b"Beast" in response.data


def test_unknown_artist_returns_404(auth_client):
    assert auth_client.get("/artist/Nobody At All").status_code == 404


def test_unknown_album_returns_404(auth_client):
    assert auth_client.get("/album/999999").status_code == 404


def test_album_page_shows_its_own_details_not_hardcoded_ones(auth_client):
    response = auth_client.get("/album/1").data.decode()
    assert "Beast" in response
    assert "Nelson Dilipkumar" in response
    # The old template hardcoded this album's crew onto every album page.
    assert "K. Vishwanath" not in response


def test_a_missing_image_file_falls_back_to_the_placeholder(auth_client):
    """Album 45 names /images/nannaku.webp, which was never committed."""
    body = auth_client.get("/album/45").data.decode()
    assert "img/placeholder.svg" in body
    assert "nannaku.webp" not in body
