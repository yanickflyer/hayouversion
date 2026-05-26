from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_API_KEY, DEFAULT_NAME, CONF_BIBLE_ID, DEFAULT_BIBLE_ID


class YouVersionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Store credentials directly; validation happens in setup
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_API_KEY: user_input[CONF_API_KEY],
                    CONF_BIBLE_ID: int(user_input.get(CONF_BIBLE_ID, DEFAULT_BIBLE_ID)),
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_BIBLE_ID, default=DEFAULT_BIBLE_ID): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
