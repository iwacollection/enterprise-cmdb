# Development Guide

## 1. Keep one source of truth

Each concern has one canonical location:

- application: `backend/app/`
- migrations: `backend/alembic/versions/`
- AKS manifests: `k8s/base/`
- Azure infrastructure: `infra/azure/`
- CI/deployment orchestration: `.github/workflows/`
- design/operations documentation: `docs/`

Do not create parallel directories that describe the same concern.

## 2. Minimal change

Only modify files required by the current task. Do not add speculative platform features.

## 3. Fail fast

Do not hide deployment or application errors. Avoid broad catches, silent fallbacks and fake production defaults.

At external boundaries, validate required configuration before mutating infrastructure.

## 4. Verification is part of the change

Every change must define:

- expected behavior
- verification method
- failure conditions

The repository CI is the minimum merge gate.

## 5. Database changes

Every schema change requires a new Alembic revision under `backend/alembic/versions/` and must pass the migration round-trip gate.

## 6. Architecture boundary

The application remains a modular monolith unless a real scaling or ownership requirement justifies decomposition.

Do not introduce a second deployment engine (for example another Helm baseline beside Kustomize) without explicitly replacing the current source of truth.
