"""Data update coordinator for the Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GreenwichLiftsApiClient, GreenwichLiftsApiError, Report
from .const import (
    AVAILABILITY_WINDOW_HOURS,
    DOMAIN,
    LOCATIONS,
    POLL_INTERVAL_SECONDS,
    STALE_THRESHOLD_HOURS,
    STATUS_FUNCTIONING,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class LocationState:
    """Aggregated state for one lift location based on the latest report and a 24h window."""

    status: str | None
    last_report_at: datetime | None
    last_report_created: datetime | None
    report_count_24h: int
    availability_pct_24h: float | None
    is_stale: bool


type GreenwichTunnelCoordinatorData = dict[str, LocationState]


class GreenwichTunnelCoordinator(DataUpdateCoordinator[GreenwichTunnelCoordinatorData]):
    """Polls greenwichlifts.co.uk and aggregates per-location state."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Set up the coordinator against a shared aiohttp session."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=POLL_INTERVAL_SECONDS),
        )
        self._client = GreenwichLiftsApiClient(async_get_clientsession(hass))

    async def _async_update_data(self) -> GreenwichTunnelCoordinatorData:
        """Fetch the latest window of reports and produce aggregate state per location."""
        try:
            reports = await self._client.async_get_recent_reports()
        except GreenwichLiftsApiError as err:
            raise UpdateFailed(f"Error fetching lift reports: {err}") from err

        now = datetime.now(tz=timezone.utc)
        return {location: _aggregate(location, reports, now) for location in LOCATIONS}


def _aggregate(
    location: str,
    all_reports: list[Report],
    now: datetime,
) -> LocationState:
    """Produce the latest status plus a 24h availability summary for one location."""
    reports = [r for r in all_reports if r.location == location]
    if not reports:
        return LocationState(
            status=None,
            last_report_at=None,
            last_report_created=None,
            report_count_24h=0,
            availability_pct_24h=None,
            is_stale=True,
        )

    latest = max(reports, key=lambda r: r.created_at)
    stale = (now - latest.created_at) > timedelta(hours=STALE_THRESHOLD_HOURS)

    window_cutoff = now - timedelta(hours=AVAILABILITY_WINDOW_HOURS)
    window_reports = [r for r in reports if r.created_at >= window_cutoff]
    if window_reports:
        functioning = sum(1 for r in window_reports if r.status == STATUS_FUNCTIONING)
        availability_pct = round(functioning / len(window_reports) * 100, 1)
    else:
        availability_pct = None

    return LocationState(
        status=latest.status,
        last_report_at=latest.timestamp,
        last_report_created=latest.created_at,
        report_count_24h=len(window_reports),
        availability_pct_24h=availability_pct,
        is_stale=stale,
    )
