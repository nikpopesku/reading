---
name: repo
type: repo
agent: CodeActAgent
---

# Project: Reading

Personal reading tracker built with Django.

## Stack
- **Python 3.14**, Django 6.0.6
- **PostgreSQL 17** (psycopg3)
- **uv** for dependency management (not pip, not poetry)
- **ruff** for linting and formatting
- **gunicorn** + **whitenoise** for serving
- Docker Swarm for production/staging deployment
- GitHub Actions for CI/CD
- Traefik as reverse proxy

## Key files
- `reading/` — Django app
- `reading_project/` — Django project settings
- `manage.py` — Django management
- `pyproject.toml` — project config and dependencies
- `uv.lock` — lockfile, always commit this
- `Makefile` — common dev commands
- `docker-compose-local.yml` — local dev environment
- `docker-compose-orion.yml` — Orion VPS dev environment
- `docker-stack.staging.yml` — staging Docker Swarm stack
- `docker-stack.prod.yml` — production Docker Swarm stack
- `.github/workflows/ci.yml` — CI: lint, tests, docker build
- `.github/workflows/deploy-staging.yml` — deploy to Sirius staging on push to master
- `.github/workflows/deploy-prod.yml` — deploy to production

## Environments
| Env | URL | Host | Stack name |
|-----|-----|------|-----------|
| Staging | https://readingstaging.a007.bid | Sirius VPS | `reading-staging` |
| Production | — | Sirius VPS | — |

## Deploy flow (staging)
Push to `master` triggers `deploy-staging.yml`:
1. Build Docker image → push to `ghcr.io/nikpopesku/reading-web:staging` + `staging-<sha>`
2. SCP `docker-stack.staging.yml` to Sirius at `/home/spacer/reading/`
3. SSH to Sirius: create DB/user if missing, create Docker secret if missing, `docker stack deploy`
4. Wait for new container with correct image tag to be running
5. Run `python manage.py migrate --noinput` inside the new container

## Secrets (GitHub Actions)
- `SIRIUS_HOST`, `SIRIUS_USER`, `SIRIUS_SSH_KEY` — SSH access to Sirius
- `STAGING_DATABASE_URL`, `STAGING_DB_PASSWORD`, `STAGING_DJANGO_SECRET_KEY`
- `CODECOV_TOKEN`

## Local dev commands
```bash
make local-up       # start local docker compose
make local-down     # stop
make shell          # sh into web container
make migrate        # run migrations
make test           # run tests
make lint           # ruff check
make format         # ruff format
```

## Running tests/checks without Docker
```bash
uv run python manage.py test
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

## Settings
`reading_project/settings.py` reads secrets from Docker secrets files (`/run/secrets/`) if the env var value starts with that path — so `DJANGO_SECRET_KEY=/run/secrets/reading_django_secret_key` works in swarm.

## Available tools in sandbox
- **SSH keys** are mounted from host at `/root/.ssh` — can SSH directly to Sirius
- **gh CLI** is authenticated via host config at `/root/.config/gh` — can trigger GitHub Actions, watch runs, create PRs
- To trigger staging deploy manually: `gh workflow run deploy-staging.yml --ref master`
- To watch a running deploy: `gh run watch`
- To verify staging after deploy: `curl -sf https://readingstaging.a007.bid`

## Rule: Plan before implementing
Before writing any code or making any changes, you MUST:
1. Describe what you plan to do and why
2. List the files you intend to create or modify
3. Wait for the user to explicitly say "go ahead" or "yes" before proceeding

Do not start implementing until the user approves the plan.

## Rule: Update this file at the end of every task
Before marking any task as complete, you MUST update this file with everything new you discovered:
- Files you read and what they do
- Bugs or gotchas you found
- Architecture decisions and why they exist
- Things that failed and why
- Any non-obvious behaviour

Then commit and push: `git add .openhands/microagents/repo.md && git commit -m "docs: update microagent knowledge" && git push`
