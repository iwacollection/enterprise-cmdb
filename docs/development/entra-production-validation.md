# Entra Production Validation

This branch exists only to run the complete delivery gate against the latest `main` after Microsoft Entra EasyAuth, application RBAC, federated identity, and production deployment wiring.

Required checks:

- uv lock consistency and frozen install
- Ruff
- Web Console JavaScript syntax
- Pytest including Entra Reader/Admin authorization and audited actor identity
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose PostgreSQL runtime smoke
- frozen Docker build
- Azure Bicep compile including Microsoft Graph v1.0 extension

Any failure is a release defect and must be fixed before Azure production deployment is triggered.

Validation iteration 2 includes the optional local actor OpenAPI contract fix.
