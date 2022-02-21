from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List

from test_project.api.auth import get_current_user, get_current_superuser
from test_project.core.db import get_db
from test_project.core.exceptions import UserExistsException
from test_project.crud.user import user as crud_user
from test_project.models.models import User as model_user
from test_project.models.schemas import UserCreate, User


router = APIRouter()


@router.get("/", response_model=List[User])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: model_user = Depends(get_current_superuser),
) -> Any:
    users = crud_user.list(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=User)
def retrieve_user_me(current_user: model_user = Depends(get_current_user)) -> Any:
    return current_user


@router.post("/register", response_model=User)
def create_user(
        *,
        db: Session = Depends(get_db),
        user_sch: UserCreate,
) -> Any:
    user = crud_user.retrieve_by_email(db, email=user_sch.email)

    if user:
        raise UserExistsException

    user = crud_user.create(db, obj=user_sch)
    return user
