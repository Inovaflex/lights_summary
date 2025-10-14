import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import area_registry, device_registry
from .const import DOMAIN, DEFAULT_LABEL

class LightsSummaryOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Lights Summary integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        area_reg = area_registry.async_get(self.hass)
        device_reg = device_registry.async_get(self.hass)

        current_area = self.config_entry.data.get("area_name")
        current_label = self.config_entry.data.get("label_name")

        areas = {area.name: area.id for area in area_reg.async_list_areas()}

        area_id = next((a.id for a in area_reg.async_list_areas() if a.name == current_area), None)

        label_names = set()
        for dev in device_reg.devices.values():
            if dev.area_id != area_id:
                continue
            labels = getattr(dev, "labels", None)
            if not labels:
                continue
            for label in labels:
                if isinstance(label, str):
                    label_names.add(label)
                else:
                    label_names.add(getattr(label, "name", str(label)))

        label_list = sorted(label_names) or [DEFAULT_LABEL]

        schema = vol.Schema({
            vol.Required("area_name", default=current_area): vol.In(list(areas.keys())),
            vol.Required("label_name", default=current_label): vol.In(label_list)
        })

        if user_input is not None:
            new_area = user_input["area_name"]
            new_label = user_input["label_name"]
            if self._is_duplicate(new_area, new_label):
                return self.async_show_form(
                    step_id="init",
                    data_schema=schema,
                    errors={"base": "already_configured"}
                )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=schema)

    def _is_duplicate(self, area_name, label_name):
        entries = self.hass.config_entries.async_entries(DOMAIN)
        for entry in entries:
            if entry.entry_id == self.config_entry.entry_id:
                continue
            if entry.data.get("area_name") == area_name and entry.data.get("label_name") == label_name:
                return True
        return False

