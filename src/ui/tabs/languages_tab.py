"""Languages tab for language selection."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QRadioButton,
    QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt


class LanguagesTab(QWidget):
    """Languages tab with language selector."""
    
    def __init__(self, config_store, translator, main_window, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel(self.translator.t("admin.languages.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        layout.addSpacing(20)
        
        # Language selection card
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(500)
        card_layout = QVBoxLayout(card)
        
        # Language radio buttons
        self.lang_group = QButtonGroup(self)
        
        self.radio_vi = QRadioButton(self.translator.t("admin.languages.vi"))
        self.radio_en = QRadioButton(self.translator.t("admin.languages.en"))
        self.radio_ru = QRadioButton(self.translator.t("admin.languages.ru"))
        
        self.lang_group.addButton(self.radio_vi, 0)
        self.lang_group.addButton(self.radio_en, 1)
        self.lang_group.addButton(self.radio_ru, 2)
        
        # Set current language
        current_lang = self.config_store.get_language()
        if current_lang == "vi":
            self.radio_vi.setChecked(True)
        elif current_lang == "en":
            self.radio_en.setChecked(True)
        elif current_lang == "ru":
            self.radio_ru.setChecked(True)
        
        # Connect signals
        self.radio_vi.clicked.connect(lambda: self.on_language_changed("vi"))
        self.radio_en.clicked.connect(lambda: self.on_language_changed("en"))
        self.radio_ru.clicked.connect(lambda: self.on_language_changed("ru"))
        
        card_layout.addWidget(self.radio_vi)
        card_layout.addWidget(self.radio_en)
        card_layout.addWidget(self.radio_ru)
        
        layout.addWidget(card)
        layout.addStretch()
    
    def on_language_changed(self, language):
        """Handle language change."""
        self.config_store.set_language(language)
        self.translator.set_language(language)
        self.main_window.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("admin.languages.title"))
        self.radio_vi.setText(self.translator.t("admin.languages.vi"))
        self.radio_en.setText(self.translator.t("admin.languages.en"))
        self.radio_ru.setText(self.translator.t("admin.languages.ru"))

