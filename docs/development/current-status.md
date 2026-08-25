# CMDB Current Status

## Phase

**V0.3 domain core complete. Deployment paths are being production-hardened.**

## Application

Completed:

- Environment / Team / Service / Asset domain
- Asset-to-Service N:M mapping
- IP / Endpoint and type-specific asset details
- Asset relation graph
- Transactional ChangeRecord audit
- FastAPI REST API
- Web Console
- PostgreSQL + SQLAlchemy 2.x
- Alembic schema migrations
- Docker / Docker Compose runtime
- `/health` liveness and `/ready` database readiness

## Authentication

The Microsoft Entra path is implemented for the Azure Container Apps runtime:

- `CMDB.Reader`
- `CMDB.Admin`
- `appRoleAssignmentRequired=true`
- EasyAuth principal validation
- Entra Object ID used as the trusted production audit actor
- managed identity / federated identity integration

Local development remains `CMDB_AUTH_MODE=local`.

## Deployment paths

### AKS — active application delivery path

`.github/workflows/deploy-aks.yml`

The workflow deploys into existing AKS/ACR/PostgreSQL resources and owns application delivery only. Kustomize manifests under `k8s/base/` are the single Kubernetes source of truth.

Current production-hardening work for this path:

- keep database configuration fail-closed
- verify ACR pull role idempotently instead of swallowing RBAC failures
- use `/ready` for Kubernetes readiness
- complete the intended production identity/ingress model before exposing the service externally

### Azure Container Apps — manual full-stack alternative

`.github/workflows/deploy-container-apps.yml`

Bicep under `infra/azure/` defines ACR, Container Apps, private PostgreSQL networking, identities and Entra EasyAuth. This path is manual-only and no longer uses a deployment marker file or special branch as an execution protocol.

## CI

The merge gate covers:

1. frozen uv dependency graph
2. Ruff
3. Web Console JavaScript syntax
4. Pytest
5. Alembic upgrade/check/downgrade/upgrade
6. Docker Compose validation
7. real PostgreSQL + FastAPI health/readiness smoke test
8. Docker image build
9. Kubernetes Kustomize render
10. Azure bootstrap/unit checks
11. Azure Bicep compile

## Repository rules

- The only executable migration tree is `backend/alembic/versions/`.
- The only Kubernetes desired-state tree is `k8s/base/`.
- Azure desired infrastructure lives under `infra/azure/`.
- GitHub Actions owns execution history; deployment status files are not committed back into the repository.
- New deployment engines require an explicit replacement/migration plan rather than being added in parallel.
