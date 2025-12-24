"""Clipboard monitoring service."""
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QClipboard
from typing import Optional
import hashlib

from tools.clipboard.storage import ClipboardStorage


class ClipboardService(QObject):
    """Service for monitoring clipboard changes and storing items."""
    
    # Signal emitted when clipboard state changes (IDLE, RUNNING, PAUSED)
    clipboard_state_changed = Signal(str)
    # Signal emitted when a new item is added to storage
    item_added = Signal()
    
    def __init__(self, storage: ClipboardStorage, parent=None):
        """Initialize clipboard service."""
        super().__init__(parent)
        self.storage = storage
        self._state = "IDLE"  # IDLE, RUNNING, PAUSED
        self._clipboard = None
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._process_clipboard_change)
        self._pending_content = None
        self._last_hash = None
        self._ignore_next_change = False  # Flag to ignore next clipboard change
        
        # Get clipboard instance when QApplication is available
        app = QApplication.instance()
        if app:
            self._clipboard = app.clipboard()
    
    def get_state(self) -> str:
        """Get current service state."""
        return self._state
    
    def start_listening(self):
        """Start monitoring clipboard changes."""
        if self._state == "IDLE":
            # Ensure clipboard is initialized
            if not self._clipboard:
                app = QApplication.instance()
                if app:
                    self._clipboard = app.clipboard()
            
            self._set_state("RUNNING")
            if self._clipboard:
                self._clipboard.dataChanged.connect(self._on_clipboard_changed)
    
    def stop_listening(self):
        """Stop monitoring clipboard changes."""
        if self._state in ["RUNNING", "PAUSED"]:
            if self._clipboard:
                try:
                    self._clipboard.dataChanged.disconnect(self._on_clipboard_changed)
                except:
                    pass
            self._debounce_timer.stop()
            self._set_state("IDLE")
    
    def pause(self):
        """Pause clipboard monitoring."""
        if self._state == "RUNNING":
            if self._clipboard:
                try:
                    self._clipboard.dataChanged.disconnect(self._on_clipboard_changed)
                except:
                    pass
            self._debounce_timer.stop()
            self._set_state("PAUSED")
    
    def resume(self):
        """Resume clipboard monitoring."""
        if self._state == "PAUSED":
            # Ensure clipboard is initialized
            if not self._clipboard:
                app = QApplication.instance()
                if app:
                    self._clipboard = app.clipboard()
            
            self._set_state("RUNNING")
            if self._clipboard:
                self._clipboard.dataChanged.connect(self._on_clipboard_changed)
    
    def _set_state(self, new_state: str):
        """Set state and emit signal."""
        if self._state != new_state:
            self._state = new_state
            self.clipboard_state_changed.emit(new_state)
    
    def ignore_next_change(self):
        """Ignore the next clipboard change (used when copying from app)."""
        self._ignore_next_change = True
    
    def _on_clipboard_changed(self):
        """Handle clipboard change event (debounced)."""
        if self._state != "RUNNING":
            return
        
        # Check if we should ignore this change
        if self._ignore_next_change:
            self._ignore_next_change = False
            return
        
        # Get clipboard text
        if not self._clipboard:
            return
        
        try:
            text = self._clipboard.text()
        except:
            return
        
        # Validate text
        if not text or not text.strip():
            return
        
        # Check max length (10k chars)
        if len(text) > 10000:
            return
        
        # Debounce: wait 150ms before processing
        self._pending_content = text.strip()
        self._debounce_timer.start(150)
    
    def _process_clipboard_change(self):
        """Process clipboard change after debounce."""
        if not self._pending_content:
            return
        
        content = self._pending_content
        self._pending_content = None
        
        # Calculate hash
        content_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()
        
        # Check for duplicate (within last 3 hours)
        # If same content exists in the last 3 hours, don't save again
        if self.storage.check_hash_exists_in_hours(content_hash, hours=3):
            # Duplicate detected, ignore
            return
        
        # Store the item
        try:
            self.storage.add_text(content)
            self._last_hash = content_hash
            # Emit signal to notify that a new item was added
            self.item_added.emit()
        except Exception as e:
            # Log error but don't crash
            print(f"Error storing clipboard item: {e}")
