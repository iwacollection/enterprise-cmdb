# CMDB Development Status

## Current Phase

**V0.3 Domain Core complete. Microsoft Entra production security path validated. Azure actual deployment reached the account credential boundary.**

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
12. Azure OIDC bootstrap shell syntax
13. Azure Bicep compile including Microsoft Graph v1.0 extension and EasyAuth/FIC resources

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
- Persistent non-sensitive deployment result on `deploy/azure-production`
- One-shot account bootstrap script at `infra/azure/bootstrap-github-oidc.sh`

## Real Azure Deployment Evidence

Production deployment was actually triggered from `deploy/azure-production`.

Observed run:

```text
run_id: 32583001170
status: failure
failure_step: Azure login with OIDC
```

The runner reported that `client-id` and `tenant-id` were not supplied. The environment also showed an empty PostgreSQL administrator password. `Validate required secret`, resource-group creation, Bicep deployment, ACR login/push, Container App deployment, Entra provisioning, and external ingress were all skipped after the login failure.

Therefore this observed run did **not** reach an Azure resource mutation step. The failure is an account/environment configuration boundary, not an application or IaC failure.

## Active Account Gate

The repository now supplies a one-shot bootstrap:

```bash
az login
gh auth login
bash infra/azure/bootstrap-github-oidc.sh
```

It uses the currently selected Azure subscription to create/reuse the dedicated GitHub deployment service principal, configure the `production` GitHub OIDC federated credential, create the target resource group, grant resource-group-scoped `Contributor`, `Role Based Access Control Administrator`, and `AcrPush`, request/admin-consent Microsoft Graph `Application.ReadWrite.OwnedBy`, generate the PostgreSQL administrator secret, store the four GitHub `production` environment secrets, and retrigger the Azure deployment.

This is the only remaining unavoidable account boundary. The signed-in Azure identity must itself have permission to create Entra applications, assign the required Azure roles, and grant tenant admin consent. Those account privileges cannot be manufactured by repository code.

After the first successful deployment, a tenant administrator must explicitly assign real users/groups to `CMDB.Reader` or `CMDB.Admin`. The repository intentionally does not automate human/group role assignment because no tenant principal IDs have been supplied and doing so would require broader Graph app-role-assignment permissions.

## Engineering Constraints

- No speculative domain fields
- No silent fallback behavior
- Schema changes require design update + migration
- Core writes require transactional audit
- System-boundary input errors must be explicit
- Every deployment path must be machine validated
- Production authentication must fail closed before public ingress is enabled
