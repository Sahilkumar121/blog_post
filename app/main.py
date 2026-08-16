from contextlib import asynccontextmanager

from db import Base, engine
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Blog Post Api", lifespan=lifespan)
