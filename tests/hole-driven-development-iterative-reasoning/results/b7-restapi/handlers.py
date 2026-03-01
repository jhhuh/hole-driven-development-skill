from storage import BookmarkStorage

# All handlers take a storage instance and a request dict,
# and return (status_code: int, response_body: dict).

def handle_create(storage: BookmarkStorage, request: dict) -> tuple:
    """Create a bookmark from request body {url, title, tags}."""
    body = request.get("body", {})
    url = body.get("url", "")
    title = body.get("title", "")
    tags = body.get("tags", [])
    if not url:
        return 400, {"error": "url is required"}
    bookmark = storage.create(url=url, title=title, tags=tags)
    return 201, bookmark.to_dict()


def handle_get(storage: BookmarkStorage, request: dict) -> tuple:
    """Get a bookmark by id from request {id}."""
    bookmark_id = request.get("id")
    bookmark = storage.get(bookmark_id)
    if bookmark is None:
        return 404, {"error": "not found"}
    return 200, bookmark.to_dict()


def handle_list(storage: BookmarkStorage, request: dict) -> tuple:
    """List all bookmarks."""
    bookmarks = storage.list_all()
    return 200, {"bookmarks": [b.to_dict() for b in bookmarks]}


def handle_update(storage: BookmarkStorage, request: dict) -> tuple:
    """Update a bookmark from request {id, ...fields}."""
    bookmark_id = request.get("id")
    body = request.get("body", {})
    bookmark = storage.update(
        bookmark_id,
        url=body.get("url"),
        title=body.get("title"),
        tags=body.get("tags"),
    )
    if bookmark is None:
        return 404, {"error": "not found"}
    return 200, bookmark.to_dict()


def handle_delete(storage: BookmarkStorage, request: dict) -> tuple:
    """Delete a bookmark by id from request {id}."""
    bookmark_id = request.get("id")
    if storage.delete(bookmark_id):
        return 204, {}
    return 404, {"error": "not found"}
