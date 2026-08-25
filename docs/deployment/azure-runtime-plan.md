# Azure Container Apps Runtime Plan

## Scope

This document describes the **manual Azure Container Apps full-stack deployment path**. It is not the AKS application delivery path.

Infrastructure source of truth: `infra/azure/`

Workflow: `.github/workflows/deploy-container-apps.yml`

## Runtime architecture

```text
GitHub Actions (OIDC)
        |
        +--> Azure Container Registry
        |
        +--> Azure Container Apps Environment
                  |
                  +--> enterprise-cmdb Container App
                  |      +-- init: alembic upgrade head
                  |      +-- app: FastAPI + Web Console
                  |      +-- Microsoft Entra EasyAuth
                  |
                  +--> VNet
                         |
                         +--> PostgreSQL Flexible Server
                              private delegated subnet
                              private DNS
```

## Implemented controls

- Azure concerns remain outside the domain layer.
- Infrastructure is defined in Bicep.
- PostgreSQL public network access is disabled.
- Container Apps and PostgreSQL use separate delegated subnets.
- ACR admin user and anonymous pull are disabled.
- Container image pull uses managed identity with `AcrPull`.
- Database credentials are injected as Container App secrets.
- Alembic runs before the application becomes ready.
- `/health` is liveness; `/ready` is database readiness.
- Microsoft Entra EasyAuth is enabled before public ingress is opened.
- `CMDB.Reader` and `CMDB.Admin` App Roles are provisioned.
- `appRoleAssignmentRequired=true` prevents unassigned tenant users from becoming CMDB users.
- Deployment authentication uses GitHub OIDC; no Azure client secret is stored in Git.

## Deployment order

1. Authenticate to Azure using GitHub OIDC.
2. Validate quota/capability prerequisites.
3. Create/update the resource group and Azure foundation.
4. Build and push the application image to ACR.
5. Deploy the Container App privately with Entra auth enabled.
6. Verify the auth configuration and service-principal assignment requirement.
7. Enable external ingress only after the auth boundary is verified.
8. Verify the active revision and protected endpoint behavior.

## Required GitHub `production` secrets

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

## Operating model

This workflow is `workflow_dispatch` only. A special deployment branch, marker file, or generated status commit is not part of the deployment protocol.

GitHub Actions is the execution/audit record. Desired infrastructure remains in `infra/azure/`.

## Relationship to AKS

The AKS workflow deploys the application into an existing Kubernetes platform and does not use this Container Apps runtime. The two paths can coexist because they own different runtime targets, but neither should create a second source of truth for the other's manifests or infrastructure.
