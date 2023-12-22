import routers
from fastapi import FastAPI
import models
from config.database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(routers.users.router)
