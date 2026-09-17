import os
import pygame as pg

from coin import Coin


class Shop:
    # Anneau coloré qui pulse brièvement autour du vaisseau à chaque achat,
    # la couleur variant selon le type d'amélioration (confirmation visuelle)
    PURCHASE_FLASH_DURATION = 500  # ms
    PURCHASE_FLASH_COLORS = {
        "damage": (255, 80, 80),
        "cadence": (80, 180, 255),
        "health": (120, 255, 140),
        "double": (200, 120, 255),
        "coin": (255, 210, 60),
    }

    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        self.purchase_flash_start: int | None = None
        self.purchase_flash_color = (255, 255, 255)

        # Polices et icones
        self.font_title = pg.font.SysFont("arial", 14, bold=True)
        self.font_desc = pg.font.SysFont("arial", 13, bold=True)
        self.small_coin = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (14, 14))

        # Données du shop
        self.items = [
            {"id": "damage", "name": "Degats", "lvl": 0, "max": float('inf'), "base_price": 100, "price": 100,
             "key_str": "1", "keys": (pg.K_1, pg.K_KP1), "unicode": ["1", "&"], "mult": "x1"},
            {"id": "cadence", "name": "Cadence de tir", "lvl": 0, "max": float('inf'), "base_price": 100, "price": 100,
             "key_str": "2", "keys": (pg.K_2, pg.K_KP2), "unicode": ["2", "é"], "mult": "x1"},
            {"id": "health", "name": "Vie Max", "lvl": 0, "max": 4, "base_price": 150, "price": 150, "key_str": "3",
             "keys": (pg.K_3, pg.K_KP3), "unicode": ["3", '"']},
            {"id": "double", "name": "Tir Double", "lvl": 0, "max": 1, "base_price": 1500, "price": 1500, "key_str": "4",
             "keys": (pg.K_4, pg.K_KP4), "unicode": ["4", "'"]},
            {"id": "coin", "name": "Coins x2", "lvl": 0, "max": 1, "base_price": 800, "price": 800, "key_str": "5",
             "keys": (pg.K_5, pg.K_KP5), "unicode": ["5", "("]}
        ]
        self.rects = []

    def draw(self):
        btn_w = 190
        btn_h = 50
        spacing = 10
        total_w = (btn_w * 5) + (spacing * 4)

        start_x = (self.screen.get_width() - total_w) // 2
        y = self.screen.get_height() - btn_h - 15

        self.rects.clear()

        for i, item in enumerate(self.items):
            x = start_x + i * (btn_w + spacing)
            self.rects.append((pg.Rect(x, y, btn_w, btn_h), item))

            is_max = item['lvl'] >= item['max']  # type: ignore
            can_afford = not is_max and self.player.coins >= item['price']

            if is_max:
                bg_color = (30, 30, 30, 150)
                border_color = (60, 60, 60, 255)
            elif can_afford:
                bg_color = (50, 60, 50, 220)
                border_color = (100, 255, 100, 255)
            else:
                bg_color = (30, 30, 30, 180)
                border_color = (100, 100, 100, 255)

            panel = pg.Surface((btn_w, btn_h), pg.SRCALPHA)
            panel.fill(bg_color)
            pg.draw.rect(panel, border_color, panel.get_rect(), 2)
            self.screen.blit(panel, (x, y))

            # 1. Titre
            titre_texte = f"{item['name']} [{item['key_str']}]"
            color_titre = (150, 150, 150) if is_max else (255, 255, 255)
            titre_surf = self.font_title.render(titre_texte, True, color_titre)
            self.screen.blit(titre_surf, (x + 8, y + 8))

            # 2. Prix
            if not is_max:
                prix_surf = self.font_title.render(str(item['price']), True, (255, 220, 80))
                prix_w = prix_surf.get_width()
                icon_w = self.small_coin.get_width()
                prix_x = x + btn_w - 8 - icon_w - 4 - prix_w
                self.screen.blit(prix_surf, (prix_x, y + 8))
                self.screen.blit(self.small_coin, (prix_x + prix_w + 4, y + 8))

            # 3. Niveau
            lvl = item['lvl']
            if item['id'] in ['damage', 'cadence']:
                lvl_str = f"Niveau {lvl}"
                mult_str = f"x{round(1 + 0.10 * lvl, 1)}"
            elif item['id'] == 'health':
                lvl_str = f"{lvl} / {item['max']}"
                mult_str = None
            else:
                lvl_str = "Acquis" if lvl > 0 else "Non acquis"
                mult_str = None

            color_lvl = (100, 150, 150) if is_max else (170, 245, 255)
            self.screen.blit(self.font_desc.render(lvl_str, True, color_lvl), (x + 8, y + 28))

            if mult_str:
                mult_surf = self.font_desc.render(mult_str, True, (150, 255, 150))
                self.screen.blit(mult_surf, (x + btn_w - 8 - mult_surf.get_width(), y + 28))

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
                    self._buy_upgrade(item)

        elif event.type == pg.KEYDOWN:
            for item in self.items:
                if event.key in item['keys'] or event.unicode in item['unicode']:
                    self._buy_upgrade(item)

    def _buy_upgrade(self, item):
        if item['lvl'] < item['max']:

            if self.player.coins >= item['price']:

                self.player.coins -= item['price']
                item['lvl'] += 1

                nouveau_prix = int(round(item['base_price'] * (1.25 ** item['lvl']) / 10) * 10)
                item['price'] = nouveau_prix

                if item['id'] == 'damage':
                    self.player.damage = 20 * (1 + 0.10 * item['lvl'])
                elif item['id'] == 'cadence':
                    self.player.fire_delay = 300 / (1 + 0.10 * item['lvl'])
                elif item['id'] == 'health':
                    self.player.max_lives += 1
                    self.player.lives += 1
                elif item['id'] == 'double':
                    self.player.double_shot = True
                elif item['id'] == 'coin':
                    Coin.value = 40

                self.purchase_flash_start = pg.time.get_ticks()
                self.purchase_flash_color = self.PURCHASE_FLASH_COLORS.get(item['id'], (255, 255, 255))