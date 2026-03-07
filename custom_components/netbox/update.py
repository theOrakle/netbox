"""Update platform for netbox."""
from __future__ import annotations

from homeassistant.components.update import UpdateEntity, UpdateEntityDescription

from .const import DOMAIN
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity

ENTITY_DESCRIPTIONS = (
    UpdateEntityDescription(
        key="netbox-version",
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
        entity_description: UpdateEntityDescription,
    ) -> None:
        """Initialize the update class."""
        super().__init__(coordinator, entity_description)
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
        return self.coordinator.data.get("netbox-latest-version")
