"""
Utility class for version management and retrieving release information

This module provides the following features:
- Get the current application version
- Retrieve and cache the latest version information
- Compare versions and check for updates
- Get release notes

Dependencies:
- requests: For making HTTP requests to retrieve version information
"""

import os
import json
import requests

from app.common import resource_path

from logging import getLogger
logger = getLogger(__name__)


# Base URL for the server API
VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/"
DEFAULT_TIMEOUT = 5  # Default timeout for network requests


class Release:
    """
    Release information class

    Encapsulates application release information and provides
    methods to access version details
    """

    def __init__(self, version: str):
        """
        Initialize Release object

        Args:
            version (str): Version string
        """
        self.json_path = resource_path(".cache/releases_info.json")
        self._api_url = VERSION_INFO_URL + version
        self._raw_data = {}
        self._version = version
        self._load_data()

    def _load_data(self):
        """Load release data from cache or API"""
        # Try to load from cache first
        if self.json_path and os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    if self._version in cache_data:
                        self._raw_data = cache_data[self._version]
                        return
            except Exception as e:
                logger.error(f"Failed to read releases_info.json: {e}")

        # If not in cache, fetch from API
        self._fetch_from_api()

    def _fetch_from_api(self):
        """Fetch release data from API and cache it"""
        try:
            res = requests.get(self._api_url, timeout=DEFAULT_TIMEOUT)
            res.raise_for_status()
            self._raw_data = res.json()
            
            # Save to cache
            self._save_to_cache()
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching release info for {self._version}: {e}")
        except Exception as e:
            logger.error(f"Error while fetching release info for {self._version}: {e}")

    def _save_to_cache(self):
        """Save release data to cache file"""
        try:
            cache_data = {}
            if self.json_path and os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as f:
                    try:
                        cache_data = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Cache file is corrupted, starting fresh")
                        cache_data = {}
            
            cache_data[self._version] = self._raw_data
            logger.debug(f"Caching release info for version {self._version} - {self._raw_data}")
            
            # Ensure directory exists
            if self.json_path:
                os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error while saving release info to cache: {e}")

    def is_latest(self) -> bool:
        """
        Check if this release is the latest version

        Returns:
            bool: True if this is the latest version
        """
        latest_version = get_latest_version()
        return self._version == latest_version

    def as_json(self) -> dict:
        """
        Get raw release data

        Returns:
            dict: Raw release information data
        """
        return self._raw_data.copy()

    def get_version(self) -> str:
        """
        Get version number

        Returns:
            str: Version number or "unknown" if not available
        """
        return self._raw_data.get("version", "unknown")

    def get_released_at(self) -> str:
        """
        Get release date

        Returns:
            str: Release date or "unknown" if not available
        """
        return self._raw_data.get("released_at", "unknown")

    def get_release_note(self) -> str:
        """
        Get release notes

        Returns:
            str: Release notes in Markdown format or "No release notes available" if not available
        """
        return self._raw_data.get("release_notes", "No release notes available")

    def get_release_url(self) -> str:
        """
        Get API URL for this release

        Returns:
            str: API URL or "unknown" if not available
        """
        return self._api_url if self._api_url else "unknown"


def get_installed_version() -> str:
    """
    Get the current installed application version number

    Returns:
        str: Version number string or "unknown" if not available
    """
    try:
        version_path = resource_path("app/resources/version")
        if version_path and os.path.exists(version_path):
            with open(version_path, "r") as f:
                return f.read().strip()
        else:
            raise FileNotFoundError("Version file not found")
    except Exception as e:
        logger.error(f"Error getting installed version: {e}")
        return "unknown"


def get_latest_version() -> str:
    """
    Get the latest version number from API

    Returns:
        str: Latest version number or "unknown" if retrieval fails
    """
    try:
        res = requests.get(VERSION_INFO_URL + "latest/version", timeout=DEFAULT_TIMEOUT)
        res.raise_for_status()
        data = res.json()
        return data.get("version", "unknown")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching latest version: {e}")
        return "unknown"
    except Exception as e:
        logger.error(f"Error while fetching latest version: {e}")
        return "unknown"


def get_installed_release() -> Release:
    """
    Get Release object for the currently installed version

    Returns:
        Release: Release object for installed version
    """
    version = get_installed_version()
    return Release(version)


def get_release(version: str) -> Release:
    """
    Get Release object for specified version

    Args:
        version (str): Version string

    Returns:
        Release: Release object for specified version
    """
    return Release(version)


def fetch_release_info(version: str) -> None:
    """
    Fetch and cache release information for specified version

    Args:
        version (str): Version string to fetch
    """
    release = Release(version)
    # Release object automatically fetches and caches the data during initialization