"""Shared fixtures for the NetBox tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_API_TOKEN, CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.netbox.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

HOST = "netbox.example.com"

DATA = {
    "change-log-last-24h-count": 12,
    "rollup-dcim-total": 100,
    "rollup-dcim-counts": {"devices": 100},
    "rollup-dcim-unavailable": [],
    "rollup-ipam-total": 50,
    "rollup-ipam-counts": {"prefixes": 50},
    "rollup-ipam-unavailable": [],
    "rollup-org-total": 5,
    "rollup-org-counts": {"sites": 5},
    "rollup-org-unavailable": [],
    "netbox-version": "4.1.0",
    "netbox-latest-version": "4.2.0",
    "python-version": "3.12.1",
    "plugins-count": 1,
    "plugins": {"a": "1.0"},
    "installed-apps-count": 3,
    "installed-apps": ["x"],
    "scripts-total": 2,
    "scripts-errored": 1,
    "script-status": {"good": "completed", "bad": "errored"},
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow Home Assistant to load the custom integration under test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a NetBox config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=HOST,
        unique_id=HOST,
        data={CONF_HOST: HOST, CONF_API_TOKEN: "token"},
    )


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    """Patch the NetBox API client everywhere it is constructed."""
    with (
        patch("custom_components.netbox.NetboxApiClient", autospec=True) as client_cls,
        patch("custom_components.netbox.config_flow.NetboxApiClient", new=client_cls),
    ):
        client = client_cls.return_value
        client._host = HOST
        client.async_get_data = AsyncMock(return_value=dict(DATA))
        yield client
