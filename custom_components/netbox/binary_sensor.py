"""Binary sensor platform for netbox."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="script-status",
        name="Script Errors",
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
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        scripts = self.coordinator.data.get(self.entity_description.key, {})
        if not isinstance(scripts, dict):
            return False
        return any(_is_error_status(status) for status in scripts.values())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return script details as attributes."""
        scripts = self.coordinator.data.get(self.entity_description.key, {})
        if not isinstance(scripts, dict):
            scripts = {}
        errored = sorted(name for name, status in scripts.items() if _is_error_status(status))
        return {
            "scripts_total": len(scripts),
            "scripts_errored": len(errored),
            "errored_scripts": errored,
            "script_status": scripts,
        }


def _is_error_status(value: str) -> bool:
    """Return True when a script status should be treated as a failed script."""
    return str(value).strip().lower() in {"errored", "error", "failed", "failure"}
