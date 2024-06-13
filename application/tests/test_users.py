from .test_utils import test_client


def test_user_creation():
    response = test_client.post(
        "/api/v0.1/auth/signup/",
        json={
            "username": "client1",
            "password": "password",
            "email": "client1@email.com",
        },
    )
    assert response.status_code == 201, response.json() == {"success": True}


def test_user_creation_invalid_credentials():
    response = test_client.post(
        "/api/v0.1/auth/signup/",
        json={"username": "", "password": "pass", "email": "invalidemail.com"},
    )
    assert response.status_code == 422
