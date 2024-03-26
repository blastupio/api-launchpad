# Default values for eazylogin.
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
  launchpad:
    has_hook: true
    deployment_enabled: true
    replicaCount: 8
    service:
      enabled: true
      ports:
        - name: http
          targetPort: 8000
          port: 8000
    command:
      - /bin/bash
      - -c
      - uvicorn main:app --proxy-headers --workers 1 --host 0.0.0.0 --port 8000 --forwarded-allow-ips '*'
    resources:
      memory: 512M
      memory_limit: 1G
      cpu: 200m
      cpu_limit: 200m

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
  launchpad:
    data:
      CELERY_RETRY_AFTER: 15

secrets:
  launchpad:
    data:
