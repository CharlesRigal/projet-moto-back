import os

from routers import auth, friends, users, admin, routes
from fastapi import FastAPI
import uvicorn
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
app.include_router(routes.router)

if __name__ == "__main__":
    if os.environ.get("ENV") == "development":
        uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)
    elif os.environ.get("ENV") == "production":
        from starter.StandaloneApplication import number_of_workers, handler_app, StandaloneApplication
        options = {
            'bind': '%s:%s' % ('0.0.0.0', '8888'),
            'workers': number_of_workers(),
        }
        StandaloneApplication(handler_app, options).run()
    else:
        raise EnvironmentError("missing ENV variable")
