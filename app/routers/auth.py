from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, utils
from app.database import get_db, get_user
from app.oauth2 import create_access_token

router = APIRouter(tags=['Authentication'])


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        return False
    if not utils.verify_password(password, user.password):
        return False
    return user


@router.post('/jwt/create/', response_model=schemas.Token)
async def login_for_access_token(
    token_data: schemas.TokenCreate,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, **token_data.model_dump())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': user.username})
    return {'access': access_token, 'refresh': 'not-implemented'}
