"""Adds config flow for Netbox."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_TOKEN, CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    NetboxApiClient,
    NetboxApiClientAuthenticationError,
    NetboxApiClientCommunicationError,
    NetboxApiClientError,
)
from .const import DOMAIN, LOGGER


class NetboxFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Netbox."""

    VERSION = 1

    async def _validate(self, host: str, api_token: str) -> str | None:
        """Test the connection and return a flow error key, or None when it works."""
        try:
            await self._test_connection(host=host, api_token=api_token)
        except NetboxApiClientAuthenticationError as exception:
            LOGGER.warning(exception)
            return "invalid_auth"
        except NetboxApiClientCommunicationError as exception:
            LOGGER.error(exception)
            return "cannot_connect"
        except NetboxApiClientError as exception:
            LOGGER.exception(exception)
            return "unknown"
        return None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if error := await self._validate(host, user_input[CONF_API_TOKEN]):
                errors["base"] = error
            else:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=host,
                    data={
                        CONF_HOST: host,
                        CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=(user_input or {}).get(CONF_HOST)
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start re-authentication after NetBox rejected the stored token."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a new API token."""
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            if error := await self._validate(
                reauth_entry.data[CONF_HOST], user_input[CONF_API_TOKEN]
            ):
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_API_TOKEN: user_input[CONF_API_TOKEN]},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            description_placeholders={"host": reauth_entry.data[CONF_HOST]},
            errors=errors,
        )

    async def _test_connection(self, host: str, api_token: str) -> None:
        """Validate host."""
        client = NetboxApiClient(
            host=host,
            token=api_token,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
