# Enterprise CMDB

企业级运维配置管理数据库（Configuration Management Database）。

## Current Version

V0.3 Schema Freeze

## Design Goal

建立企业基础设施 Source of Truth（事实源），管理：

- Asset（资产）
- Ownership（责任归属）
- Service Mapping（服务映射）
- Network Identity（IP / Endpoint）
- Type Specific Configuration（类型专属配置）
- Dependency Relation（依赖关系）
- Audit History（变更审计）

## Design Principles

- 不做过度工程
- 不引入未知需求字段
- 不使用万能 JSON 存储业务属性
- 不使用动态 EAV 模型作为第一版本核心
- 所有 Schema 变化必须经过设计评审

## Repository Status

Current phase:

Repository initialization + documentation + migration baseline
