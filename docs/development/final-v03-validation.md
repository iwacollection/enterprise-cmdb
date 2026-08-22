# Final V0.3 Validation

This branch exists only to run the complete delivery gate against the latest `main` branch after input-boundary and CRUD completion.

Required checks:

- Ruff
- Pytest
- Alembic upgrade / drift check / downgrade / upgrade
- Docker image build
- Azure Bicep compile

Any failure is treated as a development defect and must be fixed before V0.3 core is considered complete.
