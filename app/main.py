from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

API_PREFIX = '/api/v1'

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(user.router, prefix=API_PREFIX)
