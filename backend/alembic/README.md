# Alembic Migrations

This is the only executable database migration tree in the repository.

- Runtime configuration: `backend/alembic.ini`
- Alembic environment: `backend/alembic/env.py`
- Migration revisions: `backend/alembic/versions/`

## Rules

1. Every schema change requires a new Alembic revision.
2. Never edit a revision that has already been applied to a shared environment.
3. One logical schema change per revision.
4. Downgrade logic is required when technically safe; otherwise document why rollback is not reversible.
5. CI must pass `alembic upgrade head`, `alembic check`, downgrade to base, and upgrade to head again.
6. Production migrations run before the application becomes ready.

Do not create a second `migrations/` tree. Documentation about schema evolution belongs here; executable revisions belong only in `alembic/versions/`.
