from fastapi import APIRouter, Depends, status
from fastapi.responses import ORJSONResponse
from jose import jwt
from sqlalchemy.orm import Session
from typing import Any

from test_project.core.auth import oauth2_scheme, create_oauth_token
from test_project.core.settings import get_settings
from test_project.core.db import get_db
from test_project.crud.user import user as crud_user
from test_project.models.models import User as model_user
from test_project.models.schemas import Token, TokenPayload, UserCreate, User
from test_project.core.exceptions import UserNotFoundException, UserNotAdminException


router = APIRouter()


@router.post("/login/token", response_model=Token)
def login_access_token(form_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    user = crud_user.authenticate(
        db, email=form_data.email, password=form_data.password
    )

    return ORJSONResponse(
        content={
            "access_token": create_oauth_token(user.id, get_settings().auth.access_token_expire_minutes),
            "token_type": "bearer",
            "expired_minutes": get_settings().auth.access_token_expire_minutes,
        },
        status_code=status.HTTP_200_OK,
    )


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> model_user:
    payload = jwt.decode(token, get_settings().auth.secret_key, algorithms=[get_settings().auth.algorithm])
    token_data = TokenPayload(**payload)

    user = crud_user.retrieve(db, id=token_data.sub)
    if not user:
        raise UserNotFoundException

    return user


def get_current_superuser(
    current_user: model_user = Depends(get_current_user),
) -> model_user:
    if not crud_user.is_admin(current_user):
        raise UserNotAdminException

    return current_user


@router.post("/login/test-token", response_model=User)
def test_token(current_user: model_user = Depends(get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user
