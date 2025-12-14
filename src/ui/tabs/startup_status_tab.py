"""Startup Status tab showing apps that start with Windows."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QTransform, QPixmap, QPainter, QFontMetrics
import qtawesome as qta

from services.startup_monitor_service import StartupMonitorService, StartupAppInfo


class ElidedLabel(QLabel):
    """QLabel that automatically elides text when it's too long."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self._elided_text = text
    
    def setText(self, text):
        """Set text and store full text for tooltip."""
        self._full_text = text
        self.updateElidedText()
    
    def resizeEvent(self, event):
        """Update elided text when widget is resized."""
        super().resizeEvent(event)
        self.updateElidedText()
    
    def updateElidedText(self):
        """Update the displayed text with elision."""
        if not self._full_text:
            super().setText("")
            return
        
        metrics = QFontMetrics(self.font())
        available_width = self.width() - 10  # Leave some padding
        self._elided_text = metrics.elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            available_width
        )
        super().setText(self._elided_text)


class RefreshWorker(QThread):
    """Worker thread for refreshing startup apps data."""
    
    finished = Signal(list, dict)  # Signal with (apps, system_info)
    
    def __init__(self, monitor_service):
        super().__init__()
        self.monitor_service = monitor_service
    
    def run(self):
        """Run the refresh in background."""
        apps = self.monitor_service.get_startup_apps()
        system_info = self.monitor_service.get_system_info()
        self.finished.emit(apps, system_info)


