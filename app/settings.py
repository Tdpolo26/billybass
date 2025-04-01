import json
import os

SETTINGS_FILE = "settings.json"

default_settings = {
    "volume": 1.0,
    "pwm": {"mouth": 100, "body": 60, "tail": 50},
    "smoothing": 5,
    "favorites": [],
    "autoplay": False
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        except Exception:
            settings = {}
    else:
        settings = {}

    # Fill in any missing defaults
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
