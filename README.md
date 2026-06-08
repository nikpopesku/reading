# Reading

Personal reading tracker for books that are planned, in progress, or finished.

**Live:** <https://reading.a007.bid>

## Stack

- Python 3.14.5
- Django 6.0
- uv for dependency management
- PostgreSQL
- Docker Compose locally and on Orion
- Docker Swarm on staging and production

## Local development

Create an ignored local env file and fill in secret values:

```sh
cp .env.example .env.local
```

Set `POSTGRES_PASSWORD` and `DATABASE_URL` in `.env.local`; do not commit those values.

Run locally behind Traefik:

```sh
make local-up
make migrate
make createsuperuser
```

Open `https://readinglocal.a007.bid`.

## Orion

Create an ignored Orion env file with `DATABASE_URL`, then start the app:

```sh
cp .env.example .env.orion
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

