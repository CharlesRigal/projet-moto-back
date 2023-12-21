from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()


@app.get("/api/v1/public")
def public():
    """No access token required to access this route"""
    result = {
        "status": "success",
        "msg": "Public route"
    }
    return result
