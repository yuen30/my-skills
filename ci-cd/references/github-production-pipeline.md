Read when a GitHub Actions pipeline needs config validation, selective/matrix builds with registry cache, dependency-gated jobs, deploy diagnostics, or post-deploy verification.

## Advanced: Production-grade Pipeline

Pattern สำหรับ pipeline ที่มีหลาย services และต้องการ selective build (build เฉพาะ
service ที่เปลี่ยน), validate config ก่อนรัน, และ verify การ deploy อย่างละเอียด.

### 1. Validate Job — ตรวจ required Variables/Secrets ก่อนอะไรทั้งหมด

Fail fast ก่อนที่จะเสีย CI minutes ไปกับ build/deploy ที่จะพังเพราะ config ขาด รวมถึง
conditional-required (var A จำเป็นเฉพาะเมื่อ var B เป็นค่าใดค่าหนึ่ง) และ enum validation.

```yaml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Validate required config
        env:
          DEPLOY_TARGET: ${{ vars.DEPLOY_TARGET }}
          EC2_HOST: ${{ vars.EC2_HOST }}
          SFTP_HOST: ${{ vars.SFTP_HOST }}
        run: |
          set -euo pipefail
          missing=()

          # Always-required
          for name in AWS_ACCESS_KEY_ID AWS_REGION AWS_ACCOUNT_ID ECR_REPOSITORY DEPLOY_TARGET; do
            [ -z "${!name:-}" ] && missing+=("${name}")
          done

          # Conditional-required: SFTP_HOST only required when DEPLOY_TARGET=sftp
          if [ "${DEPLOY_TARGET}" = "sftp" ] && [ -z "${SFTP_HOST:-}" ]; then
            missing+=("SFTP_HOST (required when DEPLOY_TARGET=sftp)")
          fi

          if [ "${#missing[@]}" -gt 0 ]; then
            echo "Missing required vars/secrets:"
            printf '  - %s\n' "${missing[@]}"
            exit 1
          fi

          # Enum validation
          case "${DEPLOY_TARGET}" in
            ec2|sftp|ecs) ;;
            *)
              echo "DEPLOY_TARGET must be one of: ec2, sftp, ecs (got '${DEPLOY_TARGET}')"
              exit 1
              ;;
          esac
```

### 2. Detect-Services Job — selective/incremental multi-service build

Build เฉพาะ service ที่ source เปลี่ยน หรือ image ยังไม่มีใน ECR (first deploy). Diff
`before`/`current` SHA ด้วย `git diff`, fallback เป็น full tree เมื่อ `before` เป็น all-zero
(first push / force-push).

```yaml
  detect-services:
    needs: validate
    runs-on: ubuntu-latest
    outputs:
      watcher: ${{ steps.detect.outputs.watcher }}
      webapp: ${{ steps.detect.outputs.webapp }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ vars.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ vars.AWS_REGION }}

      - id: detect
        env:
          ECR_REPOSITORY: ${{ vars.ECR_REPOSITORY }}
        run: |
          set -euo pipefail
          BEFORE="${{ github.event.before }}"
          if [ -z "${BEFORE}" ] || [ "${BEFORE}" = "0000000000000000000000000000000000000000" ]; then
            CHANGED="$(git ls-tree -r --name-only HEAD)"
          else
            CHANGED="$(git diff --name-only "${BEFORE}" "${{ github.sha }}" || git ls-tree -r --name-only HEAD)"
          fi

          for svc in watcher webapp; do
            BUILD="false"
            if echo "${CHANGED}" | grep -q "^services/${svc}/\|^${svc}/"; then
              BUILD="true"
            elif ! aws ecr describe-images --repository-name "${ECR_REPOSITORY}" \
                    --image-ids imageTag="${svc}" >/dev/null 2>&1; then
              BUILD="true"  # image missing in ECR — must build at least once
            fi
            echo "${svc}=${BUILD}" >> "${GITHUB_OUTPUT}"
          done
```

### 3. Matrix Build with Skippable Steps + Registry Layer Cache

