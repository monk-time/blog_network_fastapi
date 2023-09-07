from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.database import get_db
from app.schemas import TokenData, UserInDB

SECRET_KEY = settings.secret
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/jwt/create')


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = data | {'exp': expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict) -> str:
    return create_jwt_token(
        data | {'token_type': 'access'},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict) -> str:
    return create_jwt_token(
        data | {'token_type': 'refresh'},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


def verify_jwt_token(
    token: str, credentials_exception=CREDENTIALS_EXCEPTION
) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    token_data = verify_jwt_token(token)
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return current_user
