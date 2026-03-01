from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Bookmark:
    url: str
    title: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    id: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }
