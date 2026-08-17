from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db

dbSession = Annotated[AsyncSession, Depends(get_db)]
