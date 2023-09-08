from datetime import datetime

from pydantic import AliasPath, BaseModel, EmailStr, Field


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
    id: int
    password: str


class Group(BaseModel):
    id: int
    title: str
    slug: str
    description: str


class PostCreate(BaseModel):
    text: str
    image: str | None
    group: int | None


class Post(BaseModel):
    id: int
    author: str = Field(validation_alias=AliasPath('author', 'username'))
    text: str
    pub_date: datetime
    image: str | None
    group: int | None = Field(
        default=None, validation_alias=AliasPath('group', 'id')
    )


class FollowCreate(BaseModel):
    following: str


class Follow(BaseModel):
    user: str = Field(validation_alias=AliasPath('user', 'username'))
    following: str = Field(validation_alias=AliasPath('following', 'username'))
