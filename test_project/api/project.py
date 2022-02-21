from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from test_project.api.auth import get_current_user
from test_project.core.db import get_db
from test_project.core.exceptions import (
    ProjectNotFoundException,
    PermissionException,
    UserNotFoundException
)
from test_project.crud.project import project as crud_project
from test_project.crud.user import user as crud_user
from test_project.models.models import User as model_user
from test_project.models.schemas import Project, ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/{id}", response_model=Project)
def retrieve_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: model_user = Depends(get_current_user),
) -> Any:
    project = crud_project.retrieve(db=db, id=id)

    if not project:
        raise ProjectNotFoundException

    if all([not crud_user.is_admin(current_user), current_user.id not in [project.owner_id, project.assigned_id]]):
        raise PermissionException

    return project


@router.get("/", response_model=List[Project])
def list_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: model_user = Depends(get_current_user),
) -> Any:

    if crud_user.is_admin(current_user):
        projects = crud_project.list(db, skip=skip, limit=limit)
    else:
        projects = crud_project.list_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

    return projects


@router.post("/", response_model=Project)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_sch: ProjectCreate,
    current_user: model_user = Depends(get_current_user),
) -> Any:
    # вроде не указано, что админ может создавать проект. исходила из того, что не может.
    if crud_user.is_admin(current_user):
        raise PermissionException

    project = crud_project.create_with_owner(db=db, obj=project_sch, owner_id=current_user.id)
    return project


@router.put("/{id}", response_model=Project)
def update_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    project_sch: ProjectUpdate,
    current_user: model_user = Depends(get_current_user),
) -> Any:
    project = crud_project.retrieve(db=db, id=id)

    if not project or project.is_deleted:
        raise ProjectNotFoundException

    if not crud_user.is_admin(current_user) and project.owner_id != current_user.id:
        raise PermissionException

    obj_in_data = jsonable_encoder(project_sch)
    if "assigned_id" in obj_in_data:
        user = crud_user.retrieve(db=db, id=obj_in_data.get("assigned_id"))
        if not user:
            raise UserNotFoundException

    project = crud_project.retrieve(db=db, id=id)
    project = crud_project.update(db=db, db_obj=project, obj=project_sch)

    return project


@router.delete("/{id}", response_model=Project)
def delete_project(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: model_user = Depends(get_current_user),
) -> Any:
    project = crud_project.retrieve(db=db, id=id)

    if not project or project.is_deleted:
        raise ProjectNotFoundException

    if project.owner_id != current_user.id:
        raise PermissionException

    project = crud_project.delete(db=db, id=id)
    return project
