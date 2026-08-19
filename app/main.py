from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import api_router
from app.db import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):

    yield

    await engine.dispose()


app = FastAPI(title="Blog Post Api", lifespan=lifespan)

app.include_router(api_router)


# @app.get("/post", include_in_schema=False)
@app.get("/", include_in_schema=False)
async def home():
    return {
        "message": "Blog Post Api",
        "docs": "/docs",
        "redoc": "/redoc"
        }
