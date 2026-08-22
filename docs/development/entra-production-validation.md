# Entra Production Validation

This branch exists only to run the complete delivery gate against the latest `main` after Microsoft Entra EasyAuth, application RBAC, federated identity, production deployment wiring, one-shot GitHub OIDC bootstrap automation, and the recorded real Azure login failure.

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

Any failure is a release defect and must be fixed before Azure production deployment is retried.

Validation iteration 4 is the final repository gate against the latest main, including account-boundary documentation and bootstrap automation.
