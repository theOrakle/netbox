"""NetboxEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VERSION
from .coordinator import NetboxDataUpdateCoordinator


class NetboxEntity(CoordinatorEntity):
    """NetboxEntity class."""


    def __init__(
        self, 
        coordinator: NetboxDataUpdateCoordinator, 
        entity_description,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        host = coordinator.client._host
        self._attr_unique_id = f"{DOMAIN}_{host}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=DOMAIN,
            model=f"Integration {VERSION}",
            manufacturer=DOMAIN.capitalize(),
        )
