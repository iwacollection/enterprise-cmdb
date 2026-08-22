# CMDB Development Status

## Current Phase

**V0.3 Domain Core complete. Azure deployment path validated.**

## Completed

### Domain

- Environment CRUD boundary
- Team CRUD boundary
- Service CRUD boundary
- Asset aggregate
- Asset N:M Service mapping
- IP / Endpoint child entities
- Compute / Database / Redis / Message Queue / Kubernetes detail models
- Asset relation graph
- Transactional audit for Environment / Team / Service / Asset / AssetRelation
- Reference boundary handling for Asset / Team / Service

### Runtime

- FastAPI REST API
- Web Console
- `/health` liveness
- `/ready` database readiness
- SQLAlchemy 2.x
- PostgreSQL runtime
- Alembic 001-006 migrations
- Docker image
- Docker Compose local runtime

### Verification

GitHub Actions validates:

1. Ruff
2. Pytest unit / repository / API / end-to-end tests
3. Alembic upgrade
4. Alembic schema drift check
5. Alembic downgrade to base
6. Alembic upgrade to head
7. Docker build
8. Azure Bicep compile

### Azure

- Azure Container Registry
- Azure Container Apps environment
- User-assigned identity + AcrPull
- VNet and delegated subnets
- Private PostgreSQL Flexible Server
- Private DNS
- Log Analytics
- Container App init migration
- Liveness / readiness probes
- GitHub Actions OIDC deployment workflow

## Production Gate

Before enabling external ingress, the following requires an explicit business/security decision:

1. Authentication provider (Microsoft Entra ID or existing company SSO)
2. Permission model and identity-to-role mapping

The current Azure template therefore defaults to `externalIngressEnabled=false`.

## Engineering Constraints

- No speculative domain fields
- No silent fallback behavior
- Schema changes require design update + migration
- Core writes require transactional audit
- System-boundary input errors must be explicit
- Every deployment path must be machine validated
