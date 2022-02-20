from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    is_admin: bool = False
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
    is_deleted: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class ProjectBase(BaseModel):
    title: Optional[str] = None
    assigned_id: Optional[int] = None


class ProjectCreate(ProjectBase):
    title: str


class ProjectUpdate(ProjectBase):
    pass


class ProjectInDBBase(ProjectBase):
    id: int
    title: str
    owner_id: int
    assigned_id: Optional[int] = None

    class Config:
        orm_mode = True


class Project(ProjectInDBBase):
    pass


class ProjectInDB(ProjectInDBBase):
    is_deleted: bool = False


class IssueBase(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None


class IssueCreate(IssueBase):
    title: str
    project_id: int
    status: str
    type: str


class IssueUpdate(IssueBase):
    pass


class IssueInDBBase(IssueBase):
    id: int
    title: str
    project_id: int
    status: str
    type: str

    class Config:
        orm_mode = True


class Issue(IssueInDBBase):
    pass


class IssueInDB(IssueInDBBase):
    is_deleted: bool = False
