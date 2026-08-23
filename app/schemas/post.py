from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    title: str = Field(..., max_length=50)

    description: str = Field(..., max_length=500)


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str


class PostRequestUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=50)

    description: str | None = Field(default=None, max_length=500)


class PaginatedPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    skip: int
    limit: int
    has_more: bool
    posts: list[PostResponse]
