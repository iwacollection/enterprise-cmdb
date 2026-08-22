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
- Reference boundary handling for Environment / Team / Service / Asset
- Explicit duplicate-name conflicts for Environment / Team / Service
- API input limits aligned with persistence column limits

### Runtime

- FastAPI REST API
- Web Console with create/update/delete operations exposed where V0.3 permits them
- `/health` liveness
- `/ready` database readiness
- SQLAlchemy 2.x
- PostgreSQL runtime
- Alembic 001-006 migrations
- Docker image
- Docker Compose local runtime
- `uv.lock` reproducible dependency graph

### Verification

GitHub Actions validates:

1. uv lock consistency and frozen dependency install
2. Ruff
3. Web Console JavaScript syntax
4. Pytest unit / repository / API / end-to-end tests
5. Alembic upgrade
6. Alembic schema drift check
7. Alembic downgrade to base
8. Alembic upgrade to head
9. Docker Compose configuration
10. Docker build using frozen dependencies
11. Azure Bicep compile

### Azure

- Azure Container Registry with explicit legacy RBAC mode for deterministic AcrPull/AcrPush semantics
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

Actual Azure resource creation also requires the user's Azure OIDC credentials and RBAC permissions; those credentials are not available to this repository connector.

## Engineering Constraints

- No speculative domain fields
- No silent fallback behavior
- Schema changes require design update + migration
- Core writes require transactional audit
- System-boundary input errors must be explicit
- Every deployment path must be machine validated
