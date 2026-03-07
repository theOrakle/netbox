"""Sensor platform for netbox."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import NetboxDataUpdateCoordinator
from .entity import NetboxEntity


@dataclass(frozen=True, kw_only=True)
class NetboxSensorDescription(SensorEntityDescription):
    """Description of a Netbox sensor."""

    value_key: str
    counts_key: str | None = None
    unavailable_key: str | None = None


ENTITY_DESCRIPTIONS: tuple[NetboxSensorDescription, ...] = (
    NetboxSensorDescription(
        key="change_log_last_24h",
        name="Changes Last 24 Hours",
        value_key="change-log-last-24h-count",
        icon="mdi:timeline-clock",
    ),
    NetboxSensorDescription(
        key="dcim_total_objects",
        name="DCIM Total Objects",
        value_key="rollup-dcim-total",
        counts_key="rollup-dcim-counts",
        unavailable_key="rollup-dcim-unavailable",
        icon="mdi:server-network",
    ),
    NetboxSensorDescription(
        key="ipam_total_objects",
        name="IPAM Total Objects",
        value_key="rollup-ipam-total",
        counts_key="rollup-ipam-counts",
        unavailable_key="rollup-ipam-unavailable",
        icon="mdi:ip-network",
    ),
    NetboxSensorDescription(
        key="org_total_objects",
        name="ORG Total Objects",
        value_key="rollup-org-total",
        counts_key="rollup-org-counts",
        unavailable_key="rollup-org-unavailable",
        icon="mdi:domain",
    ),
    NetboxSensorDescription(
        key="netbox_version",
        name="NetBox Version",
        value_key="netbox-version",
        icon="mdi:package-variant",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NetboxSensorDescription(
        key="python_version",
        name="Python Version",
        value_key="python-version",
        icon="mdi:language-python",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NetboxSensorDescription(
        key="plugins_count",
        name="Plugins Count",
        value_key="plugins-count",
        icon="mdi:puzzle",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NetboxSensorDescription(
        key="installed_apps_count",
        name="Installed Apps Count",
        value_key="installed-apps-count",
        icon="mdi:apps",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NetboxSensorDescription(
        key="scripts_total",
        name="Scripts Total",
        value_key="scripts-total",
        icon="mdi:script-text",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    NetboxSensorDescription(
        key="scripts_errored",
        name="Scripts Errored",
        value_key="scripts-errored",
        icon="mdi:alert-circle",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        NetboxSensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class NetboxSensor(NetboxEntity, SensorEntity):
    """Netbox sensor class."""

    entity_description: NetboxSensorDescription

    def __init__(
        self,
        coordinator: NetboxDataUpdateCoordinator,
        entity_description: NetboxSensorDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description)
        self.entity_description = entity_description

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self.entity_description.value_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra attributes for selected sensors."""
        if self.entity_description.counts_key:
            return {
                "endpoint_counts": self.coordinator.data.get(
                    self.entity_description.counts_key,
                    {},
                ),
                "unavailable_endpoints": self.coordinator.data.get(
                    self.entity_description.unavailable_key or "",
                    [],
                ),
            }
        if self.entity_description.key == "change_log_last_24h":
            return {
                "action_counts": self.coordinator.data.get(
                    "change-log-last-24h-actions",
                    {},
                ),
                "object_type_counts": self.coordinator.data.get(
                    "change-log-last-24h-object-types",
                    {},
                ),
                "pages_scanned": self.coordinator.data.get(
                    "change-log-last-24h-pages-scanned",
                    0,
                ),
                "truncated": self.coordinator.data.get(
                    "change-log-last-24h-truncated",
                    False,
                ),
                "window_start": self.coordinator.data.get(
                    "change-log-last-24h-window-start",
                ),
                "source_endpoint": self.coordinator.data.get(
                    "change-log-source-endpoint",
                ),
                "endpoint_status": self.coordinator.data.get(
                    "change-log-endpoint-status",
                    {},
                ),
            }
        if self.entity_description.key == "plugins_count":
            return {"plugins": self.coordinator.data.get("plugins", {})}
        if self.entity_description.key == "installed_apps_count":
            return {"installed_apps": self.coordinator.data.get("installed-apps", [])}
        return None
