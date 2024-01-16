from routers import auth, friends, users, admin, trips
from fastapi import FastAPI
import models
from config.database import engine
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base

Base.metadata.create_all(bind=engine)


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(friends.router)
app.include_router(trips.router)
