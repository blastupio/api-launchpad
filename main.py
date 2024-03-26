import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import router
from app.env import APP_ENV, SENTRY_DSN, ALLOWED_ORIGINS, APP_VERSION

load_dotenv()
environment = APP_ENV

if SENTRY_DSN is not None:
    sentry_sdk.init(dsn=SENTRY_DSN, enable_tracing=True)
app = FastAPI(debug=not environment.startswith("prod"))
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RootResponseData(BaseModel):
    name: str
    version: str


class RootResponse(BaseModel):
    ok: bool
    data: RootResponseData


@app.get("/", tags=["root"], response_model=RootResponse)
async def root():
    return {"ok": True, "data": {
        "name": "Blastup Launchpad",
        "version": APP_VERSION,
    }}
