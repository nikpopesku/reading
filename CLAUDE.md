# Reading — Claude Code Guide

Personal reading tracker built with Django 6.0 and Python 3.14.

## Commands

```sh
uv sync          # install dependencies (also fetches Python 3.14 if missing)
make test        # run test suite (uv run python manage.py test)
make lint        # ruff check
make format      # ruff format
make check       # django system check
```

Always run `make lint` and `make test` before committing.

If `uv` isn't on PATH, install it first: `curl -LsSf https://astral.sh/uv/install.sh | sh` (add `~/.local/bin` to PATH afterwards).

### Required env var for any `manage.py` command run directly (not via Docker)

`DJANGO_DEBUG=1` **must** be exported before running `manage.py test`, `check`, `makemigrations`, etc. outside Docker Compose. Without it, `DEBUG` defaults to `False` and Django raises `RuntimeError: DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is disabled` on startup — there is no `.env` auto-loading (no python-dotenv), so nothing else supplies `SECRET_KEY` in a bare shell.

```sh
export DJANGO_DEBUG=1
uv run python manage.py test
```

### CI runs against PostgreSQL, not SQLite

`.github/workflows/ci.yml` spins up a real `postgres:17-alpine` service and also runs `makemigrations --check --dry-run` against it. A sandbox with no Postgres will fall back to SQLite (see below) — tests passing locally against SQLite is a good signal but does **not** guarantee the Postgres-backed CI job passes. After pushing, check actual CI status with `gh pr checks --watch` before treating the PR as done; if a check fails, convert the PR to draft (`gh pr ready --undo`) and note the failure in the PR body rather than leaving it as a false ready-for-review signal.

## Project structure

```
reading/            # Django app
  models.py         # Book model (title, author, status, rating, notes, dates)
  views.py          # book_list view with filtering and pagination
  forms.py          # BookForm (ModelForm)
  admin.py          # BookAdmin
  tests.py          # all tests live here
  templatetags/     # custom template filters
  migrations/       # database migrations
reading_project/    # Django project config
  settings.py       # all settings, reads env vars
  urls.py
templates/reading/  # HTML templates
static/css/         # app.css
```

## Database

No `DATABASE_URL` set → falls back to **SQLite** automatically (see `settings.py:database_config`). Tests work without any database setup in the cloud or CI.

For local dev and Orion, set `DATABASE_URL=postgresql://...` in `.env.local` / `.env.orion`.

## Key model facts

- `Book` statuses: `will_read`, `reading`, `read`, `deleted` (deleted is hidden from the UI)
- `rating`: integer 1–5, nullable
- Default ordering: `["status", "title"]`
- Migrations live in `reading/migrations/`; always generate with `uv run python manage.py makemigrations`

## Code style

- Line length: **100**
- Ruff rules: `E, F, I, UP, B, DJ` (DJ001 ignored)
- No comments unless the WHY is non-obvious
- No docstrings on obvious methods

## Branching

- Main branch: `master`
- PR branches: `claude/<TICKET_KEY>` for automated work (e.g. `claude/RD-22`)
- One ticket per branch; never mix concerns

## Environment variables

| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | only if `DJANGO_DEBUG` is unset/0 | otherwise raises `RuntimeError` on startup |
| `DJANGO_DEBUG` | **yes, for any bare `manage.py` command** | `1` auto-supplies a placeholder `SECRET_KEY` |
| `DATABASE_URL` | no | omit to use SQLite (independent of `DJANGO_DEBUG`) |
| `DJANGO_ALLOWED_HOSTS` | no | comma-separated |