`fail-fast: false` กัน matrix job หนึ่งพังแล้วยกเลิก job อื่น. ทุก step ที่แพง (checkout,
login, buildx, build) มี `if:` gate จาก output ของ `detect-services` เพื่อ skip ไปเลยถ้า
ไม่จำเป็น (ประหยัด CI minutes จริง ๆ ไม่ใช่แค่ skip logic ข้างในสคริปต์).

```yaml
  build:
    needs: detect-services
    strategy:
      fail-fast: false
      matrix:
        service: [watcher, webapp]
    runs-on: ubuntu-latest
    steps:
      - name: Determine whether build is required
        id: gate
        run: |
          echo "required=${{ needs.detect-services.outputs[matrix.service] }}" >> "${GITHUB_OUTPUT}"

      - name: Checkout Code
        if: steps.gate.outputs.required == 'true'
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        if: steps.gate.outputs.required == 'true'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ vars.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to Amazon ECR
        if: steps.gate.outputs.required == 'true'
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Set up Docker Buildx
        if: steps.gate.outputs.required == 'true'
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        if: steps.gate.outputs.required == 'true'
        uses: docker/build-push-action@v6
        with:
          context: ./services/${{ matrix.service }}
          push: true
          tags: ${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}
          cache-from: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}-cache
          cache-to: type=registry,ref=${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ matrix.service }}-cache,mode=max
```

### 4. Dependency-Ordered Job Graph — treat "skipped" as success, not a blocker

เมื่อ matrix job บาง service ไม่ build เลย (`skipped`) job ที่ต่อจากนั้นต้องไม่ถือว่านั่นคือ
ความล้มเหลว มีแค่ `success` ของ matrix ตัวที่ build จริงเท่านั้นที่ต้อง block.

```yaml
  deploy:
    needs: [build, detect-services]
    if: >
      always() &&
      needs.detect-services.result == 'success' &&
      (needs.build.result == 'success' || needs.build.result == 'skipped')
    runs-on: ubuntu-latest
    steps:
      # ...deploy steps...
```

### 5. Deploy Script Diagnostics — report exactly which phase failed

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

PHASE="init"
trap 'echo "[ERROR] Deploy failed during ${PHASE} at line ${LINENO}: ${BASH_COMMAND}"' ERR

PHASE="login ecr"
aws ecr get-login-password --region "${TARGET_REGION}" | docker login --username AWS --password-stdin "${REGISTRY}"

PHASE="pull images"
docker pull "${IMAGE}"

PHASE="deploy webapp"
deploy_with_rollback "myapp" "${IMAGE}" "http://127.0.0.1:3000/healthz" -p 3000:3000
```

### 6. Post-Deploy Final Verification

หลัง deploy ครบทุก service แล้ว ให้ loop เช็ค container ที่ต้อง running ทั้งหมด +
HTTP health endpoint ทั้งหมด แล้ว print ตารางสถานะ — hard-fail ถ้ามีตัวไหน down/unhealthy
(catch partial failure ที่ single "docker run สำเร็จ" เช็คไม่เจอ).

```bash
PHASE="post-deploy verification"
FAILED="false"

echo "container | status"
for c in myapp watcher rabbitmq; do
  if [ "$(docker inspect -f '{{.State.Running}}' "${c}" 2>/dev/null)" = "true" ]; then
    echo "${c} | UP"
  else
    echo "${c} | DOWN"
    FAILED="true"
  fi
done

echo "service | health | url"
declare -A HEALTH_URLS=(
  [webapp]="http://127.0.0.1:3000/healthz"
  [watcher]="http://127.0.0.1:3100/healthz"
)
for svc in "${!HEALTH_URLS[@]}"; do
  url="${HEALTH_URLS[${svc}]}"
  if curl -fsS "${url}" >/dev/null 2>&1; then
    echo "${svc} | HEALTHY | ${url}"
  else
    echo "${svc} | UNHEALTHY | ${url}"
    FAILED="true"
  fi
done

if [ "${FAILED}" = "true" ]; then
  echo "Post-deploy verification failed"
  exit 1
fi
```

