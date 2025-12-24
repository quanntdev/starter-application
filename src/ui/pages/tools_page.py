"""Tools page for managing custom tools."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path

from ui.components.tool_item import ToolItemWidget
from models.config_models import Tool
from tools.clipboard.tool_manager import ClipboardToolManager
from tools.clipboard.storage import ClipboardStorage


class ToolsPage(QWidget):
    """Tools page displaying user's custom tools."""
    
    # Signal to request navigation to clipboard history
    view_clipboard_history = Signal()
    
    def __init__(self, config_store, translator, clipboard_storage=None, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        
        # Use provided storage or create new one
        if clipboard_storage is None:
            clipboard_storage = ClipboardStorage()
        self.clipboard_storage = clipboard_storage
        
        # Initialize clipboard tool manager with shared storage
        self.clipboard_manager = ClipboardToolManager()
        # Update manager's storage to use shared instance
        self.clipboard_manager.storage = self.clipboard_storage
        self.clipboard_manager.service.storage = self.clipboard_storage
        
        self.clipboard_manager.state_changed.connect(self.on_clipboard_state_changed)
        self.clipboard_manager.view_details_requested.connect(self.view_clipboard_history.emit)
        
        # Store tool widgets for state updates
        self.tool_widgets = {}
        
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
        self.tools_layout.setSpacing(0)
        self.tools_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Create grid layout for tools
        from PySide6.QtWidgets import QGridLayout
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Wrap grid in a widget - no max width, let it flow naturally
        grid_widget = QWidget()
        grid_widget.setLayout(self.grid_layout)
        # Set size policy to prevent stretching horizontally
        from PySide6.QtWidgets import QSizePolicy
        grid_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        # Add grid widget aligned to left, no stretch after it
        self.tools_layout.addWidget(grid_widget, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
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
        
        # Display tools in grid (1 column - each row 1 item)
        columns = 1
        for i, tool in enumerate(tools):
            row = i // columns
            col = i % columns
            
            # Check if this is clipboard tool
            is_running = False
            on_view_details = None
            if tool.id == "clipboard_copy":
                # Only RUNNING state shows as Active, PAUSED and IDLE show as Deactive
                is_running = self.clipboard_manager.get_state() == "RUNNING"
                on_view_details = self.on_view_clipboard_details
            
            tool_widget = ToolItemWidget(
                tool,
                self.translator,
                on_use_callback=self.on_tool_use,
                on_view_details_callback=on_view_details,
                is_running=is_running
            )
            self.tool_widgets[tool.id] = tool_widget
            self.grid_layout.addWidget(tool_widget, row, col)
    
    def get_sample_tools(self) -> list:
        """Get sample tools for demonstration."""
        tools = []
        
        # Clipboard Copy tool
        clipboard_tool = Tool(
            id="clipboard_copy",
            name="Clipboard Copy",
            icon="fa5s.clipboard",
            tags=["Productivity", "Clipboard"],
            description="Capture and manage copied text. Quick view on the left sidebar.",
            status="inactive",
            tag="free"
        )
        tools.append(clipboard_tool)
        
        # Coming soon tools - beautiful design
        coming_soon_tool_1 = Tool(
            id="coming_soon_1",
            name="Tool 1",
            icon="fa5s.rocket",
            tags=["Coming soon"],
            description="",
            status="inactive",
            tag="free"
        )
        tools.append(coming_soon_tool_1)
        
        coming_soon_tool_2 = Tool(
            id="coming_soon_2",
            name="Tool 2",
            icon="fa5s.rocket",
            tags=["Coming soon"],
            description="",
            status="inactive",
            tag="free"
        )
        tools.append(coming_soon_tool_2)
        
        coming_soon_tool_3 = Tool(
            id="coming_soon_3",
            name="Tool 3",
            icon="fa5s.rocket",
            tags=["Coming soon"],
            description="",
            status="inactive",
            tag="free"
        )
        tools.append(coming_soon_tool_3)
        
        return tools
    
    def on_tool_use(self, tool: Tool):
        """Handle tool use button click."""
        if tool.id == "clipboard_copy":
            # Handle clipboard tool Run/Pause
            state = self.clipboard_manager.get_state()
            if state == "IDLE" or state == "PAUSED":
                self.clipboard_manager.start()
            elif state == "RUNNING":
                self.clipboard_manager.pause()
        else:
            # TODO: Implement other tool execution logic
            print(f"Using tool: {tool.name}")
    
    def on_view_clipboard_details(self, tool: Tool):
        """Handle view clipboard details button click."""
        self.view_clipboard_history.emit()
    
    def on_clipboard_state_changed(self, state: str):
        """Handle clipboard tool state change."""
        if "clipboard_copy" in self.tool_widgets:
            widget = self.tool_widgets["clipboard_copy"]
            # Only RUNNING state shows as Active, PAUSED and IDLE show as Deactive
            is_running = state == "RUNNING"
            widget.update_state(is_running)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("tools.title"))
        self.description_label.setText(self.translator.t("tools.description"))
        self.load_tools()
