"""Update platform for netbox."""
from __future__ import annotations

from homeassistant.components.update import UpdateEntity, UpdateEntityDescription

from .const import DOMAIN, LOGGER
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity

from datetime import datetime as dt

ENTITY_DESCRIPTIONS = (
    UpdateEntityDescription(
        key="netbox-version",
        translation_key="netbox-latest-version",
        name="Netbox",
        icon="mdi:package",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the update platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        NetboxUpdate(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NetboxUpdate(NetboxEntity, UpdateEntity):
    """netbox Update class."""

    def __init__(
        self,
        coordinator: NetboxDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the update class."""
        super().__init__(coordinator,entity_description)
        self.entity_description = entity_description

    @property
    def installed_version(self) -> str | None:
        """Return version currently installed."""
        desc = self.entity_description
        value = self.coordinator.data.get(desc.key)
        return value

    @property
    def latest_version(self) -> str | None:
        """Return latest available version."""
        desc = self.entity_description
        value = self.coordinator.data.get(desc.translation_key)
        return value
