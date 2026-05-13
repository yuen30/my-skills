---
name: devops-helper
description: Manages containerization, environment configuration, and local runtime orchestration. Use when modifying `docker-compose.yml`, Dockerfiles, or `.env` files.
---

# DevOps Helper Workflow

This skill ensures the development and production environments are stable and reproducible.

## Docker Management
1. **Compose**: Manage services: `webapp`, `monitor`, `watcher`, `download`, `generate`, `upload`.
2. **RabbitMQ**: Ensure management plugin is active on port `15672`.
3. **PostgreSQL**: Configure external DB connection via `POSTGRES_*` env vars.

## Environment Procedures
- **Security**: Never commit real secrets; use `.env.example`.
- **Compose Quirks**: Remember to escape `$` as `$$` in YAML files.
- **Networks**: Verify `DOCKER_NETWORK_SUBNET` if services can't talk to each other.

## Maintenance
- **Pruning**: Run `docker system prune` if storage is low.
- **Logs**: Monitor service health with `docker compose logs -f <service>`.
