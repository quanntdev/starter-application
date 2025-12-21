"""Coming soon placeholder page."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ComingSoonPage(QWidget):
    """Coming soon page with automation feature announcement."""
    
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.init_ui()
    
    def init_ui(self):
        """Initialize the page UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Card container
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel("🚀")
        icon_label.setStyleSheet("font-size: 80px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title
        self.title_label = QLabel(self.translator.t("coming_soon.title"))
        self.title_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #e0e0e0;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main description
        self.main_desc_label = QLabel(self.translator.t("coming_soon.main_description"))
        self.main_desc_label.setStyleSheet("font-size: 16px; color: #c0c0c0; line-height: 1.6;")
        self.main_desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_desc_label.setWordWrap(True)
        
        # Feature description
        self.feature_desc_label = QLabel(self.translator.t("coming_soon.feature_description"))
        self.feature_desc_label.setStyleSheet("font-size: 14px; color: #a0a0a0; line-height: 1.8; padding: 20px; background-color: #1a1a1a; border-radius: 8px;")
        self.feature_desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.feature_desc_label.setWordWrap(True)
        
        # Call to action
        self.cta_label = QLabel(self.translator.t("coming_soon.call_to_action"))
        self.cta_label.setStyleSheet("font-size: 15px; color: #4a9eff; font-weight: 600; margin-top: 10px;")
        self.cta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cta_label.setWordWrap(True)
        
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.main_desc_label)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.feature_desc_label)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.cta_label)
        
        layout.addWidget(card)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("coming_soon.title"))
        self.main_desc_label.setText(self.translator.t("coming_soon.main_description"))
        self.feature_desc_label.setText(self.translator.t("coming_soon.feature_description"))
        self.cta_label.setText(self.translator.t("coming_soon.call_to_action"))

