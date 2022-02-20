from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import ExceptionMiddleware

from test_project.api.auth import router as auth_router
from test_project.api.issue import router as issue_router
from test_project.api.project import router as project_router
from test_project.api.user import router as user_router
from test_project.core.exception_handler import custom_exception_handler
from test_project.core.settings import get_settings


def make_app() -> FastAPI:
    app = FastAPI()
    app.default_response_class = ORJSONResponse

    app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
    app.include_router(issue_router, prefix="/api/issue", tags=["Issue"])
    app.include_router(project_router, prefix="/api/project", tags=["Project"])
    app.include_router(user_router, prefix="/api/user", tags=["User"])

    @app.options("/{rest_of_path:path}", include_in_schema=False)
    async def preflight_handler(request: Request, rest_of_path: str) -> Response:
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = ", ".join(
            *app.state.settings.server.cors_origins
        )
        response.headers["Access-Control-Allow-Methods"] = ", ".join(
            *app.state.settings.server.cors_methods
        )
        response.headers["Access-Control-Allow-Headers"] = ", ".join(
            *app.state.settings.server.cors_headers
        )
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(Exception, custom_exception_handler)
    app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)

    return app


app = make_app()
