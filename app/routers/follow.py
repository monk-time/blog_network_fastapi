from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.utils import validation_error

router = APIRouter(tags=['Follow'], prefix='/follow')

FOLLOW_NOT_FOUND_ERROR = validation_error(
    {'following': ['Пользователь не найден.']}
)
CANT_FOLLOW_SELF_ERROR = validation_error(
    {'following': ['Нельзя подписаться на самого себя.']}
)
FOLLOW_EXISTS_ERROR = validation_error(
    {'following': ['Подписка уже существует.']}
)


@router.get('/', response_model=list[schemas.Follow])
async def read_follows(
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    follows = crud.get_follows(db, user_id=current_user.id)
    return [
        {
            'user': follow.user.username,
            'following': follow.following.username,
        }
        for follow in follows
    ]


@router.post('/', response_model=schemas.Follow)
async def create_follow(
    data: schemas.FollowCreate,
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    following_user = crud.get_user(db, username=data.following)
    if not following_user:
        raise FOLLOW_NOT_FOUND_ERROR
    if current_user == following_user:
        raise CANT_FOLLOW_SELF_ERROR
    try:
        crud.create_follow(
            db, user_id=current_user.id, following_id=following_user.id
        )
    except crud.FollowExists:
        raise FOLLOW_EXISTS_ERROR
    return {
        'user': current_user.username,
        'following': following_user.username,
    }
