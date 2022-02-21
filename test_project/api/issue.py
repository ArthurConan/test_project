from typing import Any, List

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from test_project.api.auth import get_current_user
from test_project.core.db import get_db
from test_project.core.exceptions import (
    IssueNotFoundException,
    PermissionException,
    ProjectNotFoundException,
    ProjectRequiredException
)
from test_project.core.mail import mail
from test_project.crud.issue import issue as crud_issue
from test_project.crud.project import project as crud_project
from test_project.crud.user import user as crud_user
from test_project.models.models import User as model_user
from test_project.models.schemas import Issue, IssueCreate, IssueUpdate

router = APIRouter()


@router.get("/{id}", response_model=Issue)
def retrieve_issue(
        *,
        db: Session = Depends(get_db),
        id: int,
        current_user: model_user = Depends(get_current_user),
) -> Any:
    issue = crud_issue.retrieve(db=db, id=id)

    if not issue:
        raise IssueNotFoundException

    if all([
        not crud_user.is_admin(current_user),
        current_user.id not in [issue.project.owner_id, issue.project.assigned_id]]
    ):
        raise PermissionException

    return issue


@router.get("/", response_model=List[Issue])
def list_issues(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: model_user = Depends(get_current_user),
) -> Any:

    if crud_user.is_admin(current_user):
        issues = crud_issue.list(db, skip=skip, limit=limit)
    else:
        issues = crud_issue.list_by_user_projects(db=db, user_id=current_user.id, skip=skip, limit=limit)

    return issues


@router.get("/project/{id}", response_model=List[Issue])
def list_issues_by_project(
        id: int,
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: model_user = Depends(get_current_user),
) -> Any:
    project = crud_project.retrieve(db=db, id=id)

    if not project:
        raise ProjectNotFoundException

    if all([
        not crud_user.is_admin(current_user),
        current_user.id not in [project.owner_id, project.assigned_id]]
    ):
        raise PermissionException

    issues = crud_issue.list_by_project(db=db, project_id=project.id, skip=skip, limit=limit)

    return issues


@router.post("/", response_model=Issue)
def create_issues(
        *,
        db: Session = Depends(get_db),
        issue_sch: IssueCreate,
        current_user: model_user = Depends(get_current_user),
) -> Any:
    # вроде не указано, что админ может создавать issue. исходила из того, что не может.
    if crud_user.is_admin(current_user):
        raise PermissionException

    obj_in_data = jsonable_encoder(issue_sch)
    if "project_id" not in obj_in_data:
        raise ProjectRequiredException

    project = crud_project.retrieve(db=db, id=obj_in_data.get("project_id"))

    if not project or project.is_deleted:
        raise ProjectNotFoundException

    if project.owner_id != current_user.id:
        raise PermissionException

    issue = crud_issue.create_with_project(db=db, obj=issue_sch)
    return issue


@router.put("/{id}", response_model=Issue)
def update_issue(
        *,
        db: Session = Depends(get_db),
        id: int,
        issue_sch: IssueUpdate,
        current_user: model_user = Depends(get_current_user),
        background_tasks: BackgroundTasks
) -> Any:
    issue = crud_issue.retrieve(db=db, id=id)

    if not issue or issue.is_deleted:
        raise IssueNotFoundException

    if not crud_user.is_admin(current_user) and issue.project.owner_id != current_user.id:
        raise PermissionException

    obj_in_data = jsonable_encoder(issue_sch)
    if "status" in obj_in_data:
        background_tasks.add_task(mail.send_notification_mail, user_email=current_user.email, data_mail={
            "issue_id": issue.id,
            "project_id": issue.project.id,
            "from_status": issue.status,
            "to_status": obj_in_data["status"],

        })
    issue = crud_issue.update(db=db, db_obj=issue, obj=issue_sch)
    return issue


@router.delete("/{id}", response_model=Issue)
def delete_issue(
        *,
        db: Session = Depends(get_db),
        id: int,
        current_user: model_user = Depends(get_current_user),
) -> Any:
    issue = crud_issue.retrieve(db=db, id=id)

    if not issue or issue.is_deleted:
        raise IssueNotFoundException

    if issue.project.owner_id != current_user.id:
        raise PermissionException

    issue = crud_issue.delete(db=db, id=id)
    return issue
