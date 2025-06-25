"""
Host configuration io module.
"""

import json

config_path = "host_config.json"
default_config_path = "app/resources/host_config_default.json"

def _get_default_config():
    with open(default_config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _verify_config(config, default_config=None):
    if default_config is None:
        default_config = _get_default_config()
    if not isinstance(config, dict) or not isinstance(default_config, dict):
        return False
    for key, value in default_config.items():
        if key not in config:
            return False
        if isinstance(value, dict):
            if not _verify_config(config[key], value):
                return False
    return True

def _get_changed_items(new_config, old_config):
        result = {}
        for key in new_config:
            if key not in old_config:
                result[key] = None if not isinstance(new_config[key], dict) else {}
            elif isinstance(new_config[key], dict) and isinstance(old_config[key], dict):
                nested = _get_changed_items(new_config[key], old_config[key])
                if nested:
                    result[key] = nested
            elif new_config[key] != old_config[key]:
                result[key] = old_config[key]
        return result

def load():
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = _get_default_config()
        save(config)
    if not _verify_config(config):
        config = _get_default_config()
        save(config)
    return config

def save(config):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            old_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        old_config = _get_default_config()

    changed_keys = _get_changed_items(config, old_config)
    
    if not _verify_config(config):
        raise ValueError("Config missing required keys.")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)