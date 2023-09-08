from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.utils import not_found_error

router = APIRouter(tags=['Post'], prefix='/posts')


@router.get('/', response_model=list[schemas.Post])
async def read_posts(
    db: Session = Depends(get_db),
):
    return crud.get_posts(db)


@router.get('/{post_id}', response_model=schemas.Post)
async def read_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise not_found_error('Страница не найдена.')
    return post


@router.post('/', response_model=schemas.Post)
async def create_post(
    data: schemas.PostCreate,
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if data.group:
        group = crud.get_group(db, group_id=data.group)
        if not group:
            raise not_found_error('Страница не найдена.')
    else:
        group = None
    return crud.create_post(
        db,
        text=data.text,
        image=data.image,
        author_id=current_user.id,
        group_id=group.id if group else None,
    )
