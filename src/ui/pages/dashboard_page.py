"""Dashboard page with system metrics charts and running applications."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QTransform, QPixmap
import qtawesome as qta
from datetime import datetime

from services.system_metrics_service import SystemMetricsService, RunningAppInfo


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


class MetricsWorker(QThread):
    """Worker thread for loading metrics data."""
    
    finished = Signal(list, dict)  # Signal with (history, current_metrics)
    
    def __init__(self, metrics_service):
        super().__init__()
        self.metrics_service = metrics_service
    
    def run(self):
        """Run the data collection in background."""
        self.metrics_service.update_metrics_history()
        history = self.metrics_service.get_metrics_history(60)
        current = self.metrics_service.get_current_metrics()
        self.finished.emit(history, current)


class RunningAppsWorker(QThread):
    """Worker thread for loading running apps."""
    
    finished = Signal(list)  # Signal with apps list
    
    def __init__(self, metrics_service):
        super().__init__()
        self.metrics_service = metrics_service
    
    def run(self):
        """Run the data collection in background."""
        apps = self.metrics_service.get_running_windows()
        self.finished.emit(apps)


class MetricsChartWidget(QWidget):
    """Widget to display CPU and RAM metrics as line charts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
    
    def set_data(self, history):
        """Set metrics history data."""
        self.history = history
        self.update()
    
    def paintEvent(self, event):
        """Paint the charts."""
        super().paintEvent(event)
        
        if not self.history:
            painter = QPainter(self)
            painter.setPen(QColor("#a0a0a0"))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Loading data...")
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate drawing area
        margin = 50
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        # Draw background grid
        painter.setPen(QPen(QColor("#2d2d2d"), 1))
        for i in range(5):
            y = margin + (height * i / 4)
            painter.drawLine(margin, int(y), margin + width, int(y))
        
        if len(self.history) < 2:
            return
        
        # Draw CPU line (blue)
        painter.setPen(QPen(QColor("#0d6efd"), 2))
        for i in range(len(self.history) - 1):
            x1 = margin + (width * i / max(len(self.history) - 1, 1))
            y1 = margin + height - (height * self.history[i]['cpu'] / 100)
            x2 = margin + (width * (i + 1) / max(len(self.history) - 1, 1))
            y2 = margin + height - (height * self.history[i + 1]['cpu'] / 100)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw RAM line (green)
        painter.setPen(QPen(QColor("#198754"), 2))
        for i in range(len(self.history) - 1):
            x1 = margin + (width * i / max(len(self.history) - 1, 1))
            y1 = margin + height - (height * self.history[i]['ram'] / 100)
            x2 = margin + (width * (i + 1) / max(len(self.history) - 1, 1))
            y2 = margin + height - (height * self.history[i + 1]['ram'] / 100)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Draw labels
        painter.setPen(QColor("#e0e0e0"))
        painter.setFont(QFont("Arial", 10))
        
        # Y-axis labels (percentage)
        for i in range(5):
            y = margin + (height * i / 4)
            label = f"{100 - (i * 25)}%"
            painter.drawText(5, int(y) + 5, label)
        
        # Legend
        painter.setPen(QColor("#0d6efd"))
        painter.drawLine(width + margin - 100, 20, width + margin - 70, 20)
        painter.setPen(QColor("#e0e0e0"))
        painter.drawText(width + margin - 65, 25, "CPU")
        
        painter.setPen(QColor("#198754"))
        painter.drawLine(width + margin - 100, 40, width + margin - 70, 40)
        painter.setPen(QColor("#e0e0e0"))
        painter.drawText(width + margin - 65, 45, "RAM")


