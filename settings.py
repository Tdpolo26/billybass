import json

# Default settings
DEFAULT_SETTINGS = {
    "volume": 1.0,
    "pwm": {"mouth": 100, "body": 60, "tail": 50},
    "smoothing": 5,
    "favorites": [],
    "autoplay": False
}

SETTINGS_FILE = "settings.json"

def load_settings():
    # Load settings from the settings.json file
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is corrupted, return the default settings
        return DEFAULT_SETTINGS

def save_settings():
    # Save the settings to the settings.json file
    with open(SETTINGS_FILE, "w") as f:
        json.dump(DEFAULT_SETTINGS, f)

settings = load_settings()  # Initialize the settings variable
