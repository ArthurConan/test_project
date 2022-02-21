import asyncio

import pytest
import random
import string

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy import create_engine
from typing import Dict, Generator

from test_project import app
from test_project.models.schemas import UserCreate, ProjectCreate, IssueCreate
from test_project.models.models import User as model_user
from test_project.crud.user import user as crud_user
from test_project.crud.project import project as crud_project
from test_project.crud.issue import issue as crud_issue
from test_project.core.db import SessionLocal


#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @pytest.fixture(scope="session")
# def db():
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@pytest.fixture(scope="session")
def db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def random_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_string()}@{random_string()}.com"


@pytest.fixture(scope="module")
def random_project_user(db: Session):
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password)
    user = crud_user.create(db=db, obj=user_in)
    return user


@pytest.fixture(scope="module")
def random_project_user2(db: Session):
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password)
    user = crud_user.create(db=db, obj=user_in)
    return user


@pytest.fixture(scope="module")
def random_user(db: Session):
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password)
    crud_user.create(db=db, obj=user_in)
    return user_in


@pytest.fixture(scope="module")
def random_project(db: Session, random_project_user):
    title = random_string()
    project_in = ProjectCreate(title=title, id=id)
    return crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)


@pytest.fixture(scope="module")
def random_issue(db: Session, random_project):
    title = random_string()
    issue_in = IssueCreate(title=title, id=id, type="Bug", status="To Do", project_id=random_project.id)
    return crud_issue.create_with_project(db=db, obj=issue_in)


@pytest.fixture(scope="module")
def user_token_headers(client: TestClient, random_user: model_user) -> Dict[str, str]:
    r = client.post(
        "/api/auth/login/token",
        json={
            'email': random_user.email,
            'password': random_user.password
        }
    )
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


@pytest.fixture(scope="module")
def random_admin_user(db: Session):
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password, is_admin=True)
    crud_user.create(db=db, obj=user_in)
    return user_in


@pytest.fixture(scope="module")
def user_admin_token_headers(client: TestClient, random_admin_user: model_user) -> Dict[str, str]:
    r = client.post(
        "/api/auth/login/token",
        json={
            'email': random_admin_user.email,
            'password': random_admin_user.password
        }
    )
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


@pytest.fixture(scope="module")
def user_token_headers_with_user(db:Session, client: TestClient) -> Dict:
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password)
    user = crud_user.create(db=db, obj=user_in)

    r = client.post(
        "/api/auth/login/token",
        json={
            'email': user_in.email,
            'password': user_in.password
        }
    )
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return {"headers": headers, "user": user}
