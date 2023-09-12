from fastapi import HTTPException, Query, status
from fastapi_pagination.links import LimitOffsetPage
from passlib.context import CryptContext

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
