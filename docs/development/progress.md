# Development Progress

## Current Phase

**V0.3 implementation complete and deployment-ready.**

## Completed Delivery Chain

```text
Schema Freeze
→ Domain Models
→ Repositories
→ Services
→ REST APIs
→ Transactional Audit
→ Web Console
→ PostgreSQL Migrations
→ Docker Runtime
→ CI Validation
→ Azure Bicep
→ Azure OIDC Deployment Workflow
```

## Verified Core Flow

```text
Environment
→ Team
→ Service
→ Asset + Detail + IP + Endpoint
→ Asset Relation
→ ChangeRecord
```

The end-to-end test also verifies database readiness and audit coverage across Environment, Team, Service, Asset and AssetRelation.

## Current Validation Gate

- Ruff: required
- Pytest: required
- Migration round trip: required
- Alembic drift check: required
- Docker build: required
- Azure Bicep compile: required

## Remaining Decision Gate

No additional domain implementation is queued without a requirement change.

Production external access requires decisions for:

- Authentication provider
- Permission model / role scope

Until then Azure external ingress remains disabled by default.
