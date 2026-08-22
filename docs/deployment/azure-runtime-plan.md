# Azure Runtime Deployment Plan

## Goal

Deploy Enterprise CMDB on Microsoft Azure while keeping Azure concerns outside the domain layer.

## V0.3 Runtime Architecture

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
                  |
                  +--> VNet
                         |
                         +--> PostgreSQL Flexible Server
                              private delegated subnet
                              private DNS
```

## Implemented Baseline

- Azure SDK is not used in domain/application code.
- Infrastructure is defined in `infra/azure/main.bicep`.
- Deployment is defined in `.github/workflows/deploy-azure.yml`.
- PostgreSQL public network access is disabled.
- Container Apps and PostgreSQL use separate delegated subnets.
- ACR admin user and anonymous pull are disabled.
- Container image pull uses a user-assigned managed identity with `AcrPull`.
- Database credentials are injected as Container App secrets.
- Alembic runs in an init container before the application becomes ready.
- `/health` validates process liveness.
- `/ready` validates database connectivity.
- Log Analytics receives Container Apps logs.
- External application ingress defaults to disabled.

## Deployment Order

1. GitHub Actions authenticates to Azure using OIDC.
2. Create/update resource group.
3. Deploy network, PostgreSQL, ACR, identity, Log Analytics and Container Apps environment.
4. Build application image.
5. Push image to ACR.
6. Deploy Container App with the image.
7. Init container applies Alembic migrations.
8. Container Apps probes liveness/readiness.
9. Verify an active revision exists.
10. Run external smoke test only if external ingress was explicitly enabled.

## Required GitHub Production Secrets

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_POSTGRES_ADMIN_PASSWORD`

Azure login uses federated workload identity; no Azure client secret is stored in the repository.

## Resolved Infrastructure Defaults

- Runtime: Azure Container Apps, not AKS
- Database: Azure Database for PostgreSQL Flexible Server
- Registry: Azure Container Registry Basic
- Database networking: private VNet only
- PostgreSQL backup retention: 7 days default, parameterized up to 35
- PostgreSQL HA: disabled for the initial V0.3 baseline
- App replicas: min 1 / max 3
- Public CMDB ingress: disabled by default

These are minimal V0.3 deployment defaults, not claims about a future production SLA.

## Remaining Production Security Decision

Before external ingress is enabled, explicitly choose:

- Authentication provider (Microsoft Entra ID or existing company identity system)
- Permission model and role scope

These decisions affect production security and potentially database Schema, so they are not inferred by the implementation.
