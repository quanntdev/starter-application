"""Mini window for clipboard tool."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFontMetrics
import qtawesome as qta
from datetime import datetime
from typing import Optional

from tools.clipboard.clipboard_service import ClipboardService
from tools.clipboard.storage import ClipboardStorage
from tools.clipboard.models import ClipboardItem


class ClipboardMiniWindow(QWidget):
    """Mini floating window for clipboard history."""
    
    # Signal emitted when user requests to view details
    view_details_requested = Signal()
    # Signal emitted when window is closed
    window_closed = Signal()
    
    def __init__(self, service: ClipboardService, storage: ClipboardStorage, parent=None):
        """Initialize mini window."""
        super().__init__(parent)
        self.service = service
        self.storage = storage
        self._current_state = "IDLE"
        
        self.init_ui()
        self.refresh_recent_items()
        
        # Connect service signals to refresh list
        # Note: We'll need to add a signal to ClipboardService for new items
        
    def init_ui(self):
        """Initialize window UI."""
        # Window properties
        self.setWindowTitle("Clipboard")
        self.setMinimumSize(320, 400)
        self.resize(340, 600)
        
        # Position at left edge, centered vertically
        screen = self.screen().availableGeometry()
        self.move(0, (screen.height() - self.height()) // 2)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Recent items (no tabs, direct display)
        recent_widget = self._create_recent_tab()
        main_layout.addWidget(recent_widget, 1)
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
        """)
    
    def _create_header(self) -> QWidget:
        """Create header with title, status, and buttons."""
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel("Clipboard")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
        """)
        layout.addWidget(title_label)
        
        # Status pill
        self.status_label = QLabel("Listening")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(25, 135, 84, 0.2);
                color: #20c997;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Copy message (hidden by default)
        self.copy_message_label = QLabel("Copied!")
        self.copy_message_label.setStyleSheet("""
            QLabel {
                background-color: rgba(74, 158, 255, 0.2);
                color: #4a9eff;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
            }
        """)
        self.copy_message_label.hide()  # Hidden by default
        layout.addWidget(self.copy_message_label)
        
        layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton()
        clear_btn.setIcon(qta.icon('fa5s.trash', color='#888'))
        clear_btn.setToolTip("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        clear_btn.clicked.connect(self.on_clear_all)
        layout.addWidget(clear_btn)
        
        # Details button
        details_btn = QPushButton()
        details_btn.setIcon(qta.icon('fa5s.external-link-alt', color='#4a9eff'))
        details_btn.setToolTip("View Details")
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(74, 158, 255, 0.1);
            }
        """)
        details_btn.clicked.connect(self.on_view_details)
        layout.addWidget(details_btn)
        
        return header
    
    def _create_recent_tab(self) -> QWidget:
        """Create recent items tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.setCursor(Qt.CursorShape.PointingHandCursor)  # Pointer cursor for list
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                padding: 8px;
                min-height: 50px;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background-color: rgba(74, 158, 255, 0.15);
            }
        """)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.list_widget)
        
        return widget
    
    def refresh_recent_items(self):
        """Refresh the recent items list."""
        self.list_widget.clear()
        
        try:
            items = self.storage.list_recent(limit=50)
        except Exception as e:
            print(f"Error loading clipboard items: {e}")
            empty_item = QListWidgetItem("Error loading items")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            empty_item.setForeground(QColor("#888"))
            self.list_widget.addItem(empty_item)
            return
        
        if not items:
            # Empty state
            empty_item = QListWidgetItem("No clipboard items yet")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            empty_item.setForeground(QColor("#888"))
            self.list_widget.addItem(empty_item)
            return
        
        for item in items:
            try:
                # Skip invalid items (but allow empty content)
                if not item or not hasattr(item, 'content'):
                    continue
                
                list_item = QListWidgetItem()
                item_widget = self._create_item_widget(item)
                # Set minimum size hint to ensure consistent item height for short items
                size_hint = item_widget.sizeHint()
                size_hint.setHeight(max(50, size_hint.height()))  # Minimum 50px height
                list_item.setSizeHint(size_hint)
                self.list_widget.addItem(list_item)
                self.list_widget.setItemWidget(list_item, item_widget)
            except Exception as e:
                print(f"Error creating widget for item {getattr(item, 'id', 'unknown')}: {e}")
                continue
    
    def resizeEvent(self, event):
        """Handle window resize to refresh items with new width."""
        super().resizeEvent(event)
        # Refresh items to recalculate width
        if hasattr(self, 'list_widget') and self.list_widget.count() > 0:
            self.refresh_recent_items()
    
    def _create_item_widget(self, item: ClipboardItem) -> QWidget:
        """Create widget for a clipboard item."""
        widget = QWidget()
        # Set minimum height to ensure consistent item size
        widget.setMinimumHeight(50)
        # Set pointer cursor when hovering over item
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Validate and sanitize content
        content = item.content if item.content else ""
        # Remove null bytes and control characters that might cause display issues
        content = content.replace('\x00', '').replace('\r', '')
        # Store sanitized content
        widget.item_content = content
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Content (single line, truncated with ellipsis)
        # Calculate available width: window width - list padding - item padding - scrollbar
        available_width = max(200, self.width() - 50)  # Minimum 200px, account for padding and scrollbar
        
        content_label = QLabel()
        content_label.setWordWrap(False)  # No word wrap - single line only
        content_label.setMinimumHeight(20)  # Ensure minimum height for short items
        content_label.setMaximumHeight(20)  # Single line only
        content_label.setMaximumWidth(available_width - 16)  # Account for widget padding
        content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        # Show full content in tooltip (sanitized)
        if content:
            content_label.setToolTip(content)
        else:
            content_label.setToolTip("(Empty)")
        
        # Truncate text to single line with ellipsis
        font_metrics = QFontMetrics(content_label.font())
        max_width = available_width - 16
        
        if content:
            # Use QFontMetrics to calculate exact text width and add ellipsis
            elided_text = font_metrics.elidedText(content, Qt.TextElideMode.ElideRight, max_width)
            content_label.setText(elided_text)
        else:
            content_label.setText("(Empty)")
        
        layout.addWidget(content_label)
        
        # Timestamp with error handling
        try:
            if item.created_at and hasattr(item.created_at, 'strftime'):
                time_str = item.created_at.strftime("%H:%M:%S")
            else:
                time_str = "??:??:??"
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Error formatting timestamp: {e}, type: {type(item.created_at)}")
            time_str = "??:??:??"
        
        time_label = QLabel(time_str)
        time_label.setMinimumHeight(14)  # Ensure minimum height
        time_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10px;
            }
        """)
        layout.addWidget(time_label)
        
        return widget
    
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click - copy to clipboard."""
        widget = self.list_widget.itemWidget(item)
        if widget and hasattr(widget, 'item_content'):
            # Highlight the clicked item
            self.list_widget.setCurrentItem(item)
            
            # Ignore next clipboard change to prevent duplicate entry
            if self.service:
                self.service.ignore_next_change()
            
            # Copy to clipboard
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.clipboard().setText(widget.item_content)
            
            # Show copy message
            self.copy_message_label.show()
            # Hide message after 2 seconds
            QTimer.singleShot(2000, lambda: self.copy_message_label.hide())
            
            # Clear selection after a short delay for visual feedback
            QTimer.singleShot(300, lambda: self.list_widget.clearSelection())
    
    def on_clear_all(self):
        """Handle clear all action."""
        self.storage.clear_all()
        self.refresh_recent_items()
    
    def on_view_details(self):
        """Handle view details action."""
        self.view_details_requested.emit()
    
    def update_status(self, state: str):
        """Update status display based on service state."""
        self._current_state = state
        
        if state == "RUNNING":
            self.status_label.setText("Listening")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(25, 135, 84, 0.2);
                    color: #20c997;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """)
        elif state == "PAUSED":
            self.status_label.setText("Paused")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(128, 128, 128, 0.2);
                    color: #888;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """)
        else:  # IDLE
            self.status_label.setText("Idle")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(128, 128, 128, 0.2);
                    color: #888;
                    padding: 4px 10px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }
            """)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Emit signal to notify that window is closing
        self.window_closed.emit()
        super().closeEvent(event)
