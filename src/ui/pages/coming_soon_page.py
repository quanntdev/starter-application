"""Coming soon placeholder page."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ComingSoonPage(QWidget):
    """Coming soon empty state page."""
    
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.init_ui()
    
    def init_ui(self):
        """Initialize the page UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Card container
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(400)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel("🚀")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        self.title_label = QLabel(self.translator.t("sidebar.coming_soon_title"))
        self.title_label.setStyleSheet("font-size: 24px; font-weight: 600;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        self.desc_label = QLabel(self.translator.t("sidebar.coming_soon_desc"))
        self.desc_label.setStyleSheet("font-size: 14px; color: #a0a0a0;")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(16)
        card_layout.addWidget(self.title_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.desc_label)
        
        layout.addWidget(card)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("sidebar.coming_soon_title"))
        self.desc_label.setText(self.translator.t("sidebar.coming_soon_desc"))

