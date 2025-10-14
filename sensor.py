"""Lights Summary sensor for Home Assistant."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up Lights Summary sensor from config entry."""
    area_name = entry.data["area_name"]
    label_name = entry.data["label_name"]

    sensor = LightsSummarySensor(hass, area_name, label_name)
    async_add_entities([sensor], update_before_add=True)


class LightsSummarySensor(SensorEntity):
    """Sensor that summarizes lights/switches with a specific label in an area."""

    _attr_icon = "mdi:lightbulb-group"

    def __init__(self, hass: HomeAssistant, area_name: str, label_name: str) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._area_name = area_name
        self._label_name = label_name
        self._attr_name = f"{area_name} {label_name} Summary"
        self._attr_unique_id = (
            f"{area_name.lower().replace(' ', '_')}_{label_name.lower()}_lights_summary"
        )
        self._attr_extra_state_attributes = {}
        self._attr_native_value = None
        self._unsub = None

    async def async_added_to_hass(self):
        """When entity is added to hass, listen for state changes."""
        @callback
        def _handle_event(event):
            self.async_schedule_update_ha_state(True)

        self._unsub = self.hass.bus.async_listen("state_changed", _handle_event)

    async def async_will_remove_from_hass(self):
        """Unsubscribe from events."""
        if self._unsub:
            self._unsub()
            self._unsub = None

    async def async_update(self):
        """Recalculate the sensor state."""
        dev_reg = dr.async_get(self.hass)
        ent_reg = er.async_get(self.hass)

        area_devices = [
            dev
            for dev in dev_reg.devices.values()
            if dev.area_id
            and (area := self.hass.helpers.area_registry.async_get_area(dev.area_id))
            and area.name == self._area_name
        ]

        # Find devices matching label
        labeled_devices = [
            dev
            for dev in area_devices
            if any(
                lbl.name.lower() == self._label_name.lower()
                if hasattr(lbl, "name")
                else str(lbl).lower() == self._label_name.lower()
                for lbl in getattr(dev, "labels", [])
            )
        ]

        # Gather all entities for those devices
        entities = []
        for dev in labeled_devices:
            dev_entities = [
                ent for ent in ent_reg.entities.values() if ent.device_id == dev.id
            ]
            for ent in dev_entities:
                if ent.domain in ("light", "switch"):
                    entities.append(ent)

        # Calculate on/off state
        on_entities = [
            ent for ent in entities if self.hass.states.is_state(ent.entity_id, "on")
        ]

        self._attr_extra_state_attributes = {
            "Label": self._label_name,
            "Status": "on" if on_entities else "off",
            "Entities on": len(on_entities),
            "Entities total": len(entities),
            "Entity list": [ent.entity_id for ent in entities],
        }

        if not entities:
            self._attr_native_value = "No devices in area"
        elif on_entities:
            self._attr_native_value = f"{len(on_entities)} of {len(entities)} on"
        else:
            self._attr_native_value = "All off"
