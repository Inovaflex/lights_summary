import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import area_registry, device_registry
from .const import DOMAIN, DEFAULT_LABEL


class LightsSummaryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Lights Summary."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        area_reg = area_registry.async_get(self.hass)
        device_reg = device_registry.async_get(self.hass)

        # Get all areas
        areas = {area.name: area.id for area in area_reg.async_list_areas()}
        if not areas:
            return self.async_abort(reason="no_areas")

        # Collect all unique device labels
        label_names = set()
        for dev in device_reg.devices.values():
            labels = getattr(dev, "labels", None)
            if not labels:
                continue
            for label in labels:
                if isinstance(label, str):
                    label_names.add(label)
                else:
                    label_names.add(getattr(label, "name", str(label)))

        label_list = sorted(label_names) or [DEFAULT_LABEL]

        if user_input is not None:
            return self.async_create_entry(
                title=f"{user_input['area_name']} ({user_input['label_name']})",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("area_name"): vol.In(list(areas.keys())),
            vol.Required("label_name", default=DEFAULT_LABEL): vol.In(label_list)
        })

        return self.async_show_form(step_id="user", data_schema=schema)


@callback
def configured_instances(hass):
    """Return configured areas to prevent duplicates."""
    return {entry.data["area_name"] for entry in hass.config_entries.async_entries(DOMAIN)}
