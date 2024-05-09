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
    schedule: */10 * * * *
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "celery call app.tasks.process_history_staking_event"
  schedule-monitor-onramp-balance:
    enabled: true
    schedule: */15 * * * *
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "celery call app.tasks.monitor_onramp_bridge_balance"

  schedule-update-project-total-raised:
    enabled: true
    schedule: */9 * * * *
    concurrency_policy: Forbid
    restart_policy: OnFailure
    pass_env: true
    command:
      - /bin/sh
    args:
      - "-c"
      - "celery call app.tasks.recalculate_project_total_raised"


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
