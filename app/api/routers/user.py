from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.api import dbSession
from app.core import create_hash_password
from app.models import Users
from app.schemas import UserBase, UserResponse

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
            detail=f"There is some error {e}",
        )
    finally:
        print("User register succesfully")
        
    
