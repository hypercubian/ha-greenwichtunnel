"""Constants for the Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "greenwich_tunnel"

SUPABASE_URL: Final = "https://uhgfgayyfbtjlttescvv.supabase.co"
REPORTS_ENDPOINT: Final = f"{SUPABASE_URL}/rest/v1/reports"

# Public Supabase "anon" JWT embedded in the upstream frontend. It grants only the
# row-level-security-filtered access that greenwichlifts.co.uk already exposes to
# any browser visiting the site, so it is safe to ship in source.
SUPABASE_ANON_KEY: Final = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoZ2ZnYXl5ZmJ0amx0dGVzY3Z2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3MzIwNzQsImV4cCI6MjA2OTMwODA3NH0.6XVgmEN_BrLiohfvr4a-m8-Svsf_4HyiEcRNaknolM4"  # noqa: E501  pragma: allowlist secret
)

POLL_INTERVAL_SECONDS: Final = 300
STALE_THRESHOLD_HOURS: Final = 6
AVAILABILITY_WINDOW_HOURS: Final = 24
REPORT_FETCH_LIMIT: Final = 100

LOCATION_NORTH: Final = "north"
LOCATION_SOUTH: Final = "south"
LOCATIONS: Final = (LOCATION_NORTH, LOCATION_SOUTH)

STATUS_FUNCTIONING: Final = "functioning"
STATUS_BROKEN: Final = "broken"

UNIQUE_ID: Final = "greenwichlifts_public"
MANUFACTURER: Final = "greenwichlifts.co.uk"
MODEL: Final = "Community tunnel lift tracker"
CONFIGURATION_URL: Final = "https://www.greenwichlifts.co.uk/"
