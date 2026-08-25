# Azure Container Apps Infrastructure

This directory owns the Azure Container Apps full-stack runtime. It is separate from the AKS application delivery path under `k8s/`.

## Topology

```text
GitHub Actions OIDC
        |
        +--> quota preflight
        +--> Azure Container Registry
        +--> Azure Container Apps Environment
                  |
                  +--> enterprise-cmdb Container App
                  |      +-- Alembic init migration
                  |      +-- FastAPI + Web Console
                  |      +-- Microsoft Entra EasyAuth
                  |
                  +--> VNet
                         |
                         +--> PostgreSQL Flexible Server
                              private delegated subnet
                              private DNS
```

## Source of truth

- `main.bicep` — Azure runtime infrastructure
- `entra.bicep` — Entra application/service principal/App Roles/FIC
- `quota-policy.json` — versioned quota policy
- `quota_guard.py` — quota decision logic
- `bootstrap-github-oidc.sh` — one-time account/OIDC bootstrap
- `.github/workflows/deploy-container-apps.yml` — manual deployment orchestration

The application itself has no Azure SDK dependency.

## Security baseline

- PostgreSQL public network access is disabled.
- PostgreSQL and Container Apps use separate delegated subnets.
- ACR admin credentials and anonymous pull are disabled.
- Application image pull uses managed identity with `AcrPull`.
- External ingress is disabled during initial deployment.
- Microsoft Entra EasyAuth is configured and verified before external ingress is enabled.
- `CMDB.Reader` and `CMDB.Admin` App Roles are provisioned.
- `appRoleAssignmentRequired=true` requires explicit user/group role assignment.
- The application trusts the EasyAuth principal boundary in `CMDB_AUTH_MODE=entra` and records the Entra object ID as the production audit actor.
- GitHub authenticates to Azure with OIDC; no long-lived Azure client secret is required.

## One-time GitHub OIDC bootstrap

Run from an operator workstation with Azure CLI and GitHub CLI authentication:

```bash
az login
gh auth login
bash infra/azure/bootstrap-github-oidc.sh
```

The script creates/reuses the deployment application and service principal, configures the GitHub `production` environment federated credential, prepares the resource group and required Azure roles, grants the Microsoft Graph application permission used by the Entra Bicep deployment, generates the PostgreSQL password, writes required GitHub environment secrets, and triggers the manual Container Apps deployment workflow on `main`.

The signed-in operator must already be allowed to create Entra applications, assign the required Azure roles and grant the required tenant admin consent. The script fails at that boundary rather than weakening permissions.

## Required GitHub `production` secrets

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

## Deployment identity permissions

The GitHub OIDC deployment identity needs enough permission to:

1. deploy resources in the target resource group,
2. create the `AcrPull` assignment for the Container App pull identity,
3. push the application image to ACR,
4. read/register Azure quota capabilities and submit supported quota requests,
5. create/update the Entra application and service principal used by EasyAuth.

The bootstrap currently configures resource-group `Contributor`, `Role Based Access Control Administrator`, `AcrPush`, subscription-scoped `Quota Request Operator`, and Microsoft Graph `Application.ReadWrite.OwnedBy` with admin consent.

## Quota policy

Quota requirements are versioned in `quota-policy.json` and evaluated by `quota_guard.py` before expensive deployment steps.

- `ManagedEnvironmentCount` can be requested automatically when the workflow is allowed to do so.
- `ManagedEnvironmentConsumptionCores` is treated as a manual-request boundary when the required free capacity is not available.

Application CPU/scaling changes must update quota policy in the same change set.

## Deployment workflow

`.github/workflows/deploy-container-apps.yml` is manual-only (`workflow_dispatch`).

Production sequence:

1. Validate required GitHub environment configuration.
2. Login to Azure using OIDC.
3. Verify/register providers and quota tooling.
4. Create/update the resource group.
5. Check/request supported regional quota.
6. Deploy the Azure foundation.
7. Check environment core quota.
8. Build and push the backend image.
9. Deploy the Container App with external ingress disabled and Entra auth enabled.
10. Verify EasyAuth and assignment requirements.
11. Enable external ingress.
12. Verify the active revision, `/health`, and unauthenticated login redirect.

GitHub Actions is the deployment history. The workflow does not write generated deployment status files back into the repository and does not use a dedicated trigger branch or marker file.

## First-user assignment

After a successful deployment, explicitly assign real Entra users/groups to one of:

- `CMDB.Reader`
- `CMDB.Admin`

The repository intentionally does not guess tenant principal IDs or auto-assign all users.

## Runtime database configuration

Azure sets database components separately so URL-reserved password characters remain safe:

- `CMDB_DB_HOST`
- `CMDB_DB_PORT`
- `CMDB_DB_USER`
- `CMDB_DB_PASSWORD`
- `CMDB_DB_NAME`

`DATABASE_URL` remains supported for local development and CI.

## Health semantics

- `/health` — process liveness
- `/ready` — database readiness (`SELECT 1`)

Health paths remain available to platform probes while CMDB data/UI routes are protected by the production authentication boundary.
