"""Configuration store with persistence."""
import json
import os
from pathlib import Path
from typing import List, Optional

from models.config_models import AppConfig, UIConfig, AdminConfig, StarterSettings, Favourite


class ConfigStore:
    """Store for application configuration with atomic save."""
    
    def __init__(self):
        # Use absolute path to ensure config persists across app rebuilds
        # APPDATA is a user-specific directory that doesn't change with app location
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback to user home directory if APPDATA is not set
            appdata = os.path.expanduser("~")
        self.config_dir = Path(appdata).resolve() / "StarterAppLauncher"
        self.config_file = self.config_dir.resolve() / "config.json"
        self.config: Optional[AppConfig] = None
    
    def load(self):
        """Load configuration from file or create default."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config = self._deserialize(data)
            except Exception:
                self.config = AppConfig()
        else:
            self.config = AppConfig()
            self.save()
    
    def save(self):
        """Save configuration to file atomically."""
        if self.config is None:
            return
        
        data = self._serialize(self.config)
        
        # Atomic write
        temp_file = self.config_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        temp_file.replace(self.config_file)
    
    def _serialize(self, config: AppConfig) -> dict:
        """Serialize config to dict."""
        return {
            "version": config.version,
            "ui": {"language": config.ui.language},
            "admin": {
                "autostart_app": config.admin.autostart_app,
                "require_admin": config.admin.require_admin,
            },
            "starter_settings": {
                "trigger_selected_on_startup": config.starter_settings.trigger_selected_on_startup,
                "delay_seconds": config.starter_settings.delay_seconds,
            },
            "favourites": [
                {
                    "id": fav.id,
                    "name": fav.name,
                    "lnk_path": fav.lnk_path,
                    "kind": fav.kind,
                    "label": fav.label,
                    "selected": fav.selected,
                    "browser_links": fav.browser_links,
                }
                for fav in config.favourites
            ],
            "email_registered": config.email_registered,
        }
    
    def _deserialize(self, data: dict) -> AppConfig:
        """Deserialize dict to config."""
        ui = UIConfig(**data.get("ui", {}))
        admin = AdminConfig(**data.get("admin", {}))
        
        # Deserialize starter_settings with defaults
        starter_settings_data = data.get("starter_settings", {})
        # If trigger_selected_on_startup key doesn't exist, default to True
        if "trigger_selected_on_startup" not in starter_settings_data:
            starter_settings_data["trigger_selected_on_startup"] = True
        # If delay_seconds key doesn't exist, default to 1 second
        if "delay_seconds" not in starter_settings_data:
            starter_settings_data["delay_seconds"] = 1
        starter_settings = StarterSettings(**starter_settings_data)
        
        favourites = []
        for fav_data in data.get("favourites", []):
            favourites.append(Favourite(**fav_data))
        
        return AppConfig(
            version=data.get("version", 1),
            ui=ui,
            admin=admin,
            starter_settings=starter_settings,
            favourites=favourites,
            email_registered=data.get("email_registered", False),
        )
    
    # Convenience methods
    def get_language(self) -> str:
        """Get current language."""
        return self.config.ui.language if self.config else "en"  # Default changed to English
    
    def set_language(self, language: str):
        """Set language and save."""
        if self.config:
            self.config.ui.language = language
            self.save()
    
    def get_favourites(self) -> List[Favourite]:
        """Get favourites list."""
        return self.config.favourites if self.config else []
    
    def add_favourite(self, favourite: Favourite):
        """Add favourite and save."""
        if self.config:
            self.config.favourites.append(favourite)
            self.save()
    
    def update_favourite(self, favourite: Favourite):
        """Update favourite and save."""
        if self.config:
            for i, fav in enumerate(self.config.favourites):
                if fav.id == favourite.id:
                    self.config.favourites[i] = favourite
                    break
            self.save()
    
    def delete_favourite(self, favourite_id: str):
        """Delete favourite and save."""
        if self.config:
            self.config.favourites = [
                fav for fav in self.config.favourites if fav.id != favourite_id
            ]
            self.save()
    
    def get_starter_settings(self) -> StarterSettings:
        """Get starter settings."""
        return self.config.starter_settings if self.config else StarterSettings()
    
    def update_starter_settings(self, settings: StarterSettings):
        """Update starter settings and save."""
        if self.config:
            self.config.starter_settings = settings
            self.save()
    
    def get_autostart_enabled(self) -> bool:
        """Get autostart status."""
        return self.config.admin.autostart_app if self.config else False
    
    def set_autostart_enabled(self, enabled: bool):
        """Set autostart status and save."""
        if self.config:
            self.config.admin.autostart_app = enabled
            self.save()
    
    def get_require_admin(self) -> bool:
        """Get require admin preference."""
        return self.config.admin.require_admin if self.config else False
    
    def set_require_admin(self, required: bool):
        """Set require admin preference and save."""
        if self.config:
            self.config.admin.require_admin = required
            self.save()
    
    def is_email_registered(self) -> bool:
        """Check if email is registered."""
        return self.config.email_registered if self.config else False
    
    def set_email_registered(self, registered: bool):
        """Set email registration status and save."""
        if self.config:
            self.config.email_registered = registered
            self.save()

