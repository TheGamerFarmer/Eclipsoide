import json
import os

SETTINGS_FILE = "settings.json"

OPTIONS = {
    "volume": 50.0,
    "music": True,
    "sfx": True,
    "fullscreen": False
}

def load_settings():
    global OPTIONS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                OPTIONS.update(json.load(f))
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres : {e}")

def save_settings():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(OPTIONS, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des paramètres : {e}")