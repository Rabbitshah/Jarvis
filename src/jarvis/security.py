"""Host and Origin checks for the local API. Stops DNS rebinding and cross-site POSTs from a web page
open in your browser. This is NOT authentication: anyone who can run a command on this machine can still call the API."""
from __future__ import annotations

from urllib.parse import urlsplit

from starlette.responses import JSONResponse

CHANGING = {"POST", "PUT", "PATCH", "DELETE"}


class LocalOnly:
    """Pure ASGI (not BaseHTTPMiddleware) so the SSE stream is not buffered."""

    def __init__(self, app, port: int, extra_origins: tuple[str, ...] = ()) -> None:
        self.app = app
        self.origins = {f"http://{h}:{port}" for h in ("127.0.0.1", "localhost", "[::1]")}
        self.origins |= {o.strip().rstrip("/").lower() for o in extra_origins if o.strip()}
        self.hosts = {urlsplit(o).netloc for o in self.origins}  # an origin you trust also brings its own Host (Vite dev)

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}
            problem = None
            if headers.get("host", "").lower() not in self.hosts:
                problem = "host not allowed"
            elif scope["method"] in CHANGING and "origin" in headers and headers["origin"].rstrip("/").lower() not in self.origins:
                problem = "origin not allowed"
            if problem:
                await JSONResponse({"error": problem}, status_code=403)(scope, receive, send)
                return
        await self.app(scope, receive, send)
