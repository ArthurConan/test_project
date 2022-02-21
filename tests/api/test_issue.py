from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from test_project.crud.issue import issue as crud_issue
from test_project.models.schemas import IssueCreate, IssueUpdate, ProjectCreate
from test_project.models.models import Issue as model_issue
from test_project.crud.project import project as crud_project
from tests.conftest import random_string


# CRUD
def test_create_issue(db: Session, random_project) -> None:
    title = random_string()
    issue_in = IssueCreate(title=title, type="Bug", status="To Do", project_id=random_project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)
    assert issue.title == title
    assert issue.project_id == random_project.id


def test_retrieve_issue(db: Session, random_project) -> None:
    title = random_string()
    issue_in = IssueCreate(title=title, type="Bug", status="To Do", project_id=random_project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)
    stored_project = crud_issue.retrieve(db=db, id=issue.id)
    assert stored_project
    assert issue.id == stored_project.id
    assert issue.title == stored_project.title
    assert issue.status == stored_project.status
    assert issue.type == stored_project.type
    assert issue.project_id == stored_project.project_id


def test_update_issue(db: Session, random_project) -> None:
    title = random_string()
    issue_in = IssueCreate(title=title, type="Bug", status="To Do", project_id=random_project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)

    title2 = random_string()
    issue_update = IssueUpdate(title=title2, status="Done")
    issue2 = crud_issue.update(db=db, db_obj=issue, obj=issue_update)
    assert issue.id == issue2.id
    assert issue.title == issue2.title
    assert issue2.title == title2
    assert issue.project_id == issue2.project_id
    assert issue.status == issue2.status


def test_delete_issue(db: Session, random_project) -> None:
    title = random_string()
    issue_in = IssueCreate(title=title, type="Bug", status="To Do", project_id=random_project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)

    issue2 = crud_issue.delete(db=db, id=issue.id)
    issue3 = crud_issue.retrieve(db=db, id=issue.id)
    assert issue3 is None
    assert issue2.id == issue2.id
    assert issue2.title == title
    assert issue2.project_id == random_project.id


def test_soft_delete_issue(db: Session, random_project) -> None:
    title = random_string()
    issue_in = IssueCreate(title=title, type="Bug", status="To Do", project_id=random_project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)

    issue2 = crud_issue.delete(db=db, id=issue.id)
    issue3 = crud_issue.retrieve(db=db, id=issue.id)

    assert len(db.query(model_issue).filter(model_issue.is_deleted.is_(True)).all()) > 0


# API
def test_create_admin_issue(client, user_admin_token_headers: dict, db: Session, random_project) -> None:
    data = {"title": "Foo", "type": "Bug", "status": "To Do", "project_id": random_project.id}
    response = client.post(
        "api/issue/", headers=user_admin_token_headers, json=data,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_create_user_issue(client, user_token_headers: dict, db: Session, random_project) -> None:
    data = {"title": "Foo", "type": "Bug", "status": "To Do", "project_id": random_project.id}
    response = client.post(
        "api/issue/", headers=user_token_headers, json=data,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_create_owner_project_issue(client, db: Session, user_token_headers_with_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title, id=id)
    project = crud_project.create_with_owner(db=db, obj=project_in,
                                             owner_id=user_token_headers_with_user.get("user").id)

    data = {"title": "Foo", "type": "Bug", "status": "To Do", "project_id": project.id}
    response = client.post(
        "api/issue/", headers=user_token_headers_with_user.get("headers"), json=data,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data['title']
    assert content["type"] == data['type']
    assert content["status"] == data['status']
    assert content["project_id"] == project.id


def test_retrieve_admin_issue(client: TestClient, user_admin_token_headers: dict, db: Session, random_issue) -> None:
    response = client.get(
        f"/api/issue/{random_issue.id}", headers=user_admin_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == random_issue.title
    assert content["id"] == random_issue.id
    assert content["project_id"] == random_issue.project_id


def test_retrieve_user_issue(client: TestClient, user_token_headers: dict, db: Session, random_issue) -> None:
    response = client.get(
        f"/api/issue/{random_issue.id}", headers=user_token_headers,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_retrieve_owner_project_issue(client: TestClient, db: Session, user_token_headers_with_user) -> None:
    title = random_string()
    project_in = ProjectCreate(title=title, id=id)
    project = crud_project.create_with_owner(db=db, obj=project_in, owner_id=user_token_headers_with_user.get("user").id)

    title2 = random_string()
    issue_in = IssueCreate(title=title2, type="Bug", status="To Do", project_id=project.id)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)

    response = client.get(
        f"/api/issue/{issue.id}", headers=user_token_headers_with_user.get("headers"),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == issue.title
    assert content["id"] == issue.id
    assert content["project_id"] == issue.project_id


def test_retrieve_assigned_project_issue(
        client: TestClient, db: Session, user_admin_token_headers, user_token_headers_with_user, random_issue
) -> None:
    data = {"assigned_id": user_token_headers_with_user.get('user').id}

    response = client.put(
        f"api/project/{random_issue.project_id}", headers=user_admin_token_headers, json=data,
    )

    response = client.get(
        f"/api/issue/{random_issue.id}", headers=user_token_headers_with_user.get("headers"),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == random_issue.title
    assert content["id"] == random_issue.id
    assert content["project_id"] == random_issue.project_id


def test_delete_admin_issues(
    client: TestClient, user_admin_token_headers: dict, db: Session, random_issue
) -> None:
    response = client.delete(
        f"api/issue/{random_issue.id}", headers=user_admin_token_headers,
    )

    assert response.status_code == 400
    content = response.json()
    assert content == {'detail': 'Not enough permissions'}


def test_delete_user_issues(
    client: TestClient, user_token_headers: dict, db: Session, random_issue
) -> None:
    response = client.delete(
        f"api/issue/{random_issue.id}", headers=user_token_headers,
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

    data = {"title": "Foo", "type": "Bug", "status": "To Do", "project_id": project.id}

    issue_in = IssueCreate(**data)
    issue = crud_issue.create_with_project(db=db, obj=issue_in)

    response = client.delete(
        f"api/issue/{issue.id}", headers=user_token_headers_with_user.get("headers"),
    )

    assert response.status_code == 200
    content = response.json()
    assert content["title"] == issue.title
    assert content["id"] == issue.id
    assert content["project_id"] == issue.project_id
