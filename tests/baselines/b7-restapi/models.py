from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Bookmark:
    url: str
    title: str
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    id: int | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "tags": self.tags,
            "created_at": self.created_at,
        }
