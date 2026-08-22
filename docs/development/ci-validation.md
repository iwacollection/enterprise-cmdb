# CMDB Core Validation Gate

This branch exists to exercise the real GitHub Actions validation path for the V0.3 implementation.

The CI gate must pass:

- dependency installation with uv
- Ruff checks for backend application and tests
- Pytest including repository persistence tests
- end-to-end API flow covering Environment -> Team -> Service -> Asset -> Relation -> ChangeRecord

A failed gate is treated as a development defect and must be fixed before deployment work proceeds.

Validation iteration 2 verifies the adjusted FastAPI-aware Ruff policy and the expanded CMDB core on the latest main branch.
