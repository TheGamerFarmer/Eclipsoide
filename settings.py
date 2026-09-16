import json
import os

import pygame as pg

SETTINGS_FILE = "settings.json"

WINDOW_SIZE = (1024, 768)

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

def best_score() -> int:
    """ Retourne le meilleur score de l'historique (0 si aucune partie jouée) """
    return max(OPTIONS.get("scores", []), default=0)

def last_scores(count: int = 3) -> list[int]:
    """ Retourne les derniers scores joués, du plus récent au plus ancien """
    scores = OPTIONS.get("scores", [])
    return list(reversed(scores[-count:]))


def apply_display_mode() -> pg.Surface:
    """ Crée la fenêtre au premier appel, puis la met en plein écran ou en
    fenêtré selon l'option sauvegardée. L'objet Surface de l'écran reste le
    même : les références existantes (Eclipsoide, menus) restent valides """
    screen = pg.display.get_surface()
    if screen is None:
        if OPTIONS["fullscreen"]:
            return pg.display.set_mode(WINDOW_SIZE, pg.FULLSCREEN | pg.SCALED)
        return pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE | pg.SCALED)

    # Rappeler set_mode avec SCALED échoue sur macOS en repassant en fenêtré
    # ("failed to create renderer") : on bascule la fenêtre existante
    if bool(pg.display.is_fullscreen()) != OPTIONS["fullscreen"]:
        pg.display.toggle_fullscreen()
    return screen

def toggle_fullscreen() -> pg.Surface:
    """ Bascule plein écran <-> fenêtré et sauvegarde le choix """
    OPTIONS["fullscreen"] = not OPTIONS["fullscreen"]
    save_settings()
    return apply_display_mode()
