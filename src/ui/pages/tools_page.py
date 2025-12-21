"""Tools page for managing custom tools."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PySide6.QtCore import Qt
from pathlib import Path

from ui.components.tool_item import ToolItemWidget
from models.config_models import Tool


class ToolsPage(QWidget):
    """Tools page displaying user's custom tools."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.init_ui()
        self.load_tools()
    
    def init_ui(self):
        """Initialize page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel(self.translator.t("tools.title"))
        self.title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        """)
        layout.addWidget(self.title_label)
        
        # Description
        self.description_label = QLabel(self.translator.t("tools.description"))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            font-size: 15px;
            color: #a0a0a0;
            line-height: 1.6;
            margin-top: 8px;
            margin-bottom: 32px;
        """)
        layout.addWidget(self.description_label)
        
        # Scroll area for tools grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Tools container
        self.tools_container = QWidget()
        self.tools_layout = QHBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(20)
        
        # Create grid layout for tools
        from PySide6.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(24)
        
        # Wrap grid in a widget
        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        
        self.tools_layout.addWidget(grid_widget)
        self.tools_layout.addStretch()
        
        scroll.setWidget(self.tools_container)
        layout.addWidget(scroll, 1)
    
    def load_tools(self):
        """Load and display tools."""
        # Clear existing tools
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get tools from config (for now, use sample data)
        # TODO: Load from config_store when implemented
        tools = self.get_sample_tools()
        
        # Display tools in grid (2 columns)
        columns = 2
        for i, tool in enumerate(tools):
            row = i // columns
            col = i % columns
            
            tool_widget = ToolItemWidget(
                tool,
                self.translator,
                on_use_callback=self.on_tool_use
            )
            self.grid_layout.addWidget(tool_widget, row, col)
    
    def get_sample_tools(self) -> list:
        """Get sample tools for demonstration."""
        # This will be replaced with actual tools from config_store
        return [
            Tool(
                id="tool_1",
                name="File Organizer",
                icon="fa5s.folder-open",
                tags=["File Management", "Automation"],
                description="Automatically organize files in your Downloads folder by file type and date.",
                status="active",
                tag="free"
            ),
            Tool(
                id="tool_2",
                name="System Cleaner",
                icon="fa5s.broom",
                tags=["System", "Maintenance"],
                description="Clean temporary files, cache, and optimize your system performance.",
                status="inactive",
                tag="free"
            ),
            Tool(
                id="tool_3",
                name="Network Monitor",
                icon="fa5s.network-wired",
                tags=["Network", "Monitoring"],
                description="Monitor network traffic and bandwidth usage in real-time.",
                status="active",
                tag="free"
            ),
            Tool(
                id="tool_4",
                name="Screenshot Tool",
                icon="fa5s.camera",
                tags=["Media", "Productivity"],
                description="Take screenshots with advanced editing and annotation features.",
                status="inactive",
                tag="free"
            ),
        ]
    
    def on_tool_use(self, tool: Tool):
        """Handle tool use button click."""
        # TODO: Implement tool execution logic
        print(f"Using tool: {tool.name}")
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("tools.title"))
        self.description_label.setText(self.translator.t("tools.description"))
        self.load_tools()

