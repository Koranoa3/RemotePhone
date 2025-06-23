import os
import json
import datetime

from app.common import resource_path

from logging import getLogger
logger = getLogger(__name__)

old_registered_uuids_filename = "registered_uuids.txt"
registered_uuids_filename = "registered_uuids.json"
old_uuids_path = resource_path(old_registered_uuids_filename)
uuids_path = resource_path(registered_uuids_filename)

def migrate_registered_uuids():
    if not os.path.exists(uuids_path) and os.path.exists(old_uuids_path):
        uuids = {}
        with open(old_uuids_path, "r") as f:
            for line in f:
                uuid = line.strip()
                if uuid:
                    uuids[uuid] = {}
        with open(uuids_path, "w") as f:
            json.dump(uuids, f, indent=2)
        os.remove(old_uuids_path)
        logger.info(f"Migrated registered UUIDs from {old_uuids_path} to {uuids_path}")

def load_registered_uuids() -> dict:
    migrate_registered_uuids()
    if not os.path.exists(uuids_path):
        with open(uuids_path, "w") as f:
            json.dump({}, f)
        logger.info(f"Created new registered_uuids.json at {uuids_path}")
        return {}
    with open(uuids_path, "r") as f:
        try:
            data = json.load(f)
            logger.debug(f"Loaded registered UUIDs from {uuids_path}")
            return data
        except Exception:
            logger.error("Failed to load registered_uuids.json, resetting file.")
            return {}

def save_registered_uuids(data: dict):
    with open(uuids_path, "w") as f:
        json.dump(data, f, indent=2)
    logger.debug(f"Saved registered UUIDs to {uuids_path}")

def if_uuid_registered(uuid: str) -> bool:
    uuids = load_registered_uuids()
    exists = uuid in uuids
    logger.debug(f"Checked if UUID {uuid} is registered: {exists}")
    return exists

def register_uuid(uuid: str, timestamp=None) -> bool:
    """
    Registers a new UUID with an optional timestamp.
    
    ## Inputs:
        uuid (str): The UUID to register.
        timestamp (datetime, optional): The timestamp of the last connection. If None, current time is used.
    ## Returns:
        bool: True if the UUID was successfully registered, False if it was already registered.
    """
    uuids = load_registered_uuids()
    if uuid in uuids:
        logger.info(f"UUID {uuid} is already registered.")
        return False
    entry = {}
    if timestamp is not None:
        entry["last_connection"] = timestamp
    else:
        entry["last_connection"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uuids[uuid] = entry
    save_registered_uuids(uuids)
    logger.info(f"Registered new UUID: {uuid}")
    return True

def update_last_connection(uuid: str, timestamp=None):
    """
    Updates the last connection timestamp for a registered UUID.

    ## Inputs:
        uuid (str): The UUID to update.
        timestamp (datetime, optional): The new timestamp. If None, current time is used.
    """
    uuids = load_registered_uuids()
    if uuid not in uuids:
        logger.warning(f"UUID {uuid} is not registered, cannot update last connection.")
        return
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uuids[uuid]["last_connection"] = timestamp
    save_registered_uuids(uuids)
    logger.debug(f"Updated last connection for UUID {uuid} to {timestamp}")

def unregister_uuid(uuid: str) -> bool:
    """
    Unregisters a UUID.

    ## Inputs:
        uuid (str): The UUID to unregister.
    ## Returns:
        bool: True if the UUID was successfully unregistered, False if it was not found.
    """
    uuids = load_registered_uuids()
    if uuid not in uuids:
        logger.info(f"UUID {uuid} is not registered, cannot unregister.")
        return False
    del uuids[uuid]
    save_registered_uuids(uuids)
    logger.info(f"Unregistered UUID: {uuid}")
    return True