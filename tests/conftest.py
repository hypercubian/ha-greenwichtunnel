"""Shared test fixtures for the Greenwich Foot Tunnel Lifts integration."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import aiohttp
import aiohttp.connector
import aiohttp.resolver
import pytest
import pytest_socket

# Force ``ThreadedResolver`` everywhere for the test suite:
#   * On Windows, ``AsyncResolver`` (aiodns) refuses to run on ``ProactorEventLoop``
#     which HA uses, so every async test would crash at session setup.
#   * On Linux, ``AsyncResolver`` pulls in ``pycares`` which spawns a persistent
#     background thread that survives ``ClientSession.close()``, tripping the
#     pytest-homeassistant-custom-component teardown check that forbids lingering
#     non-dummy threads.
# ``ThreadedResolver`` routes DNS through the event loop's default executor and
# leaves no threads behind, so patching it unconditionally keeps the suite portable.
aiohttp.resolver.DefaultResolver = aiohttp.resolver.ThreadedResolver  # type: ignore[misc]
aiohttp.connector.DefaultResolver = aiohttp.resolver.ThreadedResolver  # type: ignore[misc]
aiohttp.DefaultResolver = aiohttp.resolver.ThreadedResolver  # type: ignore[attr-defined]

# HA's aiohttp_client helper hardcodes ``AsyncResolver()`` when creating sessions
# via ``async_get_clientsession()``; rebind it so HA-provided sessions also use
# the threaded resolver during tests.
import homeassistant.helpers.aiohttp_client as _ha_aiohttp_client  # noqa: E402

_ha_aiohttp_client.AsyncResolver = aiohttp.resolver.ThreadedResolver  # type: ignore[misc]

# Neutralise pytest-homeassistant-custom-component's socket block. The HA plugin
# disables ``socket.socket`` in its own ``pytest_runtest_setup`` hook, which
# prevents pytest-asyncio from creating its event loop on Windows. We mock all
# network I/O with aioresponses, so the block adds no safety here.
pytest_socket.disable_socket = lambda *_args, **_kwargs: None  # type: ignore[assignment]

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,  # noqa: ARG001
) -> Generator[None, None, None]:
    """Enable loading of the custom integration in every test automatically."""
    yield


@pytest.fixture
def bypass_get_data() -> Generator[None, None, None]:
    """Patch the coordinator's fetch path to a no-op so setup tests don't do real I/O."""
    with patch(
        "custom_components.greenwich_tunnel.coordinator.GreenwichLiftsApiClient"
        ".async_get_recent_reports",
        return_value=[],
    ):
        yield
