# Enterprise CMDB V0.3 Schema Freeze

## Overview

V0.3 is the first database schema freeze version.

The design uses:

```
Asset Aggregate
+
Type Specific Detail Tables
+
IP / Endpoint Child Entities
+
Service Many-to-Many Mapping
+
Asset Relation Graph
+
Transactional Audit
```

## Core Tables

```
environments
teams
services
assets
asset_services
asset_ips
asset_endpoints
compute_details
database_details
redis_details
message_queue_details
kubernetes_cluster_details
asset_relations
change_records
```

## Asset Model

Asset stores common fields:

- name
- asset_type
- status
- environment
- owner team

Asset does not directly reference Service.

Service relationship:

```
Asset N:M Service
```

through:

```
asset_services
```

## Ownership

Asset has one primary owner team.

Reason:

A resource needs one accountable team.

Collaboration does not equal ownership.

## Detail Model

Mapping:

```
server
  -> compute_details

virtual_machine
  -> compute_details

database
  -> database_details

redis
  -> redis_details

message_queue
  -> message_queue_details

kubernetes_cluster
  -> kubernetes_cluster_details

load_balancer
  -> no detail table yet
```

## Explicit Non Goals

V1 does not implement:

- Dynamic CIType model
- EAV attribute engine
- Cloud synchronization
- Kubernetes discovery
- IPAM
- Workflow engine
- Agent automation

## Schema Change Rule

Any schema change requires:

1. Explain current limitation
2. Explain trade-offs
3. Update design document
4. Create migration
5. Verify backward compatibility
