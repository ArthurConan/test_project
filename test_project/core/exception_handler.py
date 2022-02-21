from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from jose import JWTError
from pydantic import ValidationError

from test_project.core.exceptions import (
    UserNotAdminException,
    UserNotFoundException,
    UserExistsException,
    WrongPasswordException,
    ProjectNotFoundException,
    PermissionException,
    IssueNotFoundException,
    ProjectRequiredException
)


def custom_exception_handler(_: Request, exc: Exception) -> ORJSONResponse:
    if isinstance(exc, UserNotFoundException):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={
                "detail": "User not found"}
        )

    if isinstance(exc, WrongPasswordException):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={
                "detail": "Wrong password"}
        )

    if isinstance(exc, UserExistsException):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={
                "detail": "User already exist"}
        )

    if isinstance(exc, UserNotAdminException):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "User has no admin privileges",
            },
        )

    if isinstance(exc, JWTError):
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Could not validate credentials",
            },
        )

    if isinstance(exc, ValidationError):
        return ORJSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "detail": "Could not validate credentials",
            },
        )

    if isinstance(exc, ProjectNotFoundException):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={
                "detail": "Project not found"}
        )

    if isinstance(exc, PermissionException):
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Not enough permissions",
            },
        )

    if isinstance(exc, IssueNotFoundException):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={
                "detail": "Issue not found"}
        )

    if isinstance(exc, ProjectRequiredException):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={
                "detail": "Project is required"}
        )
