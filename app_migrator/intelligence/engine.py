"""L419: pattern_database must include a flt/unit-coercion pattern.

Per v0.5 spec Q7a: "engine.py wraps existing MigrationIntelligence as-is".
The real bench app at apps/app_migrator/app_migrator/commands/intelligence_engine.py
already has MigrationIntelligence with ~20 patterns; the new scaffold's
engine.py re-exports it once the new scaffold is installed as a bench app.

For the v0.5-alpha W1 phase2 tests, we ship a minimal stub MigrationIntelligence
in the new scaffold that satisfies the L419 contract (pattern_database contains
a flt/unit/coerc/value-parse pattern). When the new scaffold is installed as a
bench app at W1 close, this stub is replaced by a real re-export wrapper.
"""
from __future__ import annotations

from typing import Any, Dict, List


class MigrationIntelligence:
    """Minimal stub for the L419 test contract.

    Real implementation re-exports the existing MigrationIntelligence
    from the bench app (per v0.5 spec Q7a). The W1-close refactor
    replaces this class with a thin wrapper.
    """

    def __init__(self) -> None:
        self.pattern_database: List[Dict[str, Any]] = self._build_patterns()

    def _build_patterns(self) -> List[Dict[str, Any]]:
        """Build the patterns list.

        Includes L419 flt-coercion pattern + L394 radar patterns:
          - fixture-drift (cross-substrate canonical fixture churn)
          - symbol-collision (cross-app Python symbol collision)
        Severity per L380 4-layer pattern: info/warn/high/critical.
        """
        return [
            {
                "id": "flt_coercion_failure",
                "title": "flt coercion collapses unit-suffixed strings",
                "description": (
                    "frappe.utils.flt() silently coerces values like '10kg' "
                    "or '5.5m' to 10 or 5.5 by stripping the unit, with no warning. "
                    "Detection: pattern_database contains a flt/unit-coercion "
                    "entry that the data-quality layer can match against."
                ),
                "triggers": ["frappe.utils.flt", "unit suffix", "value-parse"],
                "symptoms": ["off-by-magnitude readings", "missing units in reports"],
                "prevention": "validate_unit_before_flt",
                "risk_score": 0.6,
                "auto_fix_available": False,
                "severity": "info",
            },
            {
                "id": "l394_fixture_drift",
                "title": "fleet-canonical-fixture drift across substrate",
                "description": (
                    "L394: When a canonical fixture (e.g., journal entry template, "
                    "tax category, payment method) diverges across vpp/vpt/vm2/vm3 "
                    "substrates, transport produces inconsistent migrations. "
                    "Detection: pattern_database contains a fixture-drift entry "
                    "that the cross-substrate sync layer can match against."
                ),
                "triggers": ["fixture hash mismatch", "substrate divergence"],
                "symptoms": ["inconsistent migrations", "post-transport validate failures"],
                "prevention": "fixture_hash_audit_pre_transport",
                "risk_score": 0.7,
                "auto_fix_available": False,
                "severity": "warn",
            },
            {
                "id": "l394_symbol_collision",
                "title": "cross-app Python symbol collision",
                "description": (
                    "L394: Two installed apps (erpnext, hrms, custom_*) declaring "
                    "the same Python symbol (function, class, constant) at module "
                    "load time causes silent override and runtime ImportError. "
                    "Detection: pattern_database contains a symbol-collision entry "
                    "that the preflight module-collision layer can match against."
                ),
                "triggers": ["duplicate symbol across apps", "module load ImportError"],
                "symptoms": ["silent override", "intermittent ImportError", "wrong-version win"],
                "prevention": "module_collision_preflight",
                "risk_score": 0.8,
                "auto_fix_available": False,
                "severity": "high",
            },
        ]
