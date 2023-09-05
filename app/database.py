from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

from . import schemas
from .models import User
from .utils import get_password_hash

DATABASE_URL = (
    f'postgresql://{settings.db_user}:{settings.db_pass}'
    f'@{settings.db_host}:{settings.db_port}/{settings.db_name}'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserExists(Exception):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, *, username: str):
    return db.scalar(select(User).where(User.username == username))


def create_user(db: Session, *, user: schemas.UserCreate):
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
