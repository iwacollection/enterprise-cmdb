# Final V0.3 Validation

This branch exists only to run the complete delivery gate against the latest `main` branch after input-boundary, CRUD, web-console, runtime, Azure permission-mode, frozen dependency, and documentation cleanup.

Required checks:

- uv lock consistency and frozen install
- Ruff
- Web console JavaScript syntax
- Pytest
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose configuration
- real PostgreSQL 16 + Alembic + FastAPI `/health` and `/ready` smoke test
- Docker image build with frozen dependencies
- Azure Bicep compile

Any failure is treated as a development defect and must be fixed before V0.3 core is considered complete.

Validation iteration 8 verifies the documented final main branch after the successful technical delivery gate.
