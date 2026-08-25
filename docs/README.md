# Documentation Index

This directory is the canonical documentation entry point for Enterprise CMDB.

## Architecture and product

- `schema-freeze-v0.3.md` — V0.3 domain/schema boundary.
- `development/current-status.md` — current implementation and deployment status.
- `development/roadmap.md` — next work and explicit non-goals.
- `development/guide.md` — engineering and change rules.

## Deployment

- `deployment/README.md` — supported runtime paths and which workflow owns each one.
- `deployment/azure-runtime-plan.md` — Azure Container Apps/Bicep runtime design.

## Repository ownership

```text
backend/        Application, tests, Docker runtime and the only Alembic migration tree
infra/azure/    Azure infrastructure and account/bootstrap helpers
k8s/base/       AKS/Kubernetes application manifests (Kustomize)
.github/        CI and deployment orchestration only
docs/           Architecture, operating guidance and current status
```

Deployment run status is intentionally not committed back into Git. GitHub Actions is the execution record; repository files describe desired state and operating rules.
