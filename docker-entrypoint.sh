#!/bin/sh
set -eu

if [ "$(id -u)" = "0" ]; then
  mkdir -p /app/media
  chown -R app:app /app/media
  exec runuser -u app -- "$@"
fi

exec "$@"
