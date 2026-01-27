"""Tests for shadow mode executor."""

import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import Session

from app.services.shadow_mode import ShadowModeExecutor


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.mark.asyncio
async def test_run_shadow_calls_both_and_returns_v1(monkeypatch, db_session):
    executor = ShadowModeExecutor(db_session)

    etl_v1 = MagicMock()
    etl_v1.run = AsyncMock(return_value={"success": True, "records_loaded": 5})

    etl_v2 = MagicMock()
    etl_v2.run = AsyncMock(return_value={"success": True, "records_processed": 5})

    monkeypatch.setattr(executor, "_get_etl_pair", lambda name: (etl_v1, etl_v2))

    result = await executor.run_shadow("combustibles")

    assert etl_v1.run.await_count == 1
    assert etl_v2.run.await_count == 1
    assert result["comparison"]["match"] is True
    assert result["returned"]["success"] is True
    assert result["returned"]["records_processed"] == 5


@pytest.mark.asyncio
async def test_run_shadow_detects_discrepancy(monkeypatch, db_session):
    executor = ShadowModeExecutor(db_session)

    etl_v1 = MagicMock()
    etl_v1.run = AsyncMock(return_value={"success": True, "records_loaded": 5})

    etl_v2 = MagicMock()
    etl_v2.run = AsyncMock(return_value={"success": True, "records_processed": 3})

    monkeypatch.setattr(executor, "_get_etl_pair", lambda name: (etl_v1, etl_v2))

    result = await executor.run_shadow("combustibles")

    assert result["comparison"]["match"] is False
    assert "records_processed" in result["comparison"]["differences"]
    assert result["v1"]["records_processed"] == 5
    assert result["v2"]["records_processed"] == 3


@pytest.mark.asyncio
async def test_run_shadow_handles_v2_failure(monkeypatch, db_session):
    executor = ShadowModeExecutor(db_session)

    etl_v1 = MagicMock()
    etl_v1.run = AsyncMock(return_value={"success": True, "records_loaded": 2})

    etl_v2 = MagicMock()
    etl_v2.run = AsyncMock(side_effect=Exception("boom"))

    monkeypatch.setattr(executor, "_get_etl_pair", lambda name: (etl_v1, etl_v2))

    result = await executor.run_shadow("combustibles")

    assert result["comparison"]["match"] is False
    assert result["v2"]["success"] is False
    assert "boom" in result["v2"]["errors"][0]


def test_compare_results_simple_diff():
    executor = ShadowModeExecutor(MagicMock())

    v1 = {"success": True, "records_processed": 10}
    v2 = {"success": False, "records_processed": 5}

    comparison = executor.compare_results(v1, v2)

    assert comparison["match"] is False
    assert comparison["differences"]["success"] == {"v1": True, "v2": False}
    assert comparison["differences"]["records_processed"] == {"v1": 10, "v2": 5}


@pytest.mark.asyncio
async def test_get_etl_pair_ute_wrapped(monkeypatch, db_session):
    calls = {}

    class DummyUtilities:
        def __init__(self, db):
            calls["v1_db"] = db

        async def run_ute(self):
            calls["v1_run"] = True
            return {"success": True, "records_loaded": 7}

    class DummyUTEv2:
        def __init__(self, db):
            calls["v2_db"] = db

        async def run(self):
            calls["v2_run"] = True
            return {"success": True, "records_processed": 7}

    monkeypatch.setitem(sys.modules, "app.etl.utilities", SimpleNamespace(UtilitiesETL=DummyUtilities))
    monkeypatch.setitem(sys.modules, "app.etl.ute_v2", SimpleNamespace(UTEETLv2=DummyUTEv2))

    executor = ShadowModeExecutor(db_session)
    v1_runner, v2_runner = executor._get_etl_pair("ute")

    v1_result, v2_result = await asyncio.gather(v1_runner.run(), v2_runner.run())

    assert calls["v1_db"] is db_session
    assert calls["v2_db"] is db_session
    assert calls["v1_run"] is True
    assert calls["v2_run"] is True
    assert v1_result["records_loaded"] == 7
    assert v2_result["records_processed"] == 7
