"""Clipboard history detail page."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QClipboard, QPainter, QColor, QBrush
import qtawesome as qta
from datetime import datetime

from tools.clipboard.storage import ClipboardStorage
from tools.clipboard.models import ClipboardItem


class ClipboardItemDetailWidget(QWidget):
    """Widget for displaying a clipboard item in detail page."""
    
    def __init__(self, item: ClipboardItem, on_copy=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.item = item
        self.on_copy = on_copy
        self.on_delete = on_delete
        self._hovered = False
        self.init_ui()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self._hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self._hovered = False
        self.update()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Paint item with hover effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Background on hover
        if self._hovered:
            painter.setBrush(QBrush(QColor(40, 40, 40)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
        
        super().paintEvent(event)
    
    def init_ui(self):
        """Initialize item UI."""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Content (multi-line with word wrap)
        self.content_label = QLabel(self.item.content)
        self.content_label.setWordWrap(True)
        # Allow label to expand vertically to show all content
        self.content_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Minimum
        )
        # Set maximum width to prevent horizontal overflow
        # Will be adjusted in resizeEvent based on parent width
        self.content_label.setMaximumWidth(2000)  # Large enough, will be constrained by parent
        self.content_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        # Always show full content on hover
        self.content_label.setToolTip(self.item.content)
        layout.addWidget(self.content_label)
        
        # Footer: Time + Actions
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(12)
        
        # Timestamp
        time_str = self.item.created_at.strftime("%Y-%m-%d %H:%M:%S")
        time_label = QLabel(time_str)
        time_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 11px;
            }
        """)
        footer_layout.addWidget(time_label)
        
        footer_layout.addStretch()
        
        # Copy button
        copy_btn = QPushButton()
        copy_btn.setIcon(qta.icon('fa5s.copy', color='#4a9eff'))
        copy_btn.setToolTip("Copy")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(74, 158, 255, 0.3);
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(74, 158, 255, 0.1);
                border-color: #4a9eff;
            }
        """)
        copy_btn.clicked.connect(lambda: self.on_copy(self.item) if self.on_copy else None)
        footer_layout.addWidget(copy_btn)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(qta.icon('fa5s.trash', color='#dc3545'))
        delete_btn.setToolTip("Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(220, 53, 69, 0.3);
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 0.1);
                border-color: #dc3545;
            }
        """)
        delete_btn.clicked.connect(lambda: self.on_delete(self.item) if self.on_delete else None)
        footer_layout.addWidget(delete_btn)
        
        layout.addLayout(footer_layout)
    
    def resizeEvent(self, event):
        """Handle widget resize to adjust content label width."""
        super().resizeEvent(event)
        # Update content label maximum width based on available space
        # Account for padding: 16px left + 16px right = 32px
        available_width = self.width() - 32
        if available_width > 0 and hasattr(self, 'content_label'):
            self.content_label.setMaximumWidth(available_width)


class ClipboardHistoryPage(QWidget):
    """Clipboard history detail page."""
    
    def __init__(self, storage: ClipboardStorage, translator, clipboard_service=None, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.translator = translator
        self.clipboard_service = clipboard_service  # Optional clipboard service to ignore changes when copying
        self.all_items = []  # Store all items for filtering
        self.init_ui()
        self.refresh_content()
    
    def init_ui(self):
        """Initialize page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Clipboard History")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.5px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Clear All button
        clear_btn = QPushButton("Clear All")
        clear_btn.setIcon(qta.icon('fa5s.trash', color='white'))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """)
        clear_btn.clicked.connect(self.on_clear_all)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(24)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clipboard items...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        layout.addSpacing(16)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll, 1)
    
    def refresh_content(self):
        """Refresh page content with all items (no grouping)."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get all items (no grouping)
        self.all_items = self.storage.list_recent(limit=500)
        
        # Apply search filter if any
        search_query = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        filtered_items = self.all_items
        if search_query:
            filtered_items = [item for item in self.all_items if search_query in item.content.lower()]
        
        if not filtered_items:
            # Empty state - display as normal item
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.setContentsMargins(16, 12, 16, 12)
            empty_layout.setSpacing(8)
            
            text_label = QLabel("No clipboard items found." if search_query else "No clipboard items yet. Click Run to start.")
            text_label.setStyleSheet("""
                QLabel {
                    color: #888;
                    font-size: 13px;
                }
            """)
            empty_layout.addWidget(text_label)
            
            self.content_layout.addWidget(empty_widget)
            return
        
        # Display items with separators
        for i, item in enumerate(filtered_items):
            item_widget = ClipboardItemDetailWidget(
                item,
                on_copy=self.on_copy_item,
                on_delete=self.on_delete_item
            )
            self.content_layout.addWidget(item_widget)
            
            # Add separator line between items (except after last item)
            if i < len(filtered_items) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.1);
                        border: none;
                        max-height: 1px;
                    }
                """)
                self.content_layout.addWidget(separator)
        
        self.content_layout.addStretch()
    
    def on_search_changed(self, text):
        """Handle search input change."""
        self.refresh_content()
    
    def on_copy_item(self, item: ClipboardItem):
        """Handle copy item action."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            # Ignore next clipboard change to prevent duplicate entry
            if self.clipboard_service:
                self.clipboard_service.ignore_next_change()
            app.clipboard().setText(item.content)
            # TODO: Show toast notification
    
    def on_delete_item(self, item: ClipboardItem):
        """Handle delete item action."""
        self.storage.delete_item(item.id)
        self.refresh_content()
    
    def on_clear_all(self):
        """Handle clear all action."""
        self.storage.clear_all()
        self.refresh_content()

