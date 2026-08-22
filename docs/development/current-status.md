# CMDB Development Status

## Current Phase

**V0.3 Domain Core complete. Microsoft Entra production security path validated. Azure actual deployment is the active phase.**

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
- V0.3 Schema remains frozen; production authentication did not add CMDB User/Role tables

### Authentication / Authorization

- Microsoft Entra ID selected as the production authentication provider
- Azure Container Apps EasyAuth as the platform authentication boundary
- `CMDB.Reader` App Role for read access
- `CMDB.Admin` App Role for read/write/delete access within existing V0.3 APIs
- Service Principal uses `appRoleAssignmentRequired=true`
- FastAPI trusts EasyAuth `X-MS-CLIENT-PRINCIPAL` only when `CMDB_AUTH_MODE=entra`
- Entra Object ID becomes the production `ChangeRecord.changed_by` audit actor
- Local mode remains anonymous-read / explicit `X-CMDB-Actor` write
- Secretless EasyAuth through User Assigned Managed Identity + Federated Identity Credential
- Microsoft Graph Bicep v1.0 provisions the Entra application, service principal, App Roles, and FIC

### Runtime

- FastAPI REST API
- Web Console with create/update/delete operations exposed where V0.3 permits them
- `/health` liveness
- `/ready` database readiness
- SQLAlchemy 2.x
- PostgreSQL runtime
- Alembic 001-006 migrations
- Docker image
- Docker Compose local runtime with API readiness healthcheck
- `uv.lock` reproducible dependency graph

### Verification

GitHub Actions validates:

1. uv lock consistency and frozen dependency install
2. Ruff
3. Web Console JavaScript syntax
4. Pytest unit / repository / API / end-to-end tests including Entra Reader/Admin authorization and trusted audit actor
5. Alembic upgrade
6. Alembic schema drift check
7. Alembic downgrade to base
8. Alembic upgrade to head
9. Docker Compose configuration
10. Real PostgreSQL 16 + Alembic + FastAPI `/health` and `/ready` smoke test
11. Docker build using frozen dependencies
12. Azure Bicep compile including Microsoft Graph v1.0 extension and EasyAuth/FIC resources

Current production-security validation result: `29 passed`, PostgreSQL runtime smoke succeeded, frozen Docker build succeeded, and Microsoft Graph/EasyAuth Bicep compilation succeeded. The remaining pytest warning is from the third-party FastAPI/Starlette TestClient compatibility layer.

### Azure

- Azure Container Registry with explicit legacy RBAC mode for deterministic AcrPull/AcrPush semantics
- Azure Container Apps environment
- Dedicated image-pull managed identity + AcrPull
- Dedicated authentication managed identity + Entra federated identity credential
- Microsoft Entra App Registration + Service Principal
- `CMDB.Reader` / `CMDB.Admin` App Roles
- VNet and delegated subnets
- Private PostgreSQL Flexible Server
- Private DNS
- Log Analytics
- Container App init migration
- Liveness / readiness probes
- GitHub Actions OIDC deployment workflow
- Fail-closed deployment ordering: private app + auth verification before external ingress

## Active Production Gate

The application architecture decision is complete. Actual Azure resource creation now depends on the target tenant/account boundary:

1. GitHub `production` environment must contain working `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, and `AZURE_POSTGRES_ADMIN_PASSWORD` secrets.
2. The GitHub OIDC identity needs Azure resource deployment permission, `Microsoft.Authorization/roleAssignments/write`, and ACR push permission.
3. The deployment identity needs Microsoft Graph application permission for the Entra application/service-principal resources, preferably least-privilege `Application.ReadWrite.OwnedBy` with tenant admin consent.
4. After deployment, a tenant administrator must explicitly assign real users/groups to `CMDB.Reader` or `CMDB.Admin`.

The repository intentionally does not automate human/group role assignment because no tenant principal IDs have been supplied and doing so would require broader Graph app-role-assignment permissions.

## Engineering Constraints

- No speculative domain fields
- No silent fallback behavior
- Schema changes require design update + migration
- Core writes require transactional audit
- System-boundary input errors must be explicit
- Every deployment path must be machine validated
- Production authentication must fail closed before public ingress is enabled
