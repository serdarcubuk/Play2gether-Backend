from typing import Any, Callable

from fastapi import APIRouter
from fastapi.types import DecoratedCallable
from starlette.datastructures import MutableHeaders
from starlette.websockets import WebSocket


class WebSocketMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            websocket = WebSocket(scope=scope, receive=receive, send=send)
            headers = MutableHeaders(scope=scope)
            headers["Authorization"] = websocket.query_params.get(
                "Authorization", websocket.query_params.get("authorization", "")
            )

        await self.app(scope, receive, send)


class CustomAPIRouter(APIRouter):
    """https://github.com/tiangolo/fastapi/issues/2060#issuecomment-834868906"""

    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        if path.endswith("/"):
            path = path[:-1]

        add_path = super().api_route(
            path, include_in_schema=include_in_schema, **kwargs
        )

        alternate_path = path + "/"
        add_alternate_path = super().api_route(
            alternate_path, include_in_schema=False, **kwargs
        )

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            add_alternate_path(func)
            return add_path(func)

        return decorator
