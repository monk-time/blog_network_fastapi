from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app import models
from app.database import engine
from app.routers import auth, comment, follow, group, post, user

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
add_pagination(app)

API_PREFIX = '/api/v1'

for router in (auth, comment, follow, group, post, user):
    app.include_router(router.router, prefix=API_PREFIX)


# TODO: correct documentation response for 401 (like in user.py) and 422/400
# TODO: tests
