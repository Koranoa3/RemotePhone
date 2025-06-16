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

def safe_resource_path(relative_path: str) -> str:
    """
    Wrapper for resource_path to handle edge cases like missing files or incorrect paths.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource, or None if the path is invalid.
    """
    try:
        path = resource_path(relative_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Resource not found: {path}")
        return path
    except Exception as e:
        logger.error(f"Error resolving resource path for {relative_path}: {e}")
        return None

from app.common import resource_path

# Base URL for the server API
VERSION_INFO_URL = "http://skyboxx.tplinkdns.com:8000/api/releases/"
DEFAULT_TIMEOUT = 5  # Default timeout for network requests


class Version:
    """
    Version management class

    Manages application version information and provides
    functions to retrieve and cache the latest info from the server
    """

    @staticmethod
    def get_current() -> dict:
        """
        Get details of the current version

        Returns:
            dict: Details of the current version (including release notes)
                  If it's the latest version, returns the result of get_latest()
                  Returns None if retrieval fails
        """
        # If it's the latest version, return the latest info
        if Version.is_latest():
            return Version.get_latest()

        # Get the current version number
        version = Version.get_current_version()
        current_path = safe_resource_path("app/resources/current_release.json")
        current_json = None

        # If the cache file exists, load it
        if os.path.exists(current_path):
            try:
                with open(current_path, "r", encoding="utf-8") as f:
                    current_json = json.load(f)

                # If the cached version matches the current version
                saved_version = current_json.get("version")
                if saved_version == version:
                    return current_json
            except Exception as e:
                logger.error(f"Failed to read current_release.json: {e}")

        # If the cache is invalid or the version is different, get from server
        try:
            res = requests.get(VERSION_INFO_URL + version, timeout=DEFAULT_TIMEOUT)
            res.raise_for_status()
            current_json = res.json()

            # Save the retrieved info to cache
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w", encoding="utf-8") as f:
                json.dump(current_json, f, ensure_ascii=False, indent=2)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching the current version info: {e}")
            return None
        except OSError as e:
            logger.error(f"File system error while saving the current version info: {e}")
            return None

    @staticmethod
    def get_current_version() -> str:
        """
        Get the current application version number

        Reads the version string from the version file

        Returns:
            str: Version number string (e.g., "v1.0.0")
                 Returns "unknown" if the file does not exist
        """
        try:
            version_path = safe_resource_path("app/resources/version")
            if version_path:
                with open(version_path, "r") as f:
            # Read the version number from the version file
                    try:
                        with open(resource_path("app/resources/version"), "r") as f:
                            return f.read().strip()
                    except Exception as e:
                        import logging
                        logging.error(f"Error reading version file: {e}")
                        return "unknown"
        except FileNotFoundError:
            # If the version file is not found
            return "unknown"
        except Exception as e:
            # For other errors
            return "unknown"

    @staticmethod
    def get_latest() -> dict:
        """
        Get details of the latest version

        Retrieves the latest info from the server and caches it locally

        Returns:
            dict: Details of the latest version (version number, release notes, etc.)
                  Returns None if retrieval fails
        """
        latest_path = resource_path("app/resources/latest_release.json")
        current_version = Version.get_current_version()
        latest_json = None

        # If the cache file exists, load it
        if os.path.exists(latest_path):
            try:
                with open(latest_path, "r", encoding="utf-8") as f:
                    latest_json = json.load(f)

                # If the cached latest version matches the current version
                latest_version = latest_json.get("version")
                if latest_version == current_version:
                    return latest_json
            except Exception as e:
                logger.error(f"Failed to read latest_release.json: {e}")
        try:
            res = requests.get(VERSION_INFO_URL + "latest", timeout=DEFAULT_TIMEOUT)
            res.raise_for_status()
            latest_json = res.json()

            # Save the retrieved latest info to cache
            os.makedirs(os.path.dirname(latest_path), exist_ok=True)
            with open(latest_path, "w", encoding="utf-8") as f:
                json.dump(latest_json, f, ensure_ascii=False, indent=2)

            return latest_json
        except requests.exceptions.RequestException as e:
            print(f"[Error] Network error while fetching the latest version info: {e}")
            return None
        except OSError as e:
            print(f"[Error] File system error while saving the latest version info: {e}")
            return None

    @staticmethod
    def get_latest_version() -> str:
        """
        Get only the latest version number

        Returns:
            str: Latest version number (e.g., "1.2.0")
                 Returns None if retrieval fails
        """
        latest_json = Version.get_latest()
        if latest_json and isinstance(latest_json, dict):
            return latest_json.get("version")
        return None

    @staticmethod
    def get_latest_release_notes() -> str:
        """
        Get the release notes for the latest version

        Returns:
            str: Release notes for the latest version (in Markdown format)
                 Returns None if retrieval fails
        """
        latest_json = Version.get_latest()
        if latest_json and isinstance(latest_json, dict):
            return latest_json.get("release_notes")
        return None

    @staticmethod
    def is_latest() -> bool:
        """
        Determine if the current version is the latest

        Compares the current version and the latest version

        Returns:
            bool: True = latest, False = outdated
                  Returns False if the latest version info cannot be retrieved
        """
        current_version = Version.get_current_version()
        latest_version = Version.get_latest_version()

        # Compare only if both versions can be retrieved
        return current_version == latest_version if latest_version else False