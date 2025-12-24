"""SQLite storage for clipboard history."""
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os

from tools.clipboard.models import ClipboardItem


class ClipboardStorage:
    """SQLite storage for clipboard items."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize storage with database path."""
        if db_path is None:
            # Use same directory as config store
            appdata = os.getenv("APPDATA")
            if not appdata:
                appdata = os.path.expanduser("~")
            data_dir = Path(appdata) / "StarterAppLauncher"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "clipboard.db"
        
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                source_app TEXT,
                is_pinned INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_items(created_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_items(content_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def add_text(self, content: str, source_app: Optional[str] = None) -> ClipboardItem:
        """Add text to clipboard history."""
        import uuid
        
        # Generate hash
        content_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()
        
        # Create item
        item_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        item = ClipboardItem(
            id=item_id,
            content=content,
            content_hash=content_hash,
            created_at=created_at,
            source_app=source_app,
            is_pinned=False
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clipboard_items (id, content, content_hash, created_at, source_app, is_pinned)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            item.content,
            item.content_hash,
            item.created_at.isoformat(),
            item.source_app,
            1 if item.is_pinned else 0
        ))
        
        conn.commit()
        conn.close()
        
        # Apply retention policy
        self._apply_retention()
        
        return item
    
    def list_recent(self, limit: int = 100) -> List[ClipboardItem]:
        """List recent clipboard items (newest first)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, content_hash, created_at, source_app, is_pinned
            FROM clipboard_items
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            try:
                # Parse datetime with error handling
                created_at_str = row['created_at']
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                    except ValueError:
                        # Try alternative format or use current time
                        try:
                            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()
                
                # Ensure content is not None
                content = row['content'] if row['content'] else ""
                
                items.append(ClipboardItem(
                    id=row['id'],
                    content=content,
                    content_hash=row['content_hash'] if row['content_hash'] else "",
                    created_at=created_at,
                    source_app=row['source_app'],
                    is_pinned=bool(row['is_pinned'])
                ))
            except Exception as e:
                print(f"Error parsing clipboard item {row.get('id', 'unknown')}: {e}")
                continue
        
        return items
    
    def list_grouped_by_day(self, days: int = 30) -> Dict[str, List[ClipboardItem]]:
        """List clipboard items grouped by date (YYYY-MM-DD)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, content_hash, created_at, source_app, is_pinned
            FROM clipboard_items
            WHERE created_at >= ?
            ORDER BY created_at DESC
        """, (cutoff_date.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        grouped: Dict[str, List[ClipboardItem]] = {}
        
        for row in rows:
            try:
                # Parse datetime with error handling
                created_at_str = row['created_at']
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                    except ValueError:
                        try:
                            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()
                
                date_key = created_at.strftime('%Y-%m-%d')
                
                if date_key not in grouped:
                    grouped[date_key] = []
                
                # Ensure content is not None
                content = row['content'] if row['content'] else ""
                
                grouped[date_key].append(ClipboardItem(
                    id=row['id'],
                    content=content,
                    content_hash=row['content_hash'] if row['content_hash'] else "",
                    created_at=created_at,
                    source_app=row['source_app'],
                    is_pinned=bool(row['is_pinned'])
                ))
            except Exception as e:
                print(f"Error parsing clipboard item {row.get('id', 'unknown')}: {e}")
                continue
        
        return grouped
    
    def clear_all(self):
        """Clear all clipboard items."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clipboard_items")
        
        conn.commit()
        conn.close()
    
    def delete_item(self, item_id: str):
        """Delete a specific clipboard item."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
        
        conn.commit()
        conn.close()
    
    def get_recent_hash(self, seconds: int = 3) -> Optional[str]:
        """Get the most recent content hash within the last N seconds."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=seconds)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content_hash
            FROM clipboard_items
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (cutoff_time.isoformat(),))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def check_hash_exists_in_hours(self, content_hash: str, hours: int = 3) -> bool:
        """Check if a content hash exists within the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM clipboard_items
            WHERE content_hash = ? AND created_at >= ?
        """, (content_hash, cutoff_time.isoformat()))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def _apply_retention(self, max_items: int = 500, max_days: int = 30):
        """Apply retention policy: keep max_items or max_days, whichever is more restrictive."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total items
        cursor.execute("SELECT COUNT(*) FROM clipboard_items")
        count = cursor.fetchone()[0]
        
        if count > max_items:
            # Delete oldest items
            cursor.execute("""
                DELETE FROM clipboard_items
                WHERE id IN (
                    SELECT id FROM clipboard_items
                    ORDER BY created_at ASC
                    LIMIT ?
                )
            """, (count - max_items,))
        
        # Delete items older than max_days
        cutoff_date = datetime.utcnow() - timedelta(days=max_days)
        cursor.execute("""
            DELETE FROM clipboard_items
            WHERE created_at < ?
        """, (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()





