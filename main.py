from time import time

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis.asyncio import Redis

from app import router
from app.dependencies import get_redis
from app.env import APP_ENV, SENTRY_DSN, ALLOWED_ORIGINS, APP_VERSION

load_dotenv()
environment = APP_ENV

if SENTRY_DSN is not None:
    sentry_sdk.init(dsn=SENTRY_DSN, enable_tracing=True)
app = FastAPI(debug=environment.startswith("prod"))
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RootResponse(BaseModel):
    ok: bool
    data: str


@app.get("/", tags=["root"], response_model=RootResponse)
async def root():
    return {"ok": True, "data": {
        "name": "Blastup Launchpad",
        "version": APP_VERSION,
    }}


@router.get("/rpm")
async def get_current_rpm(redis: Redis = Depends(get_redis)):
    stats = []
    for i in range(10):
        minute = int(time() / 60) * 60 - (1 + i) * 60
        if await redis.exists(f"rpm:{minute}"):
            stats.append(int((await redis.get(f"rpm:{minute}")).decode('utf-8')))

    return {
        "ok": True,
        "data": {
            "rpm": sum(stats) / len(stats) if len(stats) > 0 else 0,
            "probes": len(stats),
            "min": min(*stats) if len(stats) > 1 else 0,
            "max": max(*stats) if len(stats) > 1 else 0,
        }
    }
