"""
Shadow mode executor to run ETL v1 and v2 in parallel, compare outputs,
and return v1 results while logging discrepancies.

Use cases:
- Run during shadow/observation period before switching traffic to v2.
- Capture mismatches in success flag and records processed.
- Provide structured output for logging or persistence.
"""

import asyncio
import logging
import time
from types import SimpleNamespace
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ShadowModeExecutor:
    """Executes ETL v1 and v2 in parallel and compares the results."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def run_shadow(self, etl_name: str) -> Dict[str, Any]:
        """
        Run v1 and v2 ETL in parallel, compare their normalized outputs, and
        return v1 results while logging discrepancies.
        """
        etl_v1, etl_v2 = self._get_etl_pair(etl_name)

        # Run both ETLs concurrently
        v1_result, v2_result = await asyncio.gather(
            self._safe_run(etl_v1), self._safe_run(etl_v2)
        )

        comparison = self.compare_results(v1_result, v2_result)

        if comparison["match"]:
            logger.info("Shadow mode matched for %s", etl_name)
        else:
            logger.warning(
                "Shadow mode discrepancy for %s: %s", etl_name, comparison["differences"]
            )

        # Return v1 response to avoid impacting users
        return {
            "shadow_mode": True,
            "etl": etl_name,
            "v1": v1_result,
            "v2": v2_result,
            "comparison": comparison,
            "returned": v1_result,
        }

    async def _safe_run(self, etl) -> Dict[str, Any]:
        """Run ETL safely, capturing exceptions and normalizing output."""
        start = time.monotonic()
        try:
            raw = await etl.run()
            duration = time.monotonic() - start
            return self._normalize_result(raw, duration)
        except Exception as exc:  # pragma: no cover - defensive
            duration = time.monotonic() - start
            logger.error("Shadow mode ETL failed: %s", exc)
            return {
                "success": False,
                "records_processed": 0,
                "errors": [str(exc)],
                "duration_seconds": duration,
                "raw": None,
            }

    def _normalize_result(self, result: Optional[Dict[str, Any]], duration: float) -> Dict[str, Any]:
        """Normalize ETL result to a common shape."""
        if result is None:
            return {
                "success": False,
                "records_processed": 0,
                "errors": ["Result is None"],
                "duration_seconds": duration,
                "raw": None,
            }

        success = bool(result.get("success", True))
        records_processed = self._extract_records(result)
        errors = result.get("errors", []) or ([] if success else [result.get("message", "")])

        return {
            "success": success,
            "records_processed": records_processed,
            "errors": [e for e in errors if e],
            "duration_seconds": result.get("duration_seconds", duration),
            "raw": result,
        }

    def _extract_records(self, result: Dict[str, Any]) -> Optional[int]:
        """Extract a best-effort records_processed value from various keys."""
        for key in (
            "records_processed",
            "records_loaded",
            "records_extracted",
            "records",
        ):
            if key in result:
                try:
                    return int(result[key])
                except (TypeError, ValueError):
                    continue
        return None

    def compare_results(self, v1: Dict[str, Any], v2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare normalized results and report differences."""
        differences = {}
        for field in ("success", "records_processed"):
            if v1.get(field) != v2.get(field):
                differences[field] = {"v1": v1.get(field), "v2": v2.get(field)}

        match = len(differences) == 0
        return {"match": match, "differences": differences}

    def _get_etl_pair(self, etl_name: str) -> Tuple[Any, Any]:
        """Instantiate v1 and v2 ETLs for the requested name."""
        if etl_name == "combustibles":
            from app.etl.combustibles import CombustiblesETL
            from app.etl.combustibles_v2 import CombustiblesETLv2

            return CombustiblesETL(self.db_session), CombustiblesETLv2(self.db_session)

        if etl_name == "ute":
            from app.etl.utilities import UtilitiesETL
            from app.etl.ute_v2 import UTEETLv2

            util = UtilitiesETL(self.db_session)
            v1_runner = self._wrap_utilities_method(util.run_ute)
            return v1_runner, UTEETLv2(self.db_session)

        if etl_name == "ose":
            from app.etl.utilities import UtilitiesETL
            from app.etl.ose_v2 import OSEETLv2

            util = UtilitiesETL(self.db_session)
            v1_runner = self._wrap_utilities_method(util.run_ose)
            return v1_runner, OSEETLv2(self.db_session)

        if etl_name == "antel":
            from app.etl.utilities import UtilitiesETL
            from app.etl.antel_v2 import AntelETLv2

            util = UtilitiesETL(self.db_session)
            v1_runner = self._wrap_utilities_method(util.run_antel)
            return v1_runner, AntelETLv2(self.db_session)

        raise ValueError(f"Unknown ETL name: {etl_name}")

    def _wrap_utilities_method(self, coro_fn) -> Any:
        """Wrap legacy utilities async methods to present a run() interface."""

        class _Runner:
            def __init__(self, fn):
                self._fn = fn

            async def run(self):
                return await self._fn()

        return _Runner(coro_fn)
