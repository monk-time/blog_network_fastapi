from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.oauth2 import get_current_active_user
from app.routers.post import get_post
from app.utils import not_author_error, not_found_error

router = APIRouter(tags=['Comment'], prefix='/posts/{post_id}/comments')


async def get_comment(
    comment_id: int,
    post: Annotated[models.Post, Depends(get_post)],
    db: Session = Depends(get_db),
):
    comment = crud.get_comment(db, comment_id=comment_id, post=post)
    if not comment:
        raise not_found_error('Страница не найдена.')
    return comment


@router.get('/', response_model=list[schemas.Comment])
async def read_comments(
    post: Annotated[models.Post, Depends(get_post)],
):
    return crud.get_comments(post=post)


@router.get('/{comment_id}', response_model=schemas.Comment)
async def read_comment(
    comment: Annotated[models.Comment, Depends(get_comment)]
):
    return comment


@router.post('/', response_model=schemas.Comment)
async def create_comment(
    data: schemas.CommentCreate,
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    return crud.create_comment(
        db, data=data, post=post, author_id=current_user.id
    )


@router.patch('/{comment_id}', response_model=schemas.Comment)
@router.put('/{comment_id}', response_model=schemas.Comment)
async def update_post(
    data: schemas.CommentUpdate,
    comment: Annotated[models.Comment, Depends(get_comment)],
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if current_user != comment.author:
        raise not_author_error('Изменение чужого контента запрещено.')
    return crud.update_comment(db, comment=comment, data=data)


@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment: Annotated[models.Comment, Depends(get_comment)],
    post: Annotated[models.Post, Depends(get_post)],
    current_user: Annotated[
        schemas.UserInDB, Depends(get_current_active_user)
    ],
    db: Session = Depends(get_db),
):
    if current_user != comment.author:
        raise not_author_error('Изменение чужого контента запрещено.')
    crud.delete_comment(db, comment=comment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
