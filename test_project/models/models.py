from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Any


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean(), default=False)

    is_deleted = Column(Boolean(), default=False)


class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    issues = relationship("Issue", back_populates="project")
    assigned_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    is_deleted = Column(Boolean(), default=False)


class Issue(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="issues")

    is_deleted = Column(Boolean(), default=False)
