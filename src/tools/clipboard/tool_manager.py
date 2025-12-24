"""Tool manager for clipboard tool."""
from PySide6.QtCore import QObject, Signal

from tools.clipboard.clipboard_service import ClipboardService
from tools.clipboard.storage import ClipboardStorage
from tools.clipboard.mini_window import ClipboardMiniWindow


class ClipboardToolManager(QObject):
    """Manager for clipboard tool state and UI."""
    
    # Signals
    state_changed = Signal(str)  # IDLE, RUNNING, PAUSED
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = ClipboardStorage()
        self.service = ClipboardService(self.storage)
        self.mini_window: ClipboardMiniWindow = None
        
        # Connect service signals
        self.service.clipboard_state_changed.connect(self._on_service_state_changed)
    
    def start(self):
        """Start the clipboard tool (Run)."""
        if self.service.get_state() == "IDLE":
            self.service.start_listening()
            self._show_mini_window()
        elif self.service.get_state() == "PAUSED":
            self.service.resume()
            if not self.mini_window or not self.mini_window.isVisible():
                self._show_mini_window()
    
    def pause(self):
        """Pause the clipboard tool."""
        if self.service.get_state() == "RUNNING":
            self.service.pause()
            # Hide mini window when pausing (don't close to avoid stopping service)
            if self.mini_window:
                self.mini_window.hide()
    
    def stop(self):
        """Stop the clipboard tool."""
        self.service.stop_listening()
        if self.mini_window:
            self.mini_window.close()
    
    def get_state(self) -> str:
        """Get current tool state."""
        return self.service.get_state()
    
    def _show_mini_window(self):
        """Show or create mini window."""
        if not self.mini_window:
            self.mini_window = ClipboardMiniWindow(self.service, self.storage)
            self.mini_window.view_details_requested.connect(self._on_view_details_requested)
            self.mini_window.window_closed.connect(self._on_mini_window_closed)
            self.service.clipboard_state_changed.connect(self.mini_window.update_status)
            # Connect item_added signal to refresh mini window list
            self.service.item_added.connect(self.mini_window.refresh_recent_items)
        
        if not self.mini_window.isVisible():
            self.mini_window.show()
        
        # Update status
        self.mini_window.update_status(self.service.get_state())
    
    def _on_mini_window_closed(self):
        """Handle mini window close event."""
        # When window is closed, stop the service so button shows "Run"
        if self.service.get_state() in ["RUNNING", "PAUSED"]:
            self.service.stop_listening()
        # Clear reference to allow recreation
        self.mini_window = None
    
    def _on_view_details_requested(self):
        """Handle view details request from mini window."""
        self.view_details_requested.emit()
    
    def _on_service_state_changed(self, state: str):
        """Handle service state change."""
        self.state_changed.emit(state)
        if self.mini_window:
            self.mini_window.update_status(state)
    
    # Signal for view details (will be connected externally)
    view_details_requested = Signal()





