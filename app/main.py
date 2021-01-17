from aiocache import Cache
from fastapi import FastAPI

from app.routes.api import router as api_router


app = FastAPI(
    title="PRTS-APIs",
    description="Frontend APIs of prts.wiki",
    version="0.0.1")
app.include_router(api_router)

cache = Cache(Cache.REDIS, endpoint="127.0.0.1", port=6379, namespace="prts-apis")
