import pytest

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from test_project.crud.user import user as crud_user
from test_project.models.schemas import UserCreate
from tests.conftest import random_email, random_string
from test_project.core.exceptions import UserNotFoundException


# CRUD tests
def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj=user_in)
    authenticated_user = crud_user.authenticate(db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_string()
    with pytest.raises(UserNotFoundException) as e:
        crud_user.authenticate(db, email=email, password=password)


def test_check_if_user_is_admin(db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password, is_admin=True)
    user = crud_user.create(db, obj=user_in)
    is_admin = crud_user.is_admin(user)
    assert is_admin is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj=user_in)
    is_admin = crud_user.is_admin(user)
    assert is_admin is False


def test_get_user(db: Session) -> None:
    password = random_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_admin=True)
    user = crud_user.create(db, obj=user_in)
    user_2 = crud_user.retrieve(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


# API tests
def test_create_user_new_email(client: TestClient, user_token_headers: dict, db: Session) -> None:
    email = random_email()
    password = random_string()
    data = {"email": email, "password": password}
    r = client.post(
        "api/user/register", headers=user_token_headers, json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = crud_user.retrieve_by_email(db, email=email)
    assert user
    assert user.email == created_user["email"]


def test_create_user_existing_username(client: TestClient, user_token_headers: dict, db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    crud_user.create(db, obj=user_in)
    data = {"email": email, "password": password}
    r = client.post(
        "api/user/register", headers=user_token_headers, json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def test_get_user_me(client: TestClient, user_token_headers: Dict[str, str]) -> None:
    r = client.get("api/user/me", headers=user_token_headers)
    current_user = r.json()
    assert current_user


def test_retrieve_users_user(client: TestClient, user_token_headers: dict, db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    crud_user.create(db, obj=user_in)

    email2 = random_email()
    password2 = random_string()
    user_in2 = UserCreate(email=email2, password=password2)
    crud_user.create(db, obj=user_in2)

    r = client.get("api/user/", headers=user_token_headers)
    assert r.json() == {'detail': 'User has no admin privileges'}


def test_retrieve_users_admin(client: TestClient, user_admin_token_headers: dict, db: Session) -> None:
    email = random_email()
    password = random_string()
    user_in = UserCreate(email=email, password=password)
    crud_user.create(db, obj=user_in)

    email2 = random_email()
    password2 = random_string()
    user_in2 = UserCreate(email=email2, password=password2)
    crud_user.create(db, obj=user_in2)

    r = client.get("api/user/", headers=user_admin_token_headers)
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item
