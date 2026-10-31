Read when a GitHub Actions deploy needs smoke tests, credential cleanup, env files, multi-service ordering, concurrency, image tagging, or blue-green rollback.

## Key Patterns

### 1. Smoke Test Before Deploy

```bash
# Run container on different port
docker run -d --name smoke -p 127.0.0.1:3001:3000 "${IMAGE}"

# Health check loop (max 45 seconds)
for i in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:3001/healthz >/dev/null; then
    SMOKE_OK="true"
    break
  fi
  sleep 3
done

# Fail if health check didn't pass
if [ "${SMOKE_OK}" != "true" ]; then
  docker logs smoke || true
  docker rm -f smoke || true
  exit 1
fi

docker rm -f smoke || true
```

### 2. Credential Cleanup (Security)

```bash
# Never write AWS credentials to a fixed path on the host (~/.aws/credentials
# persists between runs). Use a throwaway file scoped to this script instead.
export AWS_SHARED_CREDENTIALS_FILE="$(mktemp)"
chmod 600 "${AWS_SHARED_CREDENTIALS_FILE}"
trap 'rm -f "${AWS_SHARED_CREDENTIALS_FILE}" "${ENV_FILE:-}"' EXIT

# Write temporary credentials
printf "[default]\naws_access_key_id = %s\naws_secret_access_key = %s\n" \
  '${ACCESS_KEY}' '${SECRET_KEY}' > "${AWS_SHARED_CREDENTIALS_FILE}"
```

### 3. Environment File for Secrets

```bash
# Create temp env file for docker --env-file
ENV_FILE="$(mktemp)"
cat > "${ENV_FILE}" <<'EOF'
AUTH_SECRET=xxx
DATABASE_URL=xxx
EOF

docker run --env-file "${ENV_FILE}" ...

# Cleaned up by trap
```

### 4. Multi-service Deployment

Order matters when services depend on each other for message delivery — a
downstream consumer must be ready before anything can safely produce to it.

```bash
# 1. Infrastructure first (message broker)
docker run -d --name rabbitmq --restart always \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER="${USER}" \
  -e RABBITMQ_DEFAULT_PASS="${PASS}" \
  rabbitmq:3.13-management-alpine

# 2. Consumer next — it must be up and subscribed before anyone publishes,
#    otherwise early messages have no consumer and can be dropped/unprocessed.
docker run -d --name consumer-service --restart always --network host \
  -e RABBITMQ_URL="amqp://${USER}:${PASS}@127.0.0.1:5672/" \
  "${CONSUMER_IMAGE}"

# 3. Producer last — safe to start only once the consumer is ready
docker run -d --name producer-service --restart always --network host \
  -e RABBITMQ_URL="amqp://${USER}:${PASS}@127.0.0.1:5672/" \
  "${PRODUCER_IMAGE}"
```

### 5. Concurrency Control

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false  # Don't cancel running deploys
```

### 6. Image Tagging Strategy

```bash
# Tag by service name (simple)
$ECR_REGISTRY/$ECR_REPOSITORY:webapp
$ECR_REGISTRY/$ECR_REPOSITORY:watcher
$ECR_REGISTRY/$ECR_REPOSITORY:download

# Tag by git SHA (for rollback)
$ECR_REGISTRY/$ECR_REPOSITORY:webapp-${{ github.sha }}

# Tag by date
$ECR_REGISTRY/$ECR_REPOSITORY:webapp-$(date +%Y%m%d-%H%M%S)
```

### 7. Blue-Green Deploy with Automatic Rollback

แทนที่จะ `docker restart` container เดิม (ซึ่งไม่ช่วยถ้า image ใหม่พังจริง ๆ) ให้ rename
container เดิมเก็บไว้เป็น `_previous`, รัน container ใหม่, health-check ด้วย polling loop,
แล้ว auto-rollback กลับไปใช้ `_previous` ถ้า health check ไม่ผ่าน:

```bash
wait_for_url() {
  local container="$1" url="$2" retries="$3"
  for i in $(seq 1 "${retries}"); do
    if [ "$(docker inspect -f '{{.State.Running}}' "${container}" 2>/dev/null)" != "true" ]; then
      return 1
    fi
    curl -fsS "${url}" >/dev/null 2>&1 && return 0
    sleep 3
  done
  return 1
}

deploy_with_rollback() {
  local name="$1" image="$2" health_url="$3"; shift 3
  local prev="${name}_previous"

  docker rm -f "${prev}" || true
  if docker inspect "${name}" >/dev/null 2>&1; then
    docker stop "${name}" >/dev/null
    docker rename "${name}" "${prev}"
  fi

  docker run -d --name "${name}" --restart always "$@" "${image}"

  if wait_for_url "${name}" "${health_url}" 15; then
    docker rm -f "${prev}" || true
  else
    docker logs --tail 200 "${name}" || true
    docker rm -f "${name}" || true
    if docker inspect "${prev}" >/dev/null 2>&1; then
      docker rename "${prev}" "${name}"
      docker start "${name}"
    fi
    return 1
  fi
}
```

