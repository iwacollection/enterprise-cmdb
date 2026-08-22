# Enterprise CMDB Backend

V0.3 implementation.

## Runtime

```text
FastAPI
  -> Service / Repository
  -> SQLAlchemy 2.x
  -> PostgreSQL
```

The backend also serves the same-origin Web Console from `/ui/`.

## Implemented V0.3 domains

- Environment CRUD
- Team CRUD
- Service CRUD
- Asset aggregate with typed details
- Asset N:M Service mapping
- IP / Endpoint
- Asset Relation graph
- Transactional ChangeRecord audit

Asset physical deletion is intentionally not part of V0.3.

## Local run

```bash
docker compose up --build
```

The API container waits for PostgreSQL, runs `alembic upgrade head`, then starts Uvicorn on port 8000.

## Dependencies

`pyproject.toml` declares dependency intent and `uv.lock` freezes the exact resolved graph. CI verifies the lockfile and installs with `uv sync --frozen --dev`; the production image installs with `uv sync --frozen --no-dev`.

When dependencies change, update both `pyproject.toml` and `uv.lock`.

## Verification

The repository CI validates:

- uv lock consistency / frozen install
- Ruff
- Web Console JavaScript syntax
- Pytest unit, repository, API and end-to-end tests
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose configuration
- Docker image build
- Azure Bicep compilation

Schema remains defined by `docs/schema-freeze-v0.3.md`. Any database schema change requires a design update and Alembic migration.
