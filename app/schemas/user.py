from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class UserBase(BaseModel):
    username: str = Field(
        ..., max_length=10, min_length=1, description="username can't be empty"
    )
    email: EmailStr = Field(..., max_length=50)
    password: SecretStr = Field(
        ...,
        max_length=12,
        min_length=10,
        description="Password with 10 to 12 charaters",
    )

    @field_validator("username")
    @classmethod
    def check_username(cls, value: str) -> str:
        if value.isalnum():
            raise ValueError("No special character and space")

        return value.lower()

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        valid_domain = ["gmail.com", "vitbhopal.ac.in"]

        email_domain = value.split("@")[-1]

        if email_domain not in valid_domain:
            raise ValueError("Enter Valid email address")

        return value


class UserRequest(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    username: str
