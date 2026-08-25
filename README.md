# Enterprise CMDB

Enterprise CMDB is a modular-monolith configuration management database for infrastructure and service relationships. The repository keeps the application, schema evolution, deployment manifests and Azure infrastructure as separate sources of truth.

## Current state

**V0.3 domain core is complete.** The application, PostgreSQL/Alembic runtime, audit model, web console and CI gate are implemented.

Deployment work currently has two explicit paths:

- **AKS application delivery** — the active cluster integration path. It deploys the application to an existing AKS/ACR/PostgreSQL platform through Kustomize.
- **Azure Container Apps full-stack deployment** — a manual alternative that provisions the Bicep-defined Azure stack and Microsoft Entra EasyAuth boundary.

These paths have different responsibilities and are documented under `docs/deployment/`.

## Repository layout

```text
enterprise-cmdb/
├── backend/                 # FastAPI application, tests, Docker and Alembic
│   ├── app/
│   ├── alembic/
│   │   └── versions/        # only executable database migration tree
│   └── tests/
├── infra/
│   └── azure/               # Azure Bicep, OIDC bootstrap and quota helpers
├── k8s/
│   └── base/                # AKS/Kubernetes Kustomize source of truth
├── docs/                    # architecture, deployment and development docs
└── .github/workflows/       # CI and deployment orchestration
```

See `docs/README.md` for the documentation map.

## Implemented domain

- Environment
- Team
- Service
- Asset
- Asset N:M Service mapping
- IP / Endpoint
- Compute / Database / Redis / Message Queue / Kubernetes details
- Asset relation graph
- Transactional ChangeRecord audit
- Web Console
- REST API

```text
Environment
    |
    +---- Asset ---- N:M ---- Service ---- Team
             |
             +---- IP / Endpoint
             +---- Type-specific Detail
             +---- Relation ---- Asset
             +---- ChangeRecord
```

## Authentication

The application supports:

- `CMDB_AUTH_MODE=local` for local development
- `CMDB_AUTH_MODE=entra` for the Microsoft Entra EasyAuth path

The Container Apps design provisions `CMDB.Reader` and `CMDB.Admin` App Roles and uses the verified Entra principal Object ID as the audit actor.

The AKS deployment workflow currently focuses on application delivery into an existing platform. Production identity/ingress controls for that runtime must be completed before treating the AKS path as an internet-facing production endpoint.

## Local development

```bash
cd backend
docker compose up --build
```

Runtime startup performs:

```text
alembic upgrade head
-> FastAPI
-> http://localhost:8000/ui/
```

Health endpoints:

```text
GET /health   # process liveness
GET /ready    # database readiness
```

## CI gate

Pull requests and pushes to `main` validate:

```text
uv lock --check
-> frozen dependency install
-> Ruff
-> Web Console JavaScript syntax
-> Pytest
-> Alembic upgrade/check/downgrade/upgrade
-> Docker Compose validation
-> PostgreSQL + FastAPI smoke test
-> Docker image build
-> Kubernetes Kustomize render
-> Azure bootstrap tests
-> Azure Bicep compile
```

## Deployment

### AKS

Use `.github/workflows/deploy-aks.yml` for the active AKS application delivery path.

It requires existing AKS, ACR and PostgreSQL resources and performs OIDC login, ACR permission verification, image build/push, Kubernetes secret update, Kustomize apply and rollout verification.

### Azure Container Apps

Use `.github/workflows/deploy-container-apps.yml` for the manual full-stack Bicep deployment path.

It provisions/updates the Azure Container Apps runtime, ACR, private PostgreSQL networking and Entra EasyAuth integration. It no longer depends on a special deployment branch or marker file.

See `docs/deployment/README.md`.

## Engineering rules

- One source of truth per concern.
- No speculative domain fields.
- No duplicate migration trees.
- No parallel Helm/Kustomize definitions for the same runtime without a migration plan.
- Schema changes require a new Alembic revision and CI verification.
- Production configuration must fail closed; do not substitute fake secrets/defaults.
- Deployment execution history belongs in GitHub Actions, not generated status files committed back to Git.