class RunningAppItemWidget(QWidget):
    """Widget for a single running application item."""
    
    def __init__(self, app_info: RunningAppInfo, on_kill_callback, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.on_kill_callback = on_kill_callback
        self.init_ui()
    
    def init_ui(self):
        """Initialize item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # App name
        name_label = QLabel(self.app_info.name[:50])  # Truncate long names
        name_label.setStyleSheet("font-weight: 500; font-size: 14px;")
        name_label.setToolTip(f"{self.app_info.name}\nProcess: {self.app_info.process_name}")
        layout.addWidget(name_label, 3)
        
        # Process name
        process_label = QLabel(self.app_info.process_name)
        process_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(process_label, 2)
        
        # PID
        pid_label = QLabel(str(self.app_info.pid))
        pid_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        pid_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pid_label, 1)
        
        # Memory
        memory_text = f"{self.app_info.memory_usage:.1f} MB" if self.app_info.memory_usage else "-"
        memory_label = QLabel(memory_text)
        memory_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        memory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(memory_label, 1)
        
        # CPU
        cpu_text = f"{self.app_info.cpu_percent:.1f}%" if self.app_info.cpu_percent else "-"
        cpu_label = QLabel(cpu_text)
        cpu_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cpu_label, 1)
        
        # Kill button
        kill_button = QPushButton()
        kill_button.setIcon(qta.icon('fa5s.times-circle', color='#dc3545'))
        kill_button.setToolTip(f"Close window\nTerminate {self.app_info.process_name}")
        kill_button.setCursor(Qt.CursorShape.PointingHandCursor)
        kill_button.clicked.connect(lambda: self.on_kill_callback(self.app_info.pid, self.app_info.name))
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
        layout.addWidget(kill_button)


class DashboardPage(QWidget):
    """Dashboard page showing system metrics and running applications."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.metrics_service = SystemMetricsService()
        self.loading_overlay = None
        self.init_ui()
        
        # Auto-refresh on page load
        QTimer.singleShot(100, self.refresh_data)
    
    def init_ui(self):
        """Initialize dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and refresh button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.translator.t("dashboard.title"))
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 600;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(qta.icon('fa5s.sync', color='white'))
        self.refresh_button.setToolTip(self.translator.t("dashboard.refresh"))
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Current metrics info
        self.metrics_info_label = QLabel("")
        self.metrics_info_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(self.metrics_info_label)
        
        layout.addSpacing(10)
        
        # Charts section
        charts_widget = QWidget()
        charts_widget.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 20px;")
        charts_layout = QVBoxLayout(charts_widget)
        
        chart_title = QLabel(self.translator.t("dashboard.charts.title"))
        chart_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        charts_layout.addWidget(chart_title)
        
        self.chart_widget = MetricsChartWidget()
        charts_layout.addWidget(self.chart_widget)
        
        layout.addWidget(charts_widget)
        
        layout.addSpacing(20)
        
        # Running apps section
        apps_header_layout = QHBoxLayout()
        
        self.apps_title = QLabel(self.translator.t("dashboard.running_apps.title"))
        self.apps_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        apps_header_layout.addWidget(self.apps_title)
        
        self.apps_count_label = QLabel("")
        self.apps_count_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        apps_header_layout.addWidget(self.apps_count_label)
        
        apps_header_layout.addStretch()
        
        layout.addLayout(apps_header_layout)
        layout.addSpacing(10)
        
        # Table header
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #252525; border-radius: 6px; padding: 8px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        headers = [
            (self.translator.t("dashboard.running_apps.window_name"), 3),
            (self.translator.t("dashboard.running_apps.process"), 2),
            (self.translator.t("dashboard.running_apps.pid"), 1),
            (self.translator.t("dashboard.running_apps.memory"), 1),
            (self.translator.t("dashboard.running_apps.cpu"), 1),
            (self.translator.t("dashboard.running_apps.action"), 0)
        ]
        
        for text, stretch in headers:
            header_label = QLabel(text)
            header_label.setStyleSheet("font-weight: 600; color: #e0e0e0;")
            if text in [self.translator.t("dashboard.running_apps.pid"), 
                       self.translator.t("dashboard.running_apps.memory"),
                       self.translator.t("dashboard.running_apps.cpu")]:
                header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if stretch > 0:
                header_layout.addWidget(header_label, stretch)
            else:
                header_layout.addWidget(header_label)
        
        layout.addWidget(header_widget)
        
        # Scroll area for running apps
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
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
        """Refresh dashboard data."""
        # Show loading overlay
        self.show_loading()
        self.refresh_button.setEnabled(False)
        
        # Track completion of both workers
        self.metrics_loaded = False
        self.apps_loaded = False
        
        # Load metrics
        self.metrics_worker = MetricsWorker(self.metrics_service)
        self.metrics_worker.finished.connect(self.on_metrics_loaded)
        self.metrics_worker.start()
        
        # Load running apps
        self.apps_worker = RunningAppsWorker(self.metrics_service)
        self.apps_worker.finished.connect(self.on_apps_loaded)
        self.apps_worker.start()
    
    def check_all_loaded(self):
        """Check if all data is loaded and hide loading overlay."""
        if self.metrics_loaded and self.apps_loaded:
            self.hide_loading()
            self.refresh_button.setEnabled(True)
    
    def on_metrics_loaded(self, history, current):
        """Handle metrics data loaded."""
        # Update chart
        self.chart_widget.set_data(history)
        
        # Update info label
        info_text = f"CPU: {current['cpu_percent']:.1f}% | RAM: {current['ram_percent']:.1f}% ({current['ram_used_gb']:.1f} GB / {current['ram_total_gb']:.1f} GB)"
        self.metrics_info_label.setText(info_text)
        
        self.metrics_loaded = True
        self.check_all_loaded()
    
    def on_apps_loaded(self, apps):
        """Handle running apps data loaded."""
        # Clear existing widgets
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Update count
        self.apps_count_label.setText(f"({len(apps)} {self.translator.t('dashboard.running_apps.windows')})")
        
        # Add app items
        if not apps:
            no_apps_label = QLabel(self.translator.t("dashboard.running_apps.no_windows"))
            no_apps_label.setStyleSheet("color: #a0a0a0; padding: 20px;")
            no_apps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.apps_layout.addWidget(no_apps_label)
        else:
            for app in apps:
                item_widget = RunningAppItemWidget(app, self.kill_app)
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
        
        self.apps_loaded = True
        self.check_all_loaded()
    
    def kill_app(self, pid: int, app_name: str):
        """Kill an application process."""
        success = self.metrics_service.kill_process(pid)
        
        if success:
            QMessageBox.information(
                self,
                self.translator.t("dashboard.messages.success"),
                self.translator.t("dashboard.messages.process_killed").format(name=app_name),
                QMessageBox.StandardButton.Ok
            )
            # Refresh after killing
            QTimer.singleShot(500, self.refresh_data)
        else:
            QMessageBox.warning(
                self,
                self.translator.t("dashboard.messages.error"),
                self.translator.t("dashboard.messages.kill_failed").format(name=app_name),
                QMessageBox.StandardButton.Ok
            )
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("dashboard.title"))
        self.refresh_button.setToolTip(self.translator.t("dashboard.refresh"))
        self.apps_title.setText(self.translator.t("dashboard.running_apps.title"))
        # Refresh data to update all labels
        self.refresh_data()

