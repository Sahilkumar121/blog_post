from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession, userSession
from app.models import Posts
from app.schemas import PostBase, PostRequestUpdate, PostResponse

route = APIRouter()


# get post by id
@route.get(
    "/api/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK
)
async def get_post_by_id(post_id: Annotated[int, Path(gt=0)], db: dbSession):

    try:
        # check if the post id is valid or not
        stmt = select(Posts).where(Posts.id == post_id)
        post = (await db.execute(stmt)).scalar_one_or_none()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post not found for {post_id}",
            )
        return post
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Internal Server Error Occur",
        )


# post new post
@route.post(
    "/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
async def post_new_post(post: PostBase, db: dbSession, current_user: userSession):

    try:
        new_posts = Posts(
            title=post.title, description=post.description, user_id=current_user["id"]
        )

        db.add(new_posts)
        await db.commit()
        await db.refresh(new_posts)

    except SQLAlchemyError as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return new_posts


# update the blog post
@route.patch(
    "/api/update/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse
)
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data was provided",
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
                detail=f"Post not found {post_id}",
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


# delete the blog post
@route.delete("/api/delete/{post_id}")
async def delete_blog_post(
    post_id: Annotated[int, Path(gt=0)], db: dbSession, current_user: userSession
):
    try:
        # check if delete id is valid or not
        stmt = select(Posts).where(
            Posts.id == post_id, Posts.user_id == current_user["id"]
        )
        post = (await db.execute(stmt)).scalar_one_or_none()

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        await db.delete(post)
        await db.refresh(post)

        return Response(
            status_code=status.HTTP_204_NO_CONTENT, content="Post delete successfully"
        )
    except SQLAlchemyError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An Internal Server Error Occur",
        )
