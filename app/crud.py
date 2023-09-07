from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schemas
from app.models import Group, User
from app.utils import get_password_hash


class UserExists(Exception):
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
