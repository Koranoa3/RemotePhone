"""
Host configuration io module.
"""

import json

config_path = "host_config.json"
default_config_path = "app/resources/host_config_default.json"

def _get_default_config():
    with open(default_config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _verify_config(config):
    default_config = _get_default_config()
    for key in default_config:
        if key not in config:
            return False
    return True

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
    if not _verify_config(config):
        raise ValueError("Config missing required keys.")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)