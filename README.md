# Enterprise CMDB

企业级运维配置管理数据库（Configuration Management Database），用于建立基础设施与服务关系的 Source of Truth（事实源）。

## Current Version

**V0.3 Core Complete / Azure Deploy-Ready**

数据库 Schema 已冻结在 V0.3。应用、迁移、容器镜像和 Azure Bicep 均已纳入 GitHub Actions 验证。

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
- Web Console（同源管理界面，覆盖 V0.3 允许的创建/编辑/删除操作）
- Health / Database Readiness
- PostgreSQL + Alembic
- Docker runtime
- Frozen `uv.lock` dependency graph
- GitHub Actions CI
- Azure Container Apps + ACR + private PostgreSQL Bicep
- GitHub Actions Azure OIDC deployment workflow

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

## Local Run

```bash
cd backend
docker compose up --build
```

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
→ Azure Bicep compile
```

最终 V0.3 技术 Gate 已验证 `28 passed`，真实 PostgreSQL runtime 与 Azure Bicep 均通过。

## Azure Deployment

目标运行时：

```text
GitHub Actions OIDC
        |
        +--> Azure Container Registry
        |
        +--> Azure Container Apps
                  |
                  +--> PostgreSQL Flexible Server (private network)
```

实际云资源通过 `.github/workflows/deploy-azure.yml` 创建。默认 `external_ingress=false`，在生产 Authentication / Permission 策略确认前不会把无认证 CMDB 暴露到公网。

详见 `infra/azure/README.md` 与 `docs/deployment/azure-runtime-plan.md`。

## Design Principles

- 不做推测性功能
- 不使用万能 JSON / 动态 EAV 代替核心 Schema
- 类型专属配置使用强类型表
- 所有 Schema 变化必须有 Migration 和设计更新
- 只在用户输入、网络、外部系统等系统边界校验
- 不吞错误，优先快速失败
- 核心变更必须可审计、可验证

## Remaining Production Decision

V0.3 Domain Core 已完成。生产公网开放前仍需要明确：

- Authentication Provider（例如 Microsoft Entra ID 或公司现有 SSO）
- Permission Model（角色、作用域与身份映射）

这两项会影响生产安全策略，不能由实现层自行假设。
