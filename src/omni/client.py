from __future__ import annotations

from typing import Literal

import requests

from .config import OmniConfig


class OmniApiClient:
    """Class for interacting with the Omni REST API. There are low level functions for making direct requests to the
    API (get, post, put, delete). These methods take a "path" arg that is equivalent to the path given in the Omni
    API docs. The client also includes convenience methods for common tasks.

    Args:
        organization_name: Omni organization name. OMNI_ORGANIZATION_NAME environment variable will be used as a fallback.
        api_key: Omni API key. OMNI_API_KEY environment variable will be used as a fallback.

    Attributes:
        base_url: Omni REST API base URL that paths will be appended to.
        api_key: Omni API key.
    """

    def __init__(
        self, organization_name: str | None = None, api_key: str | None = None
    ) -> None:
        omni_config = OmniConfig(
            required_attrs=["organization_name", "api_key"],
            organization_name=organization_name,
            api_key=api_key,
        )
        self.base_url = f"https://{omni_config.organization_name}.omniapp.co/api"
        self.api_key = omni_config.api_key

    def refresh_model(self, model_id: str) -> bool:
        """Refreshes this model to reflect the latest structures (schemas, views, fields) from the data source.
        This will remove any structures that are no longer present in the source, but will not remove anything
        created by users.

        Args:
            model_id (str): The ID of the Omni model to refresh.

        Returns:
            : True if successful.
        """
        self.post(f"/v0/model/{model_id}/refresh")
        return True

    def get(self, path: str, params: dict | None = None) -> dict:
        """Makes a GET request to the Omni REST API.

        Args:
            path: The path in the Omni REST API to make a GET request.
            params: Query string parameters to use in the GET request.

        Returns:
            JSON response from the Omni REST API.
        """
        return self._request("GET", path, params=params)

    def post(self, path: str, json_data: dict | None = None) -> dict:
        """Makes a POST request to the Omni REST API.

        Args:
            path: The path in the Omni REST API to make a POST request.
            json_data: Query string parameters to use in the POST request.

        Returns:
            JSON response from the Omni REST API.
        """
        return self._request("POST", path, json_data=json_data)

    def put(self, path: str, json_data: dict | None = None) -> dict:
        """Makes a PUT request to the Omni REST API.

        Args:
            path: The path in the Omni REST API to make a PUT request.
            json_data: Query string parameters to use in the PUT request.

        Returns:
            JSON response from the Omni REST API.
        """
        return self._request("PUT", path, json_data=json_data)

    def delete(self, path: str) -> dict:
        """Makes a DELETE request to the Omni REST API.

        Returns:
            JSON response from the Omni REST API.
        """
        return self._request("DELETE", path)

    def _get_url(self, path: str) -> str:
        return f"{self.base_url.strip('/')}/{path.strip('/')}"

    def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        json_data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        response = requests.request(
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}"},
            url=self._get_url(path),
            json=json_data,
            params=params,
        )
        response.raise_for_status()
        return response.json()
