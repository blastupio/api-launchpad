#!/usr/bin/env bash

alembic upgrade head && uvicorn main:app --workers 8 --proxy-headers --host 0.0.0.0 --port 80 --forwarded-allow-ips '*'
