import uvicorn

from test_project.core.settings import get_settings

if __name__ == '__main__':
    uvicorn.run(
        'test_project:app',
        host=get_settings().server.host,
        port=get_settings().server.port,
        reload=True
    )
