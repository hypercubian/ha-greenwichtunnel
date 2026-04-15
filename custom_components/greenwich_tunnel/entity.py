"""Shared base entity for Greenwich Foot Tunnel Lifts."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONFIGURATION_URL,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    UNIQUE_ID,
)
from .coordinator import GreenwichTunnelCoordinator


class GreenwichTunnelEntity(CoordinatorEntity[GreenwichTunnelCoordinator]):
    """Base class binding every Greenwich Foot Tunnel entity to the shared device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GreenwichTunnelCoordinator, key: str) -> None:
        """Initialise the entity with a unique ID derived from the integration key."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{UNIQUE_ID}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, UNIQUE_ID)},
            name="Greenwich Foot Tunnel Lifts",
            manufacturer=MANUFACTURER,
            model=MODEL,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=CONFIGURATION_URL,
        )
