from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import models, schemas, utils
from .db import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/jwt/create')


fake_users_db = {
    'johndoe': {
        'username': 'johndoe',
        'full_name': 'John Doe',
        'email': 'johndoe@example.com',
        'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
        'disabled': False,
    }
}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user


@app.post('/api/v1/jwt/create', response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(
        fake_users_db,
        form_data.username,
        form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = utils.create_access_token(data={'sub': user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    token_data = utils.verify_access_token(token, credentials_exception)
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return current_user


@app.get('/users/me', response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_active_user)]
):
    return current_user


@app.get('/users/me/items/')
async def read_own_items(
    current_user: Annotated[schemas.UserInDB, Depends(get_current_active_user)]
):
    return [{'item_id': 'Foo', 'owner': current_user.username}]


@app.get('/items/')
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {'token': token}
