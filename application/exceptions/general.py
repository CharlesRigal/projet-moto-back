from fastapi import Depends, HTTPException
from starlette import status


class ItemNotInListError(Exception):
    pass


class ItemUpdateError(Exception):
    pass


class ItemCreateError(Exception):
    pass


class SelectNotFoundError(Exception):
    pass


class InvalidJWTError(Exception):
    def __init__(self, detail=None):
        super().__init__(detail)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
