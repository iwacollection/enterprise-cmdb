# Enterprise CMDB

企业级运维配置管理数据库（Configuration Management Database），用于建立基础设施与服务关系的 Source of Truth（事实源）。

## Current Version

**V0.3 Core Complete / Entra Production Path Validated / Azure Deployment In Progress**

数据库 Schema 仍冻结在 V0.3，没有为认证扩张 CMDB 业务 Schema。应用、迁移、容器、Microsoft Entra RBAC、Microsoft Graph Bicep 和 Azure 运行时均纳入 GitHub Actions 验证。

## Implemented

- Environment（环境）
- Team（责任团队）
- Service（业务/技术服务）
- Asset（资产核心模型）
- Asset N:M Service Mapping（资产与服务多对多映射）
- IP / Endpoint（网络身份）
- Compute Detail：CPU / Memory / Disk
- Database Detail：Engine / Version
- Redis Detail
- Message Queue Detail
- Kubernetes Cluster Detail：K8s Version
- Asset Relation Graph（资产依赖关系）
- Transactional Audit（事务型变更审计）
- Web Console（覆盖 V0.3 允许的创建/编辑/删除操作）
- Microsoft Entra ID EasyAuth
- `CMDB.Reader` / `CMDB.Admin` App Role RBAC
- Entra Object ID trusted audit actor
- Secretless EasyAuth via User Assigned Managed Identity + Federated Identity Credential
- Health / Database Readiness
- PostgreSQL + Alembic
- Docker runtime
- Frozen `uv.lock` dependency graph
- GitHub Actions CI
- Azure Container Apps + ACR + private PostgreSQL Bicep
- Microsoft Graph Bicep v1.0 Entra provisioning
- GitHub Actions Azure OIDC production deployment workflow

## Core Model

```text
Environment
    |
    +---- Asset ---- N:M ---- Service ---- Team
             |
             +---- IP / Endpoint
             +---- Type-specific Detail
             +---- Relation ---- Asset
             +---- ChangeRecord
```

Asset 有一个明确的 Primary Owner Team；Asset 与 Service 使用多对多映射。所有可变核心配置通过 `ChangeRecord` 保留操作者、请求 ID、before/after，并与业务变更在同一数据库事务提交。

生产环境的 `changed_by` 来自 EasyAuth 已验证 Entra Principal 的 Object ID，不再信任调用方自行填写的 `X-CMDB-Actor`。本地开发模式仍允许通过该 Header 标识写操作人。

## Authorization Model

```text
Microsoft Entra ID
        |
        +-- CMDB.Reader --> GET CMDB data / audit
        |
        +-- CMDB.Admin  --> GET + existing audited writes/deletes
```

Entra Service Principal 设置 `appRoleAssignmentRequired=true`。未显式分配角色的租户用户不会被当作 CMDB 用户。V0.3 没有新增 User/Role/Binding 数据表。

## Local Run

```bash
cd backend
docker compose up --build
```

本地默认 `CMDB_AUTH_MODE=local`：读操作无需身份；写操作要求 `X-CMDB-Actor`。Azure 生产部署设置 `CMDB_AUTH_MODE=entra`。

启动过程会等待 PostgreSQL 健康并执行：

```text
alembic upgrade head
→ FastAPI
→ http://localhost:8000/ui/
```

健康检查：

```text
GET /health   # 进程存活
GET /ready    # 数据库可用
```

## Validation Gate

每次 PR / main push 都执行：

```text
uv lock --check
→ frozen dependency install
→ Ruff
→ Web Console JavaScript syntax
→ Pytest
→ Alembic upgrade
→ Alembic schema drift check
→ Alembic downgrade base
→ Alembic upgrade head
→ Docker Compose validation
→ real PostgreSQL 16 + Alembic + FastAPI /health + /ready smoke test
→ frozen Docker build
→ Azure Bicep compile including Microsoft Graph v1.0 extension
```

Entra 生产化 Gate 已验证 **29 tests passed**，其中包含 Reader/Admin 授权与可信审计身份；真实 PostgreSQL runtime、Frozen Docker 和 Graph/EasyAuth Bicep 均通过。

## Azure Production Deployment

目标运行时：

```text
GitHub Actions OIDC
        |
        +--> Azure Container Registry
        |
        +--> Azure Container Apps
                  |
                  +--> Microsoft Entra EasyAuth
                  +--> CMDB.Reader / CMDB.Admin
                  +--> PostgreSQL Flexible Server (private network)
```

部署采用 fail-closed 顺序：先私网部署应用和 Entra/FIC/AuthConfig，验证 EasyAuth 后才打开 external ingress。无认证访问 `/ui/` 必须被重定向到登录；`/health`、`/ready` 仅为平台探针保留。

详见 `infra/azure/README.md` 与 `docs/deployment/azure-runtime-plan.md`。

## Design Principles

- 不做推测性功能
- 不使用万能 JSON / 动态 EAV 代替核心 Schema
- 类型专属配置使用强类型表
- 所有 Schema 变化必须有 Migration 和设计更新
- 只在用户输入、网络、外部系统等系统边界校验
- 不吞错误，优先快速失败
- 核心变更必须可审计、可验证
- 生产认证失败时保持 fail-closed，不先暴露公网再补认证

## Remaining Production Gate

代码和 IaC 已选择并实现 Microsoft Entra ID + 两级 App Role RBAC。剩余不再是应用架构决策，而是目标 Azure/Entra 租户权限与真实身份映射：

- GitHub `production` Environment 的 Azure OIDC secrets 必须真实可用。
- 部署身份必须具备 Azure 资源部署、`roleAssignments/write`、ACR push，以及创建 Entra Application/Service Principal 所需的 Microsoft Graph 权限。
- 首次部署完成后，需要由租户管理员把真实用户或组显式分配给 `CMDB.Reader` 或 `CMDB.Admin`。

仓库不会猜测具体公司用户/组，也不会为了自动分配角色而无理由扩大 Graph 权限。
