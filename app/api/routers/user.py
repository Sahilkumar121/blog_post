from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession, userSession
from app.core import create_hash_password, create_token, setting, verify_hash_password
from app.models import Users
from app.schemas import UserBase, UserRequestUpdate, UserResponse

route = APIRouter()


# post api for register
@route.post("/api/register", response_model=UserResponse)
async def register_user(payload: UserBase, db: dbSession):

    # check if same name of username exist in database
    stmt = select(Users).where(
        Users.username == payload.username, Users.email == payload.email
    )
    user = (await db.execute(stmt)).scalar_one_or_none()

    # if user is not none then it exist
    if user != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email and username already exist",
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
            detail=f"There is some error {e!s}",
        )
    finally:
        print("User register succesfully")


# post api for login api
@route.post("/api/login")
async def login_for_access_token(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession
):

    # check if user exist for authentication
    stmt = select(Users).where(Users.username == payload.username)
    user = (await db.execute(stmt)).scalar_one_or_none()

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
    try:
        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "password":
                raw_password = create_hash_password(value)
                setattr(current_user, key, raw_password)
            else:
                setattr(current_user, key, value)

        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        )
    except SQLAlchemyError as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return current_user


# delete user
@route.delete("/api/delete")
async def delete_user(db: dbSession, current_user: userSession):
    try:
        await db.delete(current_user)
        await db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
