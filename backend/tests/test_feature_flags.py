"""Tests for feature flags and routing logic."""

import pytest

from app.core.feature_flags import ETLFeatureFlag, FeatureFlagRegistry, RolloutPhase


class TestETLFeatureFlag:
    def test_disabled_always_routes_to_v1(self):
        flag = ETLFeatureFlag(name="test", phase=RolloutPhase.DISABLED, enabled=True)
        assert flag.route_to_v2("user123") is False
        assert flag.route_to_v2("user456") is False

    def test_full_always_routes_to_v2(self):
        flag = ETLFeatureFlag(name="test", phase=RolloutPhase.FULL, enabled=True)
        assert flag.route_to_v2("user123") is True
        assert flag.route_to_v2("user456") is True

    def test_shadow_always_routes_to_v1_but_runs_v2_parallel(self):
        flag = ETLFeatureFlag(name="test", phase=RolloutPhase.SHADOW, enabled=True)
        assert flag.route_to_v2() is False  # Returns v1 to user
        # Shadow mode runs v2 in parallel internally

    def test_canary_percentage_routing(self):
        flag = ETLFeatureFlag(name="test", phase=RolloutPhase.CANARY, enabled=True, v2_percentage=50)
        # Consistent routing per user
        assert flag.route_to_v2("user_a") == flag.route_to_v2("user_a")
        assert flag.route_to_v2("user_b") == flag.route_to_v2("user_b")
        # Different users may route differently
        results = [flag.route_to_v2(f"user_{i}") for i in range(100)]
        # Roughly 50% should be True (within margin)
        true_count = sum(results)
        assert 30 <= true_count <= 70, f"Expected ~50%, got {true_count}%"

    def test_disabled_flag_returns_false_even_with_percentage(self):
        flag = ETLFeatureFlag(name="test", phase=RolloutPhase.CANARY, enabled=False, v2_percentage=100)
        assert flag.route_to_v2("user123") is False


class TestFeatureFlagRegistry:
    def test_get_flag(self):
        registry = FeatureFlagRegistry()
        flag = registry.get("combustibles")
        assert flag is not None
        assert flag.name == "combustibles"
        assert flag.phase == RolloutPhase.DISABLED

    def test_set_phase(self):
        registry = FeatureFlagRegistry()
        registry.set_phase("combustibles", RolloutPhase.FULL)
        assert registry.get("combustibles").phase == RolloutPhase.FULL

    def test_set_percentage(self):
        registry = FeatureFlagRegistry()
        registry.set_percentage("ute", 25)
        assert registry.get("ute").v2_percentage == 25

    def test_percentage_clamped(self):
        registry = FeatureFlagRegistry()
        registry.set_percentage("ose", 150)
        assert registry.get("ose").v2_percentage == 100
        registry.set_percentage("ose", -50)
        assert registry.get("ose").v2_percentage == 0

    def test_enable_disable_v2(self):
        registry = FeatureFlagRegistry()
        assert registry.get("antel").enabled is False
        registry.enable_v2("antel")
        assert registry.get("antel").enabled is True
        registry.disable_v2("antel")
        assert registry.get("antel").enabled is False

    def test_list_all_flags(self):
        registry = FeatureFlagRegistry()
        flags = registry.list_all()
        assert set(flags.keys()) == {"combustibles", "ute", "ose", "antel"}
        assert all(f.phase == RolloutPhase.DISABLED for f in flags.values())
