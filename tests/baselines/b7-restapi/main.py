from http.server import HTTPServer

from handlers import BookmarkHandler
from storage import BookmarkStore


def main(host="localhost", port=8000):
    store = BookmarkStore()
    BookmarkHandler.store = store

    server = HTTPServer((host, port), BookmarkHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
