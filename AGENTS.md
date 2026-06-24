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

## Workflow

### Creating a PR (automated, from latest master)

```
git checkout master
git pull
git checkout -b <type>/<slug>
# make changes, commit
uv run ruff check .
uv run ruff format .
uv run python manage.py check
# if models changed: uv run python manage.py makemigrations
uv run python manage.py test
git push -u origin <branch>
gh pr create \
  --title "<type>(<scope>): <description>" \
  --body "<problem>\n\n<root cause>\n\n<fix>" \
  --base master
```

PR body template:
```
**Problem:** <what the user sees — bug, missing feature, pain point>

**Root cause:** <why it happens — specific code path, missing validation, etc.>

**Fix:** <what changed and how it resolves the root cause>
```

### Self-review checklist (what Hermes checks before opening the PR)
1. `ruff check .` passes — no lint violations
2. `ruff format .` passes — code is formatted (or `ruff format --check .`)
3. `python manage.py check` passes — no Django system check errors
4. `python manage.py makemigrations --check --dry-run` passes — no unapplied model changes (or a migration was committed)
5. `python manage.py test` passes — all tests green, no regressions
6. No debug code committed (`print()`, `breakpoint()`, hardcoded secrets, commented-out blocks)
7. If a migration was generated, it was committed (one migration per PR max)
8. If dependencies changed (`pyproject.toml`), `uv.lock` was committed
9. Branch was pushed before `gh pr create`

### CI failure recovery playbook

After creating the PR, wait for the CI workflow to complete. Fetch failures with:

```
gh run view --log-failed
```

Per-check recovery:

| CI Check | What to do |
|---|---|
| `ruff check .` fails | Run `uv run ruff check --fix .`, review changes, commit, push |
| `ruff format --check .` fails | Run `uv run ruff format .`, commit, push |
| `python manage.py check` fails | Read the error, fix the model/settings/URL issue, commit, push |
| `makemigrations --check --dry-run` fails | Run `uv run python manage.py makemigrations`, verify the migration is correct (one file max), commit migration + `uv.lock` if deps changed, push |
| Tests fail | Read the test output, fix the code or the test, commit, push |
| Docker build fails | Read the build log from the `docker-build` job, fix Dockerfile or dependencies (`pyproject.toml`), commit, push |

After each fix: `git push` — CI re-triggers automatically.

### Merge authority
- Hermes merges its own PR **after CI passes** — no human review needed for routine changes.
- Merge command: `gh pr merge --squash --delete-branch`
- Squash commit: always used. The PR title becomes the commit message, the PR body becomes the commit body.
- After merge, the remote branch is automatically deleted by `--delete-branch`. Delete local branch: `git branch -D <branch>`.

### Post-merge verification
Staging auto-deploys on push to master via the `deploy-staging.yml` workflow. After merging:

1. Wait for the deploy workflow to complete:
   ```
   gh run watch $(gh run list --workflow deploy-staging.yml --limit 1 --json databaseId --jq '.[0].databaseId')
   ```
2. Verify the staging site is responsive:
   ```
   curl -sf https://readingstaging.a007.bid/ | head -c 200
   ```
   Should return HTTP 200 and HTML content. If it fails, check the deploy workflow logs with `gh run view --log-failed`.

## Migration rules
- **One migration file per PR max.** If multiple models changed, edit the generated migration to merge them, or split into separate PRs.
- If you didn't change any models but CI reports `makemigrations --check` failure, it means someone else's branch changed models and its migration was not applied to your branch's test DB — this is a false positive from parallel development. Verify by running `uv run python manage.py makemigrations` yourself; if nothing is generated (empty "No changes detected"), force-push to trigger CI again.
- Always commit `uv.lock` if `pyproject.toml` was modified (deps changed).