import argparse
import logging
import platform

from routers import auth, friends, users, admin, routes, websocket
from fastapi import FastAPI
import uvicorn
from config.database import engine
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base
from config.env import get_settings

settings = get_settings()

Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

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
app.include_router(websocket.router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI application with Uvicorn.")
    parser.add_argument('--log-config', type=str, default="./log_conf.yaml", help='Path to log configuration file')
    args = parser.parse_args()

    if settings.env == "development":
        uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True, log_config=args.log_config)
    else:
        if platform.system() != "Linux":
            raise OSError("Production setting is only suitable on Linux")
        from starter.StandaloneApplication import (
            number_of_workers,
            StandaloneApplication,
        )

        options = {
            "bind": "%s:%s" % ("0.0.0.0", "8888"),
            "workers": number_of_workers(),
            "worker_class": "uvicorn.workers.UvicornWorker",
            "logconfig": args.log_config,
        }
        StandaloneApplication(app, options).run()
