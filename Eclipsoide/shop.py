import math
import pygame as pg

def get_damage(lvl) -> int:
    return round(20 * pow(1.2, lvl), 0)

class Shop:
    # Anneau coloré qui pulse brièvement autour du vaisseau à chaque achat,
    # la couleur variant selon le type d'amélioration (confirmation visuelle)
    PURCHASE_FLASH_DURATION = 500  # ms
    PURCHASE_FLASH_COLORS = {
        "damage": (255, 80, 80),
        "cadence": (80, 180, 255),
        "health": (120, 255, 140),
        "heart": (255, 120, 150),
        "multi_shot": (200, 120, 255),
    }

    # Contour qui pulse doucement autour d'un item dès qu'il devient abordable,
    # pour attirer l'oeil au lieu de se fier au seul changement de couleur statique
    AFFORD_PULSE_PERIOD = 700  # ms pour un cycle complet
    AFFORD_PULSE_MIN_ALPHA = 130
    AFFORD_PULSE_MAX_ALPHA = 255
    AFFORD_PULSE_COLOR = (150, 255, 150)

    # Retour tactile immédiat sur le bouton cliqué/appuyé (indépendant du succès
    # de l'achat) : léger enfoncement qui revient à sa place
    PRESS_DURATION = 150  # ms
    PRESS_OFFSET = 3  # px, décalage vers le bas au pic de l'enfoncement

    # Secousse + flash rouge quand l'achat est refusé faute de pièces
    REJECT_FLASH_DURATION = 300  # ms
    REJECT_SHAKE_MAGNITUDE = 4  # px
    REJECT_COLOR = (255, 60, 60)

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        self.purchase_flash_start: int | None = None
        self.purchase_flash_color = (255, 255, 255)
        self.press_item_id: str | None = None
        self.press_start: int | None = None
        self.reject_item_id: str | None = None
        self.reject_flash_start: int | None = None

        # Polices et icones
        self.font_title = pg.font.SysFont("arial", 14, bold=True)
        self.font_desc = pg.font.SysFont("arial", 13, bold=True)
        self.small_coin = pg.transform.scale(pg.image.load('Eclipsoide/images/ui/Coins/coin_0.png'), (14, 14))

        # Données du shop
        self.items = {
            "damage": {"id": "damage", "name": "Damage", "lvl": 0, "max": float('inf'), "base_price": 50, "price": 50,
             "key_str": "1", "keys": (pg.K_1, pg.K_KP1), "unicode": ["1", "&"]},
            "cadence": {"id": "cadence", "name": "Fire rate", "lvl": 0, "max": float('inf'), "base_price": 50, "price": 50,
             "key_str": "2", "keys": (pg.K_2, pg.K_KP2), "unicode": ["2", "é"]},
            "health": {"id": "health", "name": "Max health", "lvl": 1, "max": 5, "base_price": 100, "price": 100, "key_str": "3",
             "keys": (pg.K_3, pg.K_KP3), "unicode": ["3", '"']},
            "heart": {"id": "heart", "name": "Heart chance", "lvl": 0, "max": 5, "base_price": 100, "price": 100, "key_str": "4",
             "keys": (pg.K_4, pg.K_KP4), "unicode": ["4", "'"]},
            "multi_shot": {"id": "multi_shot", "name": "Multi shot", "lvl": 1, "max": float('inf'), "base_price": 2500, "price": 2500, "key_str": "5",
             "keys": (pg.K_5, pg.K_KP5), "unicode": ["5", "("]}
        }
        self.rects = []

    def draw(self):
        btn_w = 190
        btn_h = 50
        spacing = 10
        total_w = (btn_w * 5) + (spacing * 4)

        start_x = (self.screen.get_width() - total_w) // 2
        y = self.screen.get_height() - btn_h - 15

        self.rects.clear()

        for i, item in enumerate(self.items.values()):
            x = start_x + i * (btn_w + spacing)
            self.rects.append((pg.Rect(x, y, btn_w, btn_h), item))

            is_max = item['lvl'] >= item['max']  # type: ignore
            is_locked = self._is_lock(item)
            can_afford = not is_max and not is_locked and self.player.coins >= item['price']

            if is_max or is_locked:
                bg_color = (30, 30, 30, 150)
                border_color = (60, 60, 60, 255)
            elif can_afford:
                bg_color = (50, 60, 50, 220)
                border_color = (100, 255, 100, 255)
            else:
                bg_color = (30, 30, 30, 180)
                border_color = (100, 100, 100, 255)

            # Enfoncement bref au clic/appui, indépendant du résultat de l'achat
            press_offset_y = 0
            if self.press_item_id == item['id'] and self.press_start is not None:
                press_elapsed = pg.time.get_ticks() - self.press_start
                if press_elapsed < self.PRESS_DURATION:
                    press_progress = press_elapsed / self.PRESS_DURATION
                    press_offset_y = int(self.PRESS_OFFSET * (1 - press_progress))
                else:
                    self.press_item_id = None
                    self.press_start = None

            # Secousse + flash rouge si l'achat vient d'être refusé (fonds insuffisants)
            reject_offset_x = 0
            reject_alpha = 0
            if self.reject_item_id == item['id'] and self.reject_flash_start is not None:
                reject_elapsed = pg.time.get_ticks() - self.reject_flash_start
                if reject_elapsed < self.REJECT_FLASH_DURATION:
                    reject_progress = reject_elapsed / self.REJECT_FLASH_DURATION
                    shake_mag = self.REJECT_SHAKE_MAGNITUDE * (1 - reject_progress)
                    reject_offset_x = int(shake_mag * math.sin(reject_elapsed * 0.1))
                    reject_alpha = int(200 * (1 - reject_progress))
                else:
                    self.reject_item_id = None
                    self.reject_flash_start = None

            ix = x + reject_offset_x
            iy = y + press_offset_y

            panel = pg.Surface((btn_w, btn_h), pg.SRCALPHA)
            panel.fill(bg_color)
            pg.draw.rect(panel, border_color, panel.get_rect(), 2)
            if reject_alpha > 0:
                red_overlay = panel.copy()
                red_overlay.fill((*self.REJECT_COLOR, 0), special_flags=pg.BLEND_RGBA_ADD)
                red_overlay.set_alpha(reject_alpha)
                panel.blit(red_overlay, (0, 0))
            self.screen.blit(panel, (ix, iy))

            if can_afford:
                pulse = (math.sin(pg.time.get_ticks() * (2 * math.pi / self.AFFORD_PULSE_PERIOD)) + 1) / 2
                alpha = int(self.AFFORD_PULSE_MIN_ALPHA + (self.AFFORD_PULSE_MAX_ALPHA - self.AFFORD_PULSE_MIN_ALPHA) * pulse)
                highlight = pg.Surface((btn_w + 8, btn_h + 8), pg.SRCALPHA)
                pg.draw.rect(highlight, (*self.AFFORD_PULSE_COLOR, alpha), highlight.get_rect(), width=3, border_radius=4)
                self.screen.blit(highlight, (ix - 4, iy - 4))

            # 1. Titre
            titre_texte = f"{item['name']} [{item['key_str']}]"
            color_titre = (150, 150, 150) if is_max else (255, 255, 255)
            titre_surf = self.font_title.render(titre_texte, True, color_titre)
            self.screen.blit(titre_surf, (ix + 8, iy + 8))

            # 2. Prix
            if not is_max and not self._is_lock(item):
                prix_surf = self.font_title.render(str(item['price']), True, (255, 220, 80))
                prix_w = prix_surf.get_width()
                icon_w = self.small_coin.get_width()
                prix_x = ix + btn_w - 8 - icon_w - 4 - prix_w
                self.screen.blit(prix_surf, (prix_x, iy + 8))
                self.screen.blit(self.small_coin, (prix_x + prix_w + 4, iy + 8))

            # 3. Niveau
            lvl_str = ''
            mult_str = None

            lvl = item['lvl']
            match item['id']:
                case 'damage':
                    lvl_str = f"Level {lvl}"
                    mult_str = f"{int(get_damage(lvl))}"
                case 'cadence':
                    lvl_str = f"Level {lvl}"
                    mult_str = f"x{round(1 + 0.05 * lvl, 2)}"
                case 'health':
                    lvl_str = f"{lvl} / {item['max']}"
                    mult_str = None
                case 'heart':
                    if self._is_lock(item):
                        lvl_str = "Lock"
                        mult_str = None
                    else:
                        lvl_str = f"Level {lvl}"
                        mult_str = f"{1 * lvl}%"
                case 'multi_shot' :
                    lvl_str = f"Level {lvl}"
                    mult_str = f"x{1 * lvl}"

            color_lvl = (100, 150, 150) if is_max else (170, 245, 255)
            self.screen.blit(self.font_desc.render(lvl_str, True, color_lvl), (ix + 8, iy + 28))

            if mult_str:
                mult_surf = self.font_desc.render(mult_str, True, (150, 255, 150))
                self.screen.blit(mult_surf, (ix + btn_w - 8 - mult_surf.get_width(), iy + 28))

        self._draw_purchase_flash()

    def _draw_purchase_flash(self):
        if self.purchase_flash_start is None:
            return

        elapsed = pg.time.get_ticks() - self.purchase_flash_start
        if elapsed >= self.PURCHASE_FLASH_DURATION:
            self.purchase_flash_start = None
            return

        progress = elapsed / self.PURCHASE_FLASH_DURATION
        alpha = int(220 * (1 - progress))
        radius = int(self.player.rect.width * 0.9 + 14 * progress)
        size = radius * 2 + 8
        surface = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(surface, (*self.purchase_flash_color, alpha), (size // 2, size // 2), radius, 4)
        self.screen.blit(surface, surface.get_rect(center=self.player.rect.center))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for rect, item in self.rects:
                if rect.collidepoint(event.pos):
                    self._trigger_press(item['id'])
                    self._buy_upgrade(item)

        elif event.type == pg.KEYDOWN:
            for item in self.items.values():
                if event.key in item['keys'] or event.unicode in item['unicode']:
                    self._trigger_press(item['id'])
                    self._buy_upgrade(item)

    def _trigger_press(self, item_id):
        self.press_item_id = item_id
        self.press_start = pg.time.get_ticks()

    def _trigger_reject(self, item_id):
        self.reject_item_id = item_id
        self.reject_flash_start = pg.time.get_ticks()

    def _buy_upgrade(self, item):
        if item['lvl'] < item['max']:

            if self.player.coins >= item['price']:

                self.player.coins -= item['price']
                item['lvl'] += 1

                nouveau_prix = 0

                match item['id']:
                    case 'damage':
                        nouveau_prix = round(item['base_price'] * pow(1.2, item['lvl']), 0)
                        self.player.damage = get_damage(item['lvl'])
                    case 'cadence':
                        nouveau_prix = round(item['base_price'] * pow(1.25, item['lvl']), 0)
                        self.player.fire_delay = 500 / (1 + 0.05 * item['lvl'])
                    case 'health':
                        nouveau_prix = item['base_price'] * (2 ** item['lvl'] - 1)
                        self.player.max_lives += 1
                        self.player.lives += 1
                    case 'heart':
                        nouveau_prix = round(item['base_price'] * (1.5 ** item['lvl']), 0)
                        self.player.heart_drop_chance += 0.01
                    case 'multi_shot':
                        nouveau_prix = item['base_price'] * (2 ** item['lvl'])
                        self.player.nb_shot += 1

                item['price'] = nouveau_prix

                self.purchase_flash_start = pg.time.get_ticks()
                self.purchase_flash_color = self.PURCHASE_FLASH_COLORS.get(item['id'], (255, 255, 255))
            else:
                self._trigger_reject(item['id'])

    def _is_lock(self, item):
        return item["id"] == "heart" and self.items["health"]["lvl"] == 1
