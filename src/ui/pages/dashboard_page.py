"""Dashboard page with system snapshot cards."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QTransform, QPixmap
import qtawesome as qta
from datetime import datetime

from services.system_metrics_service import SystemMetricsService
from ui.components.system_card import SystemCardWidget, SkeletonCardWidget


class MetricsWorker(QThread):
    """Worker thread for loading metrics data."""
    
    finished = Signal(dict)  # Signal with current_metrics
    
    def __init__(self, metrics_service):
        super().__init__()
        self.metrics_service = metrics_service
    
    def run(self):
        """Run the data collection in background."""
        current = self.metrics_service.get_current_metrics()
        disk = self.metrics_service.get_disk_metrics()
        network = self.metrics_service.get_network_metrics()
        battery = self.metrics_service.get_battery_metrics()
        system_info = self.metrics_service.get_system_info()
        
        data = {
            'current': current,
            'disk': disk,
            'network': network,
            'battery': battery,
            'system_info': system_info
        }
        self.finished.emit(data)


class DashboardPage(QWidget):
    """Dashboard page showing system snapshot cards."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.metrics_service = SystemMetricsService()
        self.is_loading = True
        self.last_update_time = None
        
        # Card widgets
        self.cpu_card = None
        self.ram_card = None
        self.disk_card = None
        self.uptime_card = None
        self.network_status_card = None
        self.download_speed_card = None
        self.upload_speed_card = None
        self.battery_card = None
        
        self.init_ui()
        
        # Auto-refresh timer (2 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(2000)
        
        # Initial load
        QTimer.singleShot(100, self.refresh_data)
    
    def init_ui(self):
        """Initialize dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header: Title and refresh button
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.translator.t("dashboard.title"))
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #e0e0e0;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Last update label
        self.update_label = QLabel("")
        self.update_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        header_layout.addWidget(self.update_label)
        
        header_layout.addSpacing(10)
        
        # Refresh button (optional, can be hidden)
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(qta.icon('fa5s.sync', color='white'))
        self.refresh_button.setToolTip(self.translator.t("dashboard.refresh"))
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Grid layout for cards
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(16)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        
        # Create skeleton cards for loading
        self.create_skeleton_cards()
        
        layout.addLayout(self.cards_grid)
        layout.addStretch()
    
    def create_skeleton_cards(self):
        """Create skeleton loading cards."""
        # Clear existing cards
        self.clear_cards()
        
        # Row 1: Core System
        for i in range(4):
            skeleton = SkeletonCardWidget()
            self.cards_grid.addWidget(skeleton, 0, i)
        
        # Row 2: Network & Power
        for i in range(4):
            skeleton = SkeletonCardWidget()
            self.cards_grid.addWidget(skeleton, 1, i)
    
    def clear_cards(self):
        """Clear all cards from grid."""
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def create_cards(self):
        """Create actual metric cards."""
        self.clear_cards()
        
        # Row 1: Core System
        self.cpu_card = SystemCardWidget("CPU", "fa5s.tachometer-alt", self)
        self.cpu_card.setToolTip("Current CPU usage")
        self.cards_grid.addWidget(self.cpu_card, 0, 0)
        
        self.ram_card = SystemCardWidget("RAM", "fa5s.database", self)
        self.ram_card.setToolTip("Memory usage (Used/Total)")
        self.cards_grid.addWidget(self.ram_card, 0, 1)
        
        self.disk_card = SystemCardWidget("Disk", "fa5s.hdd", self)
        self.disk_card.setToolTip("System drive usage")
        self.cards_grid.addWidget(self.disk_card, 0, 2)
        
        self.uptime_card = SystemCardWidget("Uptime", "fa5s.clock", self)
        self.uptime_card.setToolTip("System uptime since boot")
        self.cards_grid.addWidget(self.uptime_card, 0, 3)
        
        # Row 2: Network & Power
        self.network_status_card = SystemCardWidget("Network", "fa5s.wifi", self)
        self.network_status_card.setToolTip("Network connection status")
        self.cards_grid.addWidget(self.network_status_card, 1, 0)
        
        self.download_speed_card = SystemCardWidget("Download", "fa5s.download", self)
        self.download_speed_card.setToolTip("Download speed")
        self.cards_grid.addWidget(self.download_speed_card, 1, 1)
        
        self.upload_speed_card = SystemCardWidget("Upload", "fa5s.upload", self)
        self.upload_speed_card.setToolTip("Upload speed")
        self.cards_grid.addWidget(self.upload_speed_card, 1, 2)
        
        # Battery card (may be hidden if no battery)
        self.battery_card = SystemCardWidget("Battery", "fa5s.battery-half", self)
        self.battery_card.setToolTip("Battery status")
        self.cards_grid.addWidget(self.battery_card, 1, 3)
    
    def get_status(self, value: float, thresholds: tuple) -> str:
        """
        Get status based on value and thresholds.
        
        Args:
            value: The metric value
            thresholds: (normal_max, warning_max) tuple
        
        Returns:
            'normal', 'warning', or 'critical'
        """
        normal_max, warning_max = thresholds
        if value < normal_max:
            return "normal"
        elif value < warning_max:
            return "warning"
        else:
            return "critical"
    
    def format_speed(self, bytes_per_sec: float) -> str:
        """Format network speed."""
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} B/s"
        elif bytes_per_sec < 1024 * 1024:
            return f"{bytes_per_sec / 1024:.2f} KB/s"
        else:
            return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
    
    def update_cards(self, data: dict):
        """Update all cards with data."""
        if self.is_loading:
            self.create_cards()
            self.is_loading = False
        
        current = data['current']
        disk = data['disk']
        network = data['network']
        battery = data['battery']
        system_info = data['system_info']
        
        # CPU Card
        cpu_value = current['cpu_percent']
        cpu_status = self.get_status(cpu_value, (60, 80))
        self.cpu_card.set_value(
            f"{cpu_value:.1f}%",
            "Usage",
            cpu_status
        )
        
        # RAM Card
        ram_value = current['ram_percent']
        ram_status = self.get_status(ram_value, (70, 85))
        ram_subtitle = f"{current['ram_used_gb']:.1f} GB / {current['ram_total_gb']:.1f} GB"
        self.ram_card.set_value(
            f"{ram_value:.1f}%",
            ram_subtitle,
            ram_status
        )
        
        # Disk Card
        disk_value = disk['percent_used']
        disk_status = self.get_status(disk_value, (80, 90))
        disk_subtitle = f"{disk['used_gb']:.1f} GB / {disk['total_gb']:.1f} GB"
        self.disk_card.set_value(
            f"{disk['used_gb']:.1f} GB / {disk['total_gb']:.1f} GB",
            f"Free: {disk['free_gb']:.1f} GB",
            disk_status
        )
        
        # Uptime Card
        self.uptime_card.set_value(
            system_info['uptime'],
            "Since boot",
            "normal"
        )
        
        # Network Status Card
        if network['is_connected']:
            network_status = "normal"
            # Check if weak/slow (download < 100 KB/s for 10s)
            if network['download_speed_bps'] < 100 * 1024:
                network_status = "warning"
            network_value = "Connected"
            network_subtitle = network['connection_type']
        else:
            network_status = "critical"
            network_value = "Disconnected"
            network_subtitle = "No connection"
        
        self.network_status_card.set_value(
            network_value,
            network_subtitle,
            network_status
        )
        
        # Download Speed Card
        download_speed = self.format_speed(network['download_speed_bps'])
        self.download_speed_card.set_value(
            download_speed,
            "Download",
            "normal"
        )
        
        # Upload Speed Card
        upload_speed = self.format_speed(network['upload_speed_bps'])
        self.upload_speed_card.set_value(
            upload_speed,
            "Upload",
            "normal"
        )
        
        # Battery Card
        if battery['has_battery']:
            battery_value = battery['percent']
            battery_subtitle = "Charging" if not battery['is_charging'] else "On battery"
            
            if battery_value < 10:
                battery_status = "critical"
            elif battery_value < 20:
                battery_status = "warning"
            else:
                battery_status = "normal"
            
            self.battery_card.set_value(
                f"{battery_value:.0f}%",
                battery_subtitle,
                battery_status
            )
            self.battery_card.show()
        else:
            # Hide battery card if no battery
            self.battery_card.hide()
        
        # Update last update time
        self.last_update_time = datetime.now()
        self.update_update_label()
    
    def update_update_label(self):
        """Update the 'Last update' label."""
        if self.last_update_time:
            elapsed = (datetime.now() - self.last_update_time).total_seconds()
            if elapsed < 60:
                self.update_label.setText(f"Last update: {int(elapsed)}s ago")
            else:
                minutes = int(elapsed / 60)
                self.update_label.setText(f"Last update: {minutes}m ago")
        else:
            self.update_label.setText("")
    
    def refresh_data(self):
        """Refresh dashboard data."""
        # Load metrics in background thread
        self.metrics_worker = MetricsWorker(self.metrics_service)
        self.metrics_worker.finished.connect(self.on_metrics_loaded)
        self.metrics_worker.start()
    
    def on_metrics_loaded(self, data: dict):
        """Handle metrics data loaded."""
        self.update_cards(data)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("dashboard.title"))
        self.refresh_button.setToolTip(self.translator.t("dashboard.refresh"))
        # Refresh data to update all labels
        self.refresh_data()
