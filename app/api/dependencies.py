from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import decode_token
from app.db import asyncSessionLocal
from app.models import Users

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/user/api/login")


async def get_db():
    async with asyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    credential_exceptioon = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the credential",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # safely decode token
    try:
        payload = decode_token(token)
        username = payload.get("sub")

        if username is None:
            raise credential_exceptioon
    except jwt.PyJWTError:
        raise credential_exceptioon

    # safely check if person exist in database
    try:
        stmt = select(Users).where(Users.username == username)

        user = (await db.execute(stmt)).scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    except SQLAlchemyError as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

    return {"id": user.id, "username": username}
