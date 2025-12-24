"""Tool item widget component."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFontMetrics
import qtawesome as qta

from models.config_models import Tool


class ToolItemWidget(QWidget):
    """Widget for displaying a single tool item."""
    
    def __init__(self, tool: Tool, translator, on_use_callback=None, on_view_details_callback=None, is_running=False, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.translator = translator
        self.on_use_callback = on_use_callback
        self.on_view_details_callback = on_view_details_callback
        self._is_running = is_running
        self.setObjectName("toolItem")
        self._hovered = False
        self._is_coming_soon = "Coming soon" in tool.tags
        self.setMinimumHeight(100)  # Light min-height, card will fit content
        self.setMaximumHeight(200)  # Prevent excessive stretching
        # Wider width for single column layout
        self.setMinimumWidth(800)
        self.setMaximumWidth(1200)
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
        if self._is_coming_soon:
            # Use darker background with high opacity to cover all text
            bg_color = QColor(20, 20, 20, 240)  # Dark background with high opacity to hide content
        else:
            bg_color = QColor(28, 28, 28)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 12, 12)
        
        # Draw border
        if self._is_coming_soon:
            border_color = QColor(255, 255, 255, 20)  # Subtle border for coming soon
            border_width = 1
        else:
            border_color = QColor(74, 158, 255, 200) if self._hovered else QColor(255, 255, 255, 30)
            border_width = 1
        pen = QPen(border_color, border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 12, 12)
        
        super().paintEvent(event)
        
        # Update overlay widget position and size for coming soon items
        if self._is_coming_soon and hasattr(self, 'overlay_widget'):
            self.overlay_widget.setGeometry(rect)
            self.overlay_widget.show()
            self.overlay_widget.lower()  # Put overlay behind badge
    
    def init_ui(self):
        """Initialize tool item UI."""
        # Transparent background - we'll draw it in paintEvent
        self.setStyleSheet("""
            #toolItem {
                background-color: transparent;
            }
        """)
        
        # Create overlay widget for coming soon items to completely hide content
        if self._is_coming_soon:
            self.overlay_widget = QWidget(self)
            # Dark overlay with high opacity to completely cover content
            self.overlay_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(20, 20, 20, 245);
                    border-radius: 12px;
                }
            """)
            self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(0)
        
        # Header Row: Left (Icon + Title + FREE) | Right (Run + View details)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)  # Clear gap between left and right sections
        
        # Left Section: Icon + Title + FREE badge
        left_section = QHBoxLayout()
        left_section.setContentsMargins(0, 0, 0, 0)
        left_section.setSpacing(10)
        left_section.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Icon container
        icon_container = QWidget()
        icon_container.setFixedSize(36, 36)
        if self._is_coming_soon:
            # Hide icon container - overlay will cover it
            icon_container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-radius: 8px;
                    border: none;
                }
            """)
        else:
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
        if self._is_coming_soon:
            # Hide icon completely - overlay will cover it
            icon = qta.icon(self.tool.icon, color='transparent')
        else:
            icon = qta.icon(self.tool.icon, color='#4a9eff')
        icon_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        icon_label.setPixmap(icon.pixmap(18, 18))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        left_section.addWidget(icon_container)
        
        # Title with truncate support
        self.name_label = QLabel(self.tool.name)
        if self._is_coming_soon:
            # Hide text completely - overlay will cover it
            self.name_label.setStyleSheet("""
                font-size: 15px;
                font-weight: 600;
                color: transparent;
                letter-spacing: -0.2px;
            """)
        else:
            self.name_label.setStyleSheet("""
                font-size: 15px;
                font-weight: 600;
                color: #ffffff;
                letter-spacing: -0.2px;
            """)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.name_label.setTextFormat(Qt.TextFormat.PlainText)
        # Set size policy to allow shrinking
        self.name_label.setSizePolicy(
            self.name_label.sizePolicy().horizontalPolicy(),
            self.name_label.sizePolicy().verticalPolicy()
        )
        self.name_label.setMinimumWidth(0)  # Allow shrinking below content size
        left_section.addWidget(self.name_label)
        
        # FREE badge (moved to left section) - hide for coming soon
        if not self._is_coming_soon:
            free_tag = QLabel("FREE")
            free_tag.setObjectName("freeTag")
            free_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            free_tag.setStyleSheet("""
                #freeTag {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #20c997,
                        stop:0.3 #198754,
                        stop:0.6 #14b478,
                        stop:1 #22d4a3);
                    color: #ffffff;
                    padding: 3px 8px;
                    border-radius: 6px;
                    font-size: 8px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    border: none;
                }
            """)
            left_section.addWidget(free_tag)
        
        # Add stretch to push right section away, but limit left section growth
        left_section.addStretch()
        
        # Add left section with stretch factor 1 (can grow, but title will truncate)
        header_layout.addLayout(left_section, 1)
        
        # Right Section: Run + View details (fixed size, no stretch)
        right_section = QHBoxLayout()
        right_section.setContentsMargins(0, 0, 0, 0)
        right_section.setSpacing(10)  # Gap between Run and View details
        right_section.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Run/Pause button with text - fixed width to prevent jumping
        button_text = self.translator.t("tools.run") if not self._is_running else self.translator.t("tools.pause")
        self.use_button = QPushButton(button_text)
        if self._is_coming_soon:
            # Hide icon completely for coming soon items
            self.use_button.setIcon(qta.icon('fa5s.play-circle' if not self._is_running else 'fa5s.pause-circle', color='transparent'))
        else:
            self.use_button.setIcon(qta.icon('fa5s.play-circle' if not self._is_running else 'fa5s.pause-circle', color='white'))
        self.use_button.setToolTip(self.translator.t("tools.use_tool"))
        # Set fixed width to prevent layout shift when text changes
        self.use_button.setFixedWidth(90)  # Fixed width for Run/Pause button
        if not self._is_coming_soon:
            self.use_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.use_button.setEnabled(not self._is_coming_soon)
        
        if self._is_coming_soon:
            # Hide button completely - overlay will cover it
            self.use_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: transparent;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: 600;
                }
            """)
        else:
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
        if self.on_use_callback and not self._is_coming_soon:
            self.use_button.clicked.connect(lambda: self.on_use_callback(self.tool))
        right_section.addWidget(self.use_button)
        
        # View details button (secondary)
        if self.on_view_details_callback:
            self.view_details_button = QPushButton(self.translator.t("tools.view_details"))
            self.view_details_button.setCursor(Qt.CursorShape.PointingHandCursor)
            if self._is_coming_soon:
                # Hide button completely - overlay will cover it
                self.view_details_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: transparent;
                        border: none;
                        border-radius: 10px;
                        padding: 8px 14px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                """)
            else:
                self.view_details_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #4a9eff;
                        border: 1px solid rgba(74, 158, 255, 0.3);
                        border-radius: 10px;
                        padding: 8px 14px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: rgba(74, 158, 255, 0.1);
                        border-color: #4a9eff;
                    }
                """)
            self.view_details_button.clicked.connect(lambda: self.on_view_details_callback(self.tool))
            right_section.addWidget(self.view_details_button)
        
        # Right section has no stretch - takes only needed space
        header_layout.addLayout(right_section, 0)
        
        # Add header layout for all items (including coming soon)
        main_layout.addLayout(header_layout)
        
        # Create "Coming Soon" badge in top-right corner (like sale card)
        if self._is_coming_soon:
            self.coming_soon_badge = QLabel("COMING SOON")
            self.coming_soon_badge.setObjectName("comingSoonBadge")
            self.coming_soon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.coming_soon_badge.setStyleSheet("""
                #comingSoonBadge {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ff6b35,
                        stop:1 #ffc107);
                    color: #ffffff;
                    padding: 6px 16px;
                    border-radius: 0px 12px 0px 16px;
                    font-size: 10px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    border: none;
                }
            """)
            # Position badge in top-right corner
            self.coming_soon_badge.setParent(self)
            self.coming_soon_badge.raise_()
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._update_badge_position())
        
        # All items (normal and coming soon) show status and content
        main_layout.addSpacing(8)
        
        # Status row - always visible, shows Active/Deactive
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 6, 0, 6)  # Add vertical padding
        status_layout.setSpacing(6)
        
        self.status_indicator = QLabel("●")
        status_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("Active" if self._is_running else "Deactive")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Always show status container
        self.status_container = QWidget()
        self.status_container.setLayout(status_layout)
        # Set background color to match card background
        self.status_container.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
            }
        """)
        main_layout.addWidget(self.status_container)
        main_layout.addSpacing(4)
        
        # Update status styling based on state
        self._update_status_display()
        # Normal items - show tags and description
        # Tags row (moved after description, wrap naturally)
        if self.tool.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(6)  # Tighter spacing for pills
            
            for tag in self.tool.tags:
                tag_label = QLabel(tag)
                tag_label.setObjectName("toolTag")
                
                # Improved tag styling - smaller pills with better contrast
                if self._is_coming_soon:
                    # Hide tags completely - overlay will cover it
                    tag_label.setStyleSheet("""
                        #toolTag {
                            background-color: transparent;
                            color: transparent;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-size: 10px;
                            font-weight: 500;
                            border: none;
                        }
                    """)
                else:
                    tag_label.setStyleSheet("""
                        #toolTag {
                            background-color: #1f1f1f;
                            color: #b0b0b0;
                            padding: 4px 8px;
                            border-radius: 12px;
                            font-size: 10px;
                            font-weight: 500;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                        }
                    """)
                tags_layout.addWidget(tag_label)
            
            tags_layout.addStretch()
            main_layout.addLayout(tags_layout)
            main_layout.addSpacing(6)
        
        # Description (plain text, no box)
        if self.tool.description:
            self.desc_label = QLabel(self.tool.description)
            if self._is_coming_soon:
                # Hide description completely - overlay will cover it
                self.desc_label.setStyleSheet("""
                    font-size: 12px;
                    color: transparent;
                    line-height: 1.4;
                    padding: 0px;
                """)
            else:
                # Description color matching card theme
                self.desc_label.setStyleSheet("""
                    font-size: 12px;
                    color: #888888;
                    line-height: 1.4;
                    padding: 0px;
                    background-color: #1c1c1c;
                """)
            self.desc_label.setWordWrap(True)
            self.desc_label.setMaximumHeight(32)  # ~2 lines max
            main_layout.addWidget(self.desc_label)
        
        # Removed addStretch() - card will fit content naturally
        
        # Update badge position, overlay, and title truncation after layout is calculated
        from PySide6.QtCore import QTimer
        if self._is_coming_soon:
            QTimer.singleShot(0, lambda: self._update_badge_position())
            if hasattr(self, 'overlay_widget'):
                QTimer.singleShot(0, lambda: self._update_overlay())
        # Update title truncation after layout is calculated
        QTimer.singleShot(0, lambda: self._update_title_truncation())
    
    def _update_badge_position(self):
        """Update coming soon badge position in top-right corner."""
        if self._is_coming_soon and hasattr(self, 'coming_soon_badge'):
            badge_width = 140
            badge_height = 28
            x = self.width() - badge_width - 1
            y = 1
            self.coming_soon_badge.setGeometry(x, y, badge_width, badge_height)
            self.coming_soon_badge.raise_()  # Raise badge above overlay
            self.coming_soon_badge.show()
    
    def _update_overlay(self):
        """Update overlay widget position and visibility."""
        if self._is_coming_soon and hasattr(self, 'overlay_widget'):
            rect = self.rect().adjusted(1, 1, -1, -1)
            self.overlay_widget.setGeometry(rect)
            self.overlay_widget.show()
            self.overlay_widget.lower()  # Keep overlay below badge
            # Raise badge above overlay
            if hasattr(self, 'coming_soon_badge'):
                self.coming_soon_badge.raise_()
    
    def _update_status_display(self):
        """Update status display styling based on current state."""
        if hasattr(self, 'status_indicator') and hasattr(self, 'status_label'):
            if self._is_running:
                # Active - green color
                if self._is_coming_soon:
                    # Hide status completely - overlay will cover it
                    self.status_indicator.setStyleSheet("""
                        color: transparent;
                        font-size: 8px;
                    """)
                    self.status_label.setText("Active")
                    self.status_label.setStyleSheet("""
                        color: transparent;
                        font-size: 11px;
                        font-weight: 500;
                    """)
                else:
                    self.status_indicator.setStyleSheet("""
                        color: #20c997;
                        font-size: 8px;
                    """)
                    self.status_label.setText("Active")
                    self.status_label.setStyleSheet("""
                        color: #20c997;
                        font-size: 11px;
                        font-weight: 500;
                    """)
            else:
                # Deactive - muted gray color to match card theme
                if self._is_coming_soon:
                    # Hide status completely - overlay will cover it
                    self.status_indicator.setStyleSheet("""
                        color: transparent;
                        font-size: 8px;
                    """)
                    self.status_label.setText("Deactive")
                    self.status_label.setStyleSheet("""
                        color: transparent;
                        font-size: 11px;
                        font-weight: 500;
                    """)
                else:
                    # Use muted gray color matching card theme
                    self.status_indicator.setStyleSheet("""
                        color: #888888;
                        font-size: 8px;
                    """)
                    self.status_label.setText("Deactive")
                    self.status_label.setStyleSheet("""
                        color: #888888;
                        font-size: 11px;
                        font-weight: 500;
                    """)
    
    def update_state(self, is_running: bool):
        """Update button state based on running status."""
        self._is_running = is_running
        if is_running:
            self.use_button.setText(self.translator.t("tools.pause"))
            if self._is_coming_soon:
                self.use_button.setIcon(qta.icon('fa5s.pause-circle', color='transparent'))
            else:
                self.use_button.setIcon(qta.icon('fa5s.pause-circle', color='white'))
        else:
            self.use_button.setText(self.translator.t("tools.run"))
            if self._is_coming_soon:
                self.use_button.setIcon(qta.icon('fa5s.play-circle', color='transparent'))
            else:
                self.use_button.setIcon(qta.icon('fa5s.play-circle', color='white'))
        # Update status display
        self._update_status_display()
        # Ensure button width stays fixed to prevent layout shift
        self.use_button.setFixedWidth(90)
    
    def _update_title_truncation(self):
        """Update title text with proper truncation based on available space."""
        if not hasattr(self, 'name_label'):
            return
        
        # Get the header layout
        main_layout = self.layout()
        if not main_layout:
            return
        
        # Find the header layout (first item)
        header_layout = main_layout.itemAt(0)
        if not header_layout or not header_layout.layout():
            return
        
        header = header_layout.layout()
        
        # Get geometry of left and right sections
        # Left section: item 0, Right section: item 1
        if header.count() < 2:
            return
        
        left_item = header.itemAt(0)
        right_item = header.itemAt(1)
        
        if left_item and right_item and left_item.layout() and right_item.layout():
            # Get actual geometries after layout
            left_rect = left_item.geometry()
            right_rect = right_item.geometry()
            
            # Calculate available width for title within left section
            # Left section contains: icon (36) + spacing (10) + title + spacing (10) + FREE badge
            # We need to account for icon and FREE badge widths
            icon_width = 36
            spacing = 10
            free_badge_width = 55  # Approximate width for FREE badge (reduced for smaller badge)
            
            # Available width = left section width - icon - spacing - FREE badge - spacing
            available_width = left_rect.width() - icon_width - spacing - free_badge_width - spacing
            
            if available_width > 20:  # Minimum width threshold
                font_metrics = QFontMetrics(self.name_label.font())
                elided_text = font_metrics.elidedText(
                    self.tool.name,
                    Qt.TextElideMode.ElideRight,
                    available_width
                )
                self.name_label.setText(elided_text)
            else:
                # Fallback: use original name
                self.name_label.setText(self.tool.name)
    
    def resizeEvent(self, event):
        """Handle widget resize to update overlay and truncate title."""
        super().resizeEvent(event)
        
        # Update title truncation
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_title_truncation())
        
        # Update badge position and overlay on resize
        if self._is_coming_soon:
            QTimer.singleShot(0, lambda: self._update_badge_position())
            if hasattr(self, 'overlay_widget'):
                QTimer.singleShot(0, lambda: self._update_overlay())
