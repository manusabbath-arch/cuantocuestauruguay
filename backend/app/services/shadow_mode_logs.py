"""
Lightweight shadow mode logging repository.

Current implementation stores entries in-memory and logs them. This is a
placeholder to avoid schema changes; it can be replaced with a DB-backed
repository when a table is defined.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ShadowLogEntry:
    etl: str
    v1: Dict[str, Any]
    v2: Dict[str, Any]
    comparison: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ShadowModeLogRepository:
    """In-memory log repository for shadow mode results."""

    def __init__(self):
        self._entries: List[ShadowLogEntry] = []

    def save(self, etl: str, v1: Dict[str, Any], v2: Dict[str, Any], comparison: Dict[str, Any]) -> ShadowLogEntry:
        entry = ShadowLogEntry(etl=etl, v1=v1, v2=v2, comparison=comparison)
        self._entries.append(entry)
        logger.info("Shadow log stored for %s; match=%s", etl, comparison.get("match"))
        return entry

    def list(self) -> List[ShadowLogEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
