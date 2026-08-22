# Final V0.3 Validation

This branch exists only to run the complete delivery gate against the latest `main` branch after input-boundary, CRUD, web-console, runtime, and Azure permission-mode cleanup.

Required checks:

- Ruff
- Web console JavaScript syntax
- Pytest
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose validation
- Docker image build
- Azure Bicep compile

Any failure is treated as a development defect and must be fixed before V0.3 core is considered complete.

Validation iteration 3 includes the latest main branch changes.
