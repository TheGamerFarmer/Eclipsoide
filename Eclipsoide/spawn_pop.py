def ease_out_back(progress: float, overshoot: float = 1.70158) -> float:
    """ 0 -> 1 avec un léger dépassement au-dessus de 1 avant de s'y stabiliser
    (ease-out-back) : utilisé pour un effet de "pop" à la naissance d'un sprite """
    t = max(0.0, min(1.0, progress)) - 1
    c3 = overshoot + 1
    return max(0.0, 1 + c3 * t ** 3 + overshoot * t ** 2)


def spawn_scale(timer: float, duration: float, overshoot: float = 1.70158) -> float:
    """ Échelle à appliquer pendant SPAWN_ANIM_DURATION-timer/DURATION ms après la
    naissance d'un sprite : 0 au tout début, dépasse légèrement 1 puis s'y stabilise """
    if duration <= 0:
        return 1.0
    progress = 1 - (timer / duration)
    return ease_out_back(progress, overshoot)
