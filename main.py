import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import router
from app.env import APP_ENV, SENTRY_DSN, ALLOWED_ORIGINS

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
    return {"ok": True, "data": "Blastup Launchpad"}
