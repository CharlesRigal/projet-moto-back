import application.routers.users
from fastapi import FastAPI
import models
from application.config.database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(application.routers.users.router)
