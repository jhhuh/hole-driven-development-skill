from models import Bookmark


class BookmarkStore:
    def __init__(self):
        self._bookmarks: dict[int, Bookmark] = {}
        self._next_id = 1

    def create(self, bookmark: Bookmark) -> Bookmark:
        bookmark.id = self._next_id
        self._next_id += 1
        self._bookmarks[bookmark.id] = bookmark
        return bookmark

    def get_all(self) -> list[Bookmark]:
        return list(self._bookmarks.values())

    def get(self, bookmark_id: int) -> Bookmark | None:
        return self._bookmarks.get(bookmark_id)

    def delete(self, bookmark_id: int) -> bool:
        if bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            return True
        return False
