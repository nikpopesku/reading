# Reading — Claude Code Guide

Personal reading tracker built with Django 6.0 and Python 3.14.

## Commands

```sh
uv sync          # install dependencies
make test        # run test suite (uv run python manage.py test)
make lint        # ruff check
make format      # ruff format
make check       # django system check
```

Always run `make lint` and `make test` before committing.

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
| `DJANGO_SECRET_KEY` | prod only | auto-placeholder in DEBUG mode |
| `DJANGO_DEBUG` | no | `1` enables debug + SQLite fallback |
| `DATABASE_URL` | no | omit to use SQLite |
| `DJANGO_ALLOWED_HOSTS` | no | comma-separated |
