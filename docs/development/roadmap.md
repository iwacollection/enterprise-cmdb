# CMDB Development Roadmap

## V0.3 completed

- Domain model and CRUD boundaries
- Asset relation graph and transactional audit
- Web Console and REST API
- PostgreSQL + Alembic
- Docker runtime
- CI validation
- Azure Bicep infrastructure
- Microsoft Entra EasyAuth / App Role path for Container Apps
- AKS application deployment workflow and Kustomize baseline

## Next priorities

### 1. AKS production hardening

- define the final production ingress and Microsoft Entra authentication boundary for AKS
- add explicit network/security policy required by that boundary
- add rollout/rollback operating guidance
- verify database migration behavior during rolling deployment

### 2. Delivery governance

- protect `main`
- require CI before merge
- keep deployment environments approval-gated
- remove obsolete deployment branches after their history is no longer operationally needed

### 3. CMDB product capability

Only after production runtime is stable, evaluate the next product requirements such as cloud/Kubernetes discovery, reconciliation and relationship ingestion. These require a new scoped design rather than silently expanding V0.3.

## Explicit V0.3 non-goals

- Dynamic EAV/CIType platform
- Generic workflow engine
- Unbounded plugin framework
- Automatic self-healing
- Multiple parallel deployment engines for the same runtime

## Engineering rules

- one source of truth per concern
- schema changes require design + migration + tests
- core writes require audit
- production configuration fails closed
- every supported deployment path must have machine verification
