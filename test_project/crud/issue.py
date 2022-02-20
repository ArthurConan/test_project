from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from test_project.crud.base import CRUDBase
from test_project.models.models import Issue, Project
from test_project.models.schemas import IssueCreate, IssueUpdate


class IssueCrud(CRUDBase[Issue, IssueCreate, IssueUpdate]):
    def create_with_project(
        self, db: Session, *, obj: IssueCreate
    ) -> Issue:
        obj_in_data = jsonable_encoder(obj)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def list_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Issue]:
        return (
            db.query(self.model)
            .filter(Issue.project_id == project_id, self.model.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_user_projects(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Issue]:

        return (
            db.query(self.model)
            .join(Project)
            .filter(or_(Project.owner_id == user_id, Project.assigned_id == user_id), self.model.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
            .all()
        )


issue = IssueCrud(Issue)
