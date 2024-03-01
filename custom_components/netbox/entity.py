"""NetboxEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, VERSION
from .coordinator import NetboxDataUpdateCoordinator


class NetboxEntity(CoordinatorEntity):
    """NetboxEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: NetboxDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=DOMAIN,
            model=VERSION,
            manufacturer=DOMAIN,
        )
