# not_for_you.md

A personal working log. Not documentation, and nothing here is needed to use or
contribute to Music Mania. Everything a newcomer actually needs is in
[README.md](./README.md) and [DEVDOC.md](./DEVDOC.md).

---

## The database was committed, and it had real people in it

`data/Music_Mania.db` was tracked. DEVDOC even said to keep it tracked: *"do not
add it to `.gitignore`, it is the catalogue."* It was not only the catalogue.

At HEAD it held three accounts - `Delhi`, `Cherry` and `delhi` - with real first
and last names and scrypt password hashes. Published hashes are not a
catastrophe, but they are an offline attack anyone can run at their own pace, and
they should never have been in a public repository.

Then I looked at the history. **Eleven `.db` blobs are reachable in this
repository**, and one of them (`a69d9f8784`, commit `c1dcfbf`, "last update", May
2023) holds two accounts with their passwords **in plaintext**. The hashing
migration was added later, which is why HEAD looks fine and the history does not.

And it is not only in the binary. `tests/conftest.py` at HEAD logged in as one of
those real accounts with that same password written out as a plain string
literal in the `data=` dict. So the credential was readable in the source, not
just recoverable from a blob.

(The literal is deliberately not repeated here. CI greps the whole tree for it,
and a write-up that quotes the thing it is complaining about is just another copy
of it - which is how this file failed its own check on the first run.)

### What I changed

- The catalogue - artists, albums, songs, which is genuinely publishable - is now
  `data/catalogue.json`, a file a diff can actually review.
- `app/database.py` grew `SCHEMA`, `load_catalogue()` and `seed_demo()`, plus a
  `flask --app run init-db` command. A checkout builds its own database.
- `data/Music_Mania.db` is untracked and every `.db` under `data/` is gitignored.
- The tests build their database from the catalogue and the demo seed, and log in
  as `demo` / `demo1234`. No real credential remains anywhere in the tree.
- CI fails if a `.db` file is tracked again or if that password reappears.

### What is still outstanding, and needs a decision

**The history still contains all of it.** Removing a file from HEAD does not
remove it from the eleven blobs already pushed. Purging them means rewriting
history and force-pushing, which is a call for the repository owner rather than
something to do quietly. It is on the rotation list with the rest.

**Those passwords should be treated as public.** Not "should be rotated at some
point" - published, in a public repository, since May 2023, in plaintext. If
either was reused anywhere, that matters far more than this repository does.

## What was already right

- **`pip-audit` is clean.** Flask and Werkzeug are the only dependencies and both
  are current.
- **The SQL is parameterised throughout**, and there are tests that push
  `' OR '1'='1` and `x'; DROP TABLE Users;--` through the login form to prove it.
- **Passwords are hashed on write and migrated on read.** The migration that
  hashes legacy plaintext is exactly the right fix; it just cannot reach into git
  history.
- 40 tests, covering auth, playlists, reviews, pages and injection.

## Screenshots

Nine images: six screens plus three responsive. Real renders against the demo
account, signed in through the app's own login form.

**No light gallery and no `README-light.md`.** The app ships one dark palette:
`tokens.css` has a single `:root` block, no `prefers-color-scheme`, no
`data-theme`, no toggle. A light page would be the same images twice, so the
screenshots sit flat in `docs/screenshots/` rather than a misleading `dark/`
subdirectory. Same call as IIITHWebHunt earlier in this sweep.

The search screenshot is a **live iTunes query**, not a fixture: the page calls
the public iTunes Search API from the browser, and the twelve results and their
thirty second previews in that image are what the API returned.

## Left alone

- **`Users.username` has no unique constraint**, so two simultaneous signups could
  both succeed. Fixing it means rebuilding the table, which SQLite cannot do with
  a plain `ALTER`. DEVDOC already documents it.
- **Artist URLs match on name, not id**, so renaming an artist breaks links.
  Changing it is a routing decision with redirect implications, not a
  documentation-pass change.
- **The iTunes search has no rate limit handling.** It is a browser-side call to a
  public API on a student project; the page already shows a connection message
  rather than an empty list when it fails.
