"""NetboxEntity class."""
from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NetboxDataUpdateCoordinator


class NetboxEntity(CoordinatorEntity[NetboxDataUpdateCoordinator]):
    """Base class for NetBox entities (one device per NetBox server)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NetboxDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        host = coordinator.config_entry.data[CONF_HOST]
        self._attr_unique_id = f"{DOMAIN}_{host}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=DOMAIN,
            manufacturer="NetBox Labs",
            model="NetBox",
        )
