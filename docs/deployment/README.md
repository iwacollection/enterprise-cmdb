# Deployment Paths

Enterprise CMDB currently has two intentionally different Azure deployment paths. They are not two competing release pipelines.

## 1. AKS application delivery — active cluster path

Workflow: `.github/workflows/deploy-aks.yml`

Purpose: deploy the CMDB application into an existing AKS + ACR + PostgreSQL platform.

```text
GitHub Actions OIDC
  -> AKS credentials
  -> verify ACR pull access
  -> build/push image to ACR
  -> create/update Kubernetes secret
  -> kubectl apply -k k8s/base
  -> rollout verification
```

Required environment secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AKS_RESOURCE_GROUP`
- `AKS_CLUSTER_NAME`
- `ACR_NAME`
- `ACR_LOGIN_SERVER`
- `CMDB_DATABASE_URL`

This path assumes the platform resources already exist. It does not provision AKS, ACR or PostgreSQL.

## 2. Azure Container Apps full-stack provisioning — manual alternative

Workflow: `.github/workflows/deploy-container-apps.yml`

Purpose: provision/update the Bicep-defined Azure Container Apps stack, including ACR, private PostgreSQL networking and Microsoft Entra EasyAuth.

This workflow is manual-only. A marker file or special deployment branch is no longer used to trigger production deployment.

See `azure-runtime-plan.md` and `../../infra/azure/README.md`.

## Source-of-truth rules

- Application code: `backend/`
- Database migration source of truth: `backend/alembic/versions/`
- AKS desired manifests: `k8s/base/`
- Azure Container Apps desired infrastructure: `infra/azure/`
- Execution history: GitHub Actions, not generated status files committed to the repository

Do not add a second Helm/Kustomize implementation for the same deployment path without an explicit migration plan.
