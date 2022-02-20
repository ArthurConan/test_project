from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from test_project.crud.base import CRUDBase
from test_project.models.models import Project
from test_project.models.schemas import ProjectCreate, ProjectUpdate


class ProjectCrud(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def create_with_owner(
            self,
            db: Session,
            *,
            obj: ProjectCreate,
            owner_id: int
    ) -> Project:
        obj_in_data = jsonable_encoder(obj)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_user(self, db: Session, *, user_id: int = None, skip: int = 0, limit: int = 100) -> List[Project]:
        return (
            db.query(self.model)
            .filter(or_(Project.owner_id == user_id, Project.assigned_id == user_id), self.model.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
            .all()
        )


project = ProjectCrud(Project)
