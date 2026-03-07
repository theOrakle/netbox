"""Netbox API Client."""
from __future__ import annotations

import asyncio
import socket
from collections.abc import Iterable
from typing import Any

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

    async def async_get_data(self) -> dict[str, Any]:
        """Get data from the API."""
        data: dict[str, Any] = {}
        release = await self._api_wrapper(
            method="get",
            url="https://api.github.com/repos/netbox-community/netbox/releases/latest",
            headers={"accept": "application/vnd.github+json"},
        )
        latest_tag = str(release.get("tag_name", "")).lstrip("v")
        data["netbox-latest-version"] = latest_tag or None

        status = await self._api_wrapper(
            method="get",
            url=f"https://{self._host}/api/status/",
        )
        data.update(status)
        data["netbox-version"] = _coalesce(status, ("netbox-version", "netbox_version"))
        data["python-version"] = _coalesce(status, ("python-version", "python_version"))

        plugins = _coalesce(status, ("plugins",))
        installed_apps = _coalesce(status, ("installed-apps", "installed_apps"))
        workers_running = _coalesce(status, ("rq-workers-running", "rq_workers_running"))

        data["plugins"] = plugins if isinstance(plugins, dict) else {}
        data["installed-apps"] = (
            installed_apps if isinstance(installed_apps, list) else []
        )
        data["rq-workers-running"] = bool(workers_running)
        data["plugins-count"] = len(data["plugins"])
        data["installed-apps-count"] = len(data["installed-apps"])

        script_status = await self._async_get_script_status()
        data["script-status"] = script_status
        data["scripts-total"] = len(script_status)
        data["scripts-errored"] = sum(
            1 for value in script_status.values() if _is_error_status(value)
        )

        LOGGER.debug(data)
        return data

    async def _async_get_script_status(self) -> dict[str, str]:
        """Fetch script execution statuses, following paginated NetBox responses."""
        script_status: dict[str, str] = {}
        next_url: str | None = f"https://{self._host}/api/extras/scripts/"
        while next_url:
            response = await self._api_wrapper(method="get", url=next_url)
            results = response.get("results", [])
            if not isinstance(results, Iterable):
                break
            for script in results:
                if not isinstance(script, dict):
                    continue
                name = str(script.get("name", "unknown_script"))
                result = script.get("result", {}) if isinstance(script.get("result"), dict) else {}
                status = result.get("status", {}) if isinstance(result.get("status"), dict) else {}
                script_status[name] = str(status.get("value", "unknown"))
            next_candidate = response.get("next")
            next_url = str(next_candidate) if next_candidate else None
        return script_status

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> dict[str, Any]:
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


def _coalesce(source: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first key present in source."""
    for key in keys:
        if key in source:
            return source[key]
    return None


def _is_error_status(value: str) -> bool:
    """Return True when a script status should be treated as a failed script."""
    return str(value).strip().lower() in {"errored", "error", "failed", "failure"}
