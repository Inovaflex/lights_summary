import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import device_registry, area_registry, entity_registry
from homeassistant.core import callback
from .const import DOMAIN, SUPPORTED_DOMAINS

_LOGGER = logging.getLogger(__name__)


class LightsSummarySensor(SensorEntity):
    """Summarize lights/switches per area based on device labels."""

    def __init__(self, hass, area_name, label_name):
        self.hass = hass
        self.area_name = area_name
        self.label_name = label_name
        self._attr_name = f"{area_name} {label_name} Summary"
        self._attr_unique_id = f"{area_name.lower()}_{label_name.lower()}_summary"
        self._attr_native_value = "Unknown"
        self._attr_extra_state_attributes = {}

        self._area_reg = area_registry.async_get(hass)
        self._device_reg = device_registry.async_get(hass)
        self._entity_reg = entity_registry.async_get(hass)

    async def async_update(self):
        """Update sensor state by scanning devices in the area with the selected label."""
        area = self._area_reg.async_get_area_by_name(self.area_name)
        if not area:
            _LOGGER.warning("Area '%s' not found", self.area_name)
            self._attr_native_value = "Area not found"
            self._attr_extra_state_attributes = {}
            return

        # Loop over all devices
        devices_in_area = [
            d for d in self._device_reg.devices.values()
            if d.area_id == area.id
        ]
        _LOGGER.debug("Found %d devices in area '%s'", len(devices_in_area), self.area_name)

        # Filter devices by label
        labeled_devices = []
        for device in devices_in_area:
            labels = getattr(device, "labels", [])
            if any((label.lower() if isinstance(label, str) else getattr(label, "name", "").lower()) == self.label_name.lower()
                for label in labels):
                    labeled_devices.append(device)

        _LOGGER.debug("Found %d devices with label '%s'", len(labeled_devices), self.label_name)

        # Count supported entities and how many are ON
        all_entities = []
        on_count = 0
        for device in labeled_devices:
            entity_entries = [
                e.entity_id for e in self._entity_reg.entities.values()
                if e.device_id == device.id and e.entity_id.split(".")[0] in SUPPORTED_DOMAINS
            ]
            all_entities.extend(entity_entries)

        for eid in all_entities:
            if self.hass.states.is_state(eid, "on"):
                on_count += 1
                _LOGGER.info("Entity '%s' is ON", eid)

        total = len(all_entities)

        if total == 0:
            self._attr_native_value = f"No devices labeled '{self.label_name}'"
            status = "unknown"
        elif on_count > 0:
            self._attr_native_value = f"{self.label_name} on: {on_count} of {total}"
            status = "on"
        else:
            self._attr_native_value = f"All {self.label_name} Off"
            status = "off"

        self._attr_extra_state_attributes = {
            "label": self.label_name,
            "status": status,
            "entities_on": on_count,
            "entities_total": total,
            "entity_list": all_entities,
        }

        _LOGGER.debug("Updated %s [%s]: %s", self.area_name, self.label_name, self._attr_native_value)

    @callback
    def _state_listener(self, event):
        """Listen to relevant entity state changes and update sensor."""
        entity_id = event.data.get("entity_id")
        entity_entry = self._entity_reg.async_get(entity_id)
        if entity_entry and entity_entry.device_id:
            device = self._device_reg.async_get(entity_entry.device_id)
            area = self._area_reg.async_get_area_by_name(self.area_name)
            if device and area and device.area_id == area.id and entity_id.split(".")[0] in SUPPORTED_DOMAINS:
                _LOGGER.info("Entity '%s' changed, updating sensor", entity_id)
                self.schedule_update_ha_state(True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor from a config entry."""
    area_name = entry.data.get("area_name")
    label_name = entry.data.get("label_name")
    sensor = LightsSummarySensor(hass, area_name, label_name)
    async_add_entities([sensor], True)

    # Reactive updates
    hass.bus.async_listen("state_changed", sensor._state_listener)
