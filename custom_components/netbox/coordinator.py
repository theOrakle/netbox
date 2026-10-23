"""DataUpdateCoordinator for netbox."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    NetboxApiClient,
    NetboxApiClientAuthenticationError,
    NetboxApiClientError,
)
from .const import DOMAIN, LOGGER

type NetboxConfigEntry = ConfigEntry[NetboxDataUpdateCoordinator]


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class NetboxDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the API."""

    config_entry: NetboxConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: NetboxConfigEntry,
        client: NetboxApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=120),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except NetboxApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except NetboxApiClientError as exception:
            raise UpdateFailed(exception) from exception
