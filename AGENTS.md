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
- Ruff: line-length 100, target py314, select E/F/I/UP/B/DJ
- Coverage: omit migrations, manage.py, asgi/wsgi
- Clean diffs, no whitespace noise in PRs

## Workflow
- Always create a PR for each change, branched from latest master
- Master should always contain the latest merged changes
- Verify that GitHub workflow checks pass before asking for merge
- PRs must have a clear description of problem + root cause + fix