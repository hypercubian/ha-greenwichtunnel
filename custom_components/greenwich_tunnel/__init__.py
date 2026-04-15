"""The Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import GreenwichTunnelCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

type GreenwichTunnelConfigEntry = ConfigEntry[GreenwichTunnelCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GreenwichTunnelConfigEntry,
) -> bool:
    """Set up the Greenwich Foot Tunnel Lifts integration from a config entry."""
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
