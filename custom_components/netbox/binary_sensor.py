"""Binary sensor platform for netbox."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="script-status",
        name="Script Execution",
        icon="mdi:script",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        NetboxSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NetboxSensor(NetboxEntity, BinarySensorEntity):
    """netbox binary_sensor class."""

    def __init__(
        self,
        coordinator: NetboxDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description)
        self._attr_extra_state_attributes: dict[str, Any] = {}
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        desc = self.entity_description
        data = self.coordinator.data or {}
        scripts = data.get(desc.key) or {}

        if not isinstance(scripts, dict):
            self._attr_extra_state_attributes = {}
            return False

        self._attr_extra_state_attributes = {
            name: status for name, status in scripts.items()
        }
        return any(status == "errored" for status in scripts.values())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the binary sensor."""
        return self._attr_extra_state_attributes
