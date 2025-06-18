import os, sys

from logging import getLogger
logger = getLogger(__name__)

def resource_path(relative_path: str) -> str:
    """
    Resolves the absolute path to a resource, handling edge cases like missing files or incorrect paths.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource, or None if the path is invalid.
    """
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        path = os.path.join(base_path, relative_path)
        if not os.path.exists(path):
            logger.warning(f"Resource not found: {path}")
        return path
    except Exception as e:
        logger.error(f"Error resolving resource path for {relative_path}: {e}")
        return None
