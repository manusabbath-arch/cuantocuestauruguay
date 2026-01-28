"""
Shadow mode logging repository.

Stores entries in-memory and optionally persists to a JSONL file. This avoids
DB schema changes while retaining auditability across restarts when a path is
provided.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ShadowLogEntry:
    etl: str
    v1: Dict[str, Any]
    v2: Dict[str, Any]
    comparison: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ShadowModeLogRepository:
    """In-memory log repository with optional JSONL persistence."""

    def __init__(self, persist_path: Optional[str] = None):
        self._entries: List[ShadowLogEntry] = []
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, etl: str, v1: Dict[str, Any], v2: Dict[str, Any], comparison: Dict[str, Any]) -> ShadowLogEntry:
        entry = ShadowLogEntry(etl=etl, v1=v1, v2=v2, comparison=comparison)
        self._entries.append(entry)
        logger.info("Shadow log stored for %s; match=%s", etl, comparison.get("match"))
        self._persist(entry)
        return entry

    def list(self) -> List[ShadowLogEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def _persist(self, entry: ShadowLogEntry) -> None:
        if not self._persist_path:
            return
        try:
            with self._persist_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to persist shadow log: %s", exc)
