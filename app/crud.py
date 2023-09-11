from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.models import Follow, Group, Post, User
from app.utils import get_password_hash


class UserExists(Exception):
    pass


class FollowExists(Exception):
    pass


class GroupDoesNotExist(Exception):
    pass


def get_user(db: Session, *, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, *, user: schemas.UserCreate) -> User:
    stmt = select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )
    if db.execute(stmt).first():
        raise UserExists

    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump() | {'password': hashed_password}
    db_user = User(**user_data)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_groups(db: Session) -> Sequence[Group]:
    return db.scalars(select(Group)).all()


def get_group(db: Session, *, group_id: int) -> Group | None:
    return db.scalar(select(Group).where(Group.id == group_id))


def get_posts(db: Session) -> Sequence[Post]:
    return db.scalars(select(Post)).all()


def get_post(db: Session, *, post_id: int) -> Post | None:
    return db.scalar(select(Post).where(Post.id == post_id))


def create_post(
    db: Session, *, data: schemas.PostCreate, author_id: int
) -> Post:
    if data.group and not get_group(db, group_id=data.group):
        raise GroupDoesNotExist
    db_post = Post(
        **data.model_dump(exclude={'group'}),
        group_id=data.group,
        author_id=author_id,
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(
    db: Session, *, post: Post, data: schemas.PostUpdate | schemas.PostCreate
) -> Post | None:
    if data.group and not get_group(db, group_id=data.group):
        raise GroupDoesNotExist

    update_data = data.model_dump(exclude_unset=True)
    if 'group' in update_data:
        update_data['group_id'] = update_data.pop('group')
    for field, value in update_data.items():
        setattr(post, field, value)

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, *, post: Post) -> None:
    db.delete(post)
    db.commit()


def get_follows(db: Session, *, user_id: int) -> Sequence[Follow]:
    return db.scalars(select(Follow).where(Follow.user_id == user_id)).all()


def create_follow(db: Session, *, user_id: int, following_id: int) -> Follow:
    stmt = select(Follow).where(
        Follow.user_id == user_id, Follow.following_id == following_id
    )
    if db.execute(stmt).first():
        raise FollowExists

    db_follow = Follow(user_id=user_id, following_id=following_id)

    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    return db_follow
