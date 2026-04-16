"""The Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import GreenwichTunnelCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

type GreenwichTunnelConfigEntry = ConfigEntry[GreenwichTunnelCoordinator]

FRONTEND_URL_BASE = "/greenwich_tunnel_frontend"
CARD_FILENAME = "greenwich-tunnel-card.js"
CARD_URL = f"{FRONTEND_URL_BASE}/{CARD_FILENAME}"
_FRONTEND_REGISTERED = "frontend_registered"


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the Lovelace card JS once per HA process and add it to the frontend."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(_FRONTEND_REGISTERED):
        return
    frontend_dir = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url_path=FRONTEND_URL_BASE,
                path=str(frontend_dir),
                cache_headers=False,
            ),
        ]
    )
    add_extra_js_url(hass, CARD_URL)
    domain_data[_FRONTEND_REGISTERED] = True
    _LOGGER.debug("Registered Greenwich tunnel Lovelace card at %s", CARD_URL)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GreenwichTunnelConfigEntry,
) -> bool:
    """Set up the Greenwich Foot Tunnel Lifts integration from a config entry."""
    await _async_register_frontend(hass)

    coordinator = GreenwichTunnelCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Unable to fetch lift reports: {err}") from err

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: GreenwichTunnelConfigEntry,
) -> bool:
    """Unload a Greenwich Foot Tunnel Lifts config entry and its platforms."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
