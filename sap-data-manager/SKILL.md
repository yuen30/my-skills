---
name: sap-data-manager
description: Specialist in SAP file formats (EOS, EQT, MATMAS, etc.) and PostgreSQL schema design. Use when handling file parsing logic, database migrations, or verifying SAP data integrity.
---

# SAP Data Manager Workflow

This skill ensures reliable data exchange between SAP SFTP and the local PostgreSQL database.

## Supported File Types
- `MATMAS`: Material Master data.
- `EOS/EQT`: Order-related data with specific prefixes.
- `SOLDTO/SHIPTO`: Customer and partner addresses.
- `ORDER_RES`: Results/Status from SAP back to the webapp.

## Parsing & Mapping Logic
1. **Schema Validation**: Verify CSV/Text column order against known SAP formats.
2. **GORM Mapping**: Map SAP fields (often short CAPS like `NAME1`, `KUNNR`) to readable DB columns.
3. **Archive Strategy**: Ensure processed files are moved to `data/archive` with proper timestamping.
4. **Idempotency**: Use `UPSERT` (On Conflict Update) to prevent duplicate master data.

## Troubleshooting Data
- Check `download` service logs for "Parse Error" or "Value too long".
- Verify `SFTP_SOURCE_ROOT` and `WATCHER_PATHS` configuration in `.env`.
