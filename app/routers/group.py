from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.utils import raise_not_found

router = APIRouter(tags=['Group'], prefix='/groups')


@router.get('/', response_model=list[schemas.Group])
def read_groups(
    db: Session = Depends(get_db),
):
    return crud.get_groups(db)


@router.get('/{group_id}', response_model=schemas.Group)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise_not_found('Страница не найдена.')
    return group
