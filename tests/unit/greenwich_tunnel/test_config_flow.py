"""Tests for the Greenwich Foot Tunnel Lifts config flow."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.greenwich_tunnel.api import GreenwichLiftsApiError
from custom_components.greenwich_tunnel.const import DOMAIN, UNIQUE_ID

pytestmark = pytest.mark.unit


async def test_user_step_shows_form(hass: HomeAssistant) -> None:
    """The initial user step should render the confirmation form."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_step_creates_entry_on_success(hass: HomeAssistant) -> None:
    """A successful API probe should produce a config entry with no user data."""
    with patch(
        "custom_components.greenwich_tunnel.config_flow.GreenwichLiftsApiClient"
        ".async_get_recent_reports",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input={})

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Greenwich Foot Tunnel Lifts"
    assert result["data"] == {}


async def test_user_step_shows_cannot_connect_on_api_error(
    hass: HomeAssistant,
) -> None:
    """API failures should surface as cannot_connect and keep the form available."""
    with patch(
        "custom_components.greenwich_tunnel.config_flow.GreenwichLiftsApiClient"
        ".async_get_recent_reports",
        side_effect=GreenwichLiftsApiError("boom"),
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input={})

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_step_aborts_when_already_configured(
    hass: HomeAssistant,
) -> None:
    """A second setup attempt must abort with already_configured."""
    MockConfigEntry(domain=DOMAIN, unique_id=UNIQUE_ID).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
