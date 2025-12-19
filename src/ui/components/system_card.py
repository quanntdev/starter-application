"""System metric card component for Dashboard."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
import qtawesome as qta


class SystemCardWidget(QWidget):
    """Card widget displaying a system metric with status indicator."""
    
    def __init__(self, title: str, icon_name: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_name = icon_name
        self.value = ""
        self.subtitle = ""
        self.status = "normal"  # normal, warning, critical
        self.init_ui()
    
    def init_ui(self):
        """Initialize card UI."""
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
        self.setObjectName("systemCard")
        
        # Card styling
        self.setStyleSheet("""
            #systemCard {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Top row: Icon and Status badge
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        icon_label = QLabel()
        icon = qta.icon(self.icon_name, color='#e0e0e0')
        icon_label.setPixmap(icon.pixmap(24, 24))
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        # Status badge
        self.status_label = QLabel()
        self.status_label.setObjectName("statusBadge")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            #statusBadge {
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
            }
        """)
        top_layout.addWidget(self.status_label)
        
        layout.addLayout(top_layout)
        
        # Value (large)
        self.value_label = QLabel("--")
        self.value_label.setObjectName("valueLabel")
        self.value_label.setStyleSheet("""
            #valueLabel {
                font-size: 28px;
                font-weight: 700;
                color: #e0e0e0;
                background: transparent;
            }
        """)
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setStyleSheet("""
            #subtitleLabel {
                font-size: 12px;
                color: #a0a0a0;
                background: transparent;
            }
        """)
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
    
    def set_value(self, value: str, subtitle: str = "", status: str = "normal"):
        """Update card value, subtitle, and status."""
        self.value = value
        self.subtitle = subtitle
        self.status = status
        
        self.value_label.setText(value)
        self.value_label.show()  # Force visible
        self.value_label.update()  # Force repaint
        
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.show()
        self.subtitle_label.update()
        
        # Update status badge
        status_colors = {
            "normal": ("#198754", "Normal"),
            "warning": ("#ffc107", "Warning"),
            "critical": ("#dc3545", "Critical")
        }
        
        color, text = status_colors.get(status, ("#6c757d", "Unknown"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            #statusBadge {{
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                background-color: {color}20;
                color: {color};
                border: 1px solid {color}40;
            }}
        """)
    
    def paintEvent(self, event):
        """Paint subtle glow effect based on status."""
        super().paintEvent(event)
        
        if self.status == "normal":
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw subtle glow
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        if self.status == "warning":
            pen = QPen(QColor("#ffc107"), 2)
        elif self.status == "critical":
            pen = QPen(QColor("#dc3545"), 2)
        else:
            return
        
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 10, 10)


class SkeletonCardWidget(QWidget):
    """Skeleton loading card for Dashboard."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize skeleton UI."""
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Top row skeleton
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_skeleton = QLabel()
        icon_skeleton.setFixedSize(24, 24)
        icon_skeleton.setStyleSheet("background-color: #333333; border-radius: 4px;")
        top_layout.addWidget(icon_skeleton)
        
        top_layout.addStretch()
        
        badge_skeleton = QLabel()
        badge_skeleton.setFixedSize(60, 20)
        badge_skeleton.setStyleSheet("background-color: #333333; border-radius: 10px;")
        top_layout.addWidget(badge_skeleton)
        
        layout.addLayout(top_layout)
        
        # Value skeleton
        value_skeleton = QLabel()
        value_skeleton.setFixedHeight(32)
        value_skeleton.setStyleSheet("background-color: #333333; border-radius: 4px;")
        layout.addWidget(value_skeleton)
        
        # Subtitle skeleton
        subtitle_skeleton = QLabel()
        subtitle_skeleton.setFixedHeight(16)
        subtitle_skeleton.setStyleSheet("background-color: #333333; border-radius: 4px;")
        layout.addWidget(subtitle_skeleton)
        
        layout.addStretch()



