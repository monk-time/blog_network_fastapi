from pydantic import BaseModel, EmailStr


class ErrorMessage(BaseModel):
    detail: str


class Token(BaseModel):
    access: str
    refresh: str


class TokenData(BaseModel):
    username: str


class TokenCreate(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    is_active: bool


class UserInDB(User):
    password: str
