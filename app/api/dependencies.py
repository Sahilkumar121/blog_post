from db import asyncSessionLocal


async def get_db():
    async with asyncSessionLocal() as session:
        yield session
