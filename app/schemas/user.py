from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


# helper function
def check_mail_helper(value: str):
    valid_domain = ["gmail.com", "vitbhopal.ac.in"]

    email_domain = value.split("@")[-1]

    if email_domain not in valid_domain:
        raise ValueError("Enter Valid email address")

    return value


def check_username_helper(value: str) -> str:
    if not value.isalnum():
        raise ValueError("No special character and space")

    return value.lower()


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
        return check_username_helper(value)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return check_mail_helper(value)


class UserRequestUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=10, min_length=1)

    email: EmailStr | None = Field(default=None, max_length=50)

    password: SecretStr | None = Field(
        default=None,
        max_length=12,
        min_length=10,
        description="Password with 10 to 12 charaters",
    )

    @field_validator("username")
    @classmethod
    def check_username(cls, value: str) -> str:
        return check_username_helper(value)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return check_mail_helper(value)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
