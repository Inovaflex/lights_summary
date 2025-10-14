from homeassistant.helpers.entity import Entity
from homeassistant.helpers import device_registry, area_registry
from .const import DOMAIN, DEFAULT_LABEL
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    area_name = entry.data.get("area_name")
    label_name = entry.data.get("label_name", DEFAULT_LABEL)
    async_add_entities([LightsSummarySensor(hass, area_name, label_name)])

class LightsSummarySensor(Entity):
    def __init__(self, hass, area_name, label_name):
        self.hass = hass
        self.area_name = area_name
        self.label_name = label_name
        self._state = None
        self._attr_extra_state_attributes = {}

    @property
    def name(self):
        return f"{self.area_name} {self.label_name} Summary"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    async def async_update(self):
        device_reg = device_registry.async_get(self.hass)
        area_reg = area_registry.async_get(self.hass)
        area_id = next((a.id for a in area_reg.async_list_areas() if a.name == self.area_name), None)
        if not area_id:
            self._state = "No area"
            self._attr_extra_state_attributes = {}
            return

        matching_devices = [
            dev for dev in device_reg.devices.values()
            if dev.area_id == area_id and self.label_name in getattr(dev, "labels", [])
        ]

        total = len(matching_devices)
        on_count = 0
        for dev in matching_devices:
            # check any entity of the device that is on
            for ent_id in dev.entities:
                ent_state = self.hass.states.get(ent_id)
                if ent_state and ent_state.state == "on":
                    on_count += 1
                    break

        self._state = f"{on_count} of {total} on" if total else "No devices"
        self._attr_extra_state_attributes = {
            "entities_total": total,
            "entities_on": on_count,
            "entity_list": [e for dev in matching_devices for e in dev.entities]
        }
        _LOGGER.debug("Updated %s: %s", self.name, self._state)
