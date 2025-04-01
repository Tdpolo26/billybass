import json, os

SETTINGS_FILE = "settings.json"
settings = {
    "volume": 1.0,
    "pwm": {"mouth": 100, "body": 60, "tail": 50},
    "smoothing": 5,
    "favorites": [],
    "autoplay": False
}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings.update(json.load(f))

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def delete_track(path):
    import os
    base = os.path.splitext(path)[0]
    try:
        os.remove(path)
        os.remove(base + ".json")
    except:
        pass
