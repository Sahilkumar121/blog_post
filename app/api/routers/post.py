from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession, userSession
from app.models import Posts
from app.schemas import PostBase, PostRequestUpdate, PostResponse

route = APIRouter()


# post new post
@route.post("/api/post", response_model=PostResponse)
async def post_new_post(post: PostBase, db: dbSession, _current_user: userSession):

    try:
        new_posts = Posts(title=post.title, description=post.description)

        db.add(new_posts)
        await db.commit()
        await db.refresh(new_posts)

    except SQLAlchemyError as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return new_posts


# update the prev post
@route.patch("/api/update/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: Annotated[int, Path(gt=0)],
    data: PostRequestUpdate,
    db: dbSession,
    current_user: userSession,
):

    # dump model
    update_post = data.model_dump(exclude_unset=True)

    if not update_post:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No update data was provided"
        )

    try:
        # select the post usin id and user_id
        stmt = select(Posts).where(
            Posts.id == post_id, Posts.user_id == current_user["id"]
        )
        post = (await db.execute(stmt)).scalar_one_or_none()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you do not have permission to change",
            )

        for key, value in update_post.items():
            setattr(post, key, value)

        await db.commit()
        await db.refresh(post)
    except SQLAlchemyError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occur",
        )

    return post
