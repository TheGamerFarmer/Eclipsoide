from operator import truediv

import pygame as pg

class Button:
    def __init__(self, x, y, width, height, text, font, couleur=(70,70,70), hover_couleur = (100,100,130), text_couleur = (255, 255, 250)):
        self.is_hovered = False
        self.rect = pg.Rect(x,y,width,height)
        self.font = font
        self.text = text
        self.couleur = couleur
        self.hover_couleur = hover_couleur
        self.text_color = text_couleur
        self.x = x
        self.y = y

    def draw(self, surface):
        #current_couleur = self.hover_couleur if self.is_hovered else self.couleur
        pg.draw.rect(surface, (100,150,100), self.rect, border_radius=8) #current color
        pg.draw.rect(surface, (255,255,255), self.rect, width=2, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self,event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Stat:
    def __init__(self, x,y,width,height,stat,amount,showName, couleur = (70,70,70), text_couleur = (255,255,255)):
        self.x, self.y, self.width, self.height = x,y,width,height; self.stat,self.amount,self.showName = stat, amount, showName; self.couleur = couleur, text_couleur = text_couleur
