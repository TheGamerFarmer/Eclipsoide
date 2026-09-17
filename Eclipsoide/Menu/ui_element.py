import pygame as pg


class Button:
    # Bref effet d'enfoncement au clic, pour un retour tactile immédiat
    PRESS_DURATION = 150  # ms
    PRESS_OFFSET = 3  # px, décalage vers le bas au pic de l'enfoncement

    def __init__(self, x, y, width, height, text, font, image_path, text_color=(255, 255, 255)):
        self.rect = pg.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.text_color = text_color
        self.is_hovered = False
        self.press_start: int | None = None

        self.image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.image, (width, height))

        self.hover_overlay = pg.Surface((width, height), pg.SRCALPHA)
        self.hover_overlay.fill((255, 255, 255, 50))

    def draw(self, surface):
        offset_y = 0
        if self.press_start is not None:
            elapsed = pg.time.get_ticks() - self.press_start
            if elapsed < Button.PRESS_DURATION:
                offset_y = int(Button.PRESS_OFFSET * (1 - elapsed / Button.PRESS_DURATION))
            else:
                self.press_start = None

        draw_rect = self.rect.move(0, offset_y)
        surface.blit(self.image, draw_rect)

        if self.is_hovered:
            surface.blit(self.hover_overlay, draw_rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.press_start = pg.time.get_ticks()
                return True
        return False


class Checkbox:
    def __init__(self, x, y, text, font, img_unchecked_path, img_checked_path, start_state=True,
                 text_color=(255, 255, 255)):
        self.font = font
        self.text = text
        self.text_color = text_color
        self.is_checked = start_state

        self.img_unchecked = pg.image.load(img_unchecked_path).convert_alpha()
        self.img_checked = pg.image.load(img_checked_path).convert_alpha()

        self.size = 38
        self.img_unchecked = pg.transform.scale(self.img_unchecked, (self.size, self.size))
        self.img_checked = pg.transform.scale(self.img_checked, (self.size, self.size))

        self.rect = pg.Rect(x, y, self.size, self.size)

    def draw(self, surface):
        current_img = self.img_checked if self.is_checked else self.img_unchecked
        surface.blit(current_img, self.rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (self.rect.right + 15, self.rect.centery - text_surface.get_height() // 2))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_checked = not self.is_checked
                return True
        return False


class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val, img_track_path, img_handle_path):
        self.rect = pg.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = round(max(min_val, min(start_val, max_val)))
        self.is_dragging = False

        self.img_track = pg.image.load(img_track_path).convert_alpha()
        self.img_track = pg.transform.scale(self.img_track, (width, 20))

        self.img_handle = pg.image.load(img_handle_path).convert_alpha()
        self.img_handle = pg.transform.scale(self.img_handle, (28, 38))

    def draw(self, surface):
        surface.blit(self.img_track, self.rect)

        # Le curseur reste entièrement sur la barre : à max_val son bord droit
        # touche le bout de la barre au lieu de déborder de moitié
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + self._travel() * ratio
        handle_y = self.rect.centery - (self.img_handle.get_height() // 2)

        surface.blit(self.img_handle, (handle_x, handle_y))

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            click_rect = pg.Rect(self.rect.x, self.rect.y - 10, self.rect.width, 40)
            if click_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_val(event.pos[0])

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pg.MOUSEMOTION and self.is_dragging:
            self._update_val(event.pos[0])

    def _travel(self):
        """ Distance parcourue par le bord gauche du curseur entre min et max """
        return self.rect.width - self.img_handle.get_width()

    def _update_val(self, mouse_x):
        # On vise le centre du curseur sur la souris
        rel_x = mouse_x - self.rect.x - self.img_handle.get_width() / 2
        ratio = max(0.0, min(rel_x / self._travel(), 1.0))
        self.val = round(self.min_val + ratio * (self.max_val - self.min_val))


class Stat:
    def __init__(self, x, y, width, height, stat, amount, showName, couleur=(70, 70, 70), text_couleur=(255, 255, 255)):
        self.x, self.y, self.width, self.height = x, y, width, height;
        self.stat, self.amount, self.showName = stat, amount, showName;
        self.couleur = couleur, text_couleur = text_couleur