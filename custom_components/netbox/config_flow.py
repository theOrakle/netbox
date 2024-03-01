"""Adds config flow for Netbox."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_TOKEN
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    NetboxApiClient,
    NetboxApiClientAuthenticationError,
    NetboxApiClientCommunicationError,
    NetboxApiClientError,
)
from .const import DOMAIN, LOGGER


class NetboxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Netbox."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_connection(
                    host=user_input[CONF_HOST],
                    api_token=user_input[CONF_API_TOKEN],
                )
            except NetboxApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except NetboxApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except NetboxApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_connection(self, host: str, api_token: str) -> None:
        """Validate host."""
        client = NetboxApiClient(
            host=host,
            token=api_token,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
