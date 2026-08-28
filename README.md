<p align="center">
  <img src="./app/static/img/logo-mark.png" width="96" alt="ADK DEV">
</p>

# Music Mania

A music review site: browse artists and albums, rate and review them, keep a playlist of tracks, and search the iTunes catalogue for anything not covered here.

It started as a static HTML project and is now a Flask application backed by SQLite. For architecture, data model, and setup, see **[DEVDOC.md](./DEVDOC.md)**.

## Features

### Browsing
- Home page with the highest rated artists, albums and songs, plus a count of what is in your playlist
- Artist list with rating, active languages, album and track counts, and awards
- Artist pages with a full biography, their albums, and a link to related artists
- Album pages with the tracklist, the release crew (director, producer, cast), and three ratings: the album's own, the average of its tracks, and the blend of the two
- A monthly Artist Spotlight page with a live countdown to the next release
- Breadcrumbs on every catalogue page so you can climb back up a level

### Reviews
- Rate any artist or album from one to five stars and write a review
- Reviews are attached to the artist or album they were written about, so an album page only shows reviews of that album
- Each page shows the review count and the average reader rating alongside the editorial rating

### Playlist
- Add or remove any track from the home page, an album page, or the playlist itself
- The button reflects the current state, so you can see at a glance what you have already saved
- Removing a track from the playlist page drops it out of the table without a reload

### Search
- Search the iTunes catalogue by artist, album or track
- Play a 30 second preview inline
- Filter by maximum duration and choose whether to include explicit results

## Roles

There is one kind of user. Everything except the login and signup pages requires an account.

| Role | Can do |
|---|---|
| **Signed-in user** | Browse the catalogue, rate and review artists and albums, manage their own playlist, search iTunes |
| **Anonymous visitor** | Log in or sign up. Any other URL redirects to the login page and returns you there afterwards |

## The review lifecycle

1. You open an artist or album page and pick a star rating.
2. You write the review text. Both are required: a rating with no words, or words with no rating, is rejected with a message rather than saved.
3. The review is stored against that artist or album with today's date and your user id.
4. It appears immediately in the reviews list on that page, newest first, and is counted into the reader rating shown at the top.

Reviews cannot currently be edited or deleted from the interface.

## Tech stack

Flask and Jinja templates on the server, SQLite for storage, and plain CSS and JavaScript on the front end. No build step and no front-end framework.

## Getting started

See [DEVDOC.md](./DEVDOC.md#local-development) for setup. The short version:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

Then open http://127.0.0.1:5000.
