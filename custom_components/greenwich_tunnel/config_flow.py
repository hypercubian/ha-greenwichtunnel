"""Config flow for the Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GreenwichLiftsApiClient, GreenwichLiftsApiError
from .const import DOMAIN, UNIQUE_ID

_LOGGER = logging.getLogger(__name__)


class GreenwichTunnelConfigFlow(ConfigFlow, domain=DOMAIN):
    """Zero-configuration confirmation-only config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Show a confirmation form, then validate connectivity before creating the entry."""
        await self.async_set_unique_id(UNIQUE_ID)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input is not None:
            client = GreenwichLiftsApiClient(async_get_clientsession(self.hass))
            try:
                await client.async_get_recent_reports(hours=1)
            except GreenwichLiftsApiError as err:
                _LOGGER.warning(
                    "Greenwich Foot Tunnel Lifts: connection test failed: %s", err
                )
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Greenwich Foot Tunnel Lifts",
                    data={},
                )

        return self.async_show_form(step_id="user", errors=errors)
