import logging.config
import platform

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import auth, friends, users, admin, routes, websocket
from config.database import engine, Base
from config.env import get_settings

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

# CORS configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(friends.router)
app.include_router(routes.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    if settings.env == "development":
        uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)
    else:
        if platform.system() != "Linux":
            raise OSError("Production setting is only suitable on Linux")
        from starter.StandaloneApplication import (
            number_of_workers,
            StandaloneApplication,
        )

        options = {
            "bind": "0.0.0.0:8888",
            "workers": number_of_workers(),
            "worker_class": "uvicorn.workers.UvicornWorker",
        }
        StandaloneApplication(app, options).run()
