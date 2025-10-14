"""Lights Summary integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Lights Summary from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")


async def async_get_options_flow(config_entry):
    from .options_flow import LightsSummaryOptionsFlow
    return LightsSummaryOptionsFlow(config_entry)
