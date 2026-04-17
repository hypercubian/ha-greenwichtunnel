"""Unit tests for the Supabase API client."""

from __future__ import annotations

import re
from datetime import datetime, timezone

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.greenwich_tunnel.api import (
    GreenwichLiftsApiClient,
    GreenwichLiftsApiError,
    Report,
)

pytestmark = pytest.mark.unit

# Regex matcher so aioresponses fires regardless of the query string aiohttp
# appends (cutoff timestamp, select columns, ordering, limit).
REPORTS_URL_RE = re.compile(r"^https://uhgfgayyfbtjlttescvv\.supabase\.co/rest/v1/reports.*")


SAMPLE_ROWS = [
    {
        "id": "row-1",
        "location": "north",
        "status": "functioning",
        "timestamp": "2026-04-13T14:49:00+00:00",
        "created_at": "2026-04-13T14:49:40.223746+00:00",
    },
    {
        "id": "row-2",
        "location": "south",
        "status": "broken",
        "timestamp": "2026-04-13T14:49:00+00:00",
        "created_at": "2026-04-13T14:49:40.223746+00:00",
    },
]


async def test_get_recent_reports_parses_rows() -> None:
    """The client should return one Report per row with timezone-aware datetimes."""
    async with aiohttp.ClientSession() as session:
        client = GreenwichLiftsApiClient(session)
        with aioresponses() as mocked:
            mocked.get(REPORTS_URL_RE, payload=SAMPLE_ROWS)
            reports = await client.async_get_recent_reports()

    assert len(reports) == 2
    assert all(isinstance(r, Report) for r in reports)
    north = next(r for r in reports if r.location == "north")
    assert north.status == "functioning"
    assert north.timestamp == datetime(2026, 4, 13, 14, 49, tzinfo=timezone.utc)
    assert north.created_at.tzinfo is not None


async def test_get_recent_reports_wraps_http_error() -> None:
    """Any aiohttp failure must surface as GreenwichLiftsApiError."""
    async with aiohttp.ClientSession() as session:
        client = GreenwichLiftsApiClient(session)
        with aioresponses() as mocked:
            mocked.get(REPORTS_URL_RE, status=500)
            with pytest.raises(GreenwichLiftsApiError):
                await client.async_get_recent_reports()


async def test_get_recent_reports_rejects_non_list_payload() -> None:
    """A malformed (non-list) payload should raise a clear error rather than TypeError."""
    async with aiohttp.ClientSession() as session:
        client = GreenwichLiftsApiClient(session)
        with aioresponses() as mocked:
            mocked.get(REPORTS_URL_RE, payload={"error": "nope"})
            with pytest.raises(GreenwichLiftsApiError, match="Unexpected response"):
                await client.async_get_recent_reports()
