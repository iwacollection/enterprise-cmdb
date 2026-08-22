# Azure Deployment

## Runtime topology

```text
GitHub Actions (OIDC)
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
4. push the built `enterprise-cmdb` image to the created registry.

The role-assignment operation requires `Microsoft.Authorization/roleAssignments/write`; plain `Contributor` alone is not sufficient for that operation. Image push requires `AcrPush` on this RBAC-only registry. Scope these permissions as narrowly as the organization's Azure governance model permits.

## Deployment workflow

Run `.github/workflows/deploy-azure.yml` manually.

Inputs:

- resource group
- Azure region
- short resource prefix
- external ingress toggle

The workflow performs:

1. OIDC login to Azure.
2. Create/update the resource group.
3. Deploy VNet, private PostgreSQL, ACR, managed identity, Log Analytics, and Container Apps environment.
4. Build the backend Docker image.
5. Push the image to ACR.
6. Deploy the Container App.
7. Run Alembic through the Container App init container before the application starts.
8. Verify an active revision exists.
9. Run `/health` smoke test only when external ingress was explicitly enabled.

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
