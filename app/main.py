from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession
from app.api.routers import api_router
from app.db import engine
from app.models import Posts
from app.schemas import PaginatedPostResponse, PostResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):

    yield

    await engine.dispose()


app = FastAPI(title="Blog Post Api", lifespan=lifespan)

app.include_router(api_router)


@app.get("/post", include_in_schema=False, response_model=PaginatedPostResponse)
@app.get("/", include_in_schema=False, response_model=PaginatedPostResponse)
async def home(
    db: dbSession,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10,
):
    try:
        # get the total count of posts
        count_query = select(func.count()).select_from(Posts)
        total_count = await db.scalar(count_query)

        # get the paginated data
        stmt = select(Posts).order_by(Posts.created_at.desc()).offset(skip).limit(limit)

        posts = (await db.execute(stmt)).scalars().all()

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    if total_count:
        has_more: bool = skip + len(posts) < total_count
    else:
        has_more = False
        total_count = 0

    return PaginatedPostResponse(
        total=total_count,
        skip=skip,
        limit=limit,
        has_more=has_more,
        posts=[PostResponse.model_validate(post) for post in posts],
    )
