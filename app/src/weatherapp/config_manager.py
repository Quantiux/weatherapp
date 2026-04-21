"""Simple JSON-backed configuration manager for WeatherApp.

Provides load/save and basic saved-location management. Designed to be
lightweight, dependency-free (stdlib only), and safe for use from the GUI
thread. The ConfigManager performs file I/O which is quick for small JSON
files; if running in a constrained environment you may move calls to a
background thread. For Version-5.4 we keep the API simple and synchronous.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import os
from typing import List, Dict, Optional

DEFAULT_CONFIG = {
    "last_location": None,
    "saved_locations": [],
    "refresh_interval_minutes": 10,
    "default_location": None,
}


def _config_paths() -> List[Path]:
    """Return candidate config file paths in preferred order.

    1) ~/.config/weatherapp/config.json
    2) ~/.weatherapp_config.json
    """
    home = Path(os.path.expanduser("~"))
    cfg1 = home / ".config" / "weatherapp" / "config.json"
    cfg2 = home / ".weatherapp_config.json"
    return [cfg1, cfg2]


@dataclass
class ConfigManager:
    path: Optional[Path] = None
    data: Dict = field(default_factory=lambda: DEFAULT_CONFIG.copy())

    def __post_init__(self):
        if self.path is None:
            # choose the first existing path or the default preferred path
            candidates = _config_paths()
            for p in candidates:
                if p.exists():
                    self.path = p
                    break
            if self.path is None:
                # prefer ~/.config/weatherapp/config.json
                self.path = candidates[0]
        # ensure parent directory exists when saving
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            # If this fails (e.g., home not writable), fall back to the second path
            try:
                self.path = _config_paths()[1]
            except Exception:
                pass
        # Load existing config if present
        self.load()

    def load(self) -> Dict:
        """Load config from disk. If the file is corrupted, back it up and
        recreate a fresh config file.
        """
        try:
            if self.path.exists():
                with self.path.open("r", encoding="utf-8") as fh:
                    self.data = json.load(fh)
                    # Ensure required keys exist
                    if "saved_locations" not in self.data:
                        self.data["saved_locations"] = []
                    if "refresh_interval_minutes" not in self.data:
                        self.data["refresh_interval_minutes"] = 10
                    return self.data
        except Exception:
            # Backup corrupted file and reset
            try:
                bak = self.path.with_suffix(self.path.suffix + ".bak")
                self.path.replace(bak)
            except Exception:
                pass
        # If we reach here, write default config
        self.data = DEFAULT_CONFIG.copy()
        try:
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except Exception:
            # Swallow errors to avoid crashing GUI on startup; callers should
            # detect missing persistence by verifying file existence.
            pass
        return self.data

    def save(self) -> None:
        """Save current config data to disk."""
        try:
            with self.path.open("w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
        except Exception:
            # Do not raise — GUI should surface persistence failures if needed.
            pass

    def add_location(self, location: str) -> None:
        """Add a location string to saved_locations if not already present."""
        loc = (location or "").strip()
        if not loc:
            return
        saved = self.data.get("saved_locations") or []
        if loc in saved:
            return
        saved.append(loc)
        self.data["saved_locations"] = saved
        self.save()

    def remove_location(self, location: str) -> None:
        """Remove a location string if present."""
        loc = (location or "").strip()
        if not loc:
            return
        saved = self.data.get("saved_locations") or []
        try:
            saved.remove(loc)
            self.data["saved_locations"] = saved
            self.save()
        except ValueError:
            return

    def clear_all_locations(self) -> None:
        """Clear all saved locations.

        Resets the saved_locations list to empty and persists the change. This
        method is defensive and will swallow I/O errors to avoid crashing the
        GUI during shutdown or in read-only environments.
        """
        try:
            self.data["saved_locations"] = []
            self.save()
        except Exception:
            # Swallow errors to preserve existing defensive behavior
            return

    def set_last_location(self, location: str) -> None:
        self.data["last_location"] = (location or "").strip()
        self.save()

    def set_default_location(self, location: str) -> None:
        """Set a persistent default location string that the app will prefer on startup.

        The value is stored under the "default_location" key in the config JSON.
        """
        self.data["default_location"] = (location or "").strip()
        self.save()

    def get_saved_locations(self) -> List[str]:
        return list(self.data.get("saved_locations") or [])

    def get_last_location(self) -> Optional[str]:
        return self.data.get("last_location")

    def get_default_location(self) -> Optional[str]:
        """Return the configured default location or None if not set."""
        return self.data.get("default_location")
