# Entra Production Validation

This branch exists only to run the complete delivery gate against the latest `main` after Microsoft Entra EasyAuth, application RBAC, federated identity, production deployment wiring, and one-shot GitHub OIDC bootstrap automation.

Required checks:

- uv lock consistency and frozen install
- Ruff
- Web Console JavaScript syntax
- Pytest including Entra Reader/Admin authorization and audited actor identity
- Alembic upgrade / drift check / downgrade / upgrade
- Docker Compose PostgreSQL runtime smoke
- frozen Docker build
- Azure OIDC bootstrap shell syntax
- Azure Bicep compile including Microsoft Graph v1.0 extension

Any failure is a release defect and must be fixed before Azure production deployment is triggered.

Validation iteration 3 includes the account-boundary bootstrap path after the first real Azure login failure.
