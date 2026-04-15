"""Unit tests for the coordinator's pure aggregation logic."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from custom_components.greenwich_tunnel.api import Report
from custom_components.greenwich_tunnel.coordinator import _aggregate
from custom_components.greenwich_tunnel.const import (
    LOCATION_NORTH,
    LOCATION_SOUTH,
    STATUS_BROKEN,
    STATUS_FUNCTIONING,
)

pytestmark = pytest.mark.unit


NOW = datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc)


def _report(
    location: str,
    status: str,
    minutes_ago: int,
    report_id: str = "id",
) -> Report:
    created = NOW - timedelta(minutes=minutes_ago)
    return Report(
        id=report_id,
        location=location,
        status=status,
        timestamp=created,
        created_at=created,
    )


def test_aggregate_returns_empty_state_when_no_reports() -> None:
    """A location with zero reports in the window is stale and has no status."""
    result = _aggregate(LOCATION_NORTH, [], NOW)
    assert result.status is None
    assert result.report_count_24h == 0
    assert result.availability_pct_24h is None
    assert result.is_stale is True


def test_aggregate_picks_latest_report_by_created_at() -> None:
    """The coordinator must report the most recently submitted status, not the oldest."""
    reports = [
        _report(LOCATION_NORTH, STATUS_BROKEN, minutes_ago=120, report_id="old"),
        _report(LOCATION_NORTH, STATUS_FUNCTIONING, minutes_ago=10, report_id="new"),
    ]
    result = _aggregate(LOCATION_NORTH, reports, NOW)
    assert result.status == STATUS_FUNCTIONING
    assert result.report_count_24h == 2
    assert result.availability_pct_24h == 50.0
    assert result.is_stale is False


def test_aggregate_filters_out_other_locations() -> None:
    """A location's aggregates must ignore reports from the other location."""
    reports = [
        _report(LOCATION_NORTH, STATUS_FUNCTIONING, minutes_ago=30),
        _report(LOCATION_SOUTH, STATUS_BROKEN, minutes_ago=15),
    ]
    result = _aggregate(LOCATION_NORTH, reports, NOW)
    assert result.status == STATUS_FUNCTIONING
    assert result.report_count_24h == 1
    assert result.availability_pct_24h == 100.0


def test_aggregate_marks_stale_when_latest_older_than_threshold() -> None:
    """Reports older than the 6-hour staleness threshold flip the is_stale flag."""
    reports = [_report(LOCATION_NORTH, STATUS_FUNCTIONING, minutes_ago=60 * 8)]
    result = _aggregate(LOCATION_NORTH, reports, NOW)
    assert result.status == STATUS_FUNCTIONING
    assert result.is_stale is True


def test_aggregate_computes_availability_percentage() -> None:
    """Availability is the share of functioning reports across the window, rounded to 0.1."""
    reports = [
        _report(LOCATION_NORTH, STATUS_FUNCTIONING, minutes_ago=10),
        _report(LOCATION_NORTH, STATUS_FUNCTIONING, minutes_ago=20),
        _report(LOCATION_NORTH, STATUS_BROKEN, minutes_ago=30),
    ]
    result = _aggregate(LOCATION_NORTH, reports, NOW)
    assert result.availability_pct_24h == pytest.approx(66.7)
