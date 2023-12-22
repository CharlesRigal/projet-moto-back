from fastapi import Security, APIRouter

from application.services.utils import VerifyToken

auth = VerifyToken()
router = APIRouter()


@router.get("/api/v1/public")
def public():
    """No access token required to access this route"""

    result = {
        "status": "success",
        "msg": ("Hello from a public endpoint! You don't need to be "
                "authenticated to see this.")
    }
    return result


@router.get("/api/v1/private")
def private(auth_result: str = Security(auth.verify)):
    """A valid access token is required to access this route"""
    return auth_result


@app.get("/api/private-scoped")
def private_scoped(auth_result: str = Security(auth.verify, scopes=['read:messages'])):
    """A valid access token and an appropriate scope are required to access
    this route
    """

    return auth_result
