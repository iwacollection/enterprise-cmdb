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
                         +-- Microsoft Entra EasyAuth
                         +-- CMDB.Reader / CMDB.Admin App Roles
                         +-- User Assigned Managed Identity + FIC
```

The application has no Azure SDK dependency. Azure concerns remain in `infra/azure` and GitHub Actions.

## Network baseline

- Container Apps uses a dedicated VNet subnet delegated to `Microsoft.App/environments`.
- PostgreSQL Flexible Server uses a separate delegated subnet.
- PostgreSQL public network access is disabled.
- PostgreSQL name resolution uses `privatelink.postgres.database.azure.com`.
- ACR admin credentials and anonymous pull are disabled.
- ACR `roleAssignmentMode` is explicitly pinned to `LegacyRegistryPermissions` so the `AcrPull`/`AcrPush` roles used by this deployment remain deterministic.
- A dedicated user-assigned managed identity receives only `AcrPull` for application image pulls.
- The application is deployed with external ingress disabled first. External ingress is enabled only after EasyAuth configuration has been created and verified.

## Production identity model

Production authentication is Microsoft Entra ID through Azure Container Apps built-in authentication (EasyAuth).

The deployment creates a single-tenant Entra application with exactly two application roles:

- `CMDB.Reader`: read Environment, Team, Service, Asset, Relation, and Audit data.
- `CMDB.Admin`: read and perform the existing audited CMDB writes and deletes.

The service principal sets `appRoleAssignmentRequired=true`. A tenant user without either role is not intentionally admitted to the CMDB.

The application does not maintain a second User/Role database. EasyAuth validates the Entra identity and injects `X-MS-CLIENT-PRINCIPAL`; the FastAPI authorization boundary reads the role claim and uses the Entra object ID as `ChangeRecord.changed_by` for production audit records.

Local development remains separate: `CMDB_AUTH_MODE=local` permits anonymous reads and requires `X-CMDB-Actor` for writes. Azure sets `CMDB_AUTH_MODE=entra`.

## Secretless EasyAuth

No long-lived Entra client secret is stored in GitHub or Container Apps.

`infra/azure/entra.bicep` creates:

1. the Entra application,
2. its service principal,
3. `CMDB.Reader` and `CMDB.Admin` App Roles,
4. a federated identity credential that trusts the Container App authentication managed identity.

The Container App auth configuration uses that user-assigned managed identity for the EasyAuth client assertion. The token store is not enabled because the CMDB does not need to call downstream APIs with the signed-in user's token.

## One-time GitHub OIDC bootstrap

A real production deployment was triggered from `deploy/azure-production`. The observed run `32583001170` failed at `azure/login` before any Azure resource deployment step because the GitHub `production` environment did not provide `AZURE_CLIENT_ID` / `AZURE_TENANT_ID`; `AZURE_POSTGRES_ADMIN_PASSWORD` was also absent.

The repository contains a one-shot bootstrap for this account boundary:

```bash
az login
gh auth login
bash infra/azure/bootstrap-github-oidc.sh
```

The script is intentionally fail-fast. It does the following against the currently selected Azure subscription:

1. creates or reuses the dedicated `github-enterprise-cmdb-deployer` Entra application and service principal,
2. creates the GitHub environment federated credential with subject `repo:iwacollection/enterprise-cmdb:environment:production`,
3. creates `rg-enterprise-cmdb` in `eastasia` if needed,
4. grants the deployment service principal `Contributor`, `Role Based Access Control Administrator`, and `AcrPush` at that resource-group scope,
5. requests Microsoft Graph `Application.ReadWrite.OwnedBy` and performs admin consent,
6. generates a strong PostgreSQL administrator password without printing it,
7. writes the four required values to GitHub `production` environment secrets with `gh secret set`,
8. triggers `deploy-azure.yml` on `deploy/azure-production`.

This bootstrap requires the signed-in Azure user to be allowed to create Entra applications, assign Azure roles at the target resource-group scope, and grant tenant admin consent for the Graph application permission. If any of those account-level permissions are missing, the script stops at that exact boundary instead of weakening the deployment identity.

## Required GitHub production secrets

The `Deploy Azure` workflow uses Azure workload identity federation (OIDC). These GitHub `production` environment secrets are consumed:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

The bootstrap script sets them. The workflow also validates all four values before `azure/login`, so a missing value fails with its exact secret name. Do not store an Azure client secret in the repository.

## Deployment identity permissions

The GitHub OIDC deployment identity needs Azure RBAC permission to:

1. deploy resources in the selected resource group,
2. create the `AcrPull` role assignment for the Container App pull identity,
3. push the built `enterprise-cmdb` image to ACR,
4. read Azure Container Apps quota usage,
5. submit supported quota increase requests.

The role-assignment operation requires `Microsoft.Authorization/roleAssignments/write`; `Role Based Access Control Administrator` supplies that action without the broader authorization surface of `User Access Administrator`. Image push requires `AcrPush` on this RBAC-only registry. Automatic quota requests require `Microsoft.Quota/quotas/write`; use `Quota Request Operator` when a separate least-privilege quota assignment is appropriate.

The same deployment identity also needs Microsoft Graph application permission to create/update the Entra application and service principal through the Microsoft Graph Bicep extension. The bootstrap requests the least-privilege `Application.ReadWrite.OwnedBy` permission with tenant admin consent rather than `Application.ReadWrite.All`.

This deployment intentionally does **not** assign real users or groups to `CMDB.Reader` or `CMDB.Admin`. Automating that would require additional Graph app-role-assignment permission and a concrete tenant principal ID. Those privileges and mappings are not guessed by the repository.

## Quota-aware IaC policy

Quota requirements are versioned in `infra/azure/quota-policy.json` and evaluated by `infra/azure/quota_guard.py` before expensive deployment steps.

- `ManagedEnvironmentCount` is region scoped. If the target Container Apps environment does not already exist and the selected region has no free environment slot, the workflow can submit an Azure Quota Management request and poll until the new limit becomes usable.
- `ManagedEnvironmentConsumptionCores` is environment scoped. Azure treats this quota as a manual-request class, so the workflow detects insufficient capacity immediately after the environment is created and stops before image build with exact `current`, `limit`, `available`, and `requiredAvailable` values.

The current policy reserves 1.5 free consumption cores, matching three application replicas at 0.5 core each. Application CPU or scaling changes must update this policy in the same change set.

## Deployment workflow

`.github/workflows/deploy-azure.yml` can run manually or from the dedicated `deploy/azure-production` trigger branch. Normal pull requests validate application code, the OIDC bootstrap shell, quota decision logic, and Bicep without receiving production credentials.

The production sequence is fail-closed:

1. Validate required GitHub production secrets.
2. OIDC login to Azure.
3. Register/verify Azure quota tooling.
4. Create/update the resource group.
5. Check regional Container Apps quota and request supported capacity increases when required.
6. Deploy VNet, private PostgreSQL, ACR, identities, Log Analytics, and Container Apps environment.
7. Check environment consumption-core quota before image build.
8. Build and push the frozen-dependency backend image.
9. Deploy the Container App with external ingress disabled and `CMDB_AUTH_MODE=entra`.
10. Create the Entra application, App Roles, service principal, FIC, and Container Apps auth config.
11. Verify EasyAuth is enabled and `appRoleAssignmentRequired=true`.
12. Only then enable external ingress.
13. Verify an active revision exists.
14. Verify `/health` is reachable and an unauthenticated `/ui/` request is redirected to login.
15. Persist a non-sensitive deployment result containing run ID, status, commit, resource group, location, and name prefix to the deployment branch for troubleshooting.

A failure before external-ingress enablement leaves the CMDB non-public. The deployment-result step runs with `always()` on `deploy/azure-production`, so successful and failed attempts both leave an auditable run pointer.

## Assign first users

After the first successful deployment, assign an Entra user or group to one of the generated enterprise application's roles:

- operators who only inspect configuration: `CMDB.Reader`
- administrators allowed to change configuration: `CMDB.Admin`

Do not give every tenant user a default role. The application is deliberately configured to require explicit assignment.

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
- Both paths are excluded from EasyAuth so Container Apps probes continue to function.
- CMDB data and Web Console routes remain authentication protected in production.
