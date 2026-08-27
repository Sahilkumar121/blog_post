from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession, userSession
from app.core import create_hash_password, create_token, setting, verify_hash_password
from app.models import Users
from app.schemas import UserBase, UserRequestUpdate, UserResponse

route = APIRouter()


# post api for register
@route.post(
    "/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(payload: UserBase, db: dbSession):

    # check if same name of username exist in database
    stmt = select(Users).where(
        or_(Users.username == payload.username, Users.email == payload.email)
    )
    existing_user = (await db.execute(stmt)).scalar_one_or_none()

    # if user is not none then it exist
    if existing_user:
        if existing_user.username == payload.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )
        if existing_user.email == payload.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    # create a hash password
    hash_password = create_hash_password(payload.password)

    # if not exist then create new User and add to database
    new_user = Users(
        username=payload.username,
        email=payload.email,
        password=hash_password,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except SQLAlchemyError as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occur{e!s}",
        )

    return new_user


# post api for login api
@route.post("/api/login", status_code=status.HTTP_200_OK)
async def login_for_access_token(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession
):
    try:
        # check if user exist for authentication
        stmt = select(Users).where(Users.username == payload.username)
        user = (await db.execute(stmt)).scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occur",
        )

    # if user not exist or password is incorrect
    if not user or not verify_hash_password(
        plain_password=payload.password, hashed_password=user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user and password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expire = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTE)
    access_token = create_token(
        data={"sub": user.username}, expire_delta=access_token_expire
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }


# get api for user
@route.get("/me")
async def get_me(current_user: userSession):

    return current_user


# update user data
@route.patch("/api/update/", response_model=UserResponse)
async def update_user(
    data: UserRequestUpdate,
    db: dbSession,
    current_user: userSession,
):

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return current_user

    try:
        if "password" in update_data:
            update_data["password"] = create_hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(current_user, key, value)

        await db.commit()
        await db.refresh(current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
    except SQLAlchemyError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occur",
        )

    return current_user


# delete user
@route.delete("/api/delete")
async def delete_user(db: dbSession, current_user: userSession):
    try:
        await db.delete(current_user)
        await db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server occur",
        )
