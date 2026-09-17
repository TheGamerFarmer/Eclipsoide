import pygame as pg

import settings

MENU_MUSIC = 'Eclipsoide/audios/track-2.ogg'
GAME_MUSIC = 'Eclipsoide/audios/track-1.ogg'

# Morceau actuellement chargé dans le mixer (None si aucun)
_current_track: str | None = None
# Vrai pendant la pause du jeu : la musique reste coupée quel que soit le réglage
_paused = False


def play_music(track: str):
    """ Lance le morceau en boucle, sans le redémarrer s'il est déjà en cours """
    global _current_track
    if track != _current_track:
        # Le jeu doit rester jouable sans périphérique audio
        try:
            pg.mixer.music.load(track)
        except (pg.error, FileNotFoundError) as e:
            print(f"Impossible de charger la musique {track} : {e}")
            return
        _current_track = track
        pg.mixer.music.play(-1)
    apply_settings()


def apply_settings():
    """ Applique le volume et l'option musique (à appeler après le menu options) """
    if _current_track is None:
        return
    pg.mixer.music.set_volume(settings.OPTIONS["volume"] / 100)
    if settings.OPTIONS["music"] and not _paused:
        pg.mixer.music.unpause()
    else:
        pg.mixer.music.pause()


def set_paused(paused: bool):
    """ Coupe (ou relance) la musique et les bruitages pendant la pause du jeu """
    global _paused
    if paused == _paused:
        return
    _paused = paused
    if paused:
        pg.mixer.pause()
    else:
        pg.mixer.unpause()
    apply_settings()
