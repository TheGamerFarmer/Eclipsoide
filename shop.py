import pygame as pg

def get_damage(lvl) -> int:
    return round(20 * pow(1.2, lvl), 0)

class Shop:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        # Polices et icones
        self.font_title = pg.font.SysFont("arial", 14, bold=True)
        self.font_desc = pg.font.SysFont("arial", 13, bold=True)
        self.small_coin = pg.transform.scale(pg.image.load('images/ui/Coins/coin_0.png'), (14, 14))

        # Données du shop
        self.items = {
            "damage": {"id": "damage", "name": "Damage", "lvl": 0, "max": float('inf'), "base_price": 50, "price": 50,
             "key_str": "1", "keys": (pg.K_1, pg.K_KP1), "unicode": ["1", "&"]},
            "cadence": {"id": "cadence", "name": "Fire rate", "lvl": 0, "max": float('inf'), "base_price": 50, "price": 50,
             "key_str": "2", "keys": (pg.K_2, pg.K_KP2), "unicode": ["2", "é"]},
            "health": {"id": "health", "name": "Max health", "lvl": 1, "max": 5, "base_price": 150, "price": 150, "key_str": "3",
             "keys": (pg.K_3, pg.K_KP3), "unicode": ["3", '"']},
            "heart": {"id": "heart", "name": "Heart chance", "lvl": 0, "max": 5, "base_price": 500, "price": 500, "key_str": "4",
             "keys": (pg.K_5, pg.K_KP5), "unicode": ["4", "'"]},
            "multi_shot": {"id": "multi_shot", "name": "Multi shot", "lvl": 1, "max": float('inf'), "base_price": 2500, "price": 2500, "key_str": "5",
             "keys": (pg.K_4, pg.K_KP4), "unicode": ["5", "("]}
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
                    if self.items["health"]["lvl"] == 1:
                        lvl_str = "Lock"
                        mult_str = None
                    else:
                        lvl_str = f"Level {lvl}"
                        mult_str = f"{10 * lvl}%"
                case 'multi_shot' :
                    lvl_str = f"Level {lvl}"
                    mult_str = f"x{1 * lvl}"

            color_lvl = (100, 150, 150) if is_max else (170, 245, 255)
            self.screen.blit(self.font_desc.render(lvl_str, True, color_lvl), (x + 8, y + 28))

            if mult_str:
                mult_surf = self.font_desc.render(mult_str, True, (150, 255, 150))
                self.screen.blit(mult_surf, (x + btn_w - 8 - mult_surf.get_width(), y + 28))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for rect, item in self.rects:
                if rect.collidepoint(event.pos):
                    self._buy_upgrade(item)

        elif event.type == pg.KEYDOWN:
            for item in self.items.values():
                if event.key in item['keys'] or event.unicode in item['unicode']:
                    self._buy_upgrade(item)

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
                        nouveau_prix = round(item['base_price'] * (2 ** item['lvl']))
                        self.player.max_lives += 1
                        self.player.lives += 1
                    case 'heart':
                        nouveau_prix = round(item['base_price'] * (1.5 ** item['lvl']), 0)
                        self.player.heart_drop_chance += 0.01
                    case 'multi_shot':
                        nouveau_prix = item['base_price'] * (2 ** item['lvl'])
                        self.player.nb_shot += 1

                item['price'] = nouveau_prix