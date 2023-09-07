from pydantic import BaseModel, EmailStr


class ErrorMessage(BaseModel):
    detail: str


class RefreshToken(BaseModel):
    refresh: str


class AccessToken(BaseModel):
    access: str


class Tokens(AccessToken, RefreshToken):
    pass


class Token(BaseModel):
    token: str


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


class Group(BaseModel):
    id: int
    title: str
    slug: str
    description: str
