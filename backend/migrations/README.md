# Migration Rules

Migration order follows CMDB V0.3 dependency order.

1. environments
2. teams
3. services
4. assets
5. asset relations and child resources

Rules:

- Every schema change requires a migration.
- Migration must be reversible when technically possible.
- No production data changes without explicit migration review.
