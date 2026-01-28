"""
Feature flags for gradual ETL rollout (TAREA 6+).

Allows fine-grained control over v1/v2 ETL routing without code changes.
Supports percentage-based rollout (e.g., 10% users get v2, rest get v1).
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RolloutPhase(str, Enum):
    DISABLED = "disabled"  # v1 only
    SHADOW = "shadow"  # v1+v2 in parallel (shadow mode)
    CANARY = "canary"  # Small % get v2, rest v1
    GRADUAL = "gradual"  # Percentage-based rollout
    FULL = "full"  # v2 only


class ETLFeatureFlag(BaseModel):
    name: str = Field(..., description="ETL name (combustibles, ute, ose, antel)")
    phase: RolloutPhase = Field(default=RolloutPhase.DISABLED, description="Rollout phase")
    enabled: bool = Field(default=False, description="Whether v2 is enabled at all")
    v2_percentage: int = Field(default=0, description="% of requests routed to v2 (0-100; only used in CANARY/GRADUAL)")

    def route_to_v2(self, user_id: Optional[str] = None) -> bool:
        """Determine if a request should use v2 based on phase and percentage."""
        if self.phase == RolloutPhase.DISABLED or not self.enabled:
            return False
        if self.phase == RolloutPhase.FULL:
            return True
        if self.phase == RolloutPhase.SHADOW:
            # Shadow mode always uses v1 but runs v2 in parallel
            return False
        if self.phase in (RolloutPhase.CANARY, RolloutPhase.GRADUAL):
            # Hash user_id or request_id to deterministically route
            if not user_id:
                return False
            hash_val = hash(user_id) % 100
            return hash_val < self.v2_percentage
        return False


class FeatureFlagRegistry:
    """Registry of feature flags for all ETL services."""

    def __init__(self):
        # Default: all disabled (use v1)
        self._flags = {
            "combustibles": ETLFeatureFlag(name="combustibles", phase=RolloutPhase.DISABLED),
            "ute": ETLFeatureFlag(name="ute", phase=RolloutPhase.DISABLED),
            "ose": ETLFeatureFlag(name="ose", phase=RolloutPhase.DISABLED),
            "antel": ETLFeatureFlag(name="antel", phase=RolloutPhase.DISABLED),
        }
        self._load_from_file()

    def _load_from_file(self) -> None:
        """Load feature flags from JSON file if it exists"""
        try:
            from pathlib import Path

            config_file = Path(__file__).parent.parent.parent / "feature_flags_config.json"
            if config_file.exists():
                import json

                with open(config_file, "r") as f:
                    config = json.load(f)
                    for service_name, cfg in config.items():
                        if service_name in self._flags:
                            phase = RolloutPhase(cfg.get("phase", "disabled"))
                            flag = ETLFeatureFlag(
                                name=cfg.get("name", service_name),
                                phase=phase,
                                enabled=cfg.get("enabled", False),
                                v2_percentage=cfg.get("v2_percentage", 0),
                            )
                            self._flags[service_name] = flag
        except Exception:
            # If loading fails, continue with defaults
            pass

    def _save_to_file(self) -> None:
        """Save feature flags to JSON file"""
        try:
            import json
            from pathlib import Path

            config_file = Path(__file__).parent.parent.parent / "feature_flags_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)

            config = {}
            for name, flag in self._flags.items():
                config[name] = {
                    "name": flag.name,
                    "phase": flag.phase.value,
                    "enabled": flag.enabled,
                    "v2_percentage": flag.v2_percentage,
                }

            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            # If saving fails, continue anyway
            pass

    def get(self, etl_name: str) -> Optional[ETLFeatureFlag]:
        return self._flags.get(etl_name)

    def update(self, etl_name: str, flag: ETLFeatureFlag) -> None:
        if etl_name in self._flags:
            self._flags[etl_name] = flag
            self._save_to_file()

    def list_all(self) -> dict:
        return dict(self._flags)

    def set_phase(self, etl_name: str, phase: RolloutPhase) -> None:
        if flag := self.get(etl_name):
            flag.phase = phase
            self._save_to_file()

    def set_percentage(self, etl_name: str, percentage: int) -> None:
        if flag := self.get(etl_name):
            flag.v2_percentage = max(0, min(100, percentage))
            self._save_to_file()

    def enable_v2(self, etl_name: str) -> None:
        if flag := self.get(etl_name):
            flag.enabled = True
            self._save_to_file()

    def disable_v2(self, etl_name: str) -> None:
        if flag := self.get(etl_name):
            flag.enabled = False
            self._save_to_file()


# Global registry
feature_flags = FeatureFlagRegistry()
