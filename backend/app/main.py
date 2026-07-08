from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise, connections

from app.db import TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_ORM)
    yield
    await connections.close_all()


app = FastAPI(title="SNS Keyword Monitor", lifespan=lifespan)


@app.get("/health")
async def health():
    # DB까지 실제로 왕복해야 "떠 있음"이 아니라 "동작함"을 증명한다.
    try:
        await connections.get("default").execute_query("SELECT 1")
    except Exception as exc:  # noqa: BLE001 - health는 원인 문자열만 노출
        return {"status": "degraded", "db": f"error: {exc}"}
    return {"status": "ok", "db": "ok"}
