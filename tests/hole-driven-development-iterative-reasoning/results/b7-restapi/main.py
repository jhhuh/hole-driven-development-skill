import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from storage import BookmarkStorage
from handlers import handle_create, handle_get, handle_list, handle_update, handle_delete

storage = BookmarkStorage()


class BookmarkHandler(BaseHTTPRequestHandler):

    def _route(self, method: str) -> None:
        path = self.path.rstrip("/")
        parts = path.split("/")
        # /bookmarks or /bookmarks/<id>
        if len(parts) < 2 or parts[1] != "bookmarks":
            self._respond(404, {"error": "not found"})
            return

        body = {}
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = json.loads(self.rfile.read(content_length))

        bookmark_id = int(parts[2]) if len(parts) == 3 else None
        request = {"id": bookmark_id, "body": body}

        if method == "POST" and len(parts) == 2:
            status, resp = handle_create(storage, request)
        elif method == "GET" and len(parts) == 2:
            status, resp = handle_list(storage, request)
        elif method == "GET" and bookmark_id is not None:
            status, resp = handle_get(storage, request)
        elif method == "PUT" and bookmark_id is not None:
            status, resp = handle_update(storage, request)
        elif method == "DELETE" and bookmark_id is not None:
            status, resp = handle_delete(storage, request)
        else:
            status, resp = 405, {"error": "method not allowed"}

        self._respond(status, resp)

    def _respond(self, status: int, body: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_DELETE(self):
        self._route("DELETE")


def main():
    server = HTTPServer(("", 8000), BookmarkHandler)
    print("Bookmark API running on http://localhost:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
