# Final V0.3 Validation

This branch exists only to run the complete delivery gate against the latest `main` branch after input-boundary, CRUD, web-console, runtime, Azure permission-mode, and frozen dependency cleanup.

Required checks:

- uv lock consistency and frozen install
- Ruff
- Web console JavaScript syntax
- Pytest
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose validation
- Docker image build with frozen dependencies
- Azure Bicep compile

Any failure is treated as a development defect and must be fixed before V0.3 core is considered complete.

Validation iteration 4 includes the latest main branch changes.
