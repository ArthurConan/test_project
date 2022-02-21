import asyncio

import pytest
import random
import string

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy import create_engine
from typing import Dict, Generator

from test_project import app
from test_project.models.schemas import UserCreate
from test_project.models.models import User as model_user
from test_project.crud.user import user as crud_user
from test_project.core.db import SessionLocal


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
def random_user(db: Session):
    email = random_email()
    password = random_string()
    name = random_string()
    user_in = UserCreate(name=name, email=email, password=password)
    crud_user.create(db=db, obj=user_in)
    return user_in


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