class LoadingOverlay(QWidget):
    """Full-screen loading overlay with spinning icon."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.rotation_angle = 0
        self.init_ui()
        self.start_animation()
    
    def init_ui(self):
        """Initialize overlay UI."""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner icon
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setFixedSize(64, 64)
        layout.addWidget(self.spinner_label)
        
        # Loading text
        text_label = QLabel("Loading...")
        text_label.setStyleSheet("color: #e0e0e0; font-size: 16px; margin-top: 20px;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)
        
        # Store base pixmap
        icon = qta.icon('fa5s.spinner', color='#0d6efd')
        self.base_pixmap = icon.pixmap(48, 48)
    
    def start_animation(self):
        """Start rotation animation."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_icon)
        self.timer.start(50)  # Update every 50ms for smooth rotation
    
    def rotate_icon(self):
        """Rotate icon by updating pixmap."""
        self.rotation_angle = (self.rotation_angle + 15) % 360
        
        # Create transform and rotate
        transform = QTransform()
        transform.rotate(self.rotation_angle)
        rotated_pixmap = self.base_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        
        # Center the rotated pixmap
        final_pixmap = QPixmap(64, 64)
        final_pixmap.fill(Qt.GlobalColor.transparent)
        
        p = QPainter(final_pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.drawPixmap(
            (64 - rotated_pixmap.width()) // 2,
            (64 - rotated_pixmap.height()) // 2,
            rotated_pixmap
        )
        p.end()
        
        self.spinner_label.setPixmap(final_pixmap)


class StartupAppItemWidget(QWidget):
    """Widget for a single startup app item with aligned columns."""
    
    def __init__(self, app_info: StartupAppInfo, on_kill_callback, on_delete_callback, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.on_kill_callback = on_kill_callback
        self.on_delete_callback = on_delete_callback
        self.init_ui()
    
    def init_ui(self):
        """Initialize item UI with aligned columns."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Status indicator (equal width)
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(5)
        
        status_icon = QLabel()
        if self.app_info.status == "running":
            status_icon.setPixmap(qta.icon('fa5s.circle', color='#198754').pixmap(16, 16))
            status_text = "Running"
            status_color = "#198754"
            status_tooltip = f"Status: Running\nProcess ID: {self.app_info.process_id if self.app_info.process_id else 'N/A'}"
        elif self.app_info.status == "stopped":
            status_icon.setPixmap(qta.icon('fa5s.circle', color='#6c757d').pixmap(16, 16))
            status_text = "Stopped"
            status_color = "#6c757d"
            status_tooltip = "Status: Stopped\nApplication is not currently running"
        else:
            status_icon.setPixmap(qta.icon('fa5s.circle', color='#ffc107').pixmap(16, 16))
            status_text = "Unknown"
            status_color = "#ffc107"
            status_tooltip = "Status: Unknown\nUnable to determine application status"
        
        status_icon.setToolTip(status_tooltip)
        status_layout.addWidget(status_icon)
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: 500;")
        status_label.setToolTip(status_tooltip)
        status_layout.addWidget(status_label)
        layout.addWidget(status_widget, 1)  # Equal stretch
        
        # App name (equal width) - will be elided if too long
        full_name = self.app_info.name
        name_label = ElidedLabel(full_name)
        name_label.setStyleSheet("font-weight: 500; font-size: 14px;")
        name_label.setWordWrap(False)  # No word wrap
        name_label.setTextFormat(Qt.TextFormat.PlainText)
        name_label.setToolTip(f"Application: {full_name}\nPath: {self.app_info.path if self.app_info.path else 'N/A'}")
        layout.addWidget(name_label, 2)  # More space for name
        
        # Source (equal width)
        source_label = QLabel(self.app_info.source)
        source_label.setStyleSheet(f"""
            background-color: #2d2d2d;
            color: #a0a0a0;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
        """)
        source_label.setWordWrap(False)
        source_tooltip = f"Startup Source: {self.app_info.source}\nThis indicates where the startup entry is configured"
        if "Registry" in self.app_info.source:
            source_tooltip += "\n(Windows Registry)"
        elif "Startup Folder" in self.app_info.source:
            source_tooltip += "\n(Startup Folder)"
        elif "Task Scheduler" in self.app_info.source:
            source_tooltip += "\n(Task Scheduler)"
        source_label.setToolTip(source_tooltip)
        layout.addWidget(source_label, 1)  # Equal stretch
        
        # PID (equal width)
        pid_text = self.app_info.process_id if self.app_info.process_id else "-"
        pid_label = QLabel(pid_text)
        pid_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        pid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.app_info.process_id:
            pid_label.setToolTip(f"Process ID: {self.app_info.process_id}\nUnique identifier for the running process")
        else:
            pid_label.setToolTip("Process ID: Not available\nApplication is not currently running")
        layout.addWidget(pid_label, 1)  # Equal stretch
        
        # Memory (equal width)
        memory_text = "-"
        memory_tooltip = "Memory Usage: Not available"
        if self.app_info.memory_usage:
            try:
                memory_kb = int(self.app_info.memory_usage.replace(',', ''))
                memory_mb = memory_kb / 1024
                memory_text = f"{memory_mb:.1f} MB"
                memory_tooltip = f"Memory Usage: {memory_text}\n({memory_kb} KB)\nRAM consumed by this process"
            except:
                pass
        else:
            memory_tooltip = "Memory Usage: Not available\nApplication is not currently running"
        memory_label = QLabel(memory_text)
        memory_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        memory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        memory_label.setToolTip(memory_tooltip)
        layout.addWidget(memory_label, 1)  # Equal stretch
        
        # Action buttons (equal width)
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(5)
        
        # Kill button (icon "-")
        if self.app_info.status == "running" and self.app_info.process_id:
            kill_button = QPushButton()
            kill_button.setIcon(qta.icon('fa5s.minus-circle', color='#dc3545'))
            kill_button.setToolTip(f"Kill Process\nTerminate the running process (PID: {self.app_info.process_id})\nThis will stop the application immediately")
            kill_button.setCursor(Qt.CursorShape.PointingHandCursor)
            kill_button.clicked.connect(lambda: self.on_kill_callback(self.app_info.process_id, self.app_info.name))
            kill_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                    border-radius: 4px;
                }
            """)
            action_layout.addWidget(kill_button)
        else:
            placeholder = QLabel("-")
            placeholder.setToolTip("Kill Process: Not available\nApplication is not currently running")
            action_layout.addWidget(placeholder)
        
        # Delete button (icon trash) - always visible
        delete_button = QPushButton()
        delete_button.setIcon(qta.icon('fa5s.trash', color='#dc3545'))
        delete_source = self.app_info.source
        delete_tooltip = f"Remove from Startup\nPermanently remove '{self.app_info.name}' from Windows startup\nSource: {delete_source}\n\nThis will prevent the app from starting automatically on boot"
        delete_button.setToolTip(delete_tooltip)
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.clicked.connect(lambda: self.on_delete_callback(self.app_info))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-radius: 4px;
            }
        """)
        action_layout.addWidget(delete_button)
        
        layout.addLayout(action_layout, 1)  # Equal stretch


class StartupStatusTab(QWidget):
    """Startup Status tab showing apps configured to start with Windows."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.monitor_service = StartupMonitorService()
        self.apps_data = []  # Store apps data
        self.loading_overlay = None
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel(self.translator.t("starter.tabs.startup_status"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        layout.addSpacing(10)
        
        # System info and refresh button
        top_layout = QHBoxLayout()
        
        # System info
        self.system_info_label = QLabel("")
        self.system_info_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        top_layout.addWidget(self.system_info_label)
        
        top_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(qta.icon('fa5s.sync', color='white'))
        self.refresh_button.setToolTip("Refresh")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setMaximumWidth(40)
        self.refresh_button.clicked.connect(self.refresh_data)
        top_layout.addWidget(self.refresh_button)
        
        layout.addLayout(top_layout)
        
        layout.addSpacing(10)
        
        # Header row for column alignment
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #252525; border-radius: 6px; padding: 8px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(10)
        
        # Status header (equal width)
        status_header = QLabel("Status")
        status_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        header_layout.addWidget(status_header, 1)  # Equal stretch
        
        # Name header (more space)
        name_header = QLabel("Application Name")
        name_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        header_layout.addWidget(name_header, 2)  # More space for name
        
        # Source header (equal width)
        source_header = QLabel("Source")
        source_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        header_layout.addWidget(source_header, 1)  # Equal stretch
        
        # PID header (equal width)
        pid_header = QLabel("PID")
        pid_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        pid_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(pid_header, 1)  # Equal stretch
        
        # Memory header (equal width)
        memory_header = QLabel("Memory")
        memory_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        memory_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(memory_header, 1)  # Equal stretch
        
        # Action header (equal width)
        action_header = QLabel("Action")
        action_header.setStyleSheet("font-weight: 600; color: #e0e0e0;")
        action_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(action_header, 1)  # Equal stretch
        
        layout.addWidget(header_widget)
        
        # Scroll area for apps list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Apps container
        self.apps_container = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_container)
        self.apps_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.apps_layout.setSpacing(4)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.apps_container)
        layout.addWidget(scroll_area, 1)
    
    def show_loading(self):
        """Show full-screen loading overlay."""
        if self.loading_overlay is None:
            self.loading_overlay = LoadingOverlay(self)
            self.loading_overlay.setGeometry(self.rect())
        self.loading_overlay.show()
        self.loading_overlay.raise_()
    
    def hide_loading(self):
        """Hide loading overlay."""
        if self.loading_overlay:
            self.loading_overlay.hide()
    
    def resizeEvent(self, event):
        """Handle resize to update loading overlay size."""
        super().resizeEvent(event)
        if self.loading_overlay:
            self.loading_overlay.setGeometry(self.rect())
    
    def refresh_data(self):
        """Refresh startup apps data with loading indicator."""
        # Show loading overlay
        self.show_loading()
        self.refresh_button.setEnabled(False)
        
        # Create worker thread
        self.worker = RefreshWorker(self.monitor_service)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.start()
    
    def on_data_loaded(self, apps, system_info):
        """Handle data loaded from worker thread."""
        self.apps_data = apps
        
        # Update system info label
        info_text = f"Found {len(apps)} startup applications"
        if system_info.get("uptime"):
            info_text += f" | System Uptime: {system_info['uptime']}"
        self.system_info_label.setText(info_text)
        
        # Populate apps list
        self.populate_apps_list(apps)
        
        # Hide loading
        self.hide_loading()
        self.refresh_button.setEnabled(True)
    
    def populate_apps_list(self, apps):
        """Populate apps list with data."""
        # Clear existing widgets
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add app items
        if not apps:
            no_apps_label = QLabel("No startup applications found.")
            no_apps_label.setStyleSheet("color: #a0a0a0; padding: 20px;")
            no_apps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.apps_layout.addWidget(no_apps_label)
        else:
            for app in apps:
                item_widget = StartupAppItemWidget(app, self.kill_process, self.remove_from_startup)
                item_widget.setStyleSheet("""
                    QWidget {
                        background-color: transparent;
                        border-radius: 6px;
                    }
                    QWidget:hover {
                        background-color: #2d2d2d;
                    }
                """)
                self.apps_layout.addWidget(item_widget)
    
    def kill_process(self, process_id: str, app_name: str):
        """Kill a process immediately without confirmation."""
        success = self.monitor_service.kill_process(process_id)
        
        if success:
            # Show brief success message
            QMessageBox.information(
                self,
                "Success",
                f"Process {process_id} ({app_name}) has been terminated.",
                QMessageBox.StandardButton.Ok
            )
            # Refresh data immediately after killing
            self.refresh_data()
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to kill process {process_id} ({app_name}).\n\nYou may need Administrator privileges to terminate this process.\n\nGo to Admin settings > Rules to enable Administrator mode.",
                QMessageBox.StandardButton.Ok
            )
    
    def remove_from_startup(self, app_info: StartupAppInfo):
        """Remove app from Windows startup."""
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "Remove from Startup",
            f"Are you sure you want to remove '{app_info.name}' from Windows startup?\n\nThis will permanently disable the app from starting automatically.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.monitor_service.remove_from_startup(app_info)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"'{app_info.name}' has been removed from Windows startup."
                )
                # Refresh data after removal
                self.refresh_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to remove '{app_info.name}' from startup.\n\nYou may need administrator privileges for system registry entries."
                )
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("starter.tabs.startup_status"))
        # Refresh data to update list
        self.refresh_data()
