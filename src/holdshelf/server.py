"""Local hold-shelf page and API. The standard library is the only dependency."""

from __future__ import annotations

import json
import re
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, unquote, urlparse

from holdshelf.catalog import Catalog

STATIC = Path(__file__).resolve().parent / "static" / "index.html"
HOST = "127.0.0.1"
PORT = 8765
BAD_WINDOW_MESSAGE = "windowDays must be a whole number of days from 1 to 3650."


class BadWindowError(ValueError):
    def __init__(self) -> None:
        super().__init__(BAD_WINDOW_MESSAGE)


def parse_window_days(raw: list[str] | None) -> int:
    if raw is None or len(raw) == 0:
        return 7
    if len(raw) != 1:
        raise BadWindowError()
    value = raw[0]
    if re.fullmatch(r"[0-9]+", value) is None:
        raise BadWindowError()
    try:
        days = int(value)
    except ValueError:
        raise BadWindowError() from None
    if days < 1 or days > 3650:
        raise BadWindowError()
    return days


class ShelfApp:
    def __init__(
        self,
        catalog: Catalog | None = None,
        *,
        today: Callable[[], date] | None = None,
    ) -> None:
        self.catalog = catalog if catalog is not None else Catalog()
        self.today = today if today is not None else date.today

    def handle(self, method: str, target: str) -> tuple[int, object]:
        path = unquote(urlparse(target).path)
        if method == "GET" and path == "/api/health":
            return 200, {"status": "ok"}
        if method == "GET" and path == "/api/holds":
            return 200, {"holds": self.catalog.list_holds()}
        if method == "POST" and path.startswith("/api/holds/") and path.endswith("/pickup"):
            hold_id = path.removeprefix("/api/holds/").removesuffix("/pickup").strip("/")
            return self._pickup(hold_id)
        if method == "GET" and path == "/":
            return 200, STATIC.read_text(encoding="utf-8")
        if method == "GET" and path == "/api/holds/overdue":
            query = parse_qs(urlparse(target).query, keep_blank_values=True)
            try:
                window = parse_window_days(query.get("windowDays"))
            except BadWindowError:
                return 400, {"error": BAD_WINDOW_MESSAGE}
            return 200, {
                "windowDays": window,
                "holds": self.catalog.list_overdue(window, self.today()),
            }
        return 404, {"error": "That page or hold was not found."}

    def _pickup(self, hold_id: str) -> tuple[int, dict]:
        if not hold_id:
            return 400, {"error": "A hold id is required."}
        outcome, hold = self.catalog.mark_picked_up(hold_id)
        if outcome == "missing":
            return 404, {"error": f"Hold {hold_id} was not found."}
        if outcome == "already":
            return 409, {"error": f"Hold {hold_id} is already picked up."}
        return 200, {"hold": hold}


def serve(host: str = HOST, port: int = PORT, catalog: Catalog | None = None) -> None:
    app = ShelfApp(catalog)
    handler = _handler_for(app)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Hold shelf at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _handler_for(app: ShelfApp):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self._respond()

        def do_POST(self) -> None:  # noqa: N802
            self._respond()

        def _respond(self) -> None:
            status, payload = app.handle(self.command, self.path)
            if isinstance(payload, str):
                body = payload.encode("utf-8")
                content_type = "text/html; charset=utf-8"
            else:
                body = json.dumps(payload).encode("utf-8")
                content_type = "application/json"
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    return Handler
