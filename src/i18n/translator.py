"""Translator for i18n with vi/en/ru support."""
import json
from pathlib import Path
from typing import Dict


class Translator:
    """Translator with language support for vi/en/ru."""
    
    def __init__(self):
        self.current_language = "en"  # Default language changed to English
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_locales()
    
    def load_locales(self):
        """Load all locale files."""
        locale_dir = Path(__file__).parent / "locales"
        
        for lang in ["vi", "en", "ru"]:
            locale_file = locale_dir / f"{lang}.json"
            if locale_file.exists():
                with open(locale_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            else:
                self.translations[lang] = {}
    
    def set_language(self, language: str):
        """Set current language."""
        if language in self.translations:
            self.current_language = language
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key to current language with optional formatting."""
        translations = self.translations.get(self.current_language, {})
        
        # Fallback to English if key not found
        if key not in translations:
            translations = self.translations.get("en", {})
        
        # Fallback to key if still not found
        text = translations.get(key, key)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text

