FROM ghcr.io/astral-sh/uv:0.9.16 AS uv
FROM python:3.14.5-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     UV_COMPILE_BYTECODE=1     UV_LINK_MODE=copy     PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update     && apt-get install -y --no-install-recommends libpq5     && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /uvx /usr/local/bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .
RUN python manage.py collectstatic --noinput

RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["gunicorn", "reading_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
