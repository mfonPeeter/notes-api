from fastapi.testclient import TestClient
from sqlmodel import Session

from app.notes.schemas import Note
from tests.conftest import DEFAULT_PASSWORD


def test_create_note_success(auth_token, client: TestClient):
    response = client.post(
        "/api/v1/notes",
        json={
            "title": "Test note",
            "content": "Test content",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["title"] == "Test note"
    assert data["content"] == "Test content"


def test_create_note_unauthenticated(client: TestClient):
    response = client.post(
        "/api/v1/notes",
        json={
            "title": "Test note",
            "content": "Test content",
        },
    )
    assert response.status_code == 401


def test_get_notes_success(
    seeded_user, auth_token, session: Session, client: TestClient
):
    note_1 = Note(title="Test note", content="Test content", user_id=seeded_user.id)
    note_2 = Note(
        title="Test another note",
        content="Test another content",
        user_id=seeded_user.id,
    )

    session.add(note_1)
    session.add(note_2)
    session.commit()

    response = client.get(
        "/api/v1/notes",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "Test note"
    assert data[1]["title"] == "Test another note"


def test_get_notes_ownership(two_users, session: Session, client: TestClient):
    user_1, user_2 = two_users

    # create a note for each user
    note_1 = Note(title="User 1 note", content="Content", user_id=user_1.id)
    note_2 = Note(
        title="User 2 note",
        content="Content",
        user_id=user_2.id,
    )
    session.add(note_1)
    session.add(note_2)
    session.commit()

    # login as user 1
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_1.email, "password": DEFAULT_PASSWORD},
    )
    token = login_response.json()["access_token"]

    # fetch notes as user 1
    response = client.get("/api/v1/notes", headers={"Authorization": f"Bearer {token}"})
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1  # only sees thier own note
    assert data[0]["title"] == "User 1 note"


def test_get_all_notes_unauthenticated(client: TestClient):
    response = client.get("/api/v1/notes")
    assert response.status_code == 401


def test_get_note_success(seeded_note, auth_token, client: TestClient):
    response = client.get(
        f"/api/v1/notes/{seeded_note.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == seeded_note.title
    assert data["content"] == seeded_note.content


def test_get_note_wrong_user(two_users, session: Session, client: TestClient):
    user_1, user_2 = two_users

    # create a note for user 2
    note_2 = Note(
        title="User 2 note",
        content="Content",
        user_id=user_2.id,
    )
    session.add(note_2)
    session.commit()

    # login as user 1
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_1.email, "password": DEFAULT_PASSWORD},
    )
    token = login_response.json()["access_token"]

    # try to get user 2's note
    response = client.get(
        f"/api/v1/notes/{note_2.id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_get_note_not_found(auth_token, client: TestClient):
    response = client.get(
        "/api/v1/notes/99999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_get_note_unauthenticated(client: TestClient):
    response = client.get(f"/api/v1/notes/1")
    assert response.status_code == 401


def test_update_note_success(seeded_note, auth_token, client: TestClient):
    response = client.patch(
        f"/api/v1/notes/{seeded_note.id}",
        json={"title": "Testing"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Testing"
    assert data["content"] == seeded_note.content


def test_update_note_wrong_user(two_users, session: Session, client: TestClient):
    user_1, user_2 = two_users

    # create a note for user_1
    note = Note(title="User 1 note", content="Content", user_id=user_1.id)
    session.add(note)
    session.commit()

    # login as user_2
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_2.email, "password": DEFAULT_PASSWORD},
    )
    token = login_response.json()["access_token"]

    # update note for user_1
    response = client.patch(
        f"/api/v1/notes/{note.id}",
        json={"title": "User note"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_update_note_not_found(auth_token, client: TestClient):
    response = client.patch(
        "/api/v1/notes/9999",
        json={"title": "User note"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_update_note_unauthenticated(client: TestClient):
    response = client.patch(
        "/api/v1/notes/9999",
        json={"title": "User note"},
    )
    assert response.status_code == 401


def test_delete_note_success(seeded_note, auth_token, client: TestClient):
    response = client.delete(
        f"/api/v1/notes/{seeded_note.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 204


def test_delete_note_wrong_user(two_users, session: Session, client: TestClient):
    user_1, user_2 = two_users

    # create note for user 1
    note = Note(title="User 1 note", content="Content", user_id=user_1.id)
    session.add(note)
    session.commit()

    # login for user 2
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user_2.email, "password": DEFAULT_PASSWORD},
    )
    token = login_response.json()["access_token"]

    # delete note for user 1 while being logged in as user 2
    response = client.delete(
        f"/api/v1/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_delete_note_not_found(auth_token, client: TestClient):
    response = client.delete(
        "/api/v1/notes/9999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_delete_note_unauthenticated(client: TestClient):
    response = client.delete(
        "/api/v1/notes/9999",
    )
    assert response.status_code == 401
