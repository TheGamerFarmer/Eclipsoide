import json
import os

SETTINGS_FILE = "settings.json"

OPTIONS = {
    "volume": 50.0,
    "music": True,
    "sfx": True,
    "fullscreen": False,
    # Historique des scores, du plus ancien au plus récent
    "scores": []
}

# Nombre de scores conservés dans l'historique
MAX_SCORES = 20

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

def add_score(score: int):
    """ Ajoute un score à l'historique (les plus anciens sont oubliés) et sauvegarde """
    scores = OPTIONS.setdefault("scores", [])
    scores.append(int(score))
    # On ne garde que les MAX_SCORES dernières parties
    del scores[:-MAX_SCORES]
    save_settings()

def last_scores(count: int = 3) -> list[int]:
    """ Retourne les derniers scores joués, du plus récent au plus ancien """
    scores = OPTIONS.get("scores", [])
    return list(reversed(scores[-count:]))