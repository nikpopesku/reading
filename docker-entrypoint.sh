#!/bin/sh
set -eu

if [ "$(id -u)" = "0" ]; then
  mkdir -p /app/media
  chown -R app:app /app/media
fi

run_as_app() {
  if [ "$(id -u)" = "0" ]; then
    runuser -u app -- "$@"
  else
    "$@"
  fi
}

# Orion has no deploy pipeline (unlike staging/prod, where migrate runs as an
# explicit workflow step) — it's just `docker compose up` against a bind
# mount, so the container itself must keep the DB/static files in sync with
# whatever code is on disk.
if [ "${RUN_STARTUP_TASKS:-0}" = "1" ]; then
  run_as_app python manage.py migrate --noinput
  run_as_app python manage.py collectstatic --noinput
fi

if [ "$(id -u)" = "0" ]; then
  exec runuser -u app -- "$@"
fi

exec "$@"
