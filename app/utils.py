from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def raise_not_found(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
