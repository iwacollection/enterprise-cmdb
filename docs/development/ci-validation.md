# CMDB Core Validation Gate

This branch exists to exercise the real GitHub Actions validation path for the V0.3 implementation.

The CI gate must pass:

- dependency installation with uv
- Ruff checks for backend application and tests
- Pytest including repository persistence and end-to-end API tests
- Alembic upgrade -> schema drift check -> downgrade -> upgrade
- Docker image build
- Web console entrypoint

A failed gate is treated as a development defect and must be fixed before deployment work proceeds.

Validation iteration 5 verifies the OpenAPI route contract tests and complete delivery gates against the latest main branch.
