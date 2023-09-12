from typing import Sequence

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.models import Comment, Follow, Group, Post, User
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
    return paginate(db, select(Post))


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


def get_comments(post: Post) -> Sequence[Comment]:
    return post.comments


def get_comment(db: Session, *, comment_id: int, post: Post) -> Comment | None:
    return db.scalar(
        select(Comment).where(
            Comment.id == comment_id, Comment.post_id == post.id
        )
    )


def create_comment(
    db: Session, *, data: schemas.CommentCreate, post: Post, author_id: int
) -> Comment:
    db_comment = Comment(
        **data.model_dump(),
        post_id=post.id,
        author_id=author_id,
    )

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(
    db: Session, *, comment: Comment, data: schemas.CommentUpdate
) -> Comment | None:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, *, comment: Comment) -> None:
    db.delete(comment)
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
