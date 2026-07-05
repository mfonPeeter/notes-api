import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app
from app.database import get_session
from app.config import settings
from app.auth.schemas import User
from app.notes.schemas import Note
from app.auth.utils import get_password_hash

DEFAULT_PASSWORD = "qwertyasdf"


# @pytest.fixture means this is a reusable setup function.
# pytest automatically runs it before any test that asks for "session".
# The function name "session" is the fixture name - tests request it by this name.
@pytest.fixture
def session():
    # conntect to the TEST database, not the dev database
    engine = create_engine(settings.test_database_url)

    # create all tables in the test database (user, note)
    # SQLModel knows about these tables because importing "app" above
    # triggered imports of all models (User, Note) automatically
    SQLModel.metadata.create_all(engine)

    # open a session - our shopping basket for communicating with the test db
    with Session(engine) as session:
        yield session  # pause here, hand session to the test, wait for test to finish

    # test is done - drop all tables so next test starts with a completely empty database
    # this is why tests don't interfere with each other
    SQLModel.metadata.drop_all(engine)


# this fixture depends on "session" above.
# pytest sees the "session" parameter and automatically runs the session fixture first,
# then passes the result here.
@pytest.fixture
def client(session: Session):
    # define a subsitute for get_session.
    # instead of opening a connection to notes_db (production),
    # it returns our already-open test session (notes_test_db)
    def get_session_override():
        return session

    # tell FastAPI: "whenever a route calls Depends(get_session),
    # run get_session_override instead"
    # the routes don't know anything changes - they still ask for get_session
    # but secretly get the test session
    app.dependency_overrides[get_session] = get_session_override

    # create the HTTP test client - this is what your tests use to make requests
    yield TestClient(app)

    # test is done - remove the override so FastAPI goes back to normal behaviour
    # important: if you don't clear this, other tests might accidentally use the override
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_user(session: Session):
    """Creates a test user in the database. Returns the user object for tests that need it."""
    user = User(
        email="ella@test.com",
        first_name="Ella",
        last_name="Peter",
        password=get_password_hash(DEFAULT_PASSWORD),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def auth_token(seeded_user, client: TestClient):
    """Logs in the seeded user and returns the access token."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": seeded_user.email,
            "password": DEFAULT_PASSWORD,
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def two_users(session: Session):
    """Creates two test users for ownership tests."""
    user_1 = User(
        email="user_1@test.com",
        password=get_password_hash(DEFAULT_PASSWORD),
        first_name="User 1",
        last_name="Test",
    )
    user_2 = User(
        email="user_2@test.com",
        password=get_password_hash(DEFAULT_PASSWORD),
        first_name="User 2",
        last_name="Test",
    )
    session.add(user_1)
    session.add(user_2)
    session.commit()
    session.refresh(user_1)
    session.refresh(user_2)
    return user_1, user_2


@pytest.fixture
def seeded_note(seeded_user, session: Session):
    """Creates a test note for the seeded user."""
    note = Note(title="Test note", content="Test content", user_id=seeded_user.id)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note
