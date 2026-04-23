"""Simple JSON-backed configuration manager for WeatherApp.

Provides load/save and basic saved-location management. The manager is
intentionally lightweight, dependency-free (stdlib only), and safe to use from
GUI code that expects defensive, non-raising persistence behavior.
"""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any

ConfigData = dict[str, Any]

DEFAULT_CONFIG: ConfigData = {
    "last_location": None,
    "saved_locations": [],
    "refresh_interval_minutes": 10,
    "default_location": None,
}


def _config_paths() -> list[Path]:
    """Return candidate config file paths in preferred order.

    Preferred locations:
    1) ~/.config/weatherapp/config.json
    2) ~/.weatherapp_config.json
    """
    home = Path("~").expanduser()
    primary_path = home / ".config" / "weatherapp" / "config.json"
    fallback_path = home / ".weatherapp_config.json"
    return [primary_path, fallback_path]


@dataclass
class ConfigManager:
    """Manage persisted WeatherApp configuration stored in a JSON file.

    Attributes:
        path: Config file path. When omitted, the first existing preferred path
            is used, or the primary preferred path if no config file exists yet.
        data: In-memory configuration dictionary.
    """

    path: Path | None = None
    data: ConfigData = field(default_factory=lambda: DEFAULT_CONFIG.copy())

    def __post_init__(self) -> None:
        """Resolve the config path, ensure a writable parent when possible, and load data."""
        if self.path is None:
            candidate_paths = _config_paths()
            self.path = next(
                (candidate_path for candidate_path in candidate_paths if candidate_path.exists()),
                candidate_paths[0],
            )

        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            with suppress(Exception):
                self.path = _config_paths()[1]

        self.load()

    @staticmethod
    def _normalize_location(location: str | None) -> str:
        """Return a trimmed location string, or an empty string when blank."""
        return (location or "").strip()

    def _ensure_required_keys(self) -> None:
        """Populate missing top-level config keys with their default values."""
        for key, default_value in DEFAULT_CONFIG.items():
            self.data.setdefault(key, default_value)

    def load(self) -> ConfigData:
        """Load config from disk.

        If the config file is corrupt or unreadable, the file is backed up when
        possible and a fresh default config is written in its place.

        Returns:
            The in-memory configuration dictionary.
        """
        try:
            if self.path.exists():
                with self.path.open("r", encoding="utf-8") as handle:
                    loaded_data = json.load(handle)
                if not isinstance(loaded_data, dict):
                    error_message = "Config root must be a JSON object."
                    raise TypeError(error_message)
                self.data = loaded_data
                self._ensure_required_keys()
                return self.data
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            try:
                backup_path = self.path.with_suffix(self.path.suffix + ".bak")
                self.path.replace(backup_path)
            except OSError:
                pass

        self.data = DEFAULT_CONFIG.copy()
        try:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=2)
        except OSError:
            pass
        return self.data

    def save(self) -> None:
        """Persist the current in-memory configuration to disk.

        Serialization or file-system failures are swallowed to preserve the
        existing defensive, non-raising behavior expected by the GUI.
        """
        try:
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(self.data, handle, indent=2)
        except Exception:
            pass

    def add_location(self, location: str) -> None:
        """Add a location string to saved locations if it is not already present.

        Args:
            location: Human-readable location string to persist.
        """
        normalized_location = self._normalize_location(location)
        if not normalized_location:
            return

        saved_locations = self.data.get("saved_locations") or []
        if normalized_location in saved_locations:
            return

        saved_locations.append(normalized_location)
        self.data["saved_locations"] = saved_locations
        self.save()

    def remove_location(self, location: str) -> None:
        """Remove a saved location if it exists.

        Args:
            location: Human-readable location string to remove.
        """
        normalized_location = self._normalize_location(location)
        if not normalized_location:
            return

        saved_locations = self.data.get("saved_locations") or []
        try:
            saved_locations.remove(normalized_location)
            self.data["saved_locations"] = saved_locations
            self.save()
        except ValueError:
            return

    def clear_all_locations(self) -> None:
        """Clear all saved locations and persist the change."""
        try:
            self.data["saved_locations"] = []
            self.save()
        except Exception:
            return

    def set_last_location(self, location: str) -> None:
        """Persist the most recently used location string.

        Args:
            location: Human-readable location string.
        """
        self.data["last_location"] = self._normalize_location(location)
        self.save()

    def set_default_location(self, location: str) -> None:
        """Persist the preferred default location used at startup.

        Args:
            location: Human-readable location string.
        """
        self.data["default_location"] = self._normalize_location(location)
        self.save()

    def get_saved_locations(self) -> list[str]:
        """Return a copy of the saved locations list."""
        return list(self.data.get("saved_locations") or [])

    def get_last_location(self) -> str | None:
        """Return the last used location, if any."""
        return self.data.get("last_location")

    def get_default_location(self) -> str | None:
        """Return the configured default location, if any."""
        return self.data.get("default_location")
