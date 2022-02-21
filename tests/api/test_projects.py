from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from test_project.crud.project import project as crud_project
from test_project.models.schemas import ProjectCreate, ProjectUpdate
from test_project.models.models import Project as model_project
from tests.conftest import random_string


# CRUD
def test_create_project(db: Session, random_project_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)
    assert project.title == title
    assert project.owner_id == random_project_user.id


def test_create_with_assigned_project(db: Session, random_project_user, random_project_user2) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title, assigned_id=random_project_user2.id)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)
    assert project.title == title
    assert project.owner_id == random_project_user.id
    assert project.assigned_id == random_project_user2.id


def test_retrieve_item(db: Session, random_project_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)
    stored_project = crud_project.retrieve(db=db, id=project.id)
    assert stored_project
    assert project.id == stored_project.id
    assert project.title == stored_project.title
    assert project.owner_id == stored_project.owner_id


def test_update_item(db: Session, random_project_user, random_project_user2) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)

    title2 = random_string()
    project_update = ProjectUpdate(title=title2, assigned_id=random_project_user2.id)
    project2 = crud_project.update(db=db, db_obj=project, obj=project_update)
    assert project.id == project2.id
    assert project.title == project2.title
    assert project2.title == title2
    assert project.owner_id == project2.owner_id
    assert project.assigned_id == project2.assigned_id


def test_delete_item(db: Session, random_project_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)
    project2 = crud_project.delete(db=db, id=project.id)
    project3 = crud_project.retrieve(db=db, id=project.id)
    assert project3 is None
    assert project2.id == project2.id
    assert project2.title == title
    assert project2.owner_id == random_project_user.id


def test_soft_delete_item(db: Session, random_project_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=random_project_user.id)
    project2 = crud_project.delete(db=db, id=project.id)
    project3 = crud_project.retrieve(db=db, id=project.id)

    assert len(db.query(model_project).filter(model_project.is_deleted.is_(True)).all()) > 0


# API
def test_create_admin_project(client, user_admin_token_headers: dict, db: Session) -> None:
    data = {"title": "Foo"}
    response = client.post(
        "api/project/", headers=user_admin_token_headers, json=data,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_create_user_project(client, user_token_headers: dict, db: Session) -> None:
    data = {"title": "Foo"}
    response = client.post(
        "api/project/", headers=user_token_headers, json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert "id" in content
    assert "owner_id" in content


def test_retrieve_admin_project(client: TestClient, user_admin_token_headers: dict, db: Session, random_project) -> None:
    response = client.get(
        f"/api/project/{random_project.id}", headers=user_admin_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == random_project.title
    assert content["id"] == random_project.id
    assert content["owner_id"] == random_project.owner_id


def test_retrieve_user_project(client: TestClient, user_token_headers: dict, db: Session, random_project) -> None:
    response = client.get(
        f"/api/project/{random_project.id}", headers=user_token_headers,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_retrieve_owner_project(client: TestClient, db: Session, user_token_headers_with_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title, id=id)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=user_token_headers_with_user.get("user").id)

    response = client.get(
        f"/api/project/{project.id}", headers=user_token_headers_with_user.get("headers"),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == project.title
    assert content["id"] == project.id
    assert content["owner_id"] == project.owner_id


def test_retrieve_assigned_project(
        client: TestClient, user_admin_token_headers: dict, db: Session, random_project, user_token_headers_with_user
) -> None:
    data = {"assigned_id": user_token_headers_with_user.get('user').id}

    response = client.put(
        f"api/project/{random_project.id}", headers=user_admin_token_headers, json=data,
    )

    response = client.get(
        f"/api/project/{random_project.id}", headers=user_token_headers_with_user.get('headers'),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == random_project.title
    assert content["id"] == random_project.id
    assert content["owner_id"] == random_project.owner_id


def test_assign_project(
        client: TestClient, db: Session, user_admin_token_headers, random_project, random_project_user
) -> None:
    data = {"assigned_id": random_project_user.id}

    response = client.put(
        f"api/project/{random_project.id}", headers=user_admin_token_headers, json=data,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["assigned_id"] == random_project_user.id


def test_fail_assign_project(
        client: TestClient, db: Session, user_admin_token_headers, random_project
) -> None:
    data = {"assigned_id": 9999}

    response = client.put(
        f"api/project/{random_project.id}", headers=user_admin_token_headers, json=data,
    )

    assert response.status_code == 404
    content = response.json()
    assert content == {'detail': 'User not found'}


def test_delete_admin_projects(
    client: TestClient, user_admin_token_headers: dict, db: Session, random_project
) -> None:
    response = client.delete(
        f"api/project/{random_project.id}", headers=user_admin_token_headers,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_delete_user_projects(
    client: TestClient, user_token_headers: dict, db: Session, random_project
) -> None:
    response = client.delete(
        f"api/project/{random_project.id}", headers=user_token_headers,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_delete_owner_projects(
    client: TestClient, db: Session, user_token_headers_with_user
) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title, id=id)
    project = crud_project.create_with_owner(db=db, obj=project_in,
                                             owner_id=user_token_headers_with_user.get("user").id)

    response = client.delete(
        f"api/project/{project.id}", headers=user_token_headers_with_user.get("headers"),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == project.title
    assert content["id"] == project.id
    assert content["owner_id"] == project.owner_id
