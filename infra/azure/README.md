# Azure Deployment

## Runtime topology

```text
GitHub Actions (OIDC)
        |
        +--> Azure quota preflight / supported quota request
        |
        +--> Azure Container Registry
        |
        +--> Azure Container Apps Environment -- VNet -- PostgreSQL Flexible Server
                     |                              |
                     |                              +-- private delegated subnet
                     |
                     +-- enterprise-cmdb Container App
                         +-- init container: alembic upgrade head
                         +-- app container: FastAPI + Web Console
```

The application has no Azure SDK dependency. Azure concerns remain in `infra/azure` and GitHub Actions.

## Network baseline

- Container Apps uses a dedicated VNet subnet delegated to `Microsoft.App/environments`.
- PostgreSQL Flexible Server uses a separate delegated subnet.
- PostgreSQL public network access is disabled.
- PostgreSQL name resolution uses `privatelink.postgres.database.azure.com`.
- Container App external ingress defaults to `false`.
- ACR admin credentials and anonymous pull are disabled.
- ACR `roleAssignmentMode` is explicitly pinned to `LegacyRegistryPermissions` so the legacy `AcrPull`/`AcrPush` roles used by this deployment remain deterministic if Azure changes the default mode in the future.
- A user-assigned managed identity receives only `AcrPull` for application image pulls.

The Container Apps environment remains externally capable so ingress can be enabled later without recreating the environment. The CMDB app itself stays non-public until an authentication policy is selected.

## Required GitHub production secrets

The `Deploy Azure` workflow uses Azure workload identity federation (OIDC). Configure these GitHub production environment secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

Do not store an Azure client secret in the repository.

The deployment identity needs enough Azure RBAC permission to:

1. create/update the selected resource group if the workflow is expected to create it,
2. deploy the resources in that resource group,
3. create the `AcrPull` role assignment for the Container App pull identity,
4. push the built `enterprise-cmdb` image to the created registry,
5. read Azure Container Apps quota usage,
6. create supported Azure quota requests when regional capacity is exhausted.

The role-assignment operation requires `Microsoft.Authorization/roleAssignments/write`; plain `Contributor` alone is not sufficient for that operation. Image push requires `AcrPush` on this RBAC-only registry. Automatic quota increase requests require `Microsoft.Quota/quotas/write`; the built-in `Quota Request Operator` role is the intended least-privilege role for this capability. Scope these permissions as narrowly as the organization's Azure governance model permits.

## Quota-aware IaC policy

Quota policy is versioned in `infra/azure/quota-policy.json` and evaluated by `infra/azure/quota_guard.py` before deployment.

The deployment currently manages two Azure Container Apps quota classes:

- `ManagedEnvironmentCount` is region scoped. If the target environment does not already exist and the region has no free environment slot, the workflow can automatically submit an Azure Quota Management System request and wait for the new limit to become usable.
- `ManagedEnvironmentConsumptionCores` is environment scoped. Azure documents this quota as a manual request. The workflow checks it immediately after the environment exists and stops before image build if the environment does not have enough capacity for the configured application scale target.

This separation is intentional: supported integrated quota requests are automated, while approval-bound quotas are detected early and reported with exact current/limit/available values instead of failing later during application deployment.

The current policy reserves 1.5 free consumption cores, matching three 0.5-core application replicas. Update the policy together with application CPU or scaling changes.

## Deployment workflow

`.github/workflows/deploy-azure.yml` supports two controlled entry points:

- manual `workflow_dispatch`, with explicit resource-group, region, prefix, ingress, and automatic-quota-request inputs;
- a same-repository pull request whose branch name starts with `deploy/` and changes Azure IaC or the deployment workflow. This path exists so the deployment run is attached to the PR and can be inspected, fixed, and re-run before merge.

The workflow performs:

1. OIDC login to Azure.
2. Register/verify Azure quota tooling.
3. Create/update the resource group.
4. Check regional Container Apps quota and request supported capacity increases when necessary.
5. Deploy VNet, private PostgreSQL, ACR, managed identity, Log Analytics, and Container Apps environment.
6. Check environment consumption-core quota.
7. Build the backend Docker image.
8. Push the image to ACR.
9. Deploy the Container App.
10. Run Alembic through the Container App init container before the application starts.
11. Verify an active revision exists.
12. Run `/health` smoke test only when external ingress was explicitly enabled.

## Runtime database configuration

Azure sets database settings as separate environment variables so passwords with URL-reserved characters remain valid:

- `CMDB_DB_HOST`
- `CMDB_DB_PORT`
- `CMDB_DB_USER`
- `CMDB_DB_PASSWORD`
- `CMDB_DB_NAME`

`DATABASE_URL` remains supported for local development and CI. Component-based PostgreSQL configuration uses `sslmode=require`.

## Health semantics

- `/health` proves the application process is alive.
- `/ready` executes `SELECT 1` and proves the database is reachable.
- Container Apps uses `/health` for liveness and `/ready` for readiness.

## Production security gate

`external_ingress=false` is intentional. Before changing it to `true`, configure the production authentication policy (for example Microsoft Entra ID through Container Apps built-in authentication or the company's existing identity gateway).

Until authentication is connected, `X-CMDB-Actor` is a caller-supplied audit identity and must not be treated as a cryptographically verified user identity.

Authentication and permission mapping are production security decisions and are not silently replaced by a shared password or hard-coded user list.
