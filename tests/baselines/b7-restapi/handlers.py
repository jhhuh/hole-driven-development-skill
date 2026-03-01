import json
from http.server import BaseHTTPRequestHandler

from models import Bookmark
from storage import BookmarkStore


class BookmarkHandler(BaseHTTPRequestHandler):
    store: BookmarkStore

    def _send_json(self, status: int, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        return json.loads(raw)

    def _parse_path(self) -> tuple[str, int | None]:
        """Returns (resource, id_or_none)."""
        parts = [p for p in self.path.split("/") if p]
        if len(parts) == 1:
            return parts[0], None
        if len(parts) == 2:
            return parts[0], int(parts[1])
        return "", None

    def do_GET(self):
        resource, bookmark_id = self._parse_path()
        if resource != "bookmarks":
            self._send_json(404, {"error": "not found"})
            return

        if bookmark_id is None:
            bookmarks = self.store.get_all()
            self._send_json(200, [b.to_dict() for b in bookmarks])
        else:
            bookmark = self.store.get(bookmark_id)
            if bookmark is None:
                self._send_json(404, {"error": "not found"})
            else:
                self._send_json(200, bookmark.to_dict())

    def do_POST(self):
        resource, _ = self._parse_path()
        if resource != "bookmarks":
            self._send_json(404, {"error": "not found"})
            return

        data = self._read_body()
        bookmark = Bookmark(
            url=data["url"],
            title=data["title"],
            tags=data.get("tags", []),
        )
        created = self.store.create(bookmark)
        self._send_json(201, created.to_dict())

    def do_DELETE(self):
        resource, bookmark_id = self._parse_path()
        if resource != "bookmarks" or bookmark_id is None:
            self._send_json(404, {"error": "not found"})
            return

        if self.store.delete(bookmark_id):
            self._send_json(200, {"deleted": bookmark_id})
        else:
            self._send_json(404, {"error": "not found"})
