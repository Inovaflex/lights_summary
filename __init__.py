"""Lights Summary integration."""

from .config_flow import LightsSummaryConfigFlow
from .options_flow import LightsSummaryOptionsFlow

async def async_setup_entry(hass, entry):
    """Set up the integration."""
    # No setup needed at the root, sensors are forwarded
    return True

async def async_get_options_flow(config_entry):
    """Return options flow."""
    return LightsSummaryOptionsFlow(config_entry)

