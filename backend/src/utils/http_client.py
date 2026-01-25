"""
Simple HTTP client for making requests to external services
"""

import aiohttp
from typing import Dict, Any, Optional


class HttpClient:
    """
    Simple HTTP client for making requests to external services
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}

    async def post(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a POST request to the specified endpoint

        Args:
            endpoint: API endpoint to call
            json: JSON payload to send

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json, headers=self.headers) as response:
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during HTTP request: {str(e)}")

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a GET request to the specified endpoint

        Args:
            endpoint: API endpoint to call

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during HTTP request: {str(e)}")

    async def put(self, endpoint: str, json: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a PUT request to the specified endpoint

        Args:
            endpoint: API endpoint to call
            json: JSON payload to send

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=json, headers=self.headers) as response:
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during HTTP request: {str(e)}")

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request to the specified endpoint

        Args:
            endpoint: API endpoint to call

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    result = await response.json()
                    return result
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during HTTP request: {str(e)}")