"""Binary sensor platform for netbox."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .const import DOMAIN, LOGGER
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity

from datetime import datetime as dt

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="script-status",
        name="Script Execution",
        icon="mdi:script",
        device_class=BinarySensorDeviceClass.PROBLEM,
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
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator,entity_description)
        self._attributes = {}
        self.entity_description = entity_description

    @property
    def state_attributes(self):
        return self._attributes

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        desc = self.entity_description
        scripts = self.coordinator.data.get(desc.key)
        for script in self.coordinator.data.get(desc.key):
            self._attributes[script] = scripts[script]
        value = max(scripts, key=scripts.get)
        return value == "completed" 
