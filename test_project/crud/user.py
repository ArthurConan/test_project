from typing import Optional
from sqlalchemy.orm import Session

from test_project.core.auth import get_password_hash, verify_password
from test_project.core.exceptions import (
    UserNotFoundException,
    WrongPasswordException
)
from test_project.crud.base import CRUDBase
from test_project.models.models import User
from test_project.models.schemas import UserCreate, UserUpdate


class UserCrud(CRUDBase[User, UserCreate, UserUpdate]):
    def retrieve_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj: UserCreate) -> User:
        db_obj = User(
            name=obj.name,
            email=obj.email,
            hashed_password=get_password_hash(obj.password),
            is_admin=obj.is_admin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.retrieve_by_email(db, email=email)

        if not user:
            raise UserNotFoundException

        if not verify_password(password, user.hashed_password):
            raise WrongPasswordException

        return user

    def is_admin(self, user: User) -> bool:
        return user.is_admin


user = UserCrud(User)
