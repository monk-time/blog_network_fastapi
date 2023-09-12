from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.utils import Page, not_author_error, not_found_error

router = APIRouter(tags=['Post'], prefix='/posts')


async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise not_found_error('Страница не найдена.')
    return post


@router.get('/', response_model=Page[schemas.Post])  # type: ignore
async def read_posts(
    db: Session = Depends(get_db),
):
    return crud.get_posts(db)


@router.get('/{post_id}', response_model=schemas.Post)
async def read_post(post: Annotated[models.Post, Depends(get_post)]):
    return post


@router.post('/', response_model=schemas.Post)
async def create_post(
    data: schemas.PostCreate,
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    try:
        return crud.create_post(db, data=data, author_id=current_user.id)
    except crud.GroupDoesNotExist:
        raise not_found_error('Страница не найдена.')


@router.patch('/{post_id}', response_model=schemas.Post)
async def partial_update_post(
    data: schemas.PostUpdate,
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if current_user != post.author:
        raise not_author_error('Изменение чужого контента запрещено.')
    try:
        return crud.update_post(db, post=post, data=data)
    except crud.GroupDoesNotExist:
        raise not_found_error('Страница не найдена.')


@router.put('/{post_id}', response_model=schemas.Post)
async def update_post(
    data: schemas.PostCreate,
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if current_user != post.author:
        raise not_author_error('Изменение чужого контента запрещено.')
    try:
        return crud.update_post(db, post=post, data=data)
    except crud.GroupDoesNotExist:
        raise not_found_error('Страница не найдена.')


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if current_user != post.author:
        raise not_author_error('Изменение чужого контента запрещено.')
    crud.delete_post(db, post=post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
