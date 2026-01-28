"""
Persistence layer for feature flags (JSON-based for simplicity)
In production, this would use PostgreSQL
"""

import json
from pathlib import Path
from typing import Dict, Optional

from .feature_flags import ETLFeatureFlag, RolloutPhase


class FeatureFlagStorage:
    """Persistent storage for feature flags"""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            # Default: project root
            self.storage_path = Path(__file__).parent.parent.parent / "feature_flags_config.json"
        else:
            self.storage_path = Path(storage_path)

    def load(self) -> Dict[str, dict]:
        """Load feature flags from JSON file"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return self._default_config()

    def save(self, flags: Dict[str, ETLFeatureFlag]) -> None:
        """Save feature flags to JSON file"""
        config = {}
        for name, flag in flags.items():
            config[name] = {
                "name": flag.name,
                "phase": flag.phase.value,
                "enabled": flag.enabled,
                "v2_percentage": flag.v2_percentage,
            }

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.storage_path, "w") as f:
            json.dump(config, f, indent=2)

    def _default_config(self) -> Dict[str, dict]:
        """Return default configuration"""
        return {
            "combustibles": {
                "name": "combustibles",
                "phase": RolloutPhase.DISABLED.value,
                "enabled": False,
                "v2_percentage": 0,
            },
            "ute": {"name": "ute", "phase": RolloutPhase.DISABLED.value, "enabled": False, "v2_percentage": 0},
            "ose": {"name": "ose", "phase": RolloutPhase.DISABLED.value, "enabled": False, "v2_percentage": 0},
            "antel": {"name": "antel", "phase": RolloutPhase.DISABLED.value, "enabled": False, "v2_percentage": 0},
        }


# Global storage instance
feature_flag_storage = FeatureFlagStorage()
