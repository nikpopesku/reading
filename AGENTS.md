# reading — project context

## Stack
- Django 6.x, Python 3.14, PostgreSQL, Gunicorn, WhiteNoise
- uv for dependency management (no pip/poetry)
- Ruff for linting (line-length 100) and formatting
- Coverage for test coverage

## Common commands
```
make test        # uv run python manage.py test
make lint        # uv run ruff check .
make format      # uv run ruff format .
make check       # uv run python manage.py check
make migrate     # docker compose exec web python manage.py migrate
make shell       # docker compose exec web sh
make local-up    # docker compose up -d --build
make local-down  # docker compose down
```

## Deployment
- Staging (Sirius): on push to master via deploy-staging.yml
- Production (Titan): manual via workflow_dispatch (deploy-prod.yml)
- Docker Swarm with Traefik + Let's Encrypt
- Images: ghcr.io/nikpopesku/reading-web

## Code style
- Ruff: line-length 100, target py314, select E/F/I/UP/B/DJ, ignore DJ001
- Coverage: omit migrations, manage.py, asgi/wsgi
- Clean diffs, no whitespace noise in PRs

## Branch naming
- `feat/<short-slug>` — new features
- `fix/<short-slug>` — bug fixes
- `chore/<short-slug>` — tooling, deps, CI, config
- `docs/<short-slug>` — documentation-only changes
- Always branch from latest master: `git checkout master && git pull && git checkout -b <branch>`

## Commit format
Conventional commits: `type(scope): short description`

```
feat(books): add reading progress slider
fix(auth): handle expired session token
chore(deps): update ruff to 0.14
docs(readme): add local dev setup section
```

If no scope is applicable, omit it: `fix: correct typo in error message`.

## Local test environment (without full Docker stack)

Tests need a running PostgreSQL. If Docker is available:

1. Start only the database: `docker compose -f docker-compose-local.yml --env-file .env.local up -d postgres`
2. Create `.env.local` with these vars if not already present:
   - `POSTGRES_DB=reading`
   - `POSTGRES_USER=reading`
   - `POSTGRES_PASSWORD=reading`
   - `DATABASE_URL=postgresql://reading:reading@127.0.0.1:5434/reading?sslmode=disable`
   - `DJANGO_SECRET_KEY=<any-local-dev-key>`
3. Run tests: `DATABASE_URL="$DATABASE_URL" DJANGO_DEBUG=1 DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" uv run python manage.py test`
4. Run lint/format/check the same way, or using the Makefile which calls uv directly.

The CI workflow (`.github/workflows/ci.yml`) uses these exact env vars:
- `DJANGO_DEBUG=1`
- `DJANGO_SECRET_KEY=testsecret`
- `DATABASE_URL=postgresql://reading:***@127.0.0.1:5432/reading_test?sslmode=disable`


## Migration rules
- **One migration file per PR max.** If multiple models changed, edit the generated migration to merge them, or split into separate PRs.
- If you didn't change any models but CI reports `makemigrations --check` failure, it means someone else's branch changed models and its migration was not applied to your branch's test DB — this is a false positive from parallel development. Verify by running `uv run python manage.py makemigrations` yourself; if nothing is generated (empty "No changes detected"), force-push to trigger CI again.
- Always commit `uv.lock` if `pyproject.toml` was modified (deps changed).