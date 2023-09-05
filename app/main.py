from typing import Annotated

from fastapi import Depends, FastAPI

from . import models
from .database import engine
from .oauth2 import oauth2_scheme
from .routers import auth, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)


@app.get('/items/')
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {'token': token}
