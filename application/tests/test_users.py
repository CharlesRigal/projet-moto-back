from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_delete_my_account():
    # Créez un utilisateur pour le test
    username = "test_user"
    password = "test_password"
    create_test_user(username, password)

    # Authentifiez-vous en tant qu'utilisateur créé
    response = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    access_token = response.json()["access_token"]

    # Supprimez le compte de l'utilisateur authentifié
    response = client.delete(
        "/remove_my_self",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204

    # Vérifiez que le compte a été supprimé
    # Assurez-vous que la méthode `get_user_by_username` retourne None pour l'utilisateur supprimé
    assert get_user_by_username(username) is None

def test_delete_user():
    # Créez un utilisateur pour le test
    username = "test_user_to_delete"
    password = "test_password"
    create_test_user(username, password)

    # Authentifiez-vous en tant qu'administrateur
    admin_username = "admin"
    admin_password = "admin_password"
    create_admin_user(admin_username, admin_password)
    response = client.post(
        "/token",
        data={"username": admin_username, "password": admin_password}
    )
    admin_access_token = response.json()["access_token"]

    # Supprimez le compte de l'utilisateur créé
    response = client.delete(
        f"/{username}",
        headers={"Authorization": f"Bearer {admin_access_token}"}
    )
    assert response.status_code == 204

    # Vérifiez que le compte a été supprimé
    # Assurez-vous que la méthode `get_user_by_username` retourne None pour l'utilisateur supprimé
    assert get_user_by_username(username) is None
