"""Config flow for YouVersion integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_KEY, DEFAULT_NAME
from .verse import get_verse_day


class InvalidAuth(Exception):
    pass


async def validate_input(hass: HomeAssistant, data: dict):
    """Validate the user input allows us to connect.

    Raise InvalidAuth on auth failure.
    """
    api_key = data.get(CONF_API_KEY)
    result = await hass.async_add_executor_job(get_verse_day, api_key)
    if not result:
        raise InvalidAuth
    return {"title": DEFAULT_NAME}


class YouVersionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for YouVersion."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema({vol.Required(CONF_API_KEY): str})
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
