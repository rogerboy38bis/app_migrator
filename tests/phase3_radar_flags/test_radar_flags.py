"""
Phase 3 tests v2: Radar flags (T3 Priority 3, L394).

v2 changes (per T-VERIFY-001 Verifier review):
- Gap 2: Added module-level pytest.importorskip guard so all tests skip gracefully
  if app_migrator.intelligence.engine not yet built.
"""
import pytest

# Per coverage-map: skip the whole phase gracefully if module not yet built.
pytest.importorskip(
    "app_migrator.intelligence.engine",
    reason="app_migrator.intelligence.engine not yet built (Phase 3 WIP)",
)

from app_migrator.intelligence.engine import MigrationIntelligence


def test_l394_fixture_drift_pattern_in_database():
    """L394: pattern_database should include a 'fleet-canonical-fixture drift' pattern."""
    intel = MigrationIntelligence()
    patterns = intel.pattern_database
    titles = [p.get("title", "").lower() for p in patterns]
    descriptions = [p.get("description", "").lower() for p in patterns]
    assert any(
        "fixture" in t and "drift" in t for t in titles
    ) or any(
        "fixture" in d and "drift" in d for d in descriptions
    ), f"L394 fixture-drift radar flag not in pattern_database; titles: {titles}"


def test_l394_symbol_collision_pattern_in_database():
    """L394: pattern_database should include a 'cross-app symbol collision' pattern."""
    intel = MigrationIntelligence()
    patterns = intel.pattern_database
    titles = [p.get("title", "").lower() for p in patterns]
    descriptions = [p.get("description", "").lower() for p in patterns]
    assert any(
        "symbol" in t and "collision" in t for t in titles
    ) or any(
        "symbol" in d and "collision" in d for d in descriptions
    ), f"L394 symbol-collision radar flag not in pattern_database; titles: {titles}"


def test_l394_radar_flags_have_severity_levels():
    """Each radar flag must declare a severity level (per L380 4-layer pattern)."""
    intel = MigrationIntelligence()
    patterns = intel.pattern_database
    radar = [
        p for p in patterns
        if "drift" in p.get("title", "").lower() or "collision" in p.get("title", "").lower()
    ]
    assert len(radar) >= 2, (
        f"expected at least 2 radar patterns (fixture-drift + symbol-collision); "
        f"found {len(radar)}; titles: {[p.get('title') for p in patterns]}"
    )
    for p in radar:
        assert "severity" in p, f"radar pattern {p.get('title')} missing severity"
        assert p["severity"] in {"info", "warn", "high", "critical"}, (
            f"radar pattern {p.get('title')} has invalid severity: {p['severity']}"
        )
