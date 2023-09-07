from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.utils import not_found_error

router = APIRouter(tags=['Group'], prefix='/groups')


@router.get('/', response_model=list[schemas.Group])
async def read_groups(
    db: Session = Depends(get_db),
):
    return crud.get_groups(db)


@router.get('/{group_id}', response_model=schemas.Group)
async def read_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise not_found_error('Страница не найдена.')
    return group
