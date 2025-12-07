import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.model.user import Role


# Use a separate SQLite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the app's DB dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create tables once per test session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def _register_user(client: TestClient, username: str, password: str, role: Role = Role.user):
    # register
    res = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )

    if res.status_code == 201:
        # fresh user, all good
        pass
    elif res.status_code == 400 and "already registered" in res.text:
        # user already exists from a previous test – that's fine
        pass
    else:
        # anything else is a real error
        assert False, f"Unexpected response registering {username}: {res.status_code} {res.text}"

    # if we want admin/approver, call make-admin helper
    if role == Role.admin:
        res2 = client.post(f"/api/auth/make-admin/{username}")
        assert res2.status_code in (200, 400), res2.text  # 400 here would mean already admin etc.

    return username, password


@pytest.fixture
def user_credentials(client):
    return _register_user(client, username="user1", password="Secret123!")


@pytest.fixture
def admin_credentials(client):
    return _register_user(client, username="admin1", password="Admin123!", role=Role.admin)


@pytest.fixture
def user_token(client, user_credentials):
    username, password = user_credentials
    res = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return token


@pytest.fixture
def admin_token(client, admin_credentials):
    username, password = admin_credentials
    res = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return token
