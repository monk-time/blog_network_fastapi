from base64 import b64decode
from uuid import uuid4

from fastapi import HTTPException, Query, status
from fastapi_pagination.links import LimitOffsetPage
from passlib.context import CryptContext

from app.config import MEDIA_ROOT

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def not_found_error(message):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def validation_error(message):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )


def not_author_error(message):
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


Page = LimitOffsetPage.with_custom_options(
    limit=Query(10, ge=1, le=500),
)


def save_image(base64_encoded: str) -> str:
    img_format, img_str = base64_encoded.split(';base64,')
    ext = img_format.split('/')[-1]
    filename = f'{uuid4()}.{ext}'
    img_bytes = b64decode(img_str)
    MEDIA_ROOT.mkdir(exist_ok=True)
    with open(MEDIA_ROOT / filename, 'wb') as f:
        f.write(img_bytes)
    return filename
