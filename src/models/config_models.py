"""Configuration data models."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class UIConfig:
    """UI configuration."""
    language: str = "vi"


@dataclass
class AdminConfig:
    """Admin configuration."""
    autostart_app: bool = False
    require_admin: bool = False  # User wants app to always run with admin


@dataclass
class StarterSettings:
    """Starter app settings."""
    trigger_selected_on_startup: bool = False
    delay_seconds: int = 10


@dataclass
class Favourite:
    """Favourite app model."""
    id: str
    name: str
    lnk_path: str
    kind: str = "app"  # browser | app | working_app
    label: str = "App"
    selected: bool = False
    browser_links: List[str] = field(default_factory=list)


@dataclass
class AppConfig:
    """Main application configuration."""
    version: int = 1
    ui: UIConfig = field(default_factory=UIConfig)
    admin: AdminConfig = field(default_factory=AdminConfig)
    starter_settings: StarterSettings = field(default_factory=StarterSettings)
    favourites: List[Favourite] = field(default_factory=list)

