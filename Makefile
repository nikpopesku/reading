COMPOSE_LOCAL = docker compose --env-file .env.local -f docker-compose-local.yml
COMPOSE_ORION = docker compose --env-file .env.orion -f docker-compose-orion.yml

.PHONY: local-up local-down orion-up orion-down shell migrate createsuperuser test lint format check

local-up:
	$(COMPOSE_LOCAL) up -d --build

local-down:
	$(COMPOSE_LOCAL) down

orion-up:
	$(COMPOSE_ORION) up -d --build

orion-down:
	$(COMPOSE_ORION) down

shell:
	$(COMPOSE_LOCAL) exec web sh

migrate:
	$(COMPOSE_LOCAL) exec web python manage.py migrate

createsuperuser:
	$(COMPOSE_LOCAL) exec web python manage.py createsuperuser

test:
	uv run python manage.py test

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run python manage.py check
