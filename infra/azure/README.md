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
                         +-- Entra EasyAuth before public ingress
```

The application has no Azure SDK dependency. Azure concerns remain in `infra/azure` and GitHub Actions.

## Network and identity baseline

- Container Apps uses a dedicated VNet subnet delegated to `Microsoft.App/environments`.
- PostgreSQL Flexible Server uses a separate delegated subnet and public network access is disabled.
- PostgreSQL name resolution uses `privatelink.postgres.database.azure.com`.
- ACR admin credentials and anonymous pull are disabled.
- A user-assigned managed identity receives only `AcrPull` for application image pulls.
- Production deployment creates the application privately, verifies Entra EasyAuth and app-role assignment requirements, and only then enables authenticated external ingress.

## Required GitHub production secrets

The `Deploy Azure` workflow uses Azure workload identity federation (OIDC). Configure these GitHub `production` environment secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

Do not store an Azure client secret in the repository.

The deployment identity needs enough Azure RBAC permission to:

1. create/update the selected resource group,
2. deploy the resources in that resource group,
3. create the `AcrPull` role assignment for the Container App pull identity,
4. push the built image to ACR,
5. read Azure Container Apps quota usage,
6. create supported Azure quota requests.

The role-assignment operation requires `Microsoft.Authorization/roleAssignments/write`. Image push requires `AcrPush`. Automatic quota requests require `Microsoft.Quota/quotas/write`; the built-in `Quota Request Operator` role is the intended least-privilege role for quota-request capability.

The workflow validates all four required GitHub secrets before calling `azure/login`, so a missing secret is reported as a configuration error rather than an ambiguous OIDC login failure.

## Quota-aware IaC policy

Quota policy is versioned in `infra/azure/quota-policy.json` and evaluated by `infra/azure/quota_guard.py` before deployment.

- `ManagedEnvironmentCount` is region scoped. If the target environment does not already exist and the region has no free environment slot, the workflow can submit a supported Azure Quota Management request and poll until capacity is usable.
- `ManagedEnvironmentConsumptionCores` is environment scoped. Azure requires a manual request for this quota class, so the workflow detects shortage immediately after the environment exists and stops before image build with exact current, limit, available, and required values.

The current environment policy reserves 1.5 free consumption cores, matching three application replicas at 0.5 core each. Update the quota policy together with application CPU or scaling changes.

## Deployment workflow

`.github/workflows/deploy-azure.yml` has two production entry points:

- manual `workflow_dispatch` for an explicitly requested deployment;
- push to the dedicated `deploy/azure-production` branch when `.github/deploy-production` changes.

Normal pull requests validate the code, Bicep template, and quota decision logic but do not receive production deployment credentials.

The production workflow performs:

1. Validate GitHub production secrets.
2. OIDC login to Azure.
3. Register/verify Azure quota tooling.
4. Create/update the resource group.
5. Check regional Container Apps quota and request supported capacity increases when needed.
6. Deploy VNet, private PostgreSQL, ACR, managed identity, Log Analytics, and the Container Apps environment.
7. Check environment consumption-core quota.
8. Build and push the backend image.
9. Deploy the CMDB privately with Entra authentication enabled.
10. Verify EasyAuth and app-role assignment requirements.
11. Enable authenticated external ingress.
12. Verify an active revision, health endpoint, and authentication redirect.

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
