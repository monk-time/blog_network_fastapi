from datetime import datetime

from pydantic import AliasPath, BaseModel, EmailStr, Field, field_validator

from app.config import MEDIA_URL
from app.utils import save_image


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
    image: str | None = None
    group: int | None = None

    @field_validator('image')
    @classmethod
    def save_image(cls, value: str | None) -> str | None:
        if not value:
            return value
        if not value.startswith('data:image'):
            raise ValueError('Картинка должна начинаться с `data:image`.')
        try:
            filename = save_image(value)
        except Exception:
            raise ValueError('Ошибка при сохранении файла.')
        return filename


class PostUpdate(PostCreate):
    text: str | None = None

    @field_validator('text')
    @classmethod
    def text_cannot_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('Поле text не может быть пустым.')
        return value


class Post(BaseModel):
    id: int
    author: str = Field(validation_alias=AliasPath('author', 'username'))
    text: str
    pub_date: datetime
    image: str | None
    group: int | None = Field(
        default=None, validation_alias=AliasPath('group', 'id')
    )

    @field_validator('image')
    @classmethod
    def relative_url(cls, value: str | None) -> str | None:
        return MEDIA_URL + value if value else value


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(CommentCreate):
    pass


class Comment(BaseModel):
    id: int
    author: str = Field(validation_alias=AliasPath('author', 'username'))
    text: str
    created: datetime
    post: int = Field(validation_alias=AliasPath('post', 'id'))


class FollowCreate(BaseModel):
    following: str


class Follow(BaseModel):
    user: str = Field(validation_alias=AliasPath('user', 'username'))
    following: str = Field(validation_alias=AliasPath('following', 'username'))
