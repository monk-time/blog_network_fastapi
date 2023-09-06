from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import oauth2, schemas, utils
from app.database import get_db, get_user

router = APIRouter(tags=['Authentication'])


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username=username)
    if not user:
        return False
    if not utils.verify_password(password, user.password):
        return False
    return user


@router.post('/jwt/create/', response_model=schemas.Tokens)
async def login_for_jwt_tokens(
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
    data = {'sub': user.username}
    return {
        'refresh': oauth2.create_refresh_token(data=data),
        'access': oauth2.create_access_token(data=data),
    }


@router.post('/jwt/refresh/', response_model=schemas.AccessToken)
async def refresh_access_token(token: schemas.RefreshToken):
    refresh_token = token.refresh
    token_data = oauth2.verify_jwt_token(refresh_token)
    data = {'sub': token_data.username}
    return {'access': oauth2.create_access_token(data=data)}


@router.post('/jwt/verify/')
async def verify_jwt_token(token: schemas.Token):
    oauth2.verify_jwt_token(token.token)
    return Response(status_code=status.HTTP_200_OK)


# TODO: correct documentation response for 401 (like in user.py)
