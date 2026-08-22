# Database Migration

Migration directory for CMDB schema evolution.

Planned baseline:

```
001_create_environment
002_create_team
003_create_service
004_create_asset
005_create_asset_detail
006_create_asset_ip
007_create_asset_endpoint
008_create_asset_relation
009_create_change_record
```

Migration rules:

- One logical change per migration
- Never modify applied migration
- New change creates new migration
- Migration must be verified before merge
