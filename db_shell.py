# flake8: noqa
from sqlalchemy import select

from app.database import get_db
from app.models import Comment, Follow, Group, Post, User

session = next(get_db())
