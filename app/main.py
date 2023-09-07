from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import auth, follow, group, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

API_PREFIX = '/api/v1'

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(user.router, prefix=API_PREFIX)
app.include_router(group.router, prefix=API_PREFIX)
app.include_router(follow.router, prefix=API_PREFIX)
