# Azure Runtime Deployment Plan

## Goal

Deploy CMDB runtime on Microsoft Azure without coupling application design to a specific environment.

## Target Architecture V1

```
Azure Application Gateway (optional)
        |
        v
CMDB Backend Container
        |
        v
Azure Database for PostgreSQL
        |
        v
Backup / Monitoring
```

## Current Decision

The application keeps infrastructure concerns outside the domain layer.

No Azure SDK dependency is introduced into business code.

## Deployment Order

1. Local container runtime validation
2. PostgreSQL migration validation
3. Azure PostgreSQL deployment
4. Backend container deployment
5. CI/CD pipeline integration

## Pending Decisions

- Authentication provider
- Network topology
- Private endpoint requirement
- Backup retention policy
- Production availability requirements

These remain explicit until business requirements are confirmed.
