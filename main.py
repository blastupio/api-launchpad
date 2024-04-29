import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqladmin import Admin

from app import router
from onramp.router import router as onramp_router
from app.base import engine
from app.admin import add_views, authentication_backend
from app.env import settings

load_dotenv()
environment = settings.app_env

if settings.sentry_dsn is not None:
    sentry_sdk.init(dsn=settings.sentry_dsn, enable_tracing=True)
app = FastAPI(debug=not environment.startswith("prod"))
app.include_router(router)
app.include_router(onramp_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(app, engine, authentication_backend=authentication_backend)
add_views(admin)


class RootResponseData(BaseModel):
    name: str
    version: str


class RootResponse(BaseModel):
    ok: bool
    data: RootResponseData


@app.get("/", tags=["root"], response_model=RootResponse)
async def root():
    return {
        "ok": True,
        "data": {
            "name": "Blastup Launchpad",
            "version": settings.app_version,
        },
    }
