# Default values for blastup-launchpad.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

image:
  registry: ghcr.io
  name: blastupio/api-launchpad
  tag: latest
  pullPolicy: Always
  secrets:
    - name: ghcr-credentials

apps:
  worker:
    deployment_enabled: true
    replica_count: 1
    service:
      enabled: false
    command:
      - /bin/bash
      - -c
      - celery -A app.tasks worker -l INFO -c 4
    resources:
      memory: 512M
      memory_limit: 1G
      cpu: 200m
      cpu_limit: 200m
  launchpad:
    has_hook: true
    deployment_enabled: true
    replica_count: 3
    pods:
      expose_ports:
        - 8000
    service:
      enabled: true
      ports:
        - name: http
          targetPort: 8000
          port: 8000
    command:
      - /bin/bash
      - -c
      - uvicorn main:app --proxy-headers --workers 4 --host 0.0.0.0 --port 8000 --forwarded-allow-ips '*'
    liveness_probe:
      httpGet:
        path: /internal/rpm
        port: 8000
      periodSeconds: 30
      initialDelaySeconds: 30
    readiness_probe:
      httpGet:
        path: /
        port: 8000
      periodSeconds: 30
      initialDelaySeconds: 30

cron_enabled: true
cron:
  schedule-listen-staking-events:
    enabled: true
    schedule: "*/1 * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py listen-staking-events"
  schedule-listen-blp-staking-events:
    enabled: true
    schedule: "* * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py listen-blp-staking-events"
  schedule-monitor-onramp-balance:
    enabled: true
    schedule: "*/7 * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py monitor-onramp-balance"
  schedule-update-project-total-raised:
    enabled: true
    schedule: "*/1 * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py update-project-total-raised"
  schedule-process-launchpad-contract-events:
    enabled: true
    schedule: "*/15 * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py process-launchpad-contract-events"
  schedule-process-launchpad-multichain-contract-events:
    enabled: true
    schedule: "*/5 * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py process-launchpad-multichain-contract-events"
  schedule-update-tokens-cache:
    enabled: true
    schedule: "* * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py update-supported-tokens-cache"
  schedule-add-ido-points:
    enabled: true
    schedule: "1 0 * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 -c 'from app.tasks import add_ido_staking_points; add_ido_staking_points.apply_async()'"
  schedule-add-blp-staking-points:
    enabled: true
    schedule: "1 0 * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 -c 'from app.tasks import add_blp_staking_points; add_blp_staking_points.apply_async()'"
  schedule-change-projects-status:
    enabled: true
    schedule: "* * * * *"
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "python3 console.py change-projects-status"

env:
  APP_ENV: dev
  APP_VERSION: unstable

ingresses:
  launchpad:
    domain: "app-api.blastup.io"
    rules:
      - path: /
        backend:
          service:
            name: launchpad
            port:
              number: 8000
        pathType: Prefix

config:
  data:
    CELERY_RETRY_AFTER: 15

secrets:
  data:
