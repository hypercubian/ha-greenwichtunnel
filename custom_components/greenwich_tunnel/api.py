"""HTTP client for the greenwichlifts.co.uk Supabase backend."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from .const import HISTORY_WINDOW_HOURS, REPORTS_ENDPOINT, SUPABASE_ANON_KEY

_LOGGER = logging.getLogger(__name__)


class GreenwichLiftsApiError(Exception):
    """Raised when the upstream Supabase API cannot be reached or returns an error."""


@dataclass(frozen=True)
class Report:
    """A single crowdsourced lift status report from a community member."""

    id: str
    location: str
    status: str
    timestamp: datetime
    created_at: datetime

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Report:
        """Build a Report from a PostgREST row, coercing ISO timestamps to datetimes."""
        return cls(
            id=row["id"],
            location=row["location"],
            status=row["status"],
            timestamp=_parse_iso(row["timestamp"]),
            created_at=_parse_iso(row["created_at"]),
        )


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp from Supabase into a timezone-aware datetime.

    Supabase returns timestamps with offset and variable-length microseconds. Python's
    ``datetime.fromisoformat`` handles both since 3.11.
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


class GreenwichLiftsApiClient:
    """Async client for fetching recent lift reports from the Supabase REST endpoint."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialise with an aiohttp session (shared with Home Assistant)."""
        self._session = session

    async def async_get_recent_reports(
        self,
        hours: int = HISTORY_WINDOW_HOURS,
    ) -> list[Report]:
        """Return reports submitted in the last ``hours`` hours, newest first."""
        cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
        params = {
            "select": "id,location,status,timestamp,created_at",
            "created_at": f"gte.{cutoff.isoformat()}",
            "order": "created_at.desc",
            "limit": "1000",
        }
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Accept": "application/json",
        }
        try:
            async with self._session.get(
                REPORTS_ENDPOINT,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientError as err:
            raise GreenwichLiftsApiError(str(err)) from err
        except TimeoutError as err:
            raise GreenwichLiftsApiError("Request timed out") from err

        if not isinstance(data, list):
            raise GreenwichLiftsApiError(
                f"Unexpected response shape: {type(data).__name__}"
            )

        return [Report.from_row(row) for row in data]
