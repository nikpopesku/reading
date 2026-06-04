# Reading

Personal reading tracker for books that are planned, in progress, or finished.

## Stack

- Python 3.14.5
- Django 6.0
- uv for dependency management
- PostgreSQL
- Docker Compose locally and on Orion
- Docker Swarm on staging and production

## Local development

Create an env file:

```sh
cp .env.example .env
```

Run locally behind Traefik:

```sh
make local-up
make migrate
make createsuperuser
```

Open `https://readinglocal.a007.bid`.

## Orion

```sh
make orion-up
```

Open `https://readingorion.a007.bid`.

## Checks

```sh
uv sync
make lint
make check
make test
```

## GitHub deployment secrets

Repository-level secrets required for staging deploys:

- `SIRIUS_HOST`
- `SIRIUS_USER`
- `SIRIUS_SSH_KEY`
- `STAGING_DATABASE_URL`
- `STAGING_DB_PASSWORD`
- `STAGING_DJANGO_SECRET_KEY`

Production environment secrets required under the `prod` environment:

- `TITAN_HOST`
- `TITAN_USER`
- `TITAN_SSH_KEY`
- `PROD_DATABASE_URL`
- `PROD_DB_PASSWORD`
- `PROD_DJANGO_SECRET_KEY`

The staging workflow runs on pushes to `master`. The production workflow is manual via `workflow_dispatch` and deploys the `reading` Docker Swarm stack to Titan.
