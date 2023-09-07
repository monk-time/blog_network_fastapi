from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.utils import validation_error

router = APIRouter(tags=['User'], prefix='/users')


@router.get('/me', response_model=schemas.User)
async def read_me(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_active_user)]
):
    return current_user


@router.post(
    '/',
    response_model=schemas.User,
    responses={
        400: {
            'description': 'Username or email is already used',
            'model': schemas.ErrorMessage,
        },
    },
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return crud.create_user(db, user=user)
    except crud.UserExists:
        raise validation_error('Username or email is already used')
