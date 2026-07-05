from fastapi.testclient import TestClient

from tests.conftest import DEFAULT_PASSWORD


def test_register_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "mfon@test.com",
            "first_name": "Mfonobong",
            "last_name": "Peter",
            "password": "qwertyasdf",
        },
    )
    data = response.json()

    assert response.status_code == 201
    assert data["access_token"] is not None
    assert data["user"]["email"] == "mfon@test.com"
    assert "password" not in data["user"]


def test_register_existing_email(seeded_user, client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": seeded_user.email,
            "first_name": seeded_user.first_name,
            "last_name": seeded_user.last_name,
            "password": DEFAULT_PASSWORD,
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email is already registered"}


def test_login_success(seeded_user, client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": seeded_user.email,
            "password": DEFAULT_PASSWORD,
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["access_token"] is not None
    assert data["user"]["email"] == seeded_user.email
    assert "password" not in data["user"]


def test_login_wrong_password(seeded_user, client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": seeded_user.email,
            "password": "qwertyasdf_1234",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid login credentials"}


def test_login_email_not_found(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nobody@test.com",
            "password": DEFAULT_PASSWORD,
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid login credentials"}


def test_update_profile_success(seeded_user, auth_token, client: TestClient):
    response = client.patch(
        "/api/v1/auth/me",
        json={"first_name": "Mfonobong"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["first_name"] == "Mfonobong"
    assert data["last_name"] == seeded_user.last_name


def test_update_profile_unauthenticated(client: TestClient):
    response = client.patch("/api/v1/auth/me", json={"first_name": "Mfonobong"})
    assert response.status_code == 401


def test_updated_password_success(auth_token, client: TestClient):
    response = client.patch(
        "/api/v1/auth/me/update-password",
        json={
            "current_password": DEFAULT_PASSWORD,
            "new_password": "changeMe123!",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully"}


def test_updated_password_wrong_current(auth_token, client: TestClient):
    response = client.patch(
        "/api/v1/auth/me/update-password",
        json={
            "current_password": "wrongObv_suly",
            "new_password": "changeMe123!",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid password"}


def test_update_password_unauthenticated(client: TestClient):
    response = client.patch(
        "/api/v1/auth/me/update-password",
        json={
            "current_password": DEFAULT_PASSWORD,
            "new_password": "changeMe123!",
        },
    )
    assert response.status_code == 401


def test_delete_account_success(seeded_user, auth_token, client: TestClient):
    response = client.delete(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204


def test_delete_account_unauthenticated(seeded_user, client: TestClient):
    response = client.delete(
        "/api/v1/auth/me",
    )
    assert response.status_code == 401
