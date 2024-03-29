"""Netbox API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout

from .const import LOGGER 

class NetboxApiClientError(Exception):
    """Exception to indicate a general API error."""


class NetboxApiClientCommunicationError(
    NetboxApiClientError
):
    """Exception to indicate a communication error."""


class NetboxApiClientAuthenticationError(
    NetboxApiClientError
):
    """Exception to indicate an authentication error."""


class NetboxApiClient:
    """Netbox API Client."""

    def __init__(
        self,
        host: str,
        token: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Netbox API Client."""
        self._host = host
        self._token = token
        self._session = session

    async def async_get_data(self) -> any:
        """Get data from the API."""
        data = {}
        results = await self._api_wrapper(
            method="get", url="https://github.com/netbox-community/netbox/releases/latest"
        )
        data["netbox-latest-version"] = results["tag_name"][1:]
        results = await self._api_wrapper(
            method="get", url=f"https://{self._host}/api/status"
        )
        data.update(results)
        response = await self._api_wrapper(
            method="get", url=f"https://{self._host}/api/extras/scripts"
        )
        script_status = {}
        for script in response["results"]:
            try:
                script_status[script["name"]] = script["result"]["status"]["value"]
            except:
                script_status[script["name"]] = 'N/A'
        data["script-status"] = script_status
        LOGGER.debug(data)
        return data

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        if not headers:
            headers = {
                "accept": "application/json",
                "Authorization": f"Token {self._token}",
            }
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise NetboxApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise NetboxApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise NetboxApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise NetboxApiClientError(
                "Something really wrong happened!"
            ) from exception
