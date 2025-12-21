"""Tool item widget component."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
import qtawesome as qta

from models.config_models import Tool


class ToolItemWidget(QWidget):
    """Widget for displaying a single tool item."""
    
    def __init__(self, tool: Tool, translator, on_use_callback=None, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.translator = translator
        self.on_use_callback = on_use_callback
        self.setObjectName("toolItem")
        self._hovered = False
        self.setMinimumHeight(160)
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
        """Paint custom card with subtle shadow and border."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Card rectangle
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Draw subtle shadow (only on hover)
        if self._hovered:
            shadow_color = QColor(0, 0, 0, 60)
            shadow_rect = rect.adjusted(0, 2, 0, 2)
            painter.fillRect(shadow_rect, shadow_color)
        
        # Draw card background (slightly darker than page background)
        painter.setBrush(QBrush(QColor(28, 28, 28)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 12, 12)
        
        # Draw subtle border
        border_color = QColor(74, 158, 255, 100) if self._hovered else QColor(255, 255, 255, 10)
        pen = QPen(border_color, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 12, 12)
        
        super().paintEvent(event)
    
    def init_ui(self):
        """Initialize tool item UI."""
        # Transparent background - we'll draw it in paintEvent
        self.setStyleSheet("""
            #toolItem {
                background-color: transparent;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(0)
        
        # Header Row: Icon + Title | FREE + Run Button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # Left: Icon + Title
        left_section = QHBoxLayout()
        left_section.setContentsMargins(0, 0, 0, 0)
        left_section.setSpacing(12)
        
        # Icon container (subtle, not too bright, smaller)
        icon_container = QWidget()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon = qta.icon(self.tool.icon, color='#4a9eff')
        icon_label.setPixmap(icon.pixmap(20, 20))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        left_section.addWidget(icon_container)
        
        # Title
        self.name_label = QLabel(self.tool.name)
        self.name_label.setStyleSheet("""
            font-size: 17px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.2px;
        """)
        left_section.addWidget(self.name_label)
        left_section.addStretch()
        
        header_layout.addLayout(left_section, 1)
        
        # Right: FREE badge + Run button (aligned vertically center)
        right_section = QHBoxLayout()
        right_section.setContentsMargins(0, 0, 0, 0)
        right_section.setSpacing(8)
        right_section.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # FREE badge (smaller, quieter)
        free_tag = QLabel("FREE")
        free_tag.setObjectName("freeTag")
        free_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        free_tag.setStyleSheet("""
            #freeTag {
                background-color: rgba(25, 135, 84, 0.15);
                color: #20c997;
                padding: 3px 8px;
                border-radius: 8px;
                font-size: 9px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border: 1px solid rgba(25, 135, 84, 0.3);
            }
        """)
        right_section.addWidget(free_tag)
        
        # Run button with text
        self.use_button = QPushButton(self.translator.t("tools.run"))
        self.use_button.setIcon(qta.icon('fa5s.play-circle', color='white'))
        self.use_button.setToolTip(self.translator.t("tools.use_tool"))
        self.use_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.use_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5ab0ff;
                border-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: #3a8eef;
            }
        """)
        if self.on_use_callback:
            self.use_button.clicked.connect(lambda: self.on_use_callback(self.tool))
        right_section.addWidget(self.use_button)
        
        header_layout.addLayout(right_section)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(12)
        
        # Status badge row (if needed)
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("statusBadge")
        self.update_status()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        main_layout.addLayout(status_layout)
        main_layout.addSpacing(12)
        
        # Tags row
        if self.tool.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(8)
            
            for tag in self.tool.tags:
                tag_label = QLabel(tag)
                tag_label.setObjectName("toolTag")
                tag_label.setStyleSheet("""
                    #toolTag {
                        background-color: #1f1f1f;
                        color: #b0b0b0;
                        padding: 6px 10px;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 500;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                    }
                """)
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
            main_layout.addSpacing(12)
        
        # Description (plain text, no box)
        if self.tool.description:
            self.desc_label = QLabel(self.tool.description)
            self.desc_label.setStyleSheet("""
                font-size: 13px;
                color: #a0a0a0;
                line-height: 1.5;
                padding: 0px;
            """)
            self.desc_label.setWordWrap(True)
            self.desc_label.setMaximumHeight(40)  # ~2 lines max
            main_layout.addWidget(self.desc_label)
        
        main_layout.addStretch()
    
    def update_status(self):
        """Update status badge with text only."""
        if self.tool.status == "active":
            color = "#20c997"
            bg_color = "rgba(32, 201, 151, 0.15)"
            border_color = "rgba(32, 201, 151, 0.3)"
            text = "ACTIVE"
        else:
            color = "#6c757d"
            bg_color = "rgba(108, 117, 125, 0.15)"
            border_color = "rgba(108, 117, 125, 0.3)"
            text = "INACTIVE"
        
        # Create status label with text only (no dot icon)
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            #statusBadge {{
                background-color: {bg_color};
                color: {color};
                padding: 4px 10px;
                border-radius: 8px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border: 1px solid {border_color};
                max-width: fit-content;
            }}
        """)
