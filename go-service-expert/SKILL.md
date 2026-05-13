---
name: go-service-expert
description: Specialized in managing TOA E-Ordering Go microservices (watcher, download, generate, upload) and the shared common library. Use for backend logic updates, RabbitMQ jobs, or database GORM model changes.
---

# Go Service Expert Workflow

This skill provides expert guidance for developing and maintaining the Go-based backend services.

## Service Map
- `services/watcher`: SFTP scanning and job publishing.
- `services/download`: Processing download jobs, parsing files, and DB upsert.
- `services/generate`: Creating ORDER_REQ files and publishing upload jobs.
- `services/upload`: Consuming upload jobs and pushing to SFTP.
- `shared/common`: Shared logic for config, mq, sftp, and store (GORM).

## Development Procedures
1. **Work Sync**: Always run `go work sync` after adding new dependencies.
2. **Shared Library**: If adding a feature used by multiple services, implement it in `shared/common`.
3. **Job Payloads**: Ensure any change to job models in `shared/common/jobs` is backward compatible.
4. **Error Handling**: Use the structured logger from `shared/common/logger`.
5. **Testing**: Run `go test ./...` in the respective service or shared folder before committing.

## GORM Conventions
- Define models in `internal/models` within the service or `shared/common/store` if global.
- Use `SFTP_DB_AUTO_MIGRATE=true` only during development.
