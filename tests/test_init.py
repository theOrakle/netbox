"""Tests for NetBox setup, unload and entities."""
from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_API_TOKEN, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.netbox.api import (
    NetboxApiClientAuthenticationError,
    NetboxApiClientCommunicationError,
)
from custom_components.netbox.const import DOMAIN

from .conftest import HOST


async def test_setup_and_unload(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """The entry loads, creates the device and entities, and unloads cleanly."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, HOST), mock_config_entry.entry_id
    )
    assert device is not None
    assert device.model == "NetBox"

    assert hass.states.get("sensor.netbox_changes_last_24_hours").state == "12"
    assert hass.states.get("sensor.netbox_dcim_total_objects").attributes["endpoint_counts"] == {
        "devices": 100
    }
    assert hass.states.get("binary_sensor.netbox_script_errors").state == "on"
    update = hass.states.get("update.netbox_netbox")
    assert update.state == "on"
    assert update.attributes["installed_version"] == "4.1.0"
    assert update.attributes["latest_version"] == "4.2.0"

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_legacy_entry_gets_unique_id(
    hass: HomeAssistant, mock_client: MagicMock
) -> None:
    """Entries created before unique IDs existed are migrated on setup."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "NB.Example.com", CONF_API_TOKEN: "t"}
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    assert entry.unique_id == "nb.example.com"


async def test_setup_retries_when_unreachable(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A connection failure at setup is retried, not a hard error."""
    mock_client.async_get_data.side_effect = NetboxApiClientCommunicationError("down")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_starts_reauth_on_rejected_token(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """A rejected token starts a re-authentication flow."""
    mock_client.async_get_data.side_effect = NetboxApiClientAuthenticationError("bad")
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert [f["context"]["source"] for f in flows] == ["reauth"]
