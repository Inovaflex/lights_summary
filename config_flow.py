import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import area_registry, device_registry
from .const import DOMAIN, DEFAULT_LABEL


class LightsSummaryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Lights Summary."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step 1: Select area."""
        area_reg = area_registry.async_get(self.hass)
        areas = {area.name: area.id for area in area_reg.async_list_areas()}
        if not areas:
            return self.async_abort(reason="no_areas")

        if user_input is not None:
            area_name = user_input["area_name"]
            # Go to next step with chosen area
            return await self.async_step_label_select({"area_name": area_name})

        schema = vol.Schema({
            vol.Required("area_name"): vol.In(list(areas.keys()))
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={"note": "Select the area to summarize."}
        )

    async def async_step_label_select(self, user_input=None):
        """Step 2: Select label within the chosen area."""
        area_reg = area_registry.async_get(self.hass)
        device_reg = device_registry.async_get(self.hass)

        area_name = user_input.get("area_name") if user_input else None
        if not area_name:
            return self.async_abort(reason="no_area_selected")

        # Find the area ID from name
        area_id = next((a.id for a in area_reg.async_list_areas() if a.name == area_name), None)
        if not area_id:
            return self.async_abort(reason="invalid_area")

        # Gather labels only for devices in that area
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

        if user_input and "label_name" in user_input:
            label_name = user_input["label_name"]
            area_name = user_input["area_name"]

            if self._is_duplicate(area_name, label_name):
                return self.async_abort(reason="already_configured")

            return self.async_create_entry(
                title=f"{area_name} ({label_name})",
                data={"area_name": area_name, "label_name": label_name},
            )

        schema = vol.Schema({
            vol.Required("area_name", default=area_name): str,
            vol.Required("label_name", default=DEFAULT_LABEL): vol.In(label_list)
        })

        return self.async_show_form(
            step_id="label_select",
            data_schema=schema,
            description_placeholders={
                "note": f"Select a label found on devices in {area_name}."
            }
        )

    def _is_duplicate(self, area_name: str, label_name: str) -> bool:
        """Return True if the same area+label is already configured."""
        existing_entries = self.hass.config_entries.async_entries(DOMAIN)
        for entry in existing_entries:
            if (
                entry.data.get("area_name") == area_name
                and entry.data.get("label_name") == label_name
            ):
                return True
        return False


@callback
def configured_instances(hass):
    """Return configured area+label pairs."""
    entries = hass.config_entries.async_entries(DOMAIN)
    return {(e.data.get("area_name"), e.data.get("label_name")) for e in entries}
