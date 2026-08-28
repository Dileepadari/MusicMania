# Music Mania - Developer Documentation

Technical reference for the Music Mania codebase: architecture, auth model, data model, API surface, and setup. For what the app does from a user's point of view, see [README.md](./README.md).

## Table of contents

- [Tech stack](#tech-stack)
- [Architecture overview](#architecture-overview)
- [Directory layout](#directory-layout)
- [Auth model](#auth-model)
- [Data model](#data-model)
- [Migrations](#migrations)
- [Route surface](#route-surface)
- [Theming](#theming)
- [Front-end structure](#front-end-structure)
- [Testing](#testing)
- [Environment variables](#environment-variables)
- [Local development](#local-development)
- [Deployment](#deployment)
- [Known constraints and gotchas](#known-constraints-and-gotchas)

## Tech stack

Flask 3 with Jinja templates, SQLite through the standard library `sqlite3` module, and Werkzeug's `generate_password_hash` / `check_password_hash` for credentials. The front end is plain CSS and JavaScript with no build step, so anything under `app/static` is served exactly as it is written. There is no ORM: queries live in small per-table repository modules, which keeps the SQL visible and parameterised.

## Architecture overview

```
browser
   |
   |  HTML page loads                      JSON fetch (playlist)
   v                                              v
+---------------------------------------------------------------+
|  Flask app  (app/__init__.py: create_app)                      |
|                                                                |
|  blueprints/          auth  main  catalog  api                 |
|      |  each route is thin: read input, call a repository,     |
|      |  render a template or return JSON                       |
|      v                                                         |
|  repositories/        artists albums songs users reviews       |
|      |  every query parameterised, returns sqlite3.Row         |
|      v                                                         |
|  database.py          per-request connection in flask.g        |
+---------------------------------------------------------------+
                             |
                             v
                    data/Music_Mania.db
```

- **Blueprints** own HTTP concerns only: form parsing, validation, status codes, redirects.
- **Repositories** own SQL. Nothing outside `app/repositories` writes a query.
- **database.py** owns connection lifetime and the migration steps.
- **security.py** owns the session: `login_user`, `logout_user`, and the `login_required` decorator.

A `before_request` hook loads the signed-in user once per request into `g.user`, and a context processor exposes it to every template as `current_user`. Templates never query the database.

## Directory layout

```
app/
  __init__.py        application factory, template filters, error handlers
  config.py          Config and TestConfig, all values env-overridable
  database.py        connection handling, migrations, "flask migrate" command
  security.py        session helpers and the login_required decorator
  blueprints/
    auth.py          login, signup, logout
    main.py          home, playlist, search, about
    catalog.py       artists, artist, album, spotlight, review submission
    api.py           JSON playlist endpoints under /api
  repositories/      one module per table
  templates/
    base.html        the single page shell every template extends
    partials/        header, footer, flashes, section head, playlist button, reviews block
    auth/            login and signup (they hide the header and footer)
    catalog/         artists, artist, album, spotlight
    errors/          404 and 500
  static/
    css/             tokens, base, components, then one file per page under pages/
    js/              app, playlist, search, countdown
    images/          catalogue artwork carried over from the original project
    img/             the ADK DEV mark and the artwork placeholder
data/Music_Mania.db  the seeded catalogue, tracked in git
tests/               pytest suite
run.py               development entry point
```

## Auth model

Sessions are Flask's default signed cookie, holding one key: `user_id`. There is no separate token and no server-side session store.

- **Login** looks the username up with a parameterised query and calls `check_password_hash`. On success `login_user` clears the session and sets `user_id`, so a session fixation attempt cannot carry state across the login boundary.
- **Every request** runs the `load_current_user` hook, which loads the user into `g.user`. If the cookie names a user that no longer exists, the key is dropped and the request continues as anonymous.
- **`@login_required`** redirects anonymous visitors to `/login?next=<path>`. After a successful login the user is sent back to `next`, but only when it is a relative path on this site: `_safe_redirect_target` rejects anything with a scheme or a host, so `?next=https://evil.example` lands on the home page instead.
- **API routes** under `/api` return `401 {"error": "authentication required"}` rather than a redirect, since a fetch cannot follow a login page usefully.
- **Logout** pops the key and returns to the login page.

Passwords are hashed with Werkzeug's default (`scrypt` on current versions). The seeded database originally held plaintext, and the migration hashes those rows in place on first boot, so the original seed logins keep working.

## Data model

SQLite, one file, five tables plus one added by migration. Column names in `Artists` and `Albums` are inherited from the original project and are inconsistent in case; the repositories alias the awkward ones (`"index"` becomes `artist_id`, `"cast"` becomes `cast_list`) so nothing downstream has to quote a SQL keyword.

### Users
| Column | Type | Notes |
|---|---|---|
| userid | INTEGER PK | autoincrement |
| username | TEXT | the login name, expected unique (not enforced by a constraint) |
| img_url | TEXT | avatar path relative to `static/`, may or may not have a leading slash |
| playlist | TEXT | legacy comma-joined song ids, superseded by `PlaylistEntries`, left in place so an old copy of the database still opens |
| firstname, lastname | TEXT | |
| password | TEXT | Werkzeug hash |

### Artists
| Column | Type | Notes |
|---|---|---|
| uniqid | INTEGER PK | referenced by `Albums."index"` |
| name | TEXT | also the URL segment on `/artist/<name>` |
| birth | TEXT | free text, for example "4 June 1946 - 25 September 2020" |
| languages | TEXT | comma separated, rendered as chips |
| image_url | TEXT | path relative to `static/` |
| Albums, Tracks | NUMERIC | counts, aliased to `album_count` / `track_count` |
| Awards | TEXT | free text |
| description, self_page, wiki_url | TEXT | |
| special | INTEGER | 1 puts the artist in the Top Artists row on the home page |
| rating | INTEGER | 1 to 5, editorial |

### Albums
| Column | Type | Notes |
|---|---|---|
| uniqid | INTEGER PK | the URL segment on `/album/<id>` |
| author | TEXT | artist name, also used to build the breadcrumb link |
| name, year | TEXT / INTEGER | |
| rating | REAL | editorial, 0 to 5 |
| duration, tracks | TEXT / INTEGER | |
| "index" | INTEGER | the owning artist's `uniqid`, aliased to `artist_id` |
| img_url | TEXT | cover art relative to `static/` |
| release_date, director, producer, "cast" | TEXT | shown in the album detail list |

### Songs
| Column | Type | Notes |
|---|---|---|
| uniqid | INTEGER PK | |
| name, album_name | TEXT | |
| album_id | INTEGER | `Albums.uniqid` |
| rating | REAL | |
| duration | TEXT | free text, for example "4 Min 59 Sec" |
| artists | TEXT | comma separated names, not a foreign key |

### Reviews
| Column | Type | Notes |
|---|---|---|
| review_id | INTEGER PK | |
| userid | INTEGER | `Users.userid` |
| review | TEXT | |
| date | TEXT | `DD/MM/YYYY`, local date at write time, no timezone recorded |
| rating | INTEGER | 1 to 5, validated server-side |
| target_type | TEXT | `artist` or `album`, added by migration |
| target_id | INTEGER | the `uniqid` of that artist or album, added by migration |

### PlaylistEntries
Created by migration. Primary key is the pair, so adding the same track twice is a no-op.

| Column | Type | Notes |
|---|---|---|
| userid | INTEGER | `Users.userid` |
| song_id | INTEGER | `Songs.uniqid` |
| added_at | TEXT | `CURRENT_TIMESTAMP`, UTC, used to order the playlist newest first |

Dates are stored as text throughout. `Reviews.date` is a local date with no zone; `PlaylistEntries.added_at` is UTC because SQLite's `CURRENT_TIMESTAMP` is UTC. That inconsistency is inherited, not deliberate.

## Migrations

`app/database.py:migrate` runs on every boot inside `init_app`, and is also available as `flask --app run:app migrate`. Every step is idempotent, so running it against an already-migrated file does nothing. There is no version table: each step tests for the thing it would create.

1. **`reviews.target`** adds `target_type` and `target_id`, then points existing rows at artist 12. Before this, `Reviews` had no target column at all, so every review was rendered on every page that listed reviews.
2. **`playlist.table`** creates `PlaylistEntries` and copies `Users.playlist` into it, splitting on commas and ignoring anything non-numeric.
3. **`users.password_hashed`** replaces any password that does not already start with a known hash prefix.

Steps 2 and 3 rewrite the tracked `data/Music_Mania.db`, so the first run after a fresh clone produces a diff on that file. That is expected.

## Route surface

| Method | Path | Auth | Returns |
|---|---|---|---|
| GET, POST | `/login` | anonymous | Login page. 401 with an error message on a bad password |
| GET, POST | `/signup` | anonymous | Signup page. 400 with an error message on invalid input, otherwise creates the user and logs them in |
| GET | `/logout` | required | Redirect to `/login` |
| GET | `/` | required | Home: featured artists, top albums, top songs |
| GET | `/artists` | required | Every artist, ordered by rating |
| GET | `/artist/<name>` | required | One artist, their albums, related artists, their reviews. 404 if unknown |
| GET | `/album/<int:id>` | required | One album, its tracklist, its reviews. 404 if unknown |
| GET | `/spotlight` | required | The artist named by `SPOTLIGHT_ARTIST_ID` |
| GET | `/playlist` | required | The signed-in user's playlist |
| GET | `/search` | required | The iTunes search page (the query itself runs in the browser) |
| GET | `/about` | required | About and credits |
| POST | `/review/<artist\|album>/<int:id>` | required | Records a review, then redirects back to the target with a flash message. 404 on an unknown target or target type |
| POST | `/api/playlist` | required | `{"song_id": n}` in, `{"song_id": n, "in_playlist": true}` out. 400 on a non-integer id, 404 on an unknown song |
| DELETE | `/api/playlist/<int:song_id>` | required | `{"song_id": n, "in_playlist": false}`. Removing something that is not there succeeds |

## Theming

One dark theme, defined entirely in `app/static/css/tokens.css`. Every colour, radius, shadow and font in the app is a custom property on `:root`; no component hard-codes a hex value. The brand purple is the ADK DEV mark's `#47266B`, lifted to `#8b5cf6` for use on dark surfaces, with the original kept as `--brand-deep`.

The mark itself is a solid purple on transparent, so it vanishes against a dark surface. `.logo-mono` in `base.css` applies `filter: brightness(0) invert(1)` to flatten it to white while keeping the alpha shape. There is only one logo file; do not add a recoloured second copy.

A light theme is not implemented. Adding one means adding a `@media (prefers-color-scheme: light)` block that redefines the tokens, and nothing else.

## Front-end structure

CSS loads in a fixed order from `base.html`: `tokens.css`, `base.css`, `components.css`, then whatever a page adds through the `styles` block. Page CSS lives in `static/css/pages/` and is only loaded by the page that needs it.

JavaScript is four small IIFEs, no modules and no bundler:

| File | Loaded by | Does |
|---|---|---|
| `app.js` | every page | Mobile navigation toggle, and the global `showToast` helper |
| `playlist.js` | home, album, playlist | One delegated click listener for every `[data-playlist-toggle]` button |
| `search.js` | search | Calls the iTunes API with `media=music` and builds result cards as DOM nodes |
| `countdown.js` | spotlight | Ticks the release countdown from the date the server rendered |

Two conventions worth knowing:

- The playlist button's `aria-pressed` attribute is the single source of truth. CSS picks the label out of `data-add` / `data-remove` through a `::before` on the `[aria-pressed]` selector, so the JavaScript only ever flips the attribute, never the text.
- `search.js` builds nodes with `createElement` and `textContent` rather than concatenating HTML, so a track title containing quotes or angle brackets cannot break out into markup.
- `.visually-hidden` is absolutely positioned, so it needs a positioned ancestor. `.table-wrap` sets `position: relative` for exactly this reason; see the gotchas below.

Three Jinja filters, registered in `app/__init__.py`, keep the templates clean:

- `media` turns a database image path into a static URL, tolerating the leading slash some rows have and falling back to `img/placeholder.svg` when the value is empty or names a file that is not on disk.
- `tidy` collapses the stray whitespace the seed data is full of ("Nelson Dilipkumar  ").
- `stars` renders a numeric rating as filled and empty star characters.

## Testing

```bash
.venv/bin/python -m pytest tests -q
```

40 tests across five files. Each test copies `data/Music_Mania.db` into a `tmp_path` first, so the suite never touches the tracked database and the migration is exercised on every run.

| File | Covers |
|---|---|
| `test_auth.py` | Redirect when anonymous, seeded plaintext logins still working after hashing, bad password, duplicate username, password confirmation, offsite `next` |
| `test_pages.py` | Every page renders for a signed-in user and redirects for an anonymous one, unknown artist and album 404, album details are the album's own, a missing image file falls back to the placeholder |
| `test_playlist.py` | Add, remove, idempotent add, exact id membership, unknown song, non-integer id, 401 when anonymous |
| `test_reviews.py` | A review appears only on its own target, rating and text validation, unknown target |
| `test_security.py` | SQL injection through the login form, review text escaped in the rendered page |

Not covered: the browser JavaScript (no headless browser in the suite) and the iTunes search, which is a third-party call made from the browser.

## Environment variables

All server-side. None of these reach the browser.

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `dev-only-insecure-key` | Signs the session cookie. **Must** be set to a real random value in any deployment, otherwise session cookies are forgeable |
| `DATABASE` | `data/Music_Mania.db` | Path to the SQLite file |
| `SPOTLIGHT_ARTIST_ID` | `12` | Which artist `/spotlight` shows |
| `SPOTLIGHT_RELEASE_DATE` | `2026-12-05T00:00:00+05:30` | ISO 8601 target for the spotlight countdown. The whole block is hidden once the date passes |

## Local development

```bash
git clone <repo> && cd MusicMania
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python run.py
```

The app is on http://127.0.0.1:5000 with the reloader on. The first boot migrates `data/Music_Mania.db` in place, which will show as a modified file in `git status`.

To run against a scratch copy instead of the tracked one:

```bash
cp data/Music_Mania.db data/scratch.local.db
DATABASE=data/scratch.local.db .venv/bin/python run.py
```

`.gitignore` covers `data/*.local.db`.

## Deployment

Not currently deployed anywhere. To do it, `run.py` exposes `app`, so any WSGI server works:

```bash
SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  gunicorn 'run:app'
```

Two things to settle before that is a good idea:

- SQLite with a single file is fine for one process. More than one worker writing concurrently will hit `database is locked`.
- Sessions are cookie-based, so `SECRET_KEY` must be stable across restarts or everyone is logged out on every deploy.

## Known constraints and gotchas

- **The seeded database is tracked and gets rewritten on first boot.** Migrations 2 and 3 write to `data/Music_Mania.db`, so a clean clone shows that file as modified after the first run. Commit it or check it out again; do not add it to `.gitignore`, it is the catalogue.
- **`Albums."index"` is the artist id, not a row index.** The name is inherited. Every repository aliases it to `artist_id`; if you write a query outside the repositories, remember it needs double quotes because `index` is a SQL keyword.
- **Artist URLs use the name, not the id.** `/artist/<name>` matches on `Artists.name` exactly. Renaming an artist breaks any link to them. The route uses a `path` converter, so names containing a slash would still resolve, but names differing only in trailing whitespace will not.
- **Playlist membership used to be a substring test.** The old template asked whether `"4"` appeared in the string `"14,142,"`, which is true, so unrelated tracks showed as already added. `PlaylistEntries` makes it an exact match. If you touch this code, keep it an integer comparison.
- **`Users.username` has no unique constraint.** Signup checks for a duplicate before inserting, but two simultaneous signups could still both succeed. Adding the constraint means rebuilding the table, which SQLite cannot do with a plain `ALTER`.
- **Review dates are strings in `DD/MM/YYYY`.** They sort lexicographically, which is wrong, so the reviews list orders by `review_id DESC` instead. Do not switch it to order by `date`.
- **The iTunes search runs in the browser, not the server.** It will fail on a machine with no outbound internet, and the page shows a connection message rather than an empty result list. There is no API key and no rate limit handling.
- **The spotlight countdown hides itself once the date passes.** The original hardcoded 30 June 2023 and rendered negative numbers forever afterwards. If the countdown is missing, check `SPOTLIGHT_RELEASE_DATE`.
- **Image paths in the database are inconsistent.** Some start with a slash, some do not, and album 45 (`Nannaku Prematho`) names `/images/nannaku.webp`, which was never committed. The `media` filter stats the file and substitutes the placeholder, so always render through it rather than passing a path to `url_for` directly. That stat is one syscall per image, which is fine at this catalogue size; if the catalogue grows, cache it.
- **`.visually-hidden` will widen the page if you put it somewhere unpositioned.** It is `position: absolute`, so with no positioned ancestor its containing block is the initial containing block. Inside a `.table-wrap` that scrolls horizontally, that means it escapes the scroll container and sits at the table's full width, giving the whole document a horizontal scrollbar on narrow screens. `.table-wrap` sets `position: relative` to contain it. If you add another horizontally scrolling container, do the same.
- **The iTunes search sets `media=music` explicitly.** Without it the API defaults to `media=all` and returns films, ebooks and audiobooks alongside the tracks. Rows with no `trackTimeMillis` render as "Unknown length" rather than "0 min 00 sec".
