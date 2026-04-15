"""Binary sensor platform for the Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GreenwichTunnelConfigEntry
from .const import LOCATION_NORTH, LOCATION_SOUTH, STATUS_FUNCTIONING
from .coordinator import GreenwichTunnelCoordinator, LocationState
from .entity import GreenwichTunnelEntity


@dataclass(frozen=True, kw_only=True)
class GreenwichTunnelBinarySensorDescription(BinarySensorEntityDescription):
    """Binary sensor description bound to a single tunnel location."""

    location: str


SENSORS: tuple[GreenwichTunnelBinarySensorDescription, ...] = (
    GreenwichTunnelBinarySensorDescription(
        key="north_lift",
        translation_key="north_lift",
        device_class=BinarySensorDeviceClass.RUNNING,
        location=LOCATION_NORTH,
    ),
    GreenwichTunnelBinarySensorDescription(
        key="south_lift",
        translation_key="south_lift",
        device_class=BinarySensorDeviceClass.RUNNING,
        location=LOCATION_SOUTH,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GreenwichTunnelConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register one binary sensor per lift location."""
    coordinator = entry.runtime_data
    async_add_entities(
        GreenwichTunnelLiftBinarySensor(coordinator, description)
        for description in SENSORS
    )


class GreenwichTunnelLiftBinarySensor(GreenwichTunnelEntity, BinarySensorEntity):
    """Reports whether a single tunnel lift is currently functioning."""

    entity_description: GreenwichTunnelBinarySensorDescription

    def __init__(
        self,
        coordinator: GreenwichTunnelCoordinator,
        description: GreenwichTunnelBinarySensorDescription,
    ) -> None:
        """Bind the sensor to its coordinator and description."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def _state(self) -> LocationState | None:
        return self.coordinator.data.get(self.entity_description.location)

    @property
    def is_on(self) -> bool | None:
        """Return True when the latest report says the lift is functioning."""
        state = self._state
        if state is None or state.status is None:
            return None
        return state.status == STATUS_FUNCTIONING

    @property
    def available(self) -> bool:
        """Report unavailable only when there are no reports in the 24-hour window."""
        if not super().available:
            return False
        state = self._state
        return state is not None and state.status is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the aggregate state around the latest report as attributes."""
        state = self._state
        if state is None:
            return {}
        return {
            "last_report_at": (
                state.last_report_at.isoformat() if state.last_report_at else None
            ),
            "last_report_created": (
                state.last_report_created.isoformat()
                if state.last_report_created
                else None
            ),
            "report_count_24h": state.report_count_24h,
            "availability_pct_24h": state.availability_pct_24h,
            "is_stale": state.is_stale,
        }
