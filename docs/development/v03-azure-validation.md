# V0.3 Azure Delivery Validation

This pull request exists only to exercise the complete delivery gate against the latest `main` branch.

Required checks:

- Ruff
- Pytest, including end-to-end transactional audit and reference-boundary coverage
- Alembic upgrade / drift check / downgrade / upgrade
- Docker image build
- Azure Bicep compile

A failed check is treated as a development defect and must be fixed before deployment.

Validation iteration 3 verifies the latest Team/Service reference-boundary changes and the compiled Azure runtime template against current `main`.
