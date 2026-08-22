# Development Guide

## Engineering Rules

### 1. Minimal Change

Only modify files required by current task.

Do not add speculative features.

### 2. Fail Fast

Do not hide errors.

Forbidden:

- broad catch
- silent fallback
- rescue nil style handling
- fake default values

### 3. Boundary Validation

Validation is required only at system boundaries:

- API input
- external API
- network input

Internal code trusts contracts.

### 4. Success Criteria

Every feature must define:

- expected behavior
- verification method
- failure conditions

Implementation continues until verification passes.

### 5. Migration Rules

Database changes require:

- migration file
- rollback consideration
- test verification

### 6. Architecture Boundary

Current architecture target:

Modular Monolith

Not:

- microservice decomposition
- event driven platform
- distributed workflow

unless real requirements appear.
