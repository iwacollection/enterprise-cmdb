# CMDB Development Roadmap

## V0.3 Completed

### Domain

- Environment
- Team
- Service
- Asset core
- Asset type-specific details
- Asset N:M Service mapping
- IP / Endpoint
- Relation graph
- Transactional audit

### Platform

- REST API
- Web Console
- PostgreSQL + Alembic
- Docker runtime
- CI pipeline
- Azure Bicep infrastructure
- Azure OIDC deployment workflow
- Liveness and database readiness

## Production Decision Gate

These items intentionally remain unresolved because they require business/security input and can affect Schema or production access policy:

1. Authentication provider
   - Microsoft Entra ID
   - existing company SSO / identity gateway
2. Permission model
   - roles
   - scope boundaries
   - identity-to-role mapping

No User / Role / Binding Schema is introduced until this decision is made.

## Explicit V0.3 Non-Goals

Consistent with the Schema Freeze, V0.3 does not add:

- Dynamic CIType / EAV engine
- Cloud resource synchronization
- Kubernetes auto-discovery
- IPAM
- Workflow engine
- Agent automation

These require new requirements and a new design/version rather than being silently added to V0.3.

## Engineering Rules

- No speculative features
- Schema changes require design update and migration
- Every feature requires tests
- Core writes require audit
- Every deployment path requires machine verification
