"""Logs tab for viewing application logs."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta
from pathlib import Path

from services.logging_service import get_logging_service


class LogsTab(QWidget):
    """Logs tab for viewing and managing application logs."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.logging_service = get_logging_service()
        self.auto_refresh = True
        self.init_ui()
        self.load_logs()
        
        # Auto-refresh timer (every 2 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_logs)
        self.refresh_timer.start(2000)
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel(self.translator.t("admin.logs.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        # Description
        self.description_label = QLabel(self.translator.t("admin.logs.description"))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: #a0a0a0; margin-top: 8px; margin-bottom: 16px;")
        layout.addWidget(self.description_label)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t("admin.logs.search_placeholder"))
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setMaximumWidth(300)
        toolbar_layout.addWidget(self.search_input)
        
        toolbar_layout.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh_button = QPushButton()
        self.auto_refresh_button.setIcon(qta.icon('fa5s.sync', color='white'))
        self.auto_refresh_button.setText("  " + self.translator.t("admin.logs.auto_refresh"))
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.setChecked(True)
        self.auto_refresh_button.clicked.connect(self.on_auto_refresh_toggled)
        self.auto_refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar_layout.addWidget(self.auto_refresh_button)
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(qta.icon('fa5s.sync', color='white'))
        self.refresh_button.setText("  " + self.translator.t("admin.logs.refresh"))
        self.refresh_button.clicked.connect(self.load_logs)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar_layout.addWidget(self.refresh_button)
        
        # Clear button
        self.clear_button = QPushButton()
        self.clear_button.setIcon(qta.icon('fa5s.trash', color='white'))
        self.clear_button.setText("  " + self.translator.t("admin.logs.clear"))
        self.clear_button.clicked.connect(self.on_clear_logs)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setProperty("class", "danger")
        toolbar_layout.addWidget(self.clear_button)
        
        # Export button
        self.export_button = QPushButton()
        self.export_button.setIcon(qta.icon('fa5s.download', color='white'))
        self.export_button.setText("  " + self.translator.t("admin.logs.export"))
        self.export_button.clicked.connect(self.on_export_logs)
        self.export_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar_layout.addWidget(self.export_button)
        
        layout.addLayout(toolbar_layout)
        
        layout.addSpacing(10)
        
        # Logs display - styled like terminal
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Consolas', 'Courier New', 'Monaco', monospace;
                font-size: 12px;
                border: 2px solid #30363d;
                border-radius: 8px;
                padding: 12px;
            }
            QScrollBar:vertical {
                background-color: #161b22;
                width: 12px;
                border: none;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #30363d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #484f58;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.logs_text.setPlaceholderText(self.translator.t("admin.logs.no_logs"))
        layout.addWidget(self.logs_text, 1)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(self.status_label)
    
    def format_log_line(self, line: str) -> str:
        """Format a log line with colors based on log level."""
        line = line.rstrip('\n\r')
        if not line:
            return ""
        
        # Color mapping for log levels
        if " - ERROR - " in line:
            color = "#f85149"  # Red for errors
        elif " - WARNING - " in line:
            color = "#d29922"  # Yellow/Orange for warnings
        elif " - INFO - " in line:
            color = "#3fb950"  # Green for info
        elif " - DEBUG - " in line:
            color = "#8b949e"  # Gray for debug
        else:
            color = "#c9d1d9"  # Default text color
        
        # Escape HTML special characters
        line_escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Format with color
        return f'<span style="color: {color};">{line_escaped}</span><br>'
    
    def load_logs(self):
        """Load and display logs with terminal-like styling."""
        try:
            logs = self.logging_service.get_logs(lines=1000)
            
            # Filter by search term if provided
            search_term = self.search_input.text().strip().lower()
            if search_term:
                logs = [line for line in logs if search_term in line.lower()]
            
            # Format logs with colors
            formatted_logs = []
            for line in logs:
                formatted_logs.append(self.format_log_line(line))
            
            # Join formatted logs
            html_content = ''.join(formatted_logs)
            
            # Store scroll position
            scrollbar = self.logs_text.verticalScrollBar()
            was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
            
            # Set HTML content with terminal-like styling
            self.logs_text.setHtml(f"""
                <html>
                <body style="background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', 'Courier New', 'Monaco', monospace; font-size: 12px; margin: 0; padding: 0;">
                    {html_content if html_content else '<span style="color: #8b949e;">No logs available</span>'}
                </body>
                </html>
            """)
            
            # Auto-scroll to bottom if was at bottom (for auto-refresh)
            if was_at_bottom and self.auto_refresh:
                scrollbar.setValue(scrollbar.maximum())
            
            # Update status
            line_count = len(logs)
            self.status_label.setText(
                self.translator.t("admin.logs.status").format(count=line_count)
            )
        except Exception as e:
            error_html = f'<span style="color: #f85149;">Error loading logs: {e}</span>'
            self.logs_text.setHtml(f"""
                <html>
                <body style="background-color: #0d1117; color: #c9d1d9; font-family: 'Consolas', 'Courier New', 'Monaco', monospace; font-size: 12px;">
                    {error_html}
                </body>
                </html>
            """)
            self.status_label.setText(self.translator.t("admin.logs.error_loading"))
    
    def on_search_changed(self, text):
        """Handle search text change."""
        self.load_logs()
    
    def on_auto_refresh_toggled(self, checked):
        """Handle auto-refresh toggle."""
        self.auto_refresh = checked
        if checked:
            self.refresh_timer.start(2000)
            self.auto_refresh_button.setText("  " + self.translator.t("admin.logs.auto_refresh"))
        else:
            self.refresh_timer.stop()
            self.auto_refresh_button.setText("  " + self.translator.t("admin.logs.auto_refresh_off"))
    
    def on_clear_logs(self):
        """Handle clear logs button."""
        reply = QMessageBox.question(
            self,
            self.translator.t("admin.logs.clear_confirm_title"),
            self.translator.t("admin.logs.clear_confirm_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logging_service.clear_logs()
            self.load_logs()
            QMessageBox.information(
                self,
                self.translator.t("admin.logs.cleared_title"),
                self.translator.t("admin.logs.cleared_message")
            )
    
    def on_export_logs(self):
        """Handle export logs button."""
        default_path = Path.home() / "Desktop" / "StarterAppLauncher_logs.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator.t("admin.logs.export_dialog_title"),
            str(default_path),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            success = self.logging_service.export_logs(Path(file_path))
            if success:
                QMessageBox.information(
                    self,
                    self.translator.t("admin.logs.export_success_title"),
                    self.translator.t("admin.logs.export_success_message").format(path=file_path)
                )
            else:
                QMessageBox.warning(
                    self,
                    self.translator.t("admin.logs.export_error_title"),
                    self.translator.t("admin.logs.export_error_message")
                )
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("admin.logs.title"))
        self.description_label.setText(self.translator.t("admin.logs.description"))
        self.search_input.setPlaceholderText(self.translator.t("admin.logs.search_placeholder"))
        self.refresh_button.setText("  " + self.translator.t("admin.logs.refresh"))
        self.clear_button.setText("  " + self.translator.t("admin.logs.clear"))
        self.export_button.setText("  " + self.translator.t("admin.logs.export"))
        if self.auto_refresh:
            self.auto_refresh_button.setText("  " + self.translator.t("admin.logs.auto_refresh"))
        else:
            self.auto_refresh_button.setText("  " + self.translator.t("admin.logs.auto_refresh_off"))
        self.logs_text.setPlaceholderText(self.translator.t("admin.logs.no_logs"))
        self.load_logs()

