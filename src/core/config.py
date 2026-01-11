"""
Configuration Manager

Handles persistent application settings.
"""
import os
import json
from typing import Any, Optional


DEFAULT_CONFIG = {
    "output_folder": os.path.expanduser("~/Research/Papers"),
    "naming_format": "default",
    "check_updates_on_startup": True,
    "watch_folder_enabled": False,
    "watch_folder_path": "",
    "auto_confirm": False,
    "default_citation_format": "bibtex",
}


class ConfigManager:
    """Manages application configuration persistence."""

    _instance: Optional['ConfigManager'] = None

    def __new__(cls, path: str = "data/config.json"):
        """Singleton pattern to ensure single config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, path: str = "data/config.json"):
        if self._initialized:
            return

        self.path = path
        self._config = DEFAULT_CONFIG.copy()
        self._load()
        self._initialized = True

    def _load(self):
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    stored = json.load(f)
                    # Merge with defaults (stored values override defaults)
                    self._config.update(stored)
        except Exception as e:
            print(f"Failed to load config: {e}")

    def save(self):
        """Save configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self.save()

    def get_output_folder(self) -> str:
        """Get the output folder path, expanding user directory."""
        folder = self.get("output_folder", DEFAULT_CONFIG["output_folder"])
        return os.path.expanduser(folder)

    def set_output_folder(self, folder: str):
        """Set the output folder path."""
        self.set("output_folder", folder)

    def get_naming_format(self) -> str:
        """Get the naming format."""
        return self.get("naming_format", "default")

    def set_naming_format(self, format_name: str):
        """Set the naming format."""
        self.set("naming_format", format_name)

    def is_watch_folder_enabled(self) -> bool:
        """Check if watch folder mode is enabled."""
        return self.get("watch_folder_enabled", False)

    def get_watch_folder_path(self) -> str:
        """Get the watch folder path."""
        return os.path.expanduser(self.get("watch_folder_path", ""))

    def set_watch_folder(self, enabled: bool, path: str = ""):
        """Set watch folder settings."""
        self.set("watch_folder_enabled", enabled)
        if path:
            self.set("watch_folder_path", path)

    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._config = DEFAULT_CONFIG.copy()
        self.save()

    @property
    def all(self) -> dict:
        """Get all configuration as dictionary."""
        return self._config.copy()
