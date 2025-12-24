"""Data models for clipboard tool."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClipboardItem:
    """Clipboard item model."""
    id: str
    content: str
    content_hash: str
    created_at: datetime
    source_app: Optional[str] = None
    is_pinned: bool = False








