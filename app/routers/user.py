from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, schemas
from app.oauth2 import get_current_active_user

router = APIRouter(
    tags=['User'],
    prefix='/users',
)


@router.get('/me', response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_active_user)]
):
    return current_user


@router.get('/me/items/')
async def read_own_items(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_active_user)]
):
    return [{'item_id': 'Foo', 'owner': current_user.username}]


@router.post(
    '/',
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
):
    try:
        return database.create_user(db, user=user)
    except database.UserExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or email is already used',
        )