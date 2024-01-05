from pydantic import BaseModel, Field, EmailStr


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=30)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=5, max_length=200)


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    old_password: str
    new_password: str
    new_password_confirmation: str
