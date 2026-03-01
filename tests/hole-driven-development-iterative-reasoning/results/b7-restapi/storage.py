from models import Bookmark
from typing import Dict, List, Optional


class BookmarkStorage:
    """In-memory storage for bookmarks."""

    def __init__(self):
        self._bookmarks: Dict[int, Bookmark] = {}
        self._next_id: int = 1

    def create(self, url: str, title: str, tags: List[str]) -> Bookmark:
        """Create a new bookmark and return it."""
        bookmark = Bookmark(url=url, title=title, tags=tags, id=self._next_id)
        self._bookmarks[self._next_id] = bookmark
        self._next_id += 1
        return bookmark

    def get(self, bookmark_id: int) -> Optional[Bookmark]:
        """Return bookmark by id, or None if not found."""
        return self._bookmarks.get(bookmark_id)

    def list_all(self) -> List[Bookmark]:
        """Return all bookmarks."""
        return list(self._bookmarks.values())

    def update(self, bookmark_id: int, url: str = None, title: str = None, tags: List[str] = None) -> Optional[Bookmark]:
        """Update fields of an existing bookmark. Return updated bookmark or None."""
        bookmark = self._bookmarks.get(bookmark_id)
        if bookmark is None:
            return None
        if url is not None:
            bookmark.url = url
        if title is not None:
            bookmark.title = title
        if tags is not None:
            bookmark.tags = tags
        return bookmark

    def delete(self, bookmark_id: int) -> bool:
        """Delete bookmark by id. Return True if deleted, False if not found."""
        if bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            return True
        return False
